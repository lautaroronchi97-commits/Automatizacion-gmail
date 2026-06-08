#!/usr/bin/env python3
"""
Organizador de Gmail personal.

Reglas: ver prompt_ordenar_gmail.md.
Tope de seguridad: dry-run por defecto, nunca borrado permanente, lista blanca.

Uso:
    python gmail_organizer.py --dry-run             # informe, no cambia nada
    python gmail_organizer.py --execute             # aplica cambios
    python gmail_organizer.py --execute --full      # toda la casilla
    python gmail_organizer.py --execute --since 1d  # solo lo nuevo
    python gmail_organizer.py --execute --since-last-run
    python gmail_organizer.py --execute --label-only  # shadow: solo etiqueta
    python gmail_organizer.py --explain MSG_ID      # debug de un correo
"""

import argparse
import base64
import datetime as dt
import html
import io
import json
import logging
import os
import random
import re
import sys
import time
from email.utils import parseaddr
from logging.handlers import RotatingFileHandler
from pathlib import Path

try:
    from dotenv import load_dotenv
    load_dotenv()
except Exception:
    pass

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

import config

SCOPES = ["https://www.googleapis.com/auth/gmail.modify"]
BASE_DIR = Path(__file__).resolve().parent
SENDERS_FILE = BASE_DIR / "senders.json"
STATE_FILE = BASE_DIR / "state.json"
LOCK_FILE = BASE_DIR / ".organizer.lock"
LOGS_DIR = BASE_DIR / "logs"

log = logging.getLogger("gmail_organizer")


# --------------------------------------------------------------------------
# Infra: logging, retries, atomic writes, lock.
# --------------------------------------------------------------------------
def setup_logging():
    LOGS_DIR.mkdir(exist_ok=True)
    try:
        os.chmod(LOGS_DIR, 0o700)
    except Exception:
        pass
    fmt = logging.Formatter("%(asctime)s %(levelname)s %(message)s")
    fh = RotatingFileHandler(LOGS_DIR / "cron.log",
                              maxBytes=5 * 1024 * 1024, backupCount=5,
                              encoding="utf-8")
    fh.setFormatter(fmt)
    sh = logging.StreamHandler()
    sh.setFormatter(fmt)
    root = logging.getLogger()
    root.setLevel(logging.INFO)
    root.addHandler(fh)
    root.addHandler(sh)


_RETRY_STATUS = {429, 500, 502, 503, 504}


def with_retries(fn, attempts=5, base=1.5):
    """Reintenta con backoff exponencial ante 429/5xx y errores de red."""
    last = None
    for i in range(attempts):
        try:
            return fn()
        except HttpError as e:
            status = None
            try:
                status = int(e.resp.status)
            except Exception:
                pass
            if status not in _RETRY_STATUS or i == attempts - 1:
                raise
            last = e
        except (TimeoutError, ConnectionError) as e:
            if i == attempts - 1:
                raise
            last = e
        sleep = (base ** i) + random.random()
        log.warning("Retry %d/%d en %.1fs (%s)", i + 1, attempts, sleep, last)
        time.sleep(sleep)


def atomic_write_json(path: Path, data):
    tmp = path.with_suffix(path.suffix + ".tmp")
    tmp.write_text(json.dumps(data, indent=2, ensure_ascii=False),
                    encoding="utf-8")
    os.replace(tmp, path)
    try:
        os.chmod(path, 0o600)
    except Exception:
        pass


class SingleInstanceLock:
    """Evita corridas solapadas. Si hay un pid vivo en el lock, sale."""
    def __init__(self, path: Path):
        self.path = path

    def __enter__(self):
        if self.path.exists():
            try:
                pid = int(self.path.read_text().strip())
                os.kill(pid, 0)
                sys.exit(f"Otra instancia corriendo (pid {pid}). Saliendo.")
            except (ValueError, ProcessLookupError, OSError):
                pass  # lock viejo, lo sobrescribimos
        self.path.write_text(str(os.getpid()))
        return self

    def __exit__(self, *exc):
        try:
            self.path.unlink()
        except FileNotFoundError:
            pass


