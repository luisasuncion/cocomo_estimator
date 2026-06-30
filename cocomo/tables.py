RATING_LABELS = {
    "VL": "Muy bajo",
    "LO": "Bajo",
    "NM": "Nominal",
    "HI": "Alto",
    "VH": "Muy alto",
    "XH": "Extra alto",
}

SCALE_FACTORS = {
    "PREC": {"VL": 6.20, "LO": 4.96, "NM": 3.72, "HI": 2.48, "VH": 1.24, "XH": 0.00},
    "FLEX": {"VL": 5.07, "LO": 4.05, "NM": 3.04, "HI": 2.03, "VH": 1.01, "XH": 0.00},
    "RESL": {"VL": 7.07, "LO": 5.65, "NM": 4.24, "HI": 2.83, "VH": 1.41, "XH": 0.00},
    "TEAM": {"VL": 4.90, "LO": 3.92, "NM": 2.94, "HI": 1.96, "VH": 0.98, "XH": 0.00},
    "PMAT": {"VL": 7.88, "LO": 6.30, "NM": 4.73, "HI": 3.15, "VH": 1.58, "XH": 0.00},
}

PRODUCT_DRIVERS = {
    "RELY": {"VL": 0.82, "LO": 0.92, "NM": 1.00, "HI": 1.10, "VH": 1.26},
    "DATA": {"LO": 0.90, "NM": 1.00, "HI": 1.14, "VH": 1.28},
    "CPLX": {"VL": 0.73, "LO": 0.87, "NM": 1.00, "HI": 1.17, "VH": 1.34, "XH": 1.74},
    "RUSE": {"NM": 1.00, "HI": 1.15, "VH": 1.30, "XH": 1.67},
    "DOCU": {"VL": 0.81, "LO": 0.91, "NM": 1.00, "HI": 1.11, "VH": 1.23},
}

PLATFORM_DRIVERS = {
    "TIME": {"NM": 1.00, "HI": 1.11, "VH": 1.29, "XH": 1.63},
    "STOR": {"NM": 1.00, "HI": 1.05, "VH": 1.17, "XH": 1.46},
    "PVOL": {"LO": 0.89, "NM": 1.00, "HI": 1.15, "VH": 1.30},
}

PERSONNEL_DRIVERS = {
    "ACAP": {"VL": 1.42, "LO": 1.19, "NM": 1.00, "HI": 0.85, "VH": 0.71},
    "PCAP": {"VL": 1.34, "LO": 1.15, "NM": 1.00, "HI": 0.88, "VH": 0.76},
    "PCON": {"VL": 1.29, "LO": 1.12, "NM": 1.00, "HI": 0.90, "VH": 0.81},
    "AEXP": {"VL": 1.22, "LO": 1.10, "NM": 1.00, "HI": 0.88, "VH": 0.81},
    "PEXP": {"VL": 1.19, "LO": 1.09, "NM": 1.00, "HI": 0.91, "VH": 0.85},
    "LTEX": {"VL": 1.20, "LO": 1.09, "NM": 1.00, "HI": 0.91, "VH": 0.84},
}

PROJECT_DRIVERS = {
    "TOOL": {"VL": 1.17, "LO": 1.09, "NM": 1.00, "HI": 0.90, "VH": 0.78},
    "SITE": {"VL": 1.22, "LO": 1.09, "NM": 1.00, "HI": 0.93, "VH": 0.86, "XH": 0.80},
    "SCED": {"VL": 1.43, "LO": 1.14, "NM": 1.00, "HI": 1.00, "VH": 1.00},
}

FACTOR_INFO = {
    "PREC": ("Precedencia", "Experiencia previa de la organizacion con sistemas similares."),
    "FLEX": ("Flexibilidad de desarrollo", "Nivel de restricciones del proceso, contrato o producto."),
    "RESL": ("Resolucion de arquitectura y riesgos", "Grado de analisis temprano de arquitectura y mitigacion de riesgos."),
    "TEAM": ("Cohesion del equipo", "Sinergia, comunicacion y estabilidad del equipo de trabajo."),
    "PMAT": ("Madurez del proceso", "Nivel de definicion y mejora del proceso de software."),
    "RELY": ("Confiabilidad requerida", "Impacto de fallas y exigencia de funcionamiento correcto."),
    "DATA": ("Tamano de base de datos", "Relacion entre volumen de datos y tamano del software."),
    "CPLX": ("Complejidad del producto", "Complejidad de control, datos, operaciones e interfaces."),
    "RUSE": ("Reutilizacion requerida", "Nivel esperado de reutilizacion en otros proyectos o productos."),
    "DOCU": ("Documentacion", "Adecuacion de la documentacion a las necesidades del ciclo de vida."),
    "TIME": ("Restriccion de tiempo", "Porcentaje de uso requerido del tiempo de ejecucion disponible."),
    "STOR": ("Restriccion de almacenamiento", "Porcentaje de uso requerido del almacenamiento principal."),
    "PVOL": ("Volatilidad de plataforma", "Frecuencia de cambios en hardware, sistema operativo o entorno."),
    "ACAP": ("Capacidad de analistas", "Habilidad del equipo para analizar requisitos y soluciones."),
    "PCAP": ("Capacidad de programadores", "Habilidad del equipo para construir software correctamente."),
    "PCON": ("Continuidad del personal", "Estabilidad y permanencia del equipo durante el proyecto."),
    "AEXP": ("Experiencia en aplicaciones", "Familiaridad con el dominio de aplicacion."),
    "PEXP": ("Experiencia en plataforma", "Familiaridad con la plataforma tecnica objetivo."),
    "LTEX": ("Experiencia en lenguaje y herramientas", "Dominio del lenguaje de programacion y herramientas de soporte."),
    "TOOL": ("Uso de herramientas", "Soporte de herramientas automatizadas en el desarrollo."),
    "SITE": ("Desarrollo multisede", "Calidad de comunicacion y colaboracion entre ubicaciones."),
    "SCED": ("Cronograma requerido", "Restriccion o compresion del calendario de desarrollo."),
}
