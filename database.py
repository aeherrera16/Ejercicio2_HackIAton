"""
database.py - Datos simulados para el sistema de auditoria

Este archivo contiene tarifarios de referencia y siniestros de ejemplo
para auditar facturas de taller y documentacion de seguros en Ecuador.
Los valores estan en USD y sirven como base de comparacion.
"""

# Tarifarios de referencia para auditoria de taller en Ecuador
TARIFARIOS = {
    "auto": {
        "moneda": "USD",
        "zona_referencia": "Ecuador",
        "mano_obra": {
            "hora_mecanica_general": {"min": 18, "max": 28, "unidad": "hora"},
            "hora_enderezado_pintura": {"min": 22, "max": 35, "unidad": "hora"},
            "diagnostico_electronico": {"min": 20, "max": 35, "unidad": "servicio"},
            "alineacion_y_balanceo": {"min": 18, "max": 30, "unidad": "servicio"},
            "desmontaje_montaje": {"min": 15, "max": 25, "unidad": "hora"},
        },
        "insumos_y_consumibles": {
            "limpiador_frenos": {"min": 4, "max": 8, "unidad": "unidad"},
            "lija_pintura": {"min": 2, "max": 5, "unidad": "unidad"},
            "masilla": {"min": 6, "max": 12, "unidad": "kit"},
            "sellador_primer": {"min": 8, "max": 15, "unidad": "litro"},
            "cinta_mascarar": {"min": 3, "max": 6, "unidad": "rollo"},
        },
        "repuestos_referenciales": {
            "parachoques_delantero": {"min": 90, "max": 180, "unidad": "pieza"},
            "parachoques_trasero": {"min": 90, "max": 180, "unidad": "pieza"},
            "faro_delantero": {"min": 70, "max": 160, "unidad": "pieza"},
            "guardachoque": {"min": 120, "max": 260, "unidad": "pieza"},
            "espejo_lateral": {"min": 45, "max": 110, "unidad": "pieza"},
            "radiador": {"min": 130, "max": 280, "unidad": "pieza"},
            "parabrisas": {"min": 110, "max": 240, "unidad": "pieza"},
            "bateria": {"min": 60, "max": 140, "unidad": "pieza"},
        },
        "pintura": {
            "panel_pequeno": {"min": 45, "max": 80, "unidad": "panel"},
            "panel_medio": {"min": 70, "max": 120, "unidad": "panel"},
            "panel_grande": {"min": 100, "max": 160, "unidad": "panel"},
        },
        "observaciones": [
            "Los valores son rangos de referencia para auditoria, no tarifas oficiales.",
            "Un mismo concepto no debe aparecer duplicado salvo que exista sustento tecnico claro.",
            "Si el taller factura repuesto nuevo y ademas remanufacturado para el mismo item, debe justificarse.",
        ],
    },
    "hogar": {
        "moneda": "USD",
        "zona_referencia": "Ecuador",
        "mano_obra": {
            "visita_tecnica": {"min": 15, "max": 25, "unidad": "servicio"},
            "plomeria": {"min": 18, "max": 35, "unidad": "hora"},
            "electricidad": {"min": 18, "max": 35, "unidad": "hora"},
            "cerrajeria": {"min": 20, "max": 40, "unidad": "servicio"},
        },
        "insumos_y_consumibles": {
            "teflon": {"min": 1, "max": 3, "unidad": "unidad"},
            "silicona": {"min": 3, "max": 7, "unidad": "unidad"},
            "cableado_basico": {"min": 8, "max": 18, "unidad": "metro"},
            "cerradura": {"min": 18, "max": 45, "unidad": "pieza"},
        },
        "repuestos_referenciales": {
            "griferia": {"min": 25, "max": 90, "unidad": "pieza"},
            "interruptor": {"min": 3, "max": 12, "unidad": "pieza"},
            "tomacorriente": {"min": 4, "max": 15, "unidad": "pieza"},
            "cilindro_cerradura": {"min": 15, "max": 40, "unidad": "pieza"},
        },
        "observaciones": [
            "Los valores son rangos de referencia para auditoria, no tarifas oficiales.",
            "Se debe verificar si la reparacion corresponde al evento reportado y a la cobertura contratada.",
        ],
    },
}

