"""
database.py - Datos simulados para el sistema de auditoría

Este archivo contiene tarifarios y datos de siniestros de ejemplo
para demostrar el funcionamiento del agente de IA.
"""

# Tarifarios de seguros (Ejemplo: Seguros de Autos)
TARIFARIOS = {
    "auto": {
        "cobertura_basica": {
            "descripcion": "Responsabilidad Civil",
            "prima_anual": 2500,
            "deducible": 5000,
            "limite_cobertura": 100000
        },
        "cobertura_completa": {
            "descripcion": "Responsabilidad Civil + Daños Propios",
            "prima_anual": 4500,
            "deducible": 2500,
            "limite_cobertura": 150000
        },
        "cobertura_premium": {
            "descripcion": "Cobertura Integral + Asistencia",
            "prima_anual": 7000,
            "deducible": 1000,
            "limite_cobertura": 250000
        }
    },
    "hogar": {
        "cobertura_basica": {
            "descripcion": "Incendio y Robo",
            "prima_anual": 1500,
            "deducible": 3000,
            "limite_cobertura": 50000
        },
        "cobertura_completa": {
            "descripcion": "Incendio, Robo, Daños por agua",
            "prima_anual": 3000,
            "deducible": 1500,
            "limite_cobertura": 100000
        }
    }
}

# Datos de siniestros (Ejemplo de casos reales)
SINIESTROS = [
    {
        "id": "SIN001",
        "fecha": "2024-01-15",
        "tipo": "auto",
        "descripcion": "Choque frontal en Ruta 5",
        "monto_reclamado": 45000,
        "estado": "aprobado",
        "cobertura": "cobertura_completa"
    },
    {
        "id": "SIN002",
        "fecha": "2024-02-20",
        "tipo": "hogar",
        "descripcion": "Robo de electródomesticos",
        "monto_reclamado": 8500,
        "estado": "en_revision",
        "cobertura": "cobertura_basica"
    },
    {
        "id": "SIN003",
        "fecha": "2024-03-10",
        "tipo": "auto",
        "descripcion": "Daño por granizo",
        "monto_reclamado": 12000,
        "estado": "rechazado",
        "cobertura": "cobertura_basica",
        "razon_rechazo": "No cubre daños por fenómenos climáticos"
    },
    {
        "id": "SIN004",
        "fecha": "2024-03-25",
        "tipo": "auto",
        "descripcion": "Responsabilidad civil - lesiones a tercero",
        "monto_reclamado": 75000,
        "estado": "aprobado",
        "cobertura": "cobertura_premium"
    },
    {
        "id": "SIN005",
        "fecha": "2024-04-05",
        "tipo": "hogar",
        "descripcion": "Incendio parcial de cocina",
        "monto_reclamado": 35000,
        "estado": "aprobado",
        "cobertura": "cobertura_completa"
    }
]

# Información sobre políticas de auditoría
POLITICAS_AUDITORIA = {
    "monto_minimo_auditoria": 10000,
    "documentacion_requerida": [
        "Póliza de seguros vigente",
        "Reportes de peritos",
        "Facturas y cotizaciones",
        "Fotos del siniestro",
        "Declaración del asegurado"
    ],
    "criterios_rechazo": [
        "Falta de documentación",
        "Cobertura no incluye el siniestro",
        "Incumplimiento de obligaciones",
        "Fraude detectado",
        "Límite de cobertura excedido"
    ]
}


def obtener_tarifario(tipo_seguro: str) -> dict:
    """Obtiene el tarifario para un tipo de seguro específico."""
    return TARIFARIOS.get(tipo_seguro, {})


def obtener_siniestro(id_siniestro: str) -> dict:
    """Obtiene los detalles de un siniestro específico."""
    for siniestro in SINIESTROS:
        if siniestro["id"] == id_siniestro:
            return siniestro
    return None


def listar_siniestros() -> list:
    """Lista todos los siniestros disponibles."""
    return SINIESTROS


def obtener_politicas() -> dict:
    """Obtiene las políticas de auditoría."""
    return POLITICAS_AUDITORIA
