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
        "cajadevalores", "caja de valores", "eresumen.cajadevalores",
        "cnv.gob.ar",
        # newsletters bursátiles / análisis financiero
        "mercadoen5minutos", "m5m@p.mercadoen5minutos",
        "m5m@p.inversorglobal", "inversorglobal", "tomaslm.com",
        "hello@tomaslm", "rudolphtrading", "admin@rudolphtrading",
        "ole.com.ar/finanzas", "carryinvest", "puentenet", "puente.com",
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
        "quadra", "quadrasoft", "expensasquadra",
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
        "jobs-noreply@linkedin", "linkedin.com/jobs", "jobs-listings",
        "jobalerts-noreply@linkedin", "messages-noreply@linkedin",
        "talentpitch", "konzerta", "trabajos_ar",
        "atencionalusuario@zonajobs", "bebee", "hive.bebee",
    ],
    "Educación": [
        "udemy", "coursera", "platzi", "edx", "domestika",
        "fcecon.unr.edu.ar", "posgrado.rosario@austral.edu",
        "posgrado-econo", "austral.edu.ar", ".edu.ar",
        "uba.ar", "unc.edu.ar", "uns.edu.ar", "ucema.edu.ar",
    ],
    "Viajes": [
        # agencias / aerolíneas / OTAs
        "turismopasaporte", "despegar.com", "decolar.com", "booking.com",
        "trivago", "trip.com", "expedia", "edreams", "almundo",
        "atrapalo", "aviatur", "vrbo", "airbnb",
        "aerolineas.com.ar", "aerolíneas argentinas", "latam.com",
        "smiles.com.ar", "amaszonas", "flybondi", "jetsmart",
        "ezeiza", "aa2000",
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

# Palabras clave en el ASUNTO/CUERPO que hacen conservar una promo aunque la
# mande un local/comercio (ej. "20% pagando con Macro"). Si una promo
# (CATEGORY_PROMOTIONS) menciona alguno de estos bancos, va a "Promos que
# sirven" en vez de Papelera.
PROMO_KEEP_KEYWORDS = [
    "santander", "banco macro", "tarjeta macro", "con macro", "macro click",
    "banco nación", "banco nacion", "bna", "modo",
    "banco municipal", "municipal de rosario", "tarjeta municipal",
    "naranja x", "naranjax", "visa banco", "mastercard banco",
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
        # frases específicas
        "tu vuelo", "tu pasaje", "tu reserva", "tu hotel",
        "booking.com", "despegar.com", "decolar.com", "trip.com",
        "aerolineas argentinas", "aerolíneas argentinas",
        "latam.com", "latam pass", "check-in en línea",
        "check-in en linea", "itinerario de vuelo", "boarding pass",
        "tu próximo viaje", "tu proximo viaje",
        # destinos típicos de viaje (paquetes/agencias)
        "costa mujeres", "punta cana", "la romana", "punta del este",
        "puerto madryn", "bariloche", "cataratas", "cancún", "cancun",
        "playa del carmen", "all inclusive", "all-inclusive",
        "paquete turístico", "paquete turistico", "viaje organizado",
        "salida grupal", "tarifa aérea", "tarifa aerea",
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
# Remitentes que SIEMPRE van a Papelera apenas llegan. Aprendido del diff
# entre snapshots A (antes de la limpieza manual) y B (despues): remitentes
# automaticos/masivos con CERO sobrevivientes. NO se incluyen personas reales
# ni casos sensibles (turnos medicos, agencia de viajes, socios de Boca,
# justicia, escuelas): esos se rigen por la expiracion por edad de abajo.
# La lista blanca (WHITELIST / persona real) siempre gana sobre esto.
# --------------------------------------------------------------------------
AUTO_TRASH_SENDERS = [
    # MercadoLibre (notificaciones / ofertas / mercadoshops)
    "no-responder@mercadolibre.com", "no-responder@mercadolibre.com.ar",
    "no-responder@no-responder.mercadolibre.com",
    "noreply@no-responder.mercadolibre.com",
    "no-reply@mercadolibre.com", "no-reply@mercadolibre.com.ar",
    "noreply@mercadolibre.com",
    "ofertas@r.mercadolibre.com.ar", "ofertas@a.mercadolibre.com.ar",
    "comunicaciones@r.mercadolibre.com.ar",
    "comunicaciones@a.mercadolibre.com.ar",
    "comunicaciones@mercadolibre.com.ar",
    "autos@r.mercadolibre.com.ar", "info@r.mercadolibre.com.ar",
    "info@e.mercadolibre.com.ar", "no-responder@mercadoshops.com",
    # Mercado Pago (marketing, no comprobantes)
    "novedades@a.mercadopago.com", "comercial@r.mercadopago.com.ar",
    "promocion@a.mercadopago.com", "novedades@r.mercadopago.com",
    "no-responder@mercadopago.com",
    # Empleo
    "no-reply@postularse.com", "jobs-noreply@linkedin.com",
    "jobs-listings@linkedin.com", "jobalerts-noreply@linkedin.com",
    "newsletters-noreply@linkedin.com", "invitations@linkedin.com",
    "trabajos_ar@computrabajo.com", "alertas@computrabajo.com",
    "alertas_ar@computrabajo.com", "destacados@computrabajo.com",
    # NOTA: NO ponemos bancos/tarjetas ni Cocos en auto-trash. Aunque
    # historicamente borraste sus newsletters, tus reglas dicen que las
    # PROMOS de Santander/Macro/BNA se conservan ("Promos que sirven") y
    # Cocos tiene su propia etiqueta. Esos remitentes se clasifican por
    # IMPORTANT_SENDERS / Promos, no se descartan. (Si una promo puntual
    # no te sirve, la borras a mano.)
    # Nota: NO ponemos `nx-documentacion@naranjax.com` aqui. Aunque historicamente
    # los borrabas, ahora usas Naranja X y esos correos suelen ser legales/
    # documentales (cambios de terminos, etc.). Si llegan promos van por
    # PROMO_KEEP_SENDERS; los resumenes van a Finanzas.
    # Newsletters bursatiles puros (NO brokers con cuenta tuya).
    "m5m@p.inversorglobal.com", "m5m@p.mercadoen5minutos.com",
    "hello@tomaslm.com",
    # Retail / ecommerce / marketing
    "hola+compras@tiendanube.com", "newslettergr@em-grimoldi.com.ar",
    "newsletterhushpuppies@em-grimoldi.com.ar",
    "newsletter@em.cheeky.com.ar", "newsletter@email.hm.com",
    "clientes@digitalsport.com.ar", "service-ar@puma.com",
    "facturasemsa@e-musimundo.com", "ventas@hardcorecomputacion.com.ar",
    "ventas@felipesalvadorweb.com", "info@felipesalvadorweb.com",
    "noreply@vtexcommerce.com.br", "adidas@ar-info.adidas.com",
    "hola@lapanaleraencasa.com",
    # Servicios / facturacion automatica
    "factura-digital@factura.personal.com.ar",
    "aviso_factura@iplan.com.ar", "no-reply@ov.litoral-gas.com.ar",
    "jira@litoral-gas.atlassian.net", "cupondepago@serviciosiro.com.ar",
    "no-reply@viumi.com.ar", "papeleriadigital@mail.sancristobal.com.ar",
    "oficinavirtual@epe.santafe.gov.ar",
    # Inmobiliarias (avisos masivos, no conversaciones)
    "no_reply@zonaprop.com.ar", "info@hasanestudioinmobiliario.com",
    # Apps / otros
    "noreply@discord.com", "disneyplus@trx.mail2.disneyplus.com",
    "disneyplus@mail.disneyplus.com", "contacto@digitalhouse.com",
]

# Dominios completos que SIEMPRE van a Papelera (cualquier localpart).
# Util para remitentes con UUID en el localpart (ej. ML transaccional).
AUTO_TRASH_DOMAINS = [
    "mail.mercadolibre.com",
]

# --------------------------------------------------------------------------
# Expiracion por etiqueta: mails MAS VIEJOS que N dias -> Papelera (siempre
# recuperable 30 dias en Papelera). Replica tu limpieza por antiguedad: lo
# viejo se descarta, lo reciente y util se conserva. Etiqueta no listada o
# valor 0 = NUNCA expira. Personal y Revisar nunca expiran a proposito.
# --------------------------------------------------------------------------
LABEL_EXPIRY_DAYS = {
    "Impuestos y gobierno": 730,
    "Finanzas": 365,
    "Inversiones": 365,
    "Servicios y facturas": 180,
    "Salud": 180,
    "Yo enviados": 180,
    "Educación": 90,
    "Cocos": 90,
    "Compras": 60,
    "Inmuebles": 60,
    "Boca": 30,
    "Viajes": 30,
    "Trabajo": 30,
    "Suscripciones": 30,
    "Promos que sirven": 30,
    # "Personal": nunca
    # "Revisar": nunca
}

# --------------------------------------------------------------------------
# Vencimiento de promos conservadas: a los N días -> Papelera.
# (Mantengo la constante por compatibilidad; ahora "Promos que sirven"
#  tambien esta en LABEL_EXPIRY_DAYS.)
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