# Datos de siniestros (ejemplo de casos de referencia)
SINIESTROS = [
    {
        "id": "SIN001",
        "fecha": "2024-01-15",
        "tipo": "auto",
        "descripcion": "Choque frontal en Ruta 5",
        "monto_reclamado": 45000,
        "estado": "aprobado",
        "cobertura": "cobertura_completa",
        "taller_referencia": "TALLER EXPRESS S.A.",
        "tipo_dano": "choque frontal",
        "partes_afectadas": ["parachoques_delantero", "faro_delantero", "guardachoque"],
    },
    {
        "id": "SIN002",
        "fecha": "2024-02-20",
        "tipo": "hogar",
        "descripcion": "Robo de electrodomesticos",
        "monto_reclamado": 8500,
        "estado": "en_revision",
        "cobertura": "cobertura_basica",
        "taller_referencia": "SERVICIOS HOGAR ECUADOR",
        "tipo_dano": "robo",
        "partes_afectadas": ["cerradura", "puerta_ingreso"],
    },
    {
        "id": "SIN003",
        "fecha": "2024-03-10",
        "tipo": "auto",
        "descripcion": "Dano por granizo",
        "monto_reclamado": 12000,
        "estado": "rechazado",
        "cobertura": "cobertura_basica",
        "razon_rechazo": "No cubre danos por fenomenos climaticos",
        "taller_referencia": "CARROCERIAS DEL SUR",
        "tipo_dano": "granizo",
        "partes_afectadas": ["capot", "techo", "guardachoque"],
    },
    {
        "id": "SIN004",
        "fecha": "2024-03-25",
        "tipo": "auto",
        "descripcion": "Responsabilidad civil - lesiones a tercero",
        "monto_reclamado": 75000,
        "estado": "aprobado",
        "cobertura": "cobertura_premium",
        "taller_referencia": "TALLER SAN ISIDRO",
        "tipo_dano": "responsabilidad civil",
        "partes_afectadas": ["servicio_legal", "acuerdos_terceros"],
    },
    {
        "id": "SIN005",
        "fecha": "2024-04-05",
        "tipo": "hogar",
        "descripcion": "Incendio parcial de cocina",
        "monto_reclamado": 35000,
        "estado": "aprobado",
        "cobertura": "cobertura_completa",
        "taller_referencia": "HOGAR SEGURO S.A.",
        "tipo_dano": "incendio",
        "partes_afectadas": ["griferia", "instalacion_electrica", "puertas"],
    },
]

# Informacion sobre politicas de auditoria
POLITICAS_AUDITORIA = {
    "monto_minimo_auditoria": 1000,
    "documentacion_requerida": [
        "Poliza de seguros vigente",
        "Reporte de peritos",
        "Facturas y cotizaciones",
        "Fotos del siniestro",
        "Declaracion del asegurado",
    ],
    "criterios_rechazo": [
        "Falta de documentacion",
        "Cobertura no incluye el siniestro",
        "Incumplimiento de obligaciones",
        "Fraude detectado",
        "Limite de cobertura excedido",
        "Cobro duplicado sin sustento",
        "Valores fuera del tarifario de referencia",
    ],
    "criterios_sobreprecio": [
        "Valor por encima del maximo de referencia",
        "Insumo repetido con el mismo concepto",
        "Honorario desproporcionado frente al servicio",
        "Repuesto facturado varias veces",
        "Pintura o mano de obra repetida sin evidencia",
    ],
}


def obtener_tarifario(tipo_seguro: str) -> dict:
    """Obtiene el tarifario para un tipo de seguro especifico."""
    return TARIFARIOS.get(tipo_seguro, {})


def obtener_siniestro(id_siniestro: str) -> dict:
    """Obtiene los detalles de un siniestro especifico."""
    for siniestro in SINIESTROS:
        if siniestro["id"] == id_siniestro:
            return siniestro
    return None


def listar_siniestros() -> list:
    """Lista todos los siniestros disponibles."""
    return SINIESTROS


def obtener_politicas() -> dict:
    """Obtiene las politicas de auditoria."""
    return POLITICAS_AUDITORIA
