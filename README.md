# Automatización Gmail

Asistente para **ordenar y mantener limpia una casilla de Gmail personal**:
etiqueta, archiva o manda a Papelera los correos según reglas claras, con foco
en **no perder nada importante** y **nunca borrar de forma permanente**.

Las reglas de negocio están descritas en lenguaje natural en
[`prompt_ordenar_gmail.md`](prompt_ordenar_gmail.md) y traducidas a código en
[`config.py`](config.py) + [`gmail_organizer.py`](gmail_organizer.py).

## Qué hace

- **Clasifica** cada correo en etiquetas: Finanzas, Impuestos y gobierno,
  Servicios y facturas, Salud, Compras, Viajes, Promos que sirven, Personal,
  Guardar.
- **Archiva** lo importante ya etiquetado que no requiere acción.
- **Deja en Recibidos** lo que requiere que hagas algo y lo dudoso (etiqueta
  `Revisar`).
- **Manda a Papelera** (nunca borrado permanente) promociones/marketing y
  notificaciones sin relevancia. La Papelera es recuperable 30 días.
- **Conserva** promos útiles (bancos Santander/Macro/BNA, supermercados,
  combustible) y las vence solo a los 30 días.
- **Respaldo dentro de Gmail**: a lo más importante le agrega la etiqueta
  `Guardar` + estrella.
- **Lista blanca**: todo lo que venga de una **persona real** queda intacto en
  Recibidos.
- **Agente de remitentes**: mantiene un índice (`senders.json`), da de alta los
  nuevos y **reclasifica** a los que dejan de encajar.
- **Registra todo** en `logs/actions-*.jsonl`.

## Reglas de seguridad

1. **La primera corrida es dry-run** (no modifica nada). De hecho, si no pasás
   `--execute`, el script SIEMPRE corre en modo prueba.
2. **Nunca borrado permanente**: usa el scope `gmail.modify`, que no permite
   borrar definitivamente. Todo lo descartado va a Papelera.
3. La **lista blanca** (personas reales + lo que agregues en `config.WHITELIST`)
   nunca se archiva ni va a Papelera.

## Instalación

```bash
python -m venv .venv
# Windows:  .venv\Scripts\activate
# Linux/Mac: source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env   # y completá si hace falta
```

## Credenciales de Google (una sola vez)

