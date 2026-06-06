"""
Configuración de reglas para el organizador de Gmail.

Todas las reglas del prompt (prompt_ordenar_gmail.md) se traducen acá en datos
que el script gmail_organizer.py usa para clasificar. Editá estas listas para
afinar el comportamiento; no hace falta tocar el código principal.
"""

# --------------------------------------------------------------------------
# Etiquetas que se crean (si no existen) y se aplican.
# --------------------------------------------------------------------------
LABELS = [
    "Finanzas",
    "Impuestos y gobierno",
    "Servicios y facturas",
    "Salud",
    "Compras",
    "Viajes",
    "Educación",
    "Suscripciones",
    "Promos que sirven",
    "Personal",
    "Boca",
    "Cocos",
    "Guardar",
    "Revisar",  # auxiliar: correos dudosos que dejo para revisión manual
]

# --------------------------------------------------------------------------
# Remitentes importantes por categoría (match por substring en el email/dominio).
# Todo en minúsculas.
# --------------------------------------------------------------------------
IMPORTANT_SENDERS = {
    "Finanzas": [
        # bancos
        "santander", "macro", "bancomacro", "bna", "banconacion", "bancanacion",
        "galicia", "bbva", "itau", "hsbc", "comafi", "supervielle",
        "patagonia", "icbc", "credicoop", "bancociudad", "bancoprovincia",
        # redes / tarjetas
        "redlink", "visa", "mastercard", "amex", "cabal", "naranja", "naranjax",
        "creditmas",
        # billeteras / fintech
        "mercadopago", "uala", "ualá", "personalpay", "modo", "brubank", "prex",
        # cripto
        "lemon", "letsbit", "fiwind", "buenbit",
    ],
    "Impuestos y gobierno": [
        "arca", "afip", "anses", "rentas", "agip", "arba",
        "municipal", "municipalidad", "gob.ar", "gov.ar",
        "miargentina", "mi argentina", "renaper", "andis",
        "migraciones", "pami", "tarjeta sube", "argentina.gob",
    ],
    "Servicios y facturas": [
        # energía
        "edenor", "edesur", "edea", "edemsa", "edelap", "epec", "epesf",
        # gas
        "metrogas", "naturgy", "camuzzi", "litoralgas", "ecogas",
        # agua
        "aysa", "absa", "aguasdelnorte", "aguascorrentinas",
        # telco / TV
        "movistar", "claro", "personal", "telecom", "fibertel", "cablevision",
        "telecentro", "iplan", "flow", "directv",
        # expensas
        "expensaspagas", "consorcioabierto", "octopuspro", "expensaonline",
    ],
    "Salud": [
        "swissmedical", "swiss medical", "swissmedical.com.ar",
        "osde", "galenoargentina", "medicus", "omint",
        "sancorsalud", "prevencionsalud", "accord salud", "medife",
    ],
    "Suscripciones": [
        "netflix", "spotify", "disneyplus", "disney+", "hbomax", "max.com",
        "primevideo", "youtube premium", "apple.com", "icloud",
        "paramount", "starplus",
    ],
    "Boca": [
        "bocajuniors", "boca juniors", "bocajuniors.com", "cabj",
        "sociosboca",
    ],
    "Cocos": [
        "cocoscapital", "cocos capital", "cocos.capital", "micocos",
        "cocos crypto",
    ],
}

# --------------------------------------------------------------------------
# Servicios y facturas: además del match por remitente, también por keyword.
# --------------------------------------------------------------------------
SERVICE_INVOICE_KEYWORDS = [
    "factura", "factura electronica", "comprobante", "tu factura",
    "tu resumen", "vencimiento de tu", "boleta", "aviso de pago",
    "tu boleta",
]

# --------------------------------------------------------------------------
# Promociones que se CONSERVAN (etiqueta "Promos que sirven", NO van a Papelera).
# --------------------------------------------------------------------------
PROMO_KEEP_SENDERS = [
    # tarjetas / bancos
    "santander", "macro", "bancomacro", "bna", "banconacion", "galicia",
    "bbva", "naranja", "naranjax",
    # supermercados
    "carrefour", "coto", "dia", "diaonline", "jumbo", "disco", "vea",
    "laanonima", "la anonima", "makro", "changomas", "walmart",
    # combustible / estaciones de servicio
    "ypf", "shell", "axion", "puma", "gulf",
]