# --------------------------------------------------------------------------
# Auth
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
        Path(token_file).write_text(creds.to_json())
        try:
            os.chmod(token_file, 0o600)
        except Exception:
            pass
    return build("gmail", "v1", credentials=creds, cache_discovery=False)


# --------------------------------------------------------------------------
# Etiquetas
# --------------------------------------------------------------------------
def ensure_labels(service, dry_run):
    existing = with_retries(
        lambda: service.users().labels().list(userId="me").execute()
    ).get("labels", [])
    by_name = {l["name"]: l["id"] for l in existing}
    # Algunos nombres del sistema están en otro idioma según la UI de Gmail.
    # Si el usuario ya tiene una etiqueta con un nombre del sistema, no creamos.
    for name in config.LABELS:
        if name in by_name:
            continue
        if dry_run:
            by_name[name] = f"(se crearía) {name}"
            continue
        try:
            created = with_retries(lambda: service.users().labels().create(
                userId="me",
                body={"name": name,
                      "labelListVisibility": "labelShow",
                      "messageListVisibility": "show"},
            ).execute())
            by_name[name] = created["id"]
        except HttpError as e:
            status = None
            try:
                status = int(e.resp.status)
            except Exception:
                pass
            if status == 400:
                # Nombre inválido (colisión con system label, caracteres no
                # permitidos, etc.) -> seguimos sin romper la corrida.
                log.warning("No se pudo crear la etiqueta %r (400). "
                             "La omito en esta corrida.", name)
                continue
            raise
    return by_name


# --------------------------------------------------------------------------
# Índice de remitentes y state
# --------------------------------------------------------------------------
def load_senders():
    if SENDERS_FILE.exists():
        return json.loads(SENDERS_FILE.read_text(encoding="utf-8"))
    return {}


def save_senders(senders, dry_run):
    if not dry_run:
        atomic_write_json(SENDERS_FILE, senders)


def load_state():
    if STATE_FILE.exists():
        return json.loads(STATE_FILE.read_text(encoding="utf-8"))
    return {}


def save_state(state, dry_run):
    if not dry_run:
        atomic_write_json(STATE_FILE, state)


def update_sender_index(senders, email, label, when_iso, reclassifications):
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
    name, email_addr = parseaddr(from_value or "")
    return name.strip().strip('"'), email_addr.strip().lower()


_TAG_RE = re.compile(r"<[^>]+>")
_WS_RE = re.compile(r"\s+")


def _decode_part(p):
    data = p.get("body", {}).get("data")
    if not data:
        return ""
    raw = base64.urlsafe_b64decode(data)
    charset = "utf-8"
    for h in p.get("headers", []) or []:
        if h.get("name", "").lower() == "content-type":
            m = re.search(r"charset=([\w\-]+)", h.get("value", ""), re.I)
            if m:
                charset = m.group(1)
            break
    try:
        text = raw.decode(charset, errors="replace")
    except LookupError:
        text = raw.decode("utf-8", errors="replace")
    if p.get("mimeType") == "text/html":
        text = html.unescape(_TAG_RE.sub(" ", text))
    return _WS_RE.sub(" ", text).strip()


def extract_body(payload):
    """Texto del cuerpo: prefiere text/plain, cae a text/html."""
    plain, html_parts = [], []

    def walk(p):
        mime = p.get("mimeType", "")
        if mime == "text/plain":
            plain.append(_decode_part(p))
        elif mime == "text/html":
            html_parts.append(_decode_part(p))
        for ch in p.get("parts", []) or []:
            walk(ch)

    walk(payload)
    if plain:
        return " ".join(plain)
    return " ".join(html_parts)


def is_automated(email, name, headers):
    """True si parece envío automático/masivo (NO persona).

    Comparación con local-part: exacta o con separador (./-/_) como prefijo.
    También chequea dominios siempre automáticos (mail.mercadolibre.com, etc.)
    para casos en que el localpart es un UUID raro.
    """
    if "@" in email:
        local, domain = email.split("@", 1)
    else:
        local, domain = email, ""
    for p in config.AUTOMATED_LOCALPARTS:
        if local == p:
            return True
        if local.startswith(p + ".") or local.startswith(p + "-") \
                or local.startswith(p + "_"):
            return True
    for d in getattr(config, "AUTOMATED_DOMAINS", []):
        if d in domain or d in email:
            return True
    nl = (name or "").lower()
    if any(s in nl for s in config.AUTOMATED_NAME_HINTS):
        return True
    if header(headers, "List-Unsubscribe") or header(headers, "List-Id"):
        return True
    if "bulk" in header(headers, "Precedence").lower():
        return True
    return False