1. Entrá a [Google Cloud Console](https://console.cloud.google.com/) y creá un
   proyecto.
2. **APIs y servicios → Biblioteca →** habilitá **Gmail API**.
3. **Pantalla de consentimiento OAuth**: tipo *Externo*, agregá tu propio mail
   como *usuario de prueba*.
4. **Credenciales → Crear credenciales → ID de cliente de OAuth → Aplicación de
   escritorio**. Descargá el JSON y guardalo en esta carpeta como
   `credentials.json`.
5. La primera ejecución abre el navegador para que autorices; se crea
   `token.json` solo. (Ambos archivos están en `.gitignore`, no se suben.)

## Uso

```bash
# 1) PRIMERA VEZ: prueba sobre toda la casilla, NO modifica nada
python gmail_organizer.py --dry-run --full

# 2) Modo "shadow": solo etiqueta, no archiva ni manda a Papelera.
#    Útil para ganar confianza una semana antes de habilitar acciones.
python gmail_organizer.py --execute --full --label-only

# 3) Si el informe está OK, ejecutá de verdad sobre todo el historial
python gmail_organizer.py --execute --full

# 4) De ahí en más, corridas diarias solo sobre lo nuevo
python gmail_organizer.py --execute --since 1d
# o, mejor, usar la ventana persistida desde la última corrida:
python gmail_organizer.py --execute --since-last-run

# Debug: ver cómo se clasificaría un mensaje puntual
python gmail_organizer.py --explain MSG_ID
```

### Flags útiles

| Flag | Para qué |
|---|---|
| `--dry-run` / `--execute` | Modo prueba (default) o aplicar cambios. |
| `--full` | Toda la casilla. |
| `--since 1d` | Ventana relativa (ej. `12h`, `2d`). |
| `--since-last-run` | Ventana desde la última corrida (state.json). |
| `--limit N` | Tope de mensajes por corrida (útil para probar). |
| `--label-only` | Solo etiqueta, no archiva ni manda a Papelera. |
| `--no-summary-draft` | No crear draft con el resumen al terminar. |
| `--explain MSG_ID` | Mostrar la decisión que se tomaría para ese ID. |

### Qué hace además

- **Retries con backoff** ante 429/5xx de Gmail.
- **Rota** `logs/cron.log` (5MB × 5) y **poda** `logs/actions-*.jsonl` &gt; 90 días.
- **Lock** de instancia única (`.organizer.lock`) para evitar solapamientos.
- **Memoria de remitentes**: un sender con &gt; 5 correos clasificados con éxito
  se aplica su última etiqueta directo (más rápido y predecible).
- **Resumen como draft**: al terminar deja un borrador con el informe en tu
  propia casilla. Apagar con `--no-summary-draft`.
- **Privacidad**: el subject se trunca a 80 chars en los logs, el body nunca se
  guarda, `logs/` y `token.json` quedan con `chmod 600` cuando se puede.

## Tarea diaria automática (22:00)

### Windows (Programador de tareas)

1. Editá `correr_22hs.bat` si moviste la carpeta.
2. Abrí **Programador de tareas → Crear tarea básica**.
3. Desencadenador: **Diariamente**, hora **22:00**.
4. Acción: **Iniciar un programa** → seleccioná `correr_22hs.bat`.
5. Marcá *Ejecutar tanto si el usuario inició sesión como si no*.

O por línea de comandos (PowerShell como administrador):

```powershell
schtasks /Create /SC DAILY /ST 22:00 /TN "Organizar Gmail" ^
  /TR "C:\ruta\a\Automatizacion-gmail\correr_22hs.bat"
```

### Linux/Mac (cron)

```cron
# Todos los días a las 22:00
0 22 * * * cd /ruta/a/Automatizacion-gmail && /ruta/.venv/bin/python gmail_organizer.py --execute --since 1d >> logs/cron.log 2>&1
```

### GitHub Actions (corre solo en la nube, sin PC prendida)

Hay un workflow listo en [`.github/workflows/diario.yml`](.github/workflows/diario.yml) que corre todos los días a las 01:00 UTC (22:00 ARG).

**Antes de habilitarlo:**

1. **OAuth app "In production"**. En Google Cloud Console → "OAuth consent screen" → cambiá el publishing status de *Testing* a *In production*. Si no, el `refresh_token` caduca cada 7 días y la tarea se rompe. Para apps de uso personal, publicar es gratis y queda como "no verificada" — sin problema.

2. **Primera corrida local**: hacé al menos un `python gmail_organizer.py --dry-run --full` en tu máquina para que se genere `token.json` con el `refresh_token`.

3. **Subir los secrets al repo** (Settings → Secrets and variables → Actions → New repository secret):

   En tu PC, generá los base64:
   ```bash
   # Linux/Mac
   base64 -i credentials.json | tr -d '\n'
   base64 -i token.json | tr -d '\n'

   # Windows (PowerShell)
   [Convert]::ToBase64String([IO.File]::ReadAllBytes("credentials.json"))
   [Convert]::ToBase64String([IO.File]::ReadAllBytes("token.json"))
   ```
   Y cargá cada uno como secret:
   - `GMAIL_CREDENTIALS_B64`
   - `GMAIL_TOKEN_B64`

4. **Probar manual primero**: Actions → "Organizar Gmail diario" → "Run workflow" → marcá `label_only` la primera vez. Revisás los artifacts (`logs-*`) y el draft de resumen en tu Gmail.

5. **Listo**: a partir de ahí corre solo todos los días.

**Cosas a saber:**

- `senders.json` y `state.json` se persisten entre corridas vía cache de Actions.
- Si Google rota el `refresh_token`, el nuevo `token.json` queda como artifact (7 días). Bajalo y re-subilo como secret.
- Si el repo queda 60 días sin actividad, GitHub deshabilita el cron. Un push o un run manual lo reactiva.

## Afinar las reglas

Todo se edita en [`config.py`](config.py): remitentes importantes, palabras
clave, promos a conservar, lista blanca, días de vencimiento de promos, etc.
No hace falta tocar `gmail_organizer.py`.

## Archivos

| Archivo | Qué es |
|---|---|
| `prompt_ordenar_gmail.md` | Reglas de negocio en lenguaje natural. |
| `gmail_organizer.py` | Script principal. |
| `config.py` | Reglas/listas configurables. |
| `correr_22hs.bat` | Lanzador para la tarea diaria de Windows. |
| `requirements.txt` | Dependencias Python. |
| `.env.example` | Plantilla de configuración. |
| `senders.json` | Índice de remitentes (se genera solo, no se sube). |
| `logs/` | Registro de acciones (se genera solo, no se sube). |
