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
        "santander", "macro", "bancomacro", "bna", "banconacion",
        "bancanacion", "redlink", "visa", "mastercard", "amex",
    ],
    "Impuestos y gobierno": [
        "arca", "afip", "anses", "rentas", "agip", "arba",
        "municipal", "municipalidad", "gob.ar", "gov.ar",
    ],
    "Salud": [
        "swissmedical", "swiss medical", "swissmedical.com.ar",
    ],
    "Boca": [
        "bocajuniors", "boca juniors", "bocajuniors.com", "cabj",
        "sociosboca",
    ],
    "Cocos": [
        "cocos", "cocoscapital", "cocos capital", "cocos.capital",
        "micocos",
    ],
}

# --------------------------------------------------------------------------
# Servicios y facturas: NO hay lista cerrada de empresas. Cualquier correo que
# parezca una factura/comprobante de un servicio cae acá. Se detecta por
# palabras clave (abajo) combinadas con que el remitente sea automático.
# --------------------------------------------------------------------------
SERVICE_INVOICE_KEYWORDS = [
    "factura", "factura electronica", "comprobante", "tu factura",
    "tu resumen", "vencimiento de tu", "boleta", "aviso de pago",
]

# --------------------------------------------------------------------------
# Promociones que se CONSERVAN (etiqueta "Promos que sirven", NO van a Papelera).
# --------------------------------------------------------------------------
PROMO_KEEP_SENDERS = [
    # Tarjetas / bancos
    "santander", "macro", "bancomacro", "bna", "banconacion",
    # Supermercados
    "carrefour", "coto", "dia", "diaonline", "jumbo", "disco", "vea",
    "laanonima", "la anonima", "makro", "changomas", "walmart",
    # Combustible / estaciones de servicio
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
CATEGORY_KEYWORDS = {
    "Boca": ["boca juniors", "bocajuniors", "boca jrs", "club atletico boca",
              "club atlético boca", "cabj", "socios boca", "sociosboca",
              "@bocajuniors", "bocajuniors.com"],
    "Cocos": ["cocos capital", "cocoscapital", "cocos.capital", "@cocos",
               "cocos crypto", "micocos"],
    "Compras": ["mercadolibre", "mercado libre", "envio", "envío", "pedido",
                 "tu compra", "seguimiento", "garantia", "garantía", "amazon"],
    "Viajes": ["vuelo", "pasaje", "reserva", "hotel", "booking", "despegar",
                "aerolineas", "aerolíneas", "latam", "check-in", "itinerario"],
}

# Correos a los que, además, se aplica etiqueta "Guardar" + estrella (respaldo).
BACKUP_LABELS = {"Finanzas", "Impuestos y gobierno", "Servicios y facturas",
                 "Viajes"}
BACKUP_KEYWORDS = ["resumen", "comprobante", "factura", "pago", "garantia",
                    "garantía", "pasaje", "tramite", "trámite"]

# --------------------------------------------------------------------------
# Detección de remitente automático (NO persona). Si el From contiene alguno
# de estos prefijos/palabras, se considera automático y se aplica la lógica
# general. Si NO es automático, se trata como PERSONA (lista blanca: intocable).
# --------------------------------------------------------------------------
AUTOMATED_LOCALPARTS = [
    "no-reply", "noreply", "no_reply", "donotreply", "do-not-reply",
    "info", "news", "newsletter", "notificaciones", "notifications",
    "notification", "marketing", "mailer", "mailing", "ventas", "soporte",
    "support", "hello", "contacto", "comunicaciones", "avisos", "alertas",
    "billing", "facturacion", "facturación", "envios", "envíos", "team",
    "account", "accounts", "members", "membership", "store", "shop",
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
GMAIL_CATEGORY_TRASH = ["CATEGORY_PROMOTIONS", "CATEGORY_SOCIAL",
                         "CATEGORY_UPDATES", "CATEGORY_FORUMS"]
