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

# 2) Si el informe está OK, ejecutá de verdad sobre todo el historial
python gmail_organizer.py --execute --full

# 3) De ahí en más, corridas diarias solo sobre lo nuevo
python gmail_organizer.py --execute --since 1d
```

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