def is_own_email(email):
    """True si el remitente es mi propio email (los enviados van a 'Enviados')."""
    return any(e.strip().lower() == email for e in
                getattr(config, "OWN_EMAILS", []) if e.strip())


def is_whitelisted(email):
    return any(w.strip().lower() in email for w in config.WHITELIST if w.strip())


def matches_any(text, needles):
    t = (text or "").lower()
    return any(n.lower() in t for n in needles)


# --------------------------------------------------------------------------
# Clasificación
# --------------------------------------------------------------------------
class Decision:
    def __init__(self):
        self.labels = []
        self.action = "keep"        # keep | archive | trash
        self.star = False
        self.reason = ""
        self.review = False
        self.confidence = "low"     # low | medium | high


def classify(name, email, subject, body, gmail_categories, headers):
    text = f"{subject}\n{body}"
    d = Decision()

    # 0) Mis propios envíos -> etiqueta "Yo enviados", archivar.
    if is_own_email(email):
        d.labels = ["Yo enviados"]
        d.action = "archive"
        d.reason = "remitente = mi propio email (mensajes enviados)"
        d.confidence = "high"
        return d

    # 1) Remitente importante por categoría (corre antes que 'persona' para no
    #    perder bancos/gobierno/Boca/Cocos/MercadoLibre/etc.).
    for label, needles in config.IMPORTANT_SENDERS.items():
        if matches_any(email, needles) or matches_any(name, needles):
            d.labels = [label]
            d.reason = f"remitente importante ({label})"
            d.confidence = "high"
            _finish_important(d, label, text)
            return d

    # 2) Lista blanca explícita -> intocable.
    if is_whitelisted(email):
        d.labels = ["Personal"]
        d.action = "keep"
        d.reason = "whitelist explícita: se deja en Recibidos"
        d.confidence = "high"
        return d

    # 2b) No parece automático -> persona, intocable.
    if not is_automated(email, name, headers):
        d.labels = ["Personal"]
        d.action = "keep"
        d.reason = "persona: se deja en Recibidos"
        d.confidence = "high"
        return d

    # 3) Servicios y facturas (keywords).
    if matches_any(text, config.SERVICE_INVOICE_KEYWORDS):
        d.labels = ["Servicios y facturas"]
        d.reason = "parece factura/comprobante de un servicio"
        d.confidence = "high"
        _finish_important(d, "Servicios y facturas", text)
        return d

    # 4) Categorías temáticas por keyword (Boca, Cocos, Compras, Viajes, etc.).
    for label, needles in config.CATEGORY_KEYWORDS.items():
        if matches_any(text, needles):
            d.labels = [label]
            d.reason = f"palabras clave de {label}"
            d.confidence = "high"
            _finish_important(d, label, text)
            return d

    # 5) Promociones.
    if "CATEGORY_PROMOTIONS" in gmail_categories:
        if matches_any(email, config.PROMO_KEEP_SENDERS) or \
                matches_any(name, config.PROMO_KEEP_SENDERS):
            d.labels = ["Promos que sirven"]
            d.action = "archive"
            d.reason = "promo útil (banco/súper/combustible)"
            d.confidence = "high"
            return d
        d.action = "trash"
        d.reason = "promoción/marketing no relevante"
        d.confidence = "high"
        return d

    # 6) Palabras clave importantes sueltas.
    if matches_any(text, config.IMPORTANT_KEYWORDS):
        d.action = "keep"
        d.review = True
        d.reason = "palabra clave importante, sin categoría clara"
        d.confidence = "low"
        return d

    # 7) Social / Updates / Forums -> Papelera.
    if any(c in config.GMAIL_CATEGORY_TRASH for c in gmail_categories):
        d.action = "trash"
        d.reason = "categoría Social/Notificaciones sin relevancia"
        d.confidence = "medium"
        return d

    # 8) Duda.
    d.action = "keep"
    d.review = True
    d.reason = "no clasificable con seguridad"
    d.confidence = "low"
    return d


