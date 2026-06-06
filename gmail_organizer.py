#!/usr/bin/env python3
"""
Organizador de Gmail personal.

Implementa las reglas descritas en prompt_ordenar_gmail.md:
  - Primera corrida = dry-run (no modifica nada, solo informa).
  - Nunca borrado permanente: lo descartado va a Papelera.
  - Lista blanca intocable: todo correo de una PERSONA real se deja en Recibidos.
  - Etiqueta, archiva o manda a Papelera. No interactúa hacia afuera.
  - Registra cada acción en logs/actions-*.jsonl.
  - Mantiene un índice de remitentes (senders.json) y reclasifica los que
    dejan de encajar.

Uso:
    python gmail_organizer.py --dry-run            # informe, no cambia nada
    python gmail_organizer.py --execute            # aplica cambios
    python gmail_organizer.py --execute --full     # toda la casilla
    python gmail_organizer.py --execute --since 1d # solo lo nuevo (default)

La primera vez SIEMPRE corré con --dry-run y revisá el informe antes de --execute.
"""

import argparse
import base64
import datetime as dt
import json
import os
import re
import sys
from pathlib import Path

try:
    from dotenv import load_dotenv
    load_dotenv()
except Exception:  # dotenv es opcional
    pass

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build

import config

# Permisos: leer + modificar (etiquetar, archivar, mandar a Papelera).
# gmail.modify NO permite borrado permanente, lo cual es justo lo que queremos.
SCOPES = ["https://www.googleapis.com/auth/gmail.modify"]

BASE_DIR = Path(__file__).resolve().parent
SENDERS_FILE = BASE_DIR / "senders.json"
LOGS_DIR = BASE_DIR / "logs"


# --------------------------------------------------------------------------
# Autenticación
# --------------------------------------------------------------------------
def get_service():
    creds = None
    token_file = os.getenv("GMAIL_TOKEN_FILE", "token.json")
    creds_file = os.getenv("GMAIL_CREDENTIALS_FILE", "credentials.json")

    if os.path.exists(token_file):
        creds = Credentials.from_authorized_user_file(token_file, SCOPES)
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            if not os.path.exists(creds_file):
                sys.exit(
                    f"No encuentro '{creds_file}'. Descargá las credenciales OAuth "
                    "desde Google Cloud Console (ver README) y guardalas con ese nombre."
                )
            flow = InstalledAppFlow.from_client_secrets_file(creds_file, SCOPES)
            creds = flow.run_local_server(port=0)
        with open(token_file, "w") as f:
            f.write(creds.to_json())
    return build("gmail", "v1", credentials=creds)


# --------------------------------------------------------------------------
# Etiquetas
# --------------------------------------------------------------------------
def ensure_labels(service, dry_run):
    """Crea las etiquetas que falten y devuelve {nombre: id}."""
    existing = service.users().labels().list(userId="me").execute().get("labels", [])
    by_name = {l["name"]: l["id"] for l in existing}
    for name in config.LABELS:
        if name not in by_name:
            if dry_run:
                by_name[name] = f"(se crearía) {name}"
                continue
            created = service.users().labels().create(
                userId="me",
                body={"name": name,
                      "labelListVisibility": "labelShow",
                      "messageListVisibility": "show"},
            ).execute()
            by_name[name] = created["id"]
    return by_name


# --------------------------------------------------------------------------
# Índice de remitentes (aprendizaje / reclasificación)
# --------------------------------------------------------------------------
def load_senders():
    if SENDERS_FILE.exists():
        return json.loads(SENDERS_FILE.read_text(encoding="utf-8"))
    return {}


def save_senders(senders, dry_run):
    if dry_run:
        return
    SENDERS_FILE.write_text(
        json.dumps(senders, indent=2, ensure_ascii=False), encoding="utf-8")


def update_sender_index(senders, email, label, when_iso, reclassifications):
    """Da de alta remitentes nuevos y reclasifica los que cambian de categoría."""
    rec = senders.get(email)
    if rec is None:
        senders[email] = {
            "label": label, "first_seen": when_iso, "last_seen": when_iso,
            "count": 1, "status": "ok",
        }
        return
    rec["count"] += 1
    rec["last_seen"] = when_iso
    if label and rec.get("label") and label != rec["label"]:
        reclassifications.append(
            {"email": email, "from": rec["label"], "to": label, "when": when_iso})
        rec["label"] = label
    elif label and not rec.get("label"):
        rec["label"] = label


