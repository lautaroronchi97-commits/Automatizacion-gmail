"""
Configuración de reglas para el organizador de Gmail.

Todas las reglas del prompt (prompt_ordenar_gmail.md) se traducen acá en datos
que el script gmail_organizer.py usa para clasificar. Editá estas listas para
afinar el comportamiento; no hace falta tocar el código principal.
"""

# --------------------------------------------------------------------------
# Email del dueño de la casilla. Los correos cuyo From sea este email
# (mensajes enviados que terminaron en Recibidos, drafts, propios) se mandan
# a la etiqueta "Yo enviados" y se archivan.
# --------------------------------------------------------------------------
OWN_EMAILS = [
    "lautaroronchi97@gmail.com",
]

# --------------------------------------------------------------------------
# Etiquetas que se crean (si no existen) y se aplican.
# Orden de prioridad implícito por el orden en classify().
# --------------------------------------------------------------------------
LABELS = [
    "Finanzas",
    "Inversiones",
    "Impuestos y gobierno",
    "Servicios y facturas",
    "Salud",
    "Compras",
    "Inmuebles",
    "Trabajo",
    "Viajes",
    "Educación",
    "Suscripciones",
    "Promos que sirven",
    "Personal",
    "Yo enviados",
    "Boca",
    "Cocos",
    "Guardar",
    "Revisar",  # auxiliar: correos dudosos que dejo para revisión manual
]

# --------------------------------------------------------------------------
# Remitentes importantes por categoría (match por substring en email o nombre).
# Todo en minúsculas. Estas reglas tienen PRIORIDAD máxima sobre cualquier
# heurística de "persona/automático" — es decir, un remitente que matchee
# acá se etiqueta así aunque su localpart sea raro.
# --------------------------------------------------------------------------
IMPORTANT_SENDERS = {
    "Finanzas": [
        # bancos AR
        "santander", "santanderrio", "macro", "bancomacro", "bna",
        "banconacion", "bancanacion", "mailing.bna", "galicia", "bbva",
        "itau", "hsbc", "comafi", "supervielle", "patagonia", "icbc",
        "credicoop", "bancociudad", "bancoprovincia", "bancomunicipal",
        # redes / tarjetas
        "redlink", "visa", "mastercard", "amex", "cabal", "naranja",
        "naranjax", "creditmas", "infomistarjetas", "firstdata",
        # billeteras / fintech
        "mercadopago", "mercado pago", "uala", "ualá", "personalpay",
        "modo", "brubank", "prex", "globalgetnet", "payway",
        # cripto
        "lemon", "letsbit", "fiwind", "buenbit", "ripio",
    ],
    "Inversiones": [
        # brokers / bolsa AR
        "bullmarket", "bullmarketbrokers", "bull market", "rava", "rava.com",
        "balanz", "iol", "invertironline", "portfoliopersonal", "ppi",
        "allariabursatil", "allaria", "sbs.com.ar", "matba", "rofex",
        # entes / cámaras
        "bymadata", "byma", "infosocios@bcr", "bcr.com.ar", "bcra",
        "cajadevalores", "caja de valores", "cnv.gob.ar",
        # newsletters bursátiles
        "mercadoen5minutos", "m5m@p.mercadoen5minutos", "ole.com.ar/finanzas",
        "carryinvest", "puentenet", "puente.com",
    ],
    "Impuestos y gobierno": [
        "arca", "afip", "anses", "rentas", "agip", "arba",
        "municipal", "municipalidad", "gob.ar", "gov.ar",
        "miargentina", "mi argentina", "renaper", "andis",
        "migraciones", "pami", "tarjeta sube", "argentina.gob",
        "santafe.gov.ar", "santafe.gob.ar",
    ],
    "Servicios y facturas": [
        # energía
        "edenor", "edesur", "edea", "edemsa", "edelap", "epec", "epesf",
        "epe.santafe", "ese.gov.ar",
        # gas
        "metrogas", "naturgy", "camuzzi", "litoralgas", "litoral-gas",
        "ecogas",
        # agua
        "aysa", "absa", "aguasdelnorte", "aguascorrentinas",
        "aguassantafesinas",
        # telco / TV
        "movistar", "claro", "telecom", "fibertel", "cablevision",
        "telecentro", "iplan", "flow", "directv",
        "factura.personal.com.ar", "factura-digital@factura.personal",
        # expensas
        "expensaspagas", "consorcioabierto", "octopuspro", "expensaonline",
        # seguros
        "sancristobal", "sancorseguros", "lacaja", "rivadaviaseguros",
        "alianza.com.ar", "mercantilandina", "providencia",
    ],
    "Salud": [
        # prepagas
        "swissmedical", "swiss medical", "swissmedical.com.ar",
        "osde", "galenoargentina", "medicus", "omint",
        "sancorsalud", "prevencionsalud", "accord salud", "medife",
        # turnos / clínicas
        "grupocentro", "doctoralia",
    ],
    "Suscripciones": [
        "netflix", "spotify", "disneyplus", "disney+", "hbomax", "max.com",
        "primevideo", "youtube premium", "apple.com", "icloud",
        "paramount", "starplus", "deezer",
    ],
    "Compras": [
        # mercadolibre (TODOS los subdominios)
        "mercadolibre.com", "mercadolibre.com.ar", "mail.mercadolibre",
        "mercadoshops", "no-responder@mercadolibre", "no-reply@mercadolibre",
        "info@e.mercadolibre", "info@r.mercadolibre", "ofertas@a.mercadolibre",
        "ofertas@r.mercadolibre", "info@mercado",
        # otros marketplaces / retailers
        "amazon.com", "tiendamia", "tiendanube", "vtexcommerce",
        "viumi.com.ar", "frávega", "fravega", "garbarino", "musimundo",
        "heyas.zendesk", "dexpaco",
        # logística / entregas
        "correoargentino", "andreani", "oca.com", "moova", "urbano",
    ],
    "Inmuebles": [
        "zonaprop", "argenprop", "properati", "remax", "tokko",
        "inmuebles@e.mercadolibre", "inmuebles.mercadolibre",
        "mapropiedades", "bacepropiedades", "hasanestudio",
        "hasanestudioinmobiliario", "gexion.com.ar", "si.gexion",
        "sabella del castillo", "sabelladelcastillo", "habitam.com",
    ],
    "Trabajo": [
        "postularse", "computrabajo", "zonajobs", "bumeran", "indeed",
        "jobs-noreply@linkedin", "linkedin.com/jobs",
        "jobalerts-noreply@linkedin", "talentpitch", "konzerta",
        "trabajos_ar", "atencionalusuario@zonajobs",
    ],
    "Educación": [
        "udemy", "coursera", "platzi", "edx", "domestika",
        "fcecon.unr.edu.ar", "posgrado.rosario@austral.edu",
        "posgrado-econo", "austral.edu.ar", ".edu.ar",
        "uba.ar", "unc.edu.ar", "uns.edu.ar", "ucema.edu.ar",
    ],
    "Boca": [
        "bocajuniors", "boca juniors", "bocajuniors.com", "cabj",
        "sociosboca",
    ],
    "Cocos": [
        "cocoscapital", "cocos capital", "cocos.capital", "micocos",
        "cocos crypto", "mailing.cocos", "cocospro@cocos",
        "noreply@mailing.cocos",
    ],
}