def classify_from_memory(senders, name, email, subject, body):
    """Si el remitente es conocido y confiable, usa su última etiqueta.

    SOLO si las reglas vigentes (IMPORTANT_SENDERS / OWN_EMAILS) no apuntan
    a otra etiqueta. Así la memoria no propaga clasificaciones erróneas
    cuando la config se mejora.
    """
    rec = senders.get(email)
    if not rec or rec.get("status") != "ok":
        return None
    if rec.get("count", 0) < config.SENDER_CONFIDENT_COUNT:
        return None
    label = rec.get("label")
    if not label or label not in config.LABELS:
        return None
    # Si las reglas actuales asignan otra etiqueta, ignorar la memoria.
    if is_own_email(email):
        return None  # caso "Yo enviados" lo resuelve classify().
    for cfg_label, needles in config.IMPORTANT_SENDERS.items():
        if (matches_any(email, needles) or matches_any(name, needles)) \
                and cfg_label != label:
            return None  # las reglas mandan, ajustamos memoria al pasar.
    d = Decision()
    d.labels = [label]
    d.reason = f"memoria: remitente conocido ({rec['count']} mails) -> {label}"
    d.confidence = "high"
    if label in ("Personal", "Yo enviados"):
        d.action = "archive" if label == "Yo enviados" else "keep"
    else:
        _finish_important(d, label, f"{subject}\n{body}")
    return d


def _finish_important(d, label, text):
    if matches_any(text, config.ACTION_KEYWORDS):
        d.action = "keep"
    else:
        d.action = "archive"
    # Un mail = una sola etiqueta. La señal de "respaldo importante" la da
    # la estrella (no se agrega "Guardar" como segunda etiqueta).
    if label in config.BACKUP_LABELS and matches_any(text, config.BACKUP_KEYWORDS):
        d.star = True


# --------------------------------------------------------------------------
# Aplicar acciones
# --------------------------------------------------------------------------
def _safe_label_ids(names, label_ids):
    out = []
    for n in names:
        lid = label_ids.get(n)
        if lid and not str(lid).startswith("("):
            out.append(lid)
    return out


def apply_decision(service, msg_id, decision, label_ids, dry_run, label_only):
    add = _safe_label_ids(decision.labels, label_ids)
    remove = []
    if decision.star and not label_only:
        add.append("STARRED")
    if decision.action == "archive" and not label_only:
        remove.append("INBOX")
    if decision.review:
        add.extend(_safe_label_ids(["Revisar"], label_ids))

    if dry_run:
        return
    if decision.action == "trash" and not label_only:
        with_retries(lambda: service.users().messages().trash(
            userId="me", id=msg_id).execute())
        return
    if add or remove:
        with_retries(lambda: service.users().messages().modify(
            userId="me", id=msg_id,
            body={"addLabelIds": add, "removeLabelIds": remove}).execute())


def batch_trash(service, msg_ids):
    for mid in msg_ids:
        with_retries(lambda: service.users().messages().trash(
            userId="me", id=mid).execute())


# --------------------------------------------------------------------------
# Limpieza de promos vencidas
# --------------------------------------------------------------------------
def expire_promos(service, dry_run, report, label_only):
    q = (f'label:"Promos que sirven" older_than:{config.PROMO_EXPIRY_DAYS}d '
         f'-in:trash -in:spam')
    ids = list_message_ids(service, q)
    if not dry_run and not label_only:
        batch_trash(service, ids)
    report["promos_vencidas_a_papelera"] = len(ids)


# --------------------------------------------------------------------------
# Listado de mensajes (con dedup)
# --------------------------------------------------------------------------
def list_message_ids(service, query):
    seen, ids, page = set(), [], None
    while True:
        resp = with_retries(lambda: service.users().messages().list(
            userId="me", q=query, pageToken=page, maxResults=500).execute())
        for m in resp.get("messages", []):
            mid = m["id"]
            if mid not in seen:
                seen.add(mid)
                ids.append(mid)
        page = resp.get("nextPageToken")
        if not page:
            break
    return ids