# --------------------------------------------------------------------------
# Parsing de mensajes
# --------------------------------------------------------------------------
def header(headers, name):
    for h in headers:
        if h["name"].lower() == name.lower():
            return h["value"]
    return ""


def parse_from(from_value):
    """Devuelve (display_name, email_lower)."""
    m = re.search(r"<([^>]+)>", from_value)
    email = (m.group(1) if m else from_value).strip().lower()
    name = re.sub(r"<[^>]+>", "", from_value).strip().strip('"')
    return name, email


def extract_body(payload):
    """Texto plano aproximado del cuerpo (para buscar palabras clave)."""
    def walk(p):
        out = ""
        if p.get("mimeType", "").startswith("text/") and p.get("body", {}).get("data"):
            try:
                out += base64.urlsafe_b64decode(p["body"]["data"]).decode(
                    "utf-8", "ignore")
            except Exception:
                pass
        for part in p.get("parts", []) or []:
            out += walk(part)
        return out
    return walk(payload)


def is_automated(email, headers):
    """True si parece envío automático/masivo (NO persona)."""
    local = email.split("@")[0]
    if any(local.startswith(p) or p in local for p in config.AUTOMATED_LOCALPARTS):
        return True
    # Cabeceras típicas de envío masivo
    if header(headers, "List-Unsubscribe") or header(headers, "List-Id"):
        return True
    if "bulk" in header(headers, "Precedence").lower():
        return True
    return False


def is_whitelisted(email):
    return any(w.strip().lower() in email for w in config.WHITELIST if w.strip())


def matches_any(text, needles):
    t = text.lower()
    return any(n.lower() in t for n in needles)


# --------------------------------------------------------------------------
# Clasificación
# --------------------------------------------------------------------------
class Decision:
    def __init__(self):
        self.labels = []        # etiquetas a aplicar
        self.action = "keep"    # keep | archive | trash
        self.star = False
        self.reason = ""
        self.review = False


def classify(name, email, subject, body, gmail_categories, headers):
    text = f"{subject}\n{body}"
    d = Decision()

    # 1) Lista blanca: persona real o whitelist explícita -> intocable.
    if is_whitelisted(email) or not is_automated(email, headers):
        d.labels = ["Personal"]
        d.action = "keep"
        d.reason = "persona/lista blanca: se deja en Recibidos"
        return d

    # 2) Remitente importante por categoría.
    for label, needles in config.IMPORTANT_SENDERS.items():
        if matches_any(email, needles) or matches_any(name, needles):
            d.labels = [label]
            d.reason = f"remitente importante ({label})"
            _finish_important(d, label, text)
            return d

    # 3) Servicios y facturas (cualquier empresa, por palabra clave de factura).
    if matches_any(text, config.SERVICE_INVOICE_KEYWORDS):
        d.labels = ["Servicios y facturas"]
        d.reason = "parece factura/comprobante de un servicio"
        _finish_important(d, "Servicios y facturas", text)
        return d

    # 4) Categorías temáticas por palabra clave (Compras, Viajes).
    for label, needles in config.CATEGORY_KEYWORDS.items():
        if matches_any(text, needles):
            d.labels = [label]
            d.reason = f"palabras clave de {label}"
            _finish_important(d, label, text)
            return d

    # 5) Promociones.
    if "CATEGORY_PROMOTIONS" in gmail_categories:
        if matches_any(email, config.PROMO_KEEP_SENDERS) or \
           matches_any(name, config.PROMO_KEEP_SENDERS):
            d.labels = ["Promos que sirven"]
            d.action = "archive"
            d.reason = "promo útil (banco/súper/combustible)"
            return d
        d.action = "trash"
        d.reason = "promoción/marketing no relevante"
        return d

    # 6) Palabras clave importantes sueltas (seguridad, códigos, etc.).
    if matches_any(text, config.IMPORTANT_KEYWORDS):
        d.action = "keep"
        d.review = True
        d.reason = "palabra clave importante, sin categoría clara"
        return d

    # 7) Social / Notificaciones / Updates -> Papelera.
    if any(c in config.GMAIL_CATEGORY_TRASH for c in gmail_categories):
        d.action = "trash"
        d.reason = "categoría Social/Notificaciones sin relevancia"
        return d

    # 8) Ante la duda: dejar en Recibidos y marcar para revisión.
    d.action = "keep"
    d.review = True
    d.reason = "no clasificable con seguridad"
    return d


