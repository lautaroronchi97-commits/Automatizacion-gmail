"""
Comparar dos snapshots de Gmail (CSV de --snapshot) y proponer reglas.

Uso:
    python analizar_diff.py snapshot_A.csv snapshot_B.csv

Heurística:
- Para cada remitente en A:
    deleted = mails que estaban en A y no en B (fueron a Papelera)
    kept    = mails que sobrevivieron en B
- AUTO_TRASH_SENDERS: deleted >= 3 y kept == 0 (el remitente nunca se conserva).
- EXPIRA_TRAS_N_DIAS: kept >= 1 pero todos los kept son recientes (≤ N días)
  y todos los deleted son antiguos (> N días). Estimar N como la edad mínima
  de los deleted o la edad máxima de los kept + margen.
- KEEP_ALL: deleted == 0 y kept >= 1 -> remitente "intocable".
- MIXED: edge cases con datos insuficientes.

El usuario aclaro: "muchos mails eran importantes pero los elimine por pasar
mucho tiempo y perder relevancia". Por eso priorizamos la regla por edad
sobre la regla absoluta cuando hay sobrevivientes.
"""

import csv
import datetime as dt
import re
import sys
from collections import Counter, defaultdict

WHITELIST_TLDS_PERSONAS = ("gmail.com", "hotmail.com", "outlook.com",
                            "yahoo.com.ar", "yahoo.com", "live.com",
                            "icloud.com")


def parse_iso(s):
    if not s:
        return None
    try:
        return dt.datetime.fromisoformat(s)
    except Exception:
        return None


def load_csv(path):
    rows = {}
    with open(path, encoding="utf-8") as f:
        r = csv.DictReader(f)
        for row in r:
            rows[row["id"]] = row
    return rows


def primary_label(row):
    """Devuelve la primera label 'humana' que aparece (no INBOX/UNREAD/STARRED/CATEGORY_)."""
    names = (row.get("label_names") or "").split(";")
    sys_labels = {"INBOX", "UNREAD", "STARRED", "IMPORTANT", "SENT",
                   "DRAFT", "TRASH", "SPAM"}
    for n in names:
        n = n.strip()
        if not n or n in sys_labels:
            continue
        if n.startswith("CATEGORY_"):
            continue
        return n
    return "(sin etiqueta)"