# --------------------------------------------------------------------------
# Logs jsonl + poda
# --------------------------------------------------------------------------
def log_action(records, mode):
    LOGS_DIR.mkdir(exist_ok=True)
    try:
        os.chmod(LOGS_DIR, 0o700)
    except Exception:
        pass
    stamp = dt.datetime.now().strftime("%Y%m%d-%H%M%S")
    path = LOGS_DIR / f"actions-{mode}-{stamp}.jsonl"
    with open(path, "w", encoding="utf-8") as f:
        for r in records:
            f.write(json.dumps(r, ensure_ascii=False) + "\n")
    try:
        os.chmod(path, 0o600)
    except Exception:
        pass
    cutoff = dt.datetime.now() - dt.timedelta(days=config.LOG_RETENTION_DAYS)
    for p in LOGS_DIR.glob("actions-*.jsonl"):
        try:
            if dt.datetime.fromtimestamp(p.stat().st_mtime) < cutoff:
                p.unlink()
        except Exception:
            pass
    return path


# --------------------------------------------------------------------------
# Explain (debug de un mensaje)
# --------------------------------------------------------------------------
def explain_message(service, msg_id):
    msg = with_retries(lambda: service.users().messages().get(
        userId="me", id=msg_id, format="full").execute())
    payload = msg.get("payload", {})
    headers = payload.get("headers", [])
    from_name, from_email = parse_from(header(headers, "From"))
    subject = header(headers, "Subject")
    body = extract_body(payload)
    cats = [l for l in msg.get("labelIds", []) if l.startswith("CATEGORY_")]
    d = classify(from_name, from_email, subject, body, cats, headers)
    print(f"From       : {from_name} <{from_email}>")
    print(f"Subject    : {subject[:config.SUBJECT_MAX]}")
    print(f"Categorías : {cats}")
    print(f"Automático?: {is_automated(from_email, from_name, headers)}")
    print(f"Labels     : {d.labels}")
    print(f"Action     : {d.action}  star={d.star}  "
          f"review={d.review}  confidence={d.confidence}")
    print(f"Razón      : {d.reason}")


# --------------------------------------------------------------------------
# Cleanup de etiqueta "Guardar": pasamos a 1 etiqueta por mail. Sacamos
# la etiqueta "Guardar" de los mails que la tengan; la estrella queda
# como senal de respaldo. Si se le pasa --delete-label, ademas borra la
# etiqueta de Gmail.
# --------------------------------------------------------------------------
def cleanup_label(service, label_name, delete_label=False):
    labels = with_retries(lambda: service.users().labels().list(
        userId="me").execute()).get("labels", [])
    target = next((l for l in labels if l["name"] == label_name), None)
    if not target:
        print(f"No existe la etiqueta '{label_name}'. Nada que limpiar.")
        return
    lid = target["id"]
    # Busqueda: todos los mails con esa etiqueta.
    ids = list_message_ids(service, f'label:"{label_name}"')
    print(f"{label_name}: {len(ids)} mensajes la tienen aplicada")
    n = 0
    # batchModify hasta 1000 por llamada.
    for i in range(0, len(ids), 1000):
        chunk = ids[i:i + 1000]
        with_retries(lambda: service.users().messages().batchModify(
            userId="me",
            body={"ids": chunk, "removeLabelIds": [lid]},
        ).execute())
        n += len(chunk)
        print(f"  removidos {n}/{len(ids)}")
    if delete_label:
        with_retries(lambda: service.users().labels().delete(
            userId="me", id=lid).execute())
        print(f"Etiqueta '{label_name}' eliminada de Gmail.")