# --------------------------------------------------------------------------
# Servicios y facturas: también por keyword (acotado para evitar falsos
# positivos en newsletters que mencionan "factura" como ejemplo).
# --------------------------------------------------------------------------
SERVICE_INVOICE_KEYWORDS = [
    "tu factura", "factura electronica", "factura electrónica",
    "tu comprobante", "tu resumen", "vencimiento de tu", "tu boleta",
    "aviso de pago", "tu póliza", "tu poliza",
]

# --------------------------------------------------------------------------
# Promociones que se CONSERVAN (etiqueta "Promos que sirven", NO van a Papelera).
# --------------------------------------------------------------------------
PROMO_KEEP_SENDERS = [
    # tarjetas / bancos
    "santander", "santanderrio", "macro", "bancomacro", "bna",
    "banconacion", "galicia", "bbva", "naranja", "naranjax",
    "bancomunicipal",
    # supermercados
    "carrefour", "coto", "dia", "diaonline", "jumbo", "disco", "vea",
    "laanonima", "la anonima", "makro", "changomas", "walmart",
    # combustible / estaciones de servicio
    "ypf", "shell", "axion", "puma", "gulf",
]

# --------------------------------------------------------------------------
# Palabras clave que marcan un correo como IMPORTANTE (asunto o cuerpo).
# Acotadas para evitar matches falsos.
# --------------------------------------------------------------------------
IMPORTANT_KEYWORDS = [
    "tu factura", "tu comprobante", "tu recibo", "tu resumen",
    "vencimiento", "pago pendiente", "transferencia recibida",
    "tu turno", "tu reserva", "tu vuelo", "tu pasaje",
    "tu garantía", "tu garantia", "código de verificación",
    "codigo de verificacion", "verificación de seguridad",
    "verificacion de seguridad", "tu contraseña", "tu contrasena",
    "alerta de seguridad",
]