def _finish_important(d, label, text):
    """Decide archivar vs dejar en Recibidos, y respaldo (Guardar + estrella)."""
    if matches_any(text, config.ACTION_KEYWORDS):
        d.action = "keep"   # requiere que yo haga algo
    else:
        d.action = "archive"
    if label in config.BACKUP_LABELS and matches_any(text, config.BACKUP_KEYWORDS):
        d.labels.append("Guardar")
        d.star = True


# --------------------------------------------------------------------------
# Aplicar acciones
# --------------------------------------------------------------------------
def apply_decision(service, msg_id, decision, label_ids, dry_run):
    add = [label_ids[l] for l in decision.labels if l in label_ids
           and not str(label_ids[l]).startswith("(")]
    remove = []
    if decision.star:
        add.append("STARRED")
    if decision.action == "archive":
        remove.append("INBOX")
    if decision.review:
        add.append(label_ids.get("Revisar", "Revisar"))

    if dry_run:
        return
    if decision.action == "trash":
        service.users().messages().trash(userId="me", id=msg_id).execute()
        return
    if add or remove:
        service.users().messages().modify(
            userId="me", id=msg_id,
            body={"addLabelIds": add, "removeLabelIds": remove}).execute()


# --------------------------------------------------------------------------
# Limpieza de promos vencidas (>30 días -> Papelera)
# --------------------------------------------------------------------------
def expire_promos(service, dry_run, report):
    q = f'label:"Promos que sirven" older_than:{config.PROMO_EXPIRY_DAYS}d'
    ids = list_message_ids(service, q)
    for mid in ids:
        if not dry_run:
            service.users().messages().trash(userId="me", id=mid).execute()
    report["promos_vencidas_a_papelera"] = len(ids)


# --------------------------------------------------------------------------
# Listado de mensajes
# --------------------------------------------------------------------------
def list_message_ids(service, query):
    ids, page = [], None
    while True:
        resp = service.users().messages().list(
            userId="me", q=query, pageToken=page, maxResults=500).execute()
        ids.extend(m["id"] for m in resp.get("messages", []))
        page = resp.get("nextPageToken")
        if not page:
            break
    return ids


# --------------------------------------------------------------------------
# Log
# --------------------------------------------------------------------------
def log_action(records, mode):
    LOGS_DIR.mkdir(exist_ok=True)
    stamp = dt.datetime.now().strftime("%Y%m%d-%H%M%S")
    path = LOGS_DIR / f"actions-{mode}-{stamp}.jsonl"
    with open(path, "w", encoding="utf-8") as f:
        for r in records:
            f.write(json.dumps(r, ensure_ascii=False) + "\n")
    return path