def main(a_path, b_path):
    a = load_csv(a_path)
    b = load_csv(b_path)
    a_ids = set(a)
    b_ids = set(b)
    deleted = a_ids - b_ids
    kept = a_ids & b_ids
    new = b_ids - a_ids

    print(f"\n{'='*70}")
    print(f"DIFF: {a_path}  ->  {b_path}")
    print(f"{'='*70}")
    print(f"En A (antes): {len(a)} mails")
    print(f"En B (despues): {len(b)} mails")
    print(f"Eliminados (A pero no B): {len(deleted)}")
    print(f"Conservados (A y B):      {len(kept)}")
    print(f"Nuevos (B pero no A):     {len(new)}")

    now = dt.datetime.now()
    by_sender = defaultdict(lambda: {"deleted": [], "kept": []})
    for mid in deleted:
        row = a[mid]
        by_sender[row["from_email"]]["deleted"].append(row)
    for mid in kept:
        row = a[mid]
        by_sender[row["from_email"]]["kept"].append(row)

    # Buckets de remitentes
    always_trash = []
    expira_por_edad = []
    mostly_trash = []
    keep_all = []
    mixed = []

    for s, d in by_sender.items():
        nd = len(d["deleted"])
        nk = len(d["kept"])
        if nd == 0 and nk >= 1:
            keep_all.append((s, nk))
            continue
        # ages: dias desde el correo a hoy
        del_ages = [(now - parse_iso(r["internal_date"])).days
                     for r in d["deleted"] if parse_iso(r["internal_date"])]
        kept_ages = [(now - parse_iso(r["internal_date"])).days
                      for r in d["kept"] if parse_iso(r["internal_date"])]
        if nk == 0 and nd >= 3:
            always_trash.append((s, nd, del_ages))
            continue
        if nk >= 1 and nd >= 2 and kept_ages and del_ages:
            max_kept = max(kept_ages)
            min_del = min(del_ages)
            # Si los conservados son TODOS mas nuevos que los descartados,
            # hay una regla de antigüedad clara.
            if max_kept < min_del:
                threshold = min_del  # dias a partir de los cuales se descarta
                expira_por_edad.append(
                    (s, nd, nk, max_kept, min_del, threshold))
                continue
        if nd >= nk * 2 and nd >= 2:
            mostly_trash.append((s, nd, nk, del_ages, kept_ages))
            continue
        mixed.append((s, nd, nk))

    # Análisis por etiqueta (label_names): cuántos eliminó por etiqueta
    label_kept = Counter()
    label_del = Counter()
    for mid in kept:
        label_kept[primary_label(a[mid])] += 1
    for mid in deleted:
        label_del[primary_label(a[mid])] += 1
    print("\n=== Por etiqueta primaria ===")
    print(f"{'Etiqueta':30s}  {'kept':>5s}  {'del':>5s}  {'%del':>5s}")
    all_labels = sorted(set(label_kept) | set(label_del))
    for lb in all_labels:
        k = label_kept.get(lb, 0)
        di = label_del.get(lb, 0)
        tot = k + di
        pct = (di * 100 // tot) if tot else 0
        print(f"  {lb:28s}  {k:5d}  {di:5d}  {pct:4d}%")

    # Sugerencias
    print(f"\n=== SIEMPRE TRASH ({len(always_trash)} remitentes) ===")
    print("Reglas para AUTO_TRASH_SENDERS (cero sobrevivientes, >=3 descartados):")
    always_trash.sort(key=lambda x: -x[1])
    for s, n, ages in always_trash[:80]:
        edad_max = max(ages) if ages else 0
        edad_min = min(ages) if ages else 0
        print(f"  {n:4d}  edad {edad_min}-{edad_max}d  {s}")

    print(f"\n=== EXPIRA POR EDAD ({len(expira_por_edad)} remitentes) ===")
    print("Reglas EXPIRA_TRAS_N_DIAS (los sobrevivientes son TODOS mas nuevos que el mas nuevo descartado):")
    expira_por_edad.sort(key=lambda x: x[5])  # por threshold
    for s, nd, nk, max_kept, min_del, thr in expira_por_edad[:60]:
        print(f"  del={nd:3d} keep={nk:2d}  kept_max_age={max_kept}d  del_min_age={min_del}d  -> expira tras {thr}d  {s}")

    # Estimar threshold global de "expira por edad" (mediana)
    if expira_por_edad:
        thresholds = sorted(x[5] for x in expira_por_edad)
        median = thresholds[len(thresholds) // 2]
        print(f"\n>>> Threshold mediano de expiracion: {median} dias")

    print(f"\n=== MAYORMENTE TRASH ({len(mostly_trash)} remitentes) ===")
    print("Reglas SOFT_TRASH (descarte 2:1 vs conservados):")
    mostly_trash.sort(key=lambda x: -x[1])
    for s, nd, nk, dages, kages in mostly_trash[:30]:
        mkd = max(kages) if kages else 0
        mxd = max(dages) if dages else 0
        print(f"  del={nd:3d} keep={nk:2d}  keep_max_age={mkd}d  del_max_age={mxd}d  {s}")

    print(f"\n=== KEEP ALL ({len(keep_all)}) — nunca eliminados, intocables ===")
    keep_all.sort(key=lambda x: -x[1])
    for s, n in keep_all[:60]:
        print(f"  {n:4d}  {s}")

    print(f"\n=== MIXED ({len(mixed)}) — datos ambiguos ===")
    for s, nd, nk in mixed[:20]:
        print(f"  del={nd} keep={nk}  {s}")

    # Generar fragmentos de config sugeridos
    print("\n" + "="*70)
    print("FRAGMENTOS SUGERIDOS PARA config.py")
    print("="*70)

    print("\n# Senders que siempre van a Papelera (cero sobrevivientes):")
    print("AUTO_TRASH_SENDERS = [")
    for s, n, ages in always_trash:
        if "@" in s:
            domain = s.split("@", 1)[1]
            # Quedarnos con el dominio si el localpart es UUID-like
            local = s.split("@", 1)[0]
            if len(local) > 25 or re.search(r"[+_][0-9a-z]{6,}", local):
                token = domain
            else:
                token = s
        else:
            token = s
        print(f"    {token!r},   # {n} mails descartados")
    print("]")

    if expira_por_edad:
        print("\n# Senders que expiran tras N dias (todos los sobrevivientes son nuevos):")
        print("EXPIRE_SENDERS = {")
        for s, nd, nk, max_kept, min_del, thr in expira_por_edad:
            print(f"    {s!r}: {thr},   # {nd} viejos descartados, {nk} nuevos OK")
        print("}")


if __name__ == "__main__":
    if len(sys.argv) != 3:
        sys.exit("Uso: python analizar_diff.py snapshot_A.csv snapshot_B.csv")
    main(sys.argv[1], sys.argv[2])