# Palabras clave que sugieren que el correo REQUIERE ACCIÓN -> dejar en Recibidos
# (en vez de archivar), aunque esté etiquetado.
ACTION_KEYWORDS = [
    "vence", "vencimiento", "vencido", "pago pendiente", "impago",
    "confirmar tu", "acción requerida", "accion requerida",
    "último aviso", "ultimo aviso", "corte de servicio",
    "tu turno", "confirmá tu",
]

# Palabras clave por categoría temática (asunto/cuerpo). MUY específicas para
# no contagiar (ej. "reserva" suelto matcheaba newsletters de Bull Market que
# decían "reservá tu lugar"; ahora se exige "tu reserva" o "reserva confirmada").
CATEGORY_KEYWORDS = {
    "Boca": [
        "boca juniors", "bocajuniors", "boca jrs", "club atletico boca",
        "club atlético boca", "cabj", "socios boca", "sociosboca",
    ],
    "Cocos": [
        "cocos capital", "cocoscapital", "cocos.capital", "micocos",
        "cocos crypto", "mailing.cocos",
    ],
    "Inversiones": [
        "mercado de capitales", "mercado de valores", "operador de mercado",
        "comercial de mercado", "broker bursátil", "broker bursatil",
        "bolsa de comercio", "rueda bursátil", "rueda bursatil",
        "panel general", "panel líder", "panel lider", "panel pyme",
        "cedear", "cedears", "merval", "s&p merval", "rofex",
        "dólar mep", "dolar mep", "dólar ccl", "dolar ccl",
        "dólar bolsa", "dolar bolsa",
        "fondo común de inversión", "fondo comun de inversion", "fci",
        "cotización del mercado", "renta fija", "renta variable",
    ],
    "Trabajo": [
        "avisos de búsqueda", "avisos de busqueda", "ofertas de trabajo",
        "tu postulación", "tu postulacion", "te postulaste",
        "actualizá tu cv", "actualiza tu cv", "tu currículum",
        "tu curriculum", "alertas de empleo", "alertas de búsqueda",
        "alertas de busqueda", "linkedin jobs", "tu próxima oportunidad",
    ],
    "Inmuebles": [
        "zonaprop", "argenprop", "properati",
        "alquiler de departamento", "venta de departamento",
        "tu propiedad", "tu inmueble", "garantía de alquiler",
        "garantia de alquiler", "recibo pago/cobro", "expensas del mes",
    ],
    "Compras": [
        "mercadolibre", "mercado libre", "tu envío", "tu envio",
        "envío en camino", "envio en camino", "tu pedido", "tu compra",
        "seguimiento de tu", "amazon.com", "número de seguimiento",
        "numero de seguimiento", "rechazamos tu pago",
    ],
    "Viajes": [
        # MUY específicas; sacamos "reserva" suelto, "hotel" suelto, etc.
        "tu vuelo", "tu pasaje", "tu reserva", "tu hotel",
        "booking.com", "despegar.com", "decolar.com", "trip.com",
        "aerolineas argentinas", "aerolíneas argentinas",
        "latam.com", "latam pass", "check-in en línea",
        "check-in en linea", "itinerario de vuelo", "boarding pass",
        "tu próximo viaje", "tu proximo viaje",
    ],
    "Educación": [
        "udemy", "coursera", "platzi", "edx", "domestika",
        ".edu.ar", "universidad nacional", "facultad de",
        "posgrado en", "maestría en", "maestria en",
        "curso de", "diplomatura en", "tu inscripción",
        "tu inscripcion",
    ],
    "Suscripciones": [
        "renovación de tu", "renovacion de tu", "tu suscripción",
        "tu suscripcion", "cobro automático", "cobro automatico",
        "tu plan se renueva", "tu plan se renovó", "tu plan se renovo",
    ],
}