# --------------------------------------------------------------------------
# Main
# --------------------------------------------------------------------------
def run(dry_run, query, max_messages):
    service = get_service()
    label_ids = ensure_labels(service, dry_run)
    senders = load_senders()

    ids = list_message_ids(service, query)
    if max_messages:
        ids = ids[:max_messages]

    report = {
        "modo": "DRY-RUN (no se modifica nada)" if dry_run else "EJECUCIÓN REAL",
        "consulta": query, "total": len(ids),
        "por_etiqueta": {}, "archivados": 0, "a_papelera": 0,
        "para_revisar": [], "ejemplos": {"archivar": [], "papelera": [], "etiquetar": []},
    }
    reclassifications, records = [], []

    for mid in ids:
        msg = service.users().messages().get(
            userId="me", id=mid, format="full").execute()
        payload = msg.get("payload", {})
        headers = payload.get("headers", [])
        from_name, from_email = parse_from(header(headers, "From"))
        subject = header(headers, "Subject")
        body = extract_body(payload)
        gmail_categories = [l for l in msg.get("labelIds", []) if l.startswith("CATEGORY_")]
        when_iso = dt.datetime.fromtimestamp(
            int(msg.get("internalDate", "0")) / 1000).isoformat()

        d = classify(from_name, from_email, subject, body, gmail_categories, headers)

        primary = d.labels[0] if d.labels else "(sin etiqueta)"
        update_sender_index(senders, from_email, primary, when_iso, reclassifications)

        for l in d.labels:
            report["por_etiqueta"][l] = report["por_etiqueta"].get(l, 0) + 1
        if d.action == "archive":
            report["archivados"] += 1
            _sample(report["ejemplos"]["archivar"], from_email, subject)
        elif d.action == "trash":
            report["a_papelera"] += 1
            _sample(report["ejemplos"]["papelera"], from_email, subject)
        if d.labels:
            _sample(report["ejemplos"]["etiquetar"], from_email, f"[{primary}] {subject}")
        if d.review:
            report["para_revisar"].append(f"{from_email} — {subject}")

        records.append({"id": mid, "from": from_email, "subject": subject,
                         "labels": d.labels, "action": d.action, "star": d.star,
                         "review": d.review, "reason": d.reason})

        apply_decision(service, mid, d, label_ids, dry_run)

    expire_promos(service, dry_run, report)
    save_senders(senders, dry_run)
    report["reclasificaciones"] = reclassifications
    log_path = log_action(records, "dryrun" if dry_run else "exec")

    print_report(report, log_path)
    return report


def _sample(bucket, email, subject, limit=10):
    if len(bucket) < limit:
        bucket.append(f"{email} — {subject[:80]}")


def print_report(r, log_path):
    line = "=" * 70
    print(f"\n{line}\nINFORME — {r['modo']}\n{line}")
    print(f"Consulta Gmail     : {r['consulta']}")
    print(f"Correos procesados : {r['total']}")
    print(f"Archivados         : {r['archivados']}")
    print(f"Enviados a Papelera: {r['a_papelera']}")
    print(f"Promos vencidas    : {r.get('promos_vencidas_a_papelera', 0)} a Papelera")
    print("\nPor etiqueta:")
    for k, v in sorted(r["por_etiqueta"].items()):
        print(f"  - {k}: {v}")
    if r["reclasificaciones"]:
        print("\nRemitentes reclasificados:")
        for rc in r["reclasificaciones"]:
            print(f"  - {rc['email']}: {rc['from']} -> {rc['to']}")
    if r["para_revisar"]:
        print(f"\nDejados para tu revisión ({len(r['para_revisar'])}):")
        for item in r["para_revisar"][:20]:
            print(f"  - {item}")
        if len(r["para_revisar"]) > 20:
            print(f"  ... y {len(r['para_revisar']) - 20} más")
    print(f"\nLog detallado: {log_path}")
    if "DRY-RUN" in r["modo"]:
        print("\n>>> Esto fue una PRUEBA. Si está OK, corré de nuevo con --execute.")
    print(line + "\n")


def parse_args():
    p = argparse.ArgumentParser(description="Organizador de Gmail personal")
    g = p.add_mutually_exclusive_group()
    g.add_argument("--dry-run", action="store_true",
                   help="No modifica nada, solo informa (default si no se aclara).")
    g.add_argument("--execute", action="store_true",
                   help="Aplica los cambios reales.")
    p.add_argument("--full", action="store_true",
                   help="Procesa toda la casilla (primera corrida).")
    p.add_argument("--since", default="1d",
                   help="Ventana de tiempo para correos nuevos (ej. 1d, 2d, 12h). "
                        "Se ignora con --full.")
    return p.parse_args()


def main():
    args = parse_args()
    dry_run = not args.execute  # por seguridad: si no pasás --execute, es dry-run
    if args.full:
        query = "in:anywhere -in:trash -in:spam"
    else:
        query = f"newer_than:{args.since} -in:trash -in:spam"
    max_messages = int(os.getenv("MAX_MESSAGES", "0") or "0")
    run(dry_run, query, max_messages)


if __name__ == "__main__":
    main()