# --------------------------------------------------------------------------
# Snapshot: vuelca un CSV con todos los mails actuales (id, from, subject,
# labels, fecha). Util para comparar antes/despues de una limpieza manual y
# aprender que correos el usuario considera descartables.
# --------------------------------------------------------------------------
def snapshot(service, out_path, query=None, include_trash=False):
    import csv
    q = query or ("in:anywhere -in:spam" if include_trash
                   else "in:anywhere -in:trash -in:spam")
    log.info("Snapshot: query=%s", q)
    ids = list_message_ids(service, q)
    log.info("Snapshot: %d mensajes a leer", len(ids))

    # Mapear labelId -> nombre para que el snapshot sea legible.
    labels_list = with_retries(lambda: service.users().labels().list(
        userId="me").execute()).get("labels", [])
    id_to_name = {l["id"]: l["name"] for l in labels_list}

    out_path = Path(out_path)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    n_ok, n_err = 0, 0
    with open(out_path, "w", encoding="utf-8", newline="") as f:
        w = csv.writer(f, quoting=csv.QUOTE_MINIMAL)
        w.writerow(["id", "internal_date", "from_email", "from_name",
                     "subject", "label_ids", "label_names",
                     "gmail_categories", "in_inbox", "in_trash"])
        for i, mid in enumerate(ids, 1):
            try:
                msg = with_retries(lambda: service.users().messages().get(
                    userId="me", id=mid, format="metadata",
                    metadataHeaders=["From", "Subject"]).execute())
            except Exception:
                log.exception("snapshot: error en %s", mid)
                n_err += 1
                continue
            headers = msg.get("payload", {}).get("headers", [])
            from_name, from_email = parse_from(header(headers, "From"))
            subject = header(headers, "Subject")
            lbls = msg.get("labelIds", []) or []
            label_ids = ";".join(lbls)
            label_names = ";".join(id_to_name.get(l, l) for l in lbls)
            cats = ";".join(l for l in lbls if l.startswith("CATEGORY_"))
            internal = msg.get("internalDate", "0")
            try:
                date_iso = dt.datetime.fromtimestamp(
                    int(internal) / 1000).isoformat(timespec="seconds")
            except Exception:
                date_iso = ""
            w.writerow([
                mid, date_iso, from_email, from_name,
                subject[:200], label_ids, label_names, cats,
                "1" if "INBOX" in lbls else "0",
                "1" if "TRASH" in lbls else "0",
            ])
            n_ok += 1
            if i % 200 == 0:
                log.info("snapshot: %d / %d procesados", i, len(ids))
    log.info("snapshot: %d ok, %d errores -> %s", n_ok, n_err, out_path)
    print(f"Snapshot OK: {n_ok} mensajes ({n_err} errores) en {out_path}")


# --------------------------------------------------------------------------
# Resumen como draft en Gmail
# --------------------------------------------------------------------------
def create_summary_draft(service, report, log_path):
    from email.mime.text import MIMEText
    today = dt.datetime.now().strftime("%Y-%m-%d %H:%M")
    profile = with_retries(lambda: service.users().getProfile(
        userId="me").execute())
    me = profile.get("emailAddress", "me")
    body = build_summary_text(report, log_path)
    mime = MIMEText(body, "plain", "utf-8")
    mime["to"] = me
    mime["from"] = me
    mime["subject"] = f"Resumen organizador Gmail — {today}"
    raw = base64.urlsafe_b64encode(mime.as_bytes()).decode()
    with_retries(lambda: service.users().drafts().create(
        userId="me", body={"message": {"raw": raw}}).execute())


def build_summary_text(r, log_path):
    out = io.StringIO()
    out.write(f"Modo: {r['modo']}\n")
    out.write(f"Consulta: {r['consulta']}\n")
    out.write(f"Procesados: {r['total']}   Archivados: {r['archivados']}   "
               f"Papelera: {r['a_papelera']}\n")
    out.write(f"Promos vencidas: {r.get('promos_vencidas_a_papelera', 0)}   "
               f"Errores: {r.get('errores', 0)}\n\n")
    out.write("Por etiqueta:\n")
    for k, v in sorted(r["por_etiqueta"].items()):
        out.write(f"  - {k}: {v}\n")
    if r.get("nuevos_remitentes"):
        out.write(f"\nRemitentes nuevos: {len(r['nuevos_remitentes'])}\n")
        for s in r["nuevos_remitentes"][:30]:
            out.write(f"  - {s}\n")
    if r.get("reclasificaciones"):
        out.write(f"\nReclasificaciones: {len(r['reclasificaciones'])}\n")
        for rc in r["reclasificaciones"][:30]:
            out.write(f"  - {rc['email']}: {rc['from']} -> {rc['to']}\n")
    if r["para_revisar"]:
        out.write(f"\nPara revisar ({len(r['para_revisar'])}):\n")
        for it in r["para_revisar"][:50]:
            out.write(f"  - {it}\n")
    out.write(f"\nLog: {log_path}\n")
    return out.getvalue()