# Correos a los que, además, se aplica etiqueta "Guardar" + estrella (respaldo).
BACKUP_LABELS = {
    "Finanzas", "Inversiones", "Impuestos y gobierno",
    "Servicios y facturas", "Viajes", "Suscripciones",
}
BACKUP_KEYWORDS = [
    "resumen", "comprobante", "factura", "pago", "garantía", "garantia",
    "pasaje", "trámite", "tramite", "póliza", "poliza",
]

# --------------------------------------------------------------------------
# Detección de remitente automático. La comparación se hace con local-part
# EXACTA o con prefijo + separador (./-/_), no como substring.
# Esta lista ahora cubre los patterns que vimos en la pasada full:
# no-responder, mensajesyavisos, factura-digital, etc.
# --------------------------------------------------------------------------
AUTOMATED_LOCALPARTS = [
    "no-reply", "noreply", "no_reply", "no-responder", "no-responde",
    "donotreply", "do-not-reply",
    "info", "news", "newsletter", "newsletters", "novedades",
    "notificaciones", "notifications", "notification",
    "marketing", "mailer", "mailing", "mailings", "mailings-noreply",
    "ventas", "sales", "soporte", "support", "atencion", "atención",
    "atencionalusuario", "atencionalcliente", "atencion_cliente",
    "atcliente", "atc",
    "hello", "contacto", "comunicaciones", "avisos", "alertas",
    "alerta", "alarmas", "billing", "facturacion", "facturación",
    "factura", "factura-digital", "facturas", "envios", "envíos",
    "account", "accounts", "members", "membership", "store", "shop",
    "ofertas", "promociones", "promos", "destacados",
    "mensajesyavisos", "jobs-noreply", "jobalerts-noreply",
    "newsletters-noreply", "updates-noreply", "noreply-news",
    "trabajos_ar", "trabajos-ar",
    "team", "equipo", "comunidad", "boletin", "boletín",
    "feedback", "encuestas", "encuesta", "papeleriadigital",
    "graduados", "posgrado", "posgrado-econo",
    "oficinavirtual", "forms-receipts", "forms-receipts-noreply",
]

# Substrings en el nombre del remitente que delatan envío masivo.
AUTOMATED_NAME_HINTS = [
    "equipo de", "notificaciones de", "newsletter", "no responda",
    "no-reply", "marketing", "comunicaciones",
]

# Dominios que SIEMPRE se tratan como automáticos (aunque el localpart sea
# raro, ej. UUID@mail.mercadolibre.com).
AUTOMATED_DOMAINS = [
    "mail.mercadolibre.com", "mercadolibre.com", "e.mercadolibre.com.ar",
    "r.mercadolibre.com.ar", "a.mercadolibre.com.ar",
    "mailing.cocos.capital", "mails.santander.com.ar",
    "mails.santanderrio.com.ar", "mails.bancomunicipal.com.ar",
    "mailing.bna.com.ar", "p.mercadoen5minutos.com",
    "mailing.cocos", "linkedin.com", "noticias.ole.com.ar",
    "computrabajo.com", "postularse.com", "zonaprop.com.ar",
    "argenprop.com", "em-grimoldi.com.ar", "newsletter@",
]

# --------------------------------------------------------------------------
# Lista blanca explícita adicional (además de "toda persona real").
# Agregá acá mails o dominios puntuales que NUNCA se tocan.
# --------------------------------------------------------------------------
WHITELIST = [
    # "contador@estudio.com",
]

# --------------------------------------------------------------------------
# Vencimiento de promos conservadas: a los N días -> Papelera.
# --------------------------------------------------------------------------
PROMO_EXPIRY_DAYS = 30

# Categorías de Gmail candidatas a Papelera (salvo excepciones de arriba).
GMAIL_CATEGORY_TRASH = [
    "CATEGORY_PROMOTIONS", "CATEGORY_SOCIAL", "CATEGORY_UPDATES",
    "CATEGORY_FORUMS",
]

# --------------------------------------------------------------------------
# Memoria de remitentes. Subimos el umbral a 10 (antes 5) para no propagar
# clasificaciones erróneas tempranas. Y agregamos un mecanismo: si la última
# clasificación no es la misma que el resultado actual de la heurística por
# IMPORTANT_SENDERS, se sobreescribe la memoria.
# --------------------------------------------------------------------------
SENDER_CONFIDENT_COUNT = 10

# Días de retención de los logs jsonl. Más viejo se borra.
LOG_RETENTION_DAYS = 90

# Tope de caracteres del subject en los logs/registros (privacidad).
SUBJECT_MAX = 80
