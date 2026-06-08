# GUÍA — Organizador de Gmail

Esta guía resume cómo funciona el sistema, cómo ajustarlo y cómo operarlo,
sin depender del chat. Está pensada para vos (no hace falta ser programador).

---

## 1. Qué hace, en una frase

Todas las noches a las **22:00 (hora Argentina)**, un robot en la nube
(GitHub Actions) revisa tu Gmail y: **etiqueta**, **archiva**, manda a
**Papelera** lo descartable y **expira** lo viejo. Nunca borra de forma
permanente (todo a Papelera, recuperable 30 días). Corre solo, sin tu PC.

Cada corrida deja un **borrador con el resumen** en tu propia casilla.

---

## 2. Las reglas (cómo decide)

El orden de decisión para cada correo es:

1. **Mis propios envíos** (`lautaroronchi97@gmail.com`) → etiqueta `Yo enviados`, archiva.
2. **Lista blanca** (`config.WHITELIST`) → intocable, queda en Recibidos.
3. **Auto-trash** (`config.AUTO_TRASH_SENDERS`) → Papelera apenas llega.
4. **Remitente importante** (`config.IMPORTANT_SENDERS`) → su etiqueta (Finanzas, Salud, Boca, Cocos, etc.).
5. **Persona real** (no parece automático) → `Personal`, intocable.
6. **Palabras clave** (factura, servicios, viajes…) → etiqueta temática.
7. **Promociones** → se conservan si son útiles (banco/súper/combustible), si no a Papelera.
8. **Social / Notificaciones / Foros** → Papelera.
9. **Duda** → queda en Recibidos con etiqueta `Revisar`.

Además, en cada corrida:
- **Expiración por edad**: los correos más viejos que el umbral de su
  etiqueta van a Papelera (ver tabla abajo).
- **1 etiqueta por mail**: lo importante lleva además una **estrella** ⭐
  como respaldo (no una segunda etiqueta).

---

## 3. Etiquetas y expiración por edad

| Etiqueta | Expira a los… |
|---|---|
| Impuestos y gobierno | 730 días (2 años) |
| Finanzas | 365 días |
| Inversiones | 365 días |
| Servicios y facturas | 180 días |
| Salud | 180 días |
| Yo enviados | 180 días |
| Educación | 90 días |
| Cocos | 90 días |
| Compras | 60 días |
| Inmuebles | 60 días |
| Boca | 30 días |
| Viajes | 30 días |
| Trabajo | 30 días |
| Suscripciones | 30 días |
| Promos que sirven | 30 días |
| **Personal** | **nunca** |
| **Revisar** | **nunca** |

Para cambiar un umbral: editá `LABEL_EXPIRY_DAYS` en `config.py`.
Ej.: querés que Compras dure 90 días → cambiá `"Compras": 60` por `"Compras": 90`.
Para que una etiqueta **no expire nunca**, sacala del diccionario o ponela en `0`.

---

## 4. Cómo ajustar las reglas (archivo `config.py`)

Todo se edita en `config.py`. No hace falta tocar el código principal.

- **Un remitente importante quedó mal etiquetado** → agregá su dominio/mail
  a la categoría correcta en `IMPORTANT_SENDERS`.
- **Querés que un remitente vaya siempre a Papelera** → agregá su email a
  `AUTO_TRASH_SENDERS`. (Ojo: NO pongas un contacto personal que querés
  conservar a futuro; esos van por expiración.)
- **Querés proteger a alguien para que nunca se toque** → agregá su mail o
  dominio a `WHITELIST`.
- **Sumar palabras clave a una categoría** → editá `CATEGORY_KEYWORDS`.
- **Cambiar plazos de expiración** → `LABEL_EXPIRY_DAYS`.

Después de editar, guardá y subí el cambio (o pedímelo a mí en el chat).

---

## 5. Operación diaria (no tenés que hacer nada)

La tarea corre sola. Si querés mirar:

- **Resumen**: cada noche aparece un borrador "Resumen organizador Gmail —
  fecha" en tu Gmail (carpeta Borradores).
- **Ver detalle de una corrida**: GitHub → pestaña **Actions** →
  "Organizar Gmail diario" → entrá a la corrida → artifact `logs-…`.

---

## 6. Correr a mano cuando quieras

GitHub → **Actions** → "Organizar Gmail diario" → botón **Run workflow**.
Opciones (inputs):

- **label_only = true** → modo seguro: solo etiqueta, NO archiva ni manda a
  Papelera. Útil para probar cambios sin riesgo.
- **full = true** → procesa TODA la casilla (no solo lo nuevo).

Sin marcar nada, procesa lo nuevo desde la última corrida y aplica todo.

---

## 7. Modos: completo vs prueba

- **Hoy está en MODO COMPLETO**: la corrida diaria archiva y manda a Papelera.
- **Volver a modo prueba** (solo etiquetar) de forma temporal: corré a mano
  con `label_only = true`.
- **Volver a modo prueba permanente**: en `.github/workflows/diario.yml`,
  paso "Correr organizador", agregá de nuevo el bloque:
  ```bash
  if [ "${{ github.event_name }}" = "schedule" ]; then
    FLAGS="$FLAGS --label-only"
  fi
  ```

---

## 8. Herramientas extra (workflows en Actions)

- **Snapshot de la casilla** (`snapshot.yml`): genera un CSV con todos tus
  mails (id, remitente, asunto, etiquetas, fecha). Sirve para comparar
  antes/después de una limpieza.
- **Analizar diff** (`analizar_diff.yml`): compara dos snapshots (A y B) y
  detecta patrones de lo que eliminaste, para proponer reglas nuevas.
- **Dump de estado** (`dump.yml`): vuelca `senders.json` y el último log
  para diagnóstico.

Así fue como el sistema "aprendió" tu criterio: comparando tu casilla antes
y después de que limpiaras a mano 2.295 correos.

---

## 9. Mantenimiento ocasional

- **Si Google corta el acceso** (raro, ya publicaste la app OAuth): el token
  nuevo queda como artifact `token-…` en la última corrida. Bajalo, pasalo a
  base64 y reemplazá el secret `GMAIL_TOKEN_B64`. (O pedímelo y te guío.)
- **Si el repo queda 60 días sin actividad**, GitHub pausa el cron. Un push o
  un "Run workflow" lo reactiva.
- **Reset de memoria de remitentes**: si cambian mucho las reglas, se sube el
  número de versión del cache (`organizer-state-vN`) en el workflow.

---

## 10. Garantías de seguridad (siempre)

- **Nunca borrado permanente** — todo va a Papelera (recuperable 30 días).
- **Personal y personas reales** nunca se archivan ni descartan.
- **Lista blanca** gana sobre cualquier otra regla.
- **Logs de cada acción** quedan registrados (artifacts) para auditar.

---

## Archivos del proyecto

| Archivo | Qué es |
|---|---|
| `gmail_organizer.py` | Script principal. |
| `config.py` | **Todas las reglas editables.** |
| `prompt_ordenar_gmail.md` | Reglas de negocio en lenguaje natural. |
| `analizar_diff.py` | Comparador de snapshots. |
| `.github/workflows/diario.yml` | Tarea diaria 22:00. |
| `.github/workflows/snapshot.yml` | Genera CSV de la casilla. |
| `.github/workflows/analizar_diff.yml` | Analiza diff A vs B. |
| `.github/workflows/dump.yml` | Diagnóstico de estado. |
| `subir_secrets.ps1` / `.sh` | Subir credenciales como secrets. |
| `README.md` | Instalación y puesta en marcha. |
| `GUIA.md` | Esta guía. |