# --------------------------------------------------------------------------
# Main
# --------------------------------------------------------------------------
def _sample(bucket, email, subject, limit=10):
    if len(bucket) < limit:
        bucket.append(f"{email} — {subject[:config.SUBJECT_MAX]}")


def build_query(args, state):
    if args.full:
        return "in:anywhere -in:trash -in:spam"
    if args.since_last_run:
        last = state.get("last_run_at")
        if last:
            after_ts = int(dt.datetime.fromisoformat(last).timestamp())
            return f"after:{after_ts} -in:trash -in:spam"
    return f"newer_than:{args.since} -in:trash -in:spam"


def run(args):
    dry_run = not args.execute
    service = get_service()
    label_ids = ensure_labels(service, dry_run)
    senders = load_senders()
    state = load_state()

    query = build_query(args, state)
    ids = list_message_ids(service, query)
    cap = args.limit or int(os.getenv("MAX_MESSAGES", "0") or "0")
    if cap:
        ids = ids[:cap]

    if dry_run:
        modo = "DRY-RUN (no se modifica nada)"
    elif args.label_only:
        modo = "EJECUCIÓN — solo etiquetas (sin archivar ni Papelera)"
    else:
        modo = "EJECUCIÓN REAL"

    report = {
        "modo": modo, "consulta": query, "total": len(ids),
        "por_etiqueta": {}, "archivados": 0, "a_papelera": 0,
        "para_revisar": [], "errores": 0,
        "ejemplos": {"archivar": [], "papelera": [], "etiquetar": []},
    }
    reclassifications, records, new_senders = [], [], []

    for mid in ids:
        try:
            msg = with_retries(lambda: service.users().messages().get(
                userId="me", id=mid, format="full").execute())
        except Exception as e:
            log.exception("Error obteniendo %s", mid)
            report["errores"] += 1
            continue

        payload = msg.get("payload", {})
        headers = payload.get("headers", [])
        from_name, from_email = parse_from(header(headers, "From"))
        subject = header(headers, "Subject")
        body = extract_body(payload)
        gmail_categories = [l for l in msg.get("labelIds", [])
                              if l.startswith("CATEGORY_")]
        when_iso = dt.datetime.fromtimestamp(
            int(msg.get("internalDate", "0")) / 1000).isoformat()

        # memoria de remitentes
        d = classify_from_memory(senders, from_name, from_email, subject, body)
        if d is None:
            if from_email not in senders:
                new_senders.append(from_email)
            d = classify(from_name, from_email, subject, body,
                          gmail_categories, headers)

        primary = d.labels[0] if d.labels else "(sin etiqueta)"
        update_sender_index(senders, from_email, primary, when_iso,
                             reclassifications)

        for l in d.labels:
            report["por_etiqueta"][l] = report["por_etiqueta"].get(l, 0) + 1

        # acción efectiva (en label_only no archiva ni manda a Papelera)
        effective = d.action
        if args.label_only and effective in ("archive", "trash"):
            effective = "keep"

        if effective == "archive":
            report["archivados"] += 1
            _sample(report["ejemplos"]["archivar"], from_email, subject)
        elif effective == "trash":
            report["a_papelera"] += 1
            _sample(report["ejemplos"]["papelera"], from_email, subject)
        if d.labels:
            _sample(report["ejemplos"]["etiquetar"], from_email,
                     f"[{primary}] {subject}")
        if d.review:
            report["para_revisar"].append(
                f"{from_email} — {subject[:config.SUBJECT_MAX]}")

        records.append({
            "id": mid, "from": from_email,
            "subject": subject[:config.SUBJECT_MAX],
            "labels": d.labels, "action": effective, "star": d.star,
            "review": d.review, "confidence": d.confidence, "reason": d.reason,
        })

        try:
            apply_decision(service, mid, d, label_ids, dry_run, args.label_only)
        except Exception:
            log.exception("Error aplicando acción a %s", mid)
            report["errores"] += 1

    expire_promos(service, dry_run, report, args.label_only)
    save_senders(senders, dry_run)
    state["last_run_at"] = dt.datetime.now().isoformat()
    save_state(state, dry_run)

    report["reclasificaciones"] = reclassifications
    report["nuevos_remitentes"] = new_senders
    log_path = log_action(records, "dryrun" if dry_run else "exec")

    print_report(report, log_path)

    if not dry_run and not args.no_summary_draft:
        try:
            create_summary_draft(service, report, log_path)
        except Exception as e:
            log.warning("No pude crear draft de resumen: %s", e)

    return report