# --------------------------------------------------------------------------
# Palabras clave que marcan un correo como IMPORTANTE (asunto o cuerpo).
# --------------------------------------------------------------------------
IMPORTANT_KEYWORDS = [
    "factura", "comprobante", "recibo", "resumen", "vencimiento", "pago",
    "transferencia", "turno", "reserva", "vuelo", "pasaje", "hotel",
    "garantia", "garantía", "codigo", "código", "verificacion",
    "verificación", "seguridad", "contraseña", "contrasena",
]

# Palabras clave que sugieren que el correo REQUIERE ACCIÓN -> dejar en Recibidos
# (en vez de archivar), aunque esté etiquetado.
ACTION_KEYWORDS = [
    "vence", "vencimiento", "vencido", "pago pendiente", "impago",
    "turno", "confirmar", "accion requerida", "acción requerida",
    "ultimo aviso", "último aviso", "corte de servicio",
]

# Palabras clave por categoría temática (para etiquetar correctamente).
# Importante: keywords específicas para evitar falsos positivos. "boca" suelta
# está prohibida (matchearía "boca de expendio", etc.).
CATEGORY_KEYWORDS = {
    "Boca": [
        "boca juniors", "bocajuniors", "boca jrs", "club atletico boca",
        "club atlético boca", "cabj", "socios boca", "sociosboca",
    ],
    "Cocos": [
        "cocos capital", "cocoscapital", "cocos.capital", "micocos",
        "cocos crypto",
    ],
    "Compras": [
        "mercadolibre", "mercado libre", "tu envio", "tu envío",
        "envio en camino", "envío en camino", "tu pedido", "tu compra",
        "seguimiento de tu", "amazon.com",
    ],
    "Viajes": [
        "vuelo", "pasaje", "reserva", "hotel", "booking", "despegar",
        "aerolineas", "aerolíneas", "latam", "check-in", "itinerario",
    ],
    "Educación": [
        "udemy", "coursera", "platzi", "edx", "domestika",
        ".edu.ar", "universidad",
    ],
    "Suscripciones": [
        "renovacion", "renovación", "tu suscripcion", "tu suscripción",
        "cobro automatico", "cobro automático",
    ],
}

# Correos a los que, además, se aplica etiqueta "Guardar" + estrella (respaldo).
BACKUP_LABELS = {
    "Finanzas", "Impuestos y gobierno", "Servicios y facturas",
    "Viajes", "Suscripciones",
}
BACKUP_KEYWORDS = [
    "resumen", "comprobante", "factura", "pago", "garantia", "garantía",
    "pasaje", "tramite", "trámite",
]

# --------------------------------------------------------------------------
# Detección de remitente automático. La comparación se hace con local-part
# EXACTA o con prefijo + separador (./-/_), no como substring. Eso evita
# falsos positivos del estilo "jose.team@gmail.com".
# --------------------------------------------------------------------------
AUTOMATED_LOCALPARTS = [
    "no-reply", "noreply", "no_reply", "donotreply", "do-not-reply",
    "info", "news", "newsletter", "notificaciones", "notifications",
    "notification", "marketing", "mailer", "mailing", "ventas", "soporte",
    "support", "hello", "contacto", "comunicaciones", "avisos", "alertas",
    "billing", "facturacion", "facturación", "envios", "envíos",
    "account", "accounts", "members", "membership", "store", "shop",
]

# Substrings en el nombre del remitente que delatan envío masivo.
AUTOMATED_NAME_HINTS = [
    "equipo de", "notificaciones de", "newsletter", "no responda", "no-reply",
]

# --------------------------------------------------------------------------
# Lista blanca explícita adicional (además de "toda persona real").
# Agregá acá mails o dominios puntuales que NUNCA se tocan, aunque parezcan
# automáticos. Ej: "contador@estudio.com", "@miempresa.com".
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
# Memoria de remitentes: si un remitente ya tiene este número de correos
# clasificados con éxito (status "ok"), se aplica su última etiqueta directa.
# --------------------------------------------------------------------------
SENDER_CONFIDENT_COUNT = 5

# Días de retención de los logs jsonl. Más viejo se borra.
LOG_RETENTION_DAYS = 90

# Tope de caracteres del subject en los logs/registros (privacidad).
SUBJECT_MAX = 80