def print_report(r, log_path):
    line = "=" * 70
    print(f"\n{line}\nINFORME — {r['modo']}\n{line}")
    print(f"Consulta Gmail     : {r['consulta']}")
    print(f"Correos procesados : {r['total']}")
    print(f"Archivados         : {r['archivados']}")
    print(f"Enviados a Papelera: {r['a_papelera']}")
    print(f"Promos vencidas    : {r.get('promos_vencidas_a_papelera', 0)} a Papelera")
    print(f"Errores            : {r.get('errores', 0)}")
    print("\nPor etiqueta:")
    for k, v in sorted(r["por_etiqueta"].items()):
        print(f"  - {k}: {v}")
    if r.get("nuevos_remitentes"):
        print(f"\nRemitentes nuevos ({len(r['nuevos_remitentes'])}):")
        for s in r["nuevos_remitentes"][:20]:
            print(f"  - {s}")
        if len(r["nuevos_remitentes"]) > 20:
            print(f"  ... y {len(r['nuevos_remitentes']) - 20} más")
    if r["reclasificaciones"]:
        print(f"\nReclasificaciones ({len(r['reclasificaciones'])}):")
        for rc in r["reclasificaciones"][:20]:
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
                   help="No modifica nada (default si no se aclara).")
    g.add_argument("--execute", action="store_true",
                   help="Aplica los cambios reales.")
    p.add_argument("--full", action="store_true",
                   help="Procesa toda la casilla.")
    p.add_argument("--since", default="1d",
                   help="Ventana de tiempo para correos nuevos (ej. 1d, 12h).")
    p.add_argument("--since-last-run", action="store_true",
                   help="Usa el timestamp persistido en state.json.")
    p.add_argument("--limit", type=int, default=0,
                   help="Tope de mensajes por corrida (0 = sin límite).")
    p.add_argument("--label-only", action="store_true",
                   help="Solo etiqueta; no archiva ni manda a Papelera.")
    p.add_argument("--no-summary-draft", action="store_true",
                   help="No crear draft de resumen al terminar.")
    p.add_argument("--explain", metavar="MSG_ID",
                   help="Mostrar cómo se clasificaría un mensaje y salir.")
    p.add_argument("--snapshot", metavar="OUT_CSV",
                   help="Vuelca un CSV con id/from/subject/labels de cada "
                        "mail (toda la casilla) y sale.")
    p.add_argument("--snapshot-include-trash", action="store_true",
                   help="Junto con --snapshot, incluir tambien Papelera.")
    p.add_argument("--cleanup-label", metavar="NAME",
                   help="Saca la etiqueta NAME de todos los mails que la "
                        "tengan (no toca star). Util para migrar a 1 "
                        "etiqueta por mail.")
    p.add_argument("--delete-label", action="store_true",
                   help="Junto con --cleanup-label, elimina la etiqueta de "
                        "Gmail despues de removerla de los mails.")
    return p.parse_args()


def main():
    setup_logging()
    args = parse_args()
    if args.explain:
        service = get_service()
        explain_message(service, args.explain)
        return
    if args.snapshot:
        service = get_service()
        snapshot(service, args.snapshot,
                  include_trash=args.snapshot_include_trash)
        return
    if args.cleanup_label:
        service = get_service()
        cleanup_label(service, args.cleanup_label,
                       delete_label=args.delete_label)
        return
    with SingleInstanceLock(LOCK_FILE):
        run(args)


if __name__ == "__main__":
    main()
