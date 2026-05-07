"""
agente.py - Logica del agente de IA con OpenRouter + Llama

Este archivo contiene el cerebro del sistema, donde se configura
el agente de IA y se definen las herramientas que puede utilizar.
"""

import os
import io
import json
import base64
import requests
from dotenv import load_dotenv
from PIL import Image
from database import (
    obtener_tarifario,
    obtener_siniestro,
    listar_siniestros,
    obtener_politicas,
)

# Cargar variables de entorno
load_dotenv()

def _obtener_openrouter_api_key() -> str | None:
    """Obtiene API key desde entorno o Streamlit secrets con nombres alternos."""
    posibles_nombres = [
        "OPENROUTER_API_KEY",
        "OPEN_ROUTER_API_KEY",
        "OPENROUTER_KEY",
    ]

    for nombre in posibles_nombres:
        valor = os.getenv(nombre)
        if valor and str(valor).strip():
            return str(valor).strip()

    try:
        import streamlit as _st

        for nombre in posibles_nombres:
            if nombre in _st.secrets:
                valor = _st.secrets[nombre]
                if valor and str(valor).strip():
                    return str(valor).strip()

        # Compatibilidad extra si el secreto se guardo como minusculas.
        for nombre in posibles_nombres:
            nombre_lower = nombre.lower()
            if nombre_lower in _st.secrets:
                valor = _st.secrets[nombre_lower]
                if valor and str(valor).strip():
                    return str(valor).strip()
    except Exception:
        pass

    return None


def _detectar_proveedor(api_key: str | None) -> str:
    """Detecta proveedor por prefijo de clave."""
    if not api_key:
        return "none"
    if str(api_key).startswith("sk-or-"):
        return "openrouter"
    if str(api_key).startswith("gsk_"):
        return "groq"
    return "unknown"


# Configurar API de OpenRouter
OPENROUTER_API_KEY = _obtener_openrouter_api_key()
API_PROVIDER = _detectar_proveedor(OPENROUTER_API_KEY)

HERRAMIENTAS_DISPONIBLES = """
Herramientas disponibles:
1. obtener_tarifario(tipo_seguro: str) - Obtiene tarifarios para auto u hogar
2. obtener_siniestro(id_siniestro: str) - Obtiene detalles de un siniestro (ej: SIN001)
3. listar_siniestros() - Lista todos los siniestros disponibles
4. obtener_politicas() - Obtiene las politicas de auditoria
"""

MAX_ADJUNTOS = 3
MAX_PDF_CHARS = 12000
MAX_IMAGE_SIDE = 1400
MODEL_NAME = "meta-llama/llama-4-scout-17b-16e-instruct"


def _resumen_referencia_database() -> str:
    """Construye un resumen compacto de los tarifarios y siniestros de referencia."""
    tarifario_auto = obtener_tarifario("auto")
    tarifario_hogar = obtener_tarifario("hogar")
    siniestros = listar_siniestros()
    politicas = obtener_politicas()

    def resumir_tarifario(nombre: str, tarifario: dict) -> str:
        if not tarifario:
            return f"- {nombre}: sin datos"

        secciones = []
        for categoria in ("mano_obra", "insumos_y_consumibles", "repuestos_referenciales", "pintura"):
            items = tarifario.get(categoria, {})
            if items:
                ejemplos = ", ".join(
                    f"{k}({v.get('min')} - {v.get('max')} USD)" for k, v in list(items.items())[:4]
                )
                secciones.append(f"{categoria}: {ejemplos}")

        return (
            f"- {nombre}: moneda={tarifario.get('moneda', 'USD')}, zona={tarifario.get('zona_referencia', 'Ecuador')}; "
            + " | ".join(secciones)
        )

    return (
        "BASE DE REFERENCIA (Ecuador, datos de ejemplo de database.py)\n"
        + resumir_tarifario("auto", tarifario_auto)
        + "\n"
        + resumir_tarifario("hogar", tarifario_hogar)
        + f"\n- Siniestros de referencia: {len(siniestros)} casos con tipo, cobertura, taller y partes afectadas."
        + f"\n- Politicas: documentacion requerida={len(politicas.get('documentacion_requerida', []))}, "
        + f"criterios_rechazo={len(politicas.get('criterios_rechazo', []))}, criterios_sobreprecio={len(politicas.get('criterios_sobreprecio', []))}."
    )


class AgenteAuditoria:
    """Clase principal del agente de auditoria de seguros."""

    def __init__(self):
        contexto_herramientas = f"""
{HERRAMIENTAS_DISPONIBLES}

REGLAS DE AUDITORIA BASADAS EN DATABASE.PY:
- Usa los tarifarios y siniestros de ejemplo como referencia principal para comparar facturas del taller.
- Si el archivo o la consulta menciona un siniestro, valida que los montos reclamados y la cobertura coincidan con la siniestralidad reportada.
- Si hay facturas, verifica insumos, mano de obra, repuestos, honorarios y conceptos repetidos contra el tarifario de referencia.
- Detecta cobros duplicados, conceptos duplicados, montos repetidos sospechosos, valores fuera de rango y conceptos no respaldados.
- Si el documento no coincide con un siniestro o no tiene respaldo suficiente, indica inconsistencia y por qué.
- No inventes tarifas ni reglas fuera de la base de ejemplo.

INSTRUCCIONES PARA USAR LAS HERRAMIENTAS:
- Si el usuario pregunta por tarifarios, usa: obtener_tarifario(tipo_seguro)
- Si pregunta por un siniestro especifico, usa: obtener_siniestro(id_siniestro)
- Si pregunta por todos los siniestros, usa: listar_siniestros()
- Si pregunta por politicas de auditoria, usa: obtener_politicas()
- Si hay archivo adjunto, analizalo directamente sin pedir ID.
- Si hay facturas en el adjunto, compara contra tarifario y consistencia del siniestro.
- Detecta discrepancias, cobros duplicados, montos fuera de tarifario o archivos no relacionados.

Nunca escribas llamadas de funciones literalmente en la respuesta final.
"""

        self.system_instruction = (
            "Eres un auditor experto en seguros de Ecuador. Tu tarea es auditar automaticamente "
            "la documentacion y las facturas enviadas por el taller a la aseguradora. "
            "Debes verificar que los insumos, repuestos, mano de obra y honorarios cobrados "
            "correspondan al tarifario acordado y a la siniestralidad reportada. "
            "Detecta discrepancias, cobros duplicados, valores fuera de rango y conceptos no respaldados "
            "antes de que un humano revise la cuenta. "
            "Cuando recibas adjuntos, usalos como evidencia principal. "
            "Responde con tono amable, claro y profesional. Empieza con una frase corta como 'He analizado los archivos' "
            "o 'Revisé la documentación' y luego explica tus hallazgos sin sonar robotico. "
            "NO muestres la base de datos en bruto, NO pegues JSON, y NO expliques la referencia a menos que sea necesario. "
            "Responde siempre en este formato:\n"
            "1. Resumen inicial amable de 1 o 2 lineas\n"
            "2. Veredicto: Aprobado, Requiere revision o Rechazado\n"
            "3. Sobreprecio detectado: si/no + detalle\n"
            "4. Cobros duplicados: si/no + detalle\n"
            "5. Diferencias contra tarifario: lista breve y sencilla\n"
            "6. Coherencia con siniestralidad reportada: si/no + detalle\n"
            "7. Recomendacion final: una accion concreta y amable\n"
            "Puedes analizar hasta 3 archivos por consulta (PDF/JPG/PNG).\n\n"
            + contexto_herramientas
            + "\n\n"
            + _resumen_referencia_database()
        )

        if API_PROVIDER == "groq":
            self.api_url = "https://api.groq.com/openai/v1/chat/completions"
            self.headers = {
                "Authorization": f"Bearer {OPENROUTER_API_KEY or ''}",
                "Content-Type": "application/json",
            }
        else:
            self.api_url = "https://openrouter.ai/api/v1/chat/completions"
            self.headers = {
                "Authorization": f"Bearer {OPENROUTER_API_KEY or ''}",
                "Content-Type": "application/json",
                "HTTP-Referer": "https://streamlit.app",
                "X-Title": "Auditor IA - Seguros",
            }
        self.historial = []

    def analizar_reclamo(self, pregunta_usuario: str, adjuntos: list | None = None) -> str:
        """Analiza un reclamo usando el agente de IA."""
        respuesta_mejorada = self._procesar_peticion(pregunta_usuario)
        partes_generacion = self._construir_partes_generacion(respuesta_mejorada, adjuntos)

        self.historial.append({"role": "user", "content": pregunta_usuario})
        respuesta_texto = self._consultar_modelo(partes_generacion)
        self.historial.append({"role": "assistant", "content": respuesta_texto})
        return respuesta_texto

    def _consultar_modelo(self, partes_generacion: list) -> str:
        """Llama al modelo del proveedor detectado."""
        if not OPENROUTER_API_KEY:
            return (
                "Falta configurar API key en Streamlit Cloud. "
                "En Settings -> Secrets agrega: OPENROUTER_API_KEY = \"tu_api_key\" "
                "y luego haz Reboot."
            )

        if API_PROVIDER == "unknown":
            return (
                "No pude identificar el proveedor de la API key. "
                "Usa una key de OpenRouter (sk-or-...) o de Groq (gsk_...)."
            )

        if API_PROVIDER == "groq":
            # Groq se usa en modo texto para evitar errores con contenido image_url.
            texto_usuario = "\n\n".join([p for p in partes_generacion if isinstance(p, str)])
            payload = {
                "model": MODEL_NAME,
                "messages": [
                    {"role": "system", "content": self.system_instruction},
                    {"role": "user", "content": texto_usuario},
                ],
                "temperature": 0.4,
                "max_tokens": 1200,
            }
        else:
            contenido_usuario = []
            for parte in partes_generacion:
                if isinstance(parte, str):
                    contenido_usuario.append({"type": "text", "text": parte})
                elif isinstance(parte, dict) and parte.get("type") == "image_url":
                    contenido_usuario.append(parte)

            payload = {
                "model": MODEL_NAME,
                "messages": [
                    {"role": "system", "content": self.system_instruction},
                    {"role": "user", "content": contenido_usuario},
                ],
                "temperature": 0.4,
                "max_tokens": 1200,
            }

        try:
            resp = requests.post(self.api_url, headers=self.headers, json=payload, timeout=120)
            resp.raise_for_status()
            data = resp.json()
            texto = data["choices"][0]["message"]["content"]
            return self._limpiar_respuesta(texto)
        except requests.HTTPError:
            status = getattr(resp, "status_code", None)
            detalle = ""
            try:
                detalle = resp.text
            except Exception:
                pass
            if status == 401 and "Missing Authentication header" in detalle:
                return (
                    "El proveedor respondió 401 por autenticación faltante. "
                    "Revisa en Streamlit Secrets que exista exactamente OPENROUTER_API_KEY "
                    "(sin secciones, sin espacios extra)."
                )
            return f"No pude completar el analisis con Llama. Error HTTP: {detalle[:400]}"
        except requests.RequestException as exc:
            return f"No pude conectar con el modelo Llama: {exc}"
        except (KeyError, IndexError, TypeError):
            return "No pude interpretar la respuesta del modelo Llama."

    def _limpiar_respuesta(self, texto: str) -> str:
        import re

        patrones = [
            r"^.*obtener_[a-z_]+\([^\)]*\).*$",
            r"^.*consultar la herramienta.*$",
            r"^.*voy a consultar.*$",
        ]

        lineas_limpias = []
        for linea in texto.splitlines():
            if any(re.match(patron, linea.strip(), flags=re.IGNORECASE) for patron in patrones):
                continue
            lineas_limpias.append(linea)

        resultado = "\n".join(lineas_limpias).strip()
        resultado = resultado or texto.strip()

        if resultado and not resultado.lower().startswith(("he analizado", "revisé", "revisé la documentación", "he revisado")):
            resultado = "He analizado los archivos y encontré lo siguiente:\n\n" + resultado

        return resultado

    def _construir_partes_generacion(self, texto_base: str, adjuntos: list | None) -> list:
        """
        Flujo PDF:
        1. Extraer texto del PDF
        2. Extraer imagenes embebidas del PDF
        3. Enviar texto + imagenes al modelo IA
        4. Generar auditoria
        """
        partes = [texto_base]

        if not adjuntos:
            return partes

        partes.append(
            "\n\nObjetivo del analisis: determinar si el archivo adjunto corresponde a un "
            "siniestro o documentacion relacionada (factura, poliza, cotizacion, peritaje, evidencia). "
            "No pidas ID. Si hay facturas, revisa coherencia y posibles cobros fuera de tarifario. "
            "Prioriza detectar sobreprecio, cobros duplicados y conceptos no respaldados."
        )

        for adjunto in adjuntos[:MAX_ADJUNTOS]:
            tipo = adjunto.get("tipo")
            nombre = adjunto.get("nombre", "archivo")

            if tipo == "pdf" and adjunto.get("texto"):
                texto_pdf = self._compactar_texto_pdf(adjunto["texto"])
                partes.append(f"\n\nAdjunto PDF: {nombre}\n{texto_pdf}")

                for idx, imagen_pdf in enumerate(adjunto.get("imagenes_pdf", [])[:2], start=1):
                    partes.append(f"\n\nImagen extraida del PDF {nombre} (#{idx})")
                    partes.append(self._imagen_a_contenido(imagen_pdf))

            elif tipo == "imagen" and adjunto.get("imagen") is not None:
                partes.append(f"\n\nImagen adjunta: {nombre}")
                partes.append(self._imagen_a_contenido(adjunto["imagen"]))

        return partes

    def _compactar_texto_pdf(self, texto: str) -> str:
        texto_limpio = (texto or "").strip()
        if len(texto_limpio) <= MAX_PDF_CHARS:
            return texto_limpio

        inicio = texto_limpio[:9000]
        fin = texto_limpio[-2500:]
        return f"{inicio}\n\n[... contenido omitido para reducir tamano ...]\n\n{fin}"

    def _optimizar_imagen(self, imagen: Image.Image) -> Image.Image:
        imagen_opt = imagen.copy()
        imagen_opt.thumbnail((MAX_IMAGE_SIDE, MAX_IMAGE_SIDE))
        return imagen_opt

    def _imagen_a_contenido(self, imagen: Image.Image) -> dict:
        imagen_opt = self._optimizar_imagen(imagen)
        if imagen_opt.mode not in ("RGB", "L"):
            imagen_opt = imagen_opt.convert("RGB")

        formato = "PNG"
        mime = "image/png"
        if imagen_opt.mode == "RGB":
            formato = "JPEG"
            mime = "image/jpeg"

        buffer = io.BytesIO()
        imagen_opt.save(buffer, format=formato, quality=85)
        encoded = base64.b64encode(buffer.getvalue()).decode("utf-8")
        return {
            "type": "image_url",
            "image_url": {"url": f"data:{mime};base64,{encoded}"},
        }

    def _procesar_peticion(self, pregunta_usuario: str) -> str:
        pregunta_lower = pregunta_usuario.lower()
        contexto_adicional = ""

        if "tarifario" in pregunta_lower or "cobertura" in pregunta_lower or "prima" in pregunta_lower:
            tipo_seguro = "auto" if "auto" in pregunta_lower else "hogar" if "hogar" in pregunta_lower else None
            if tipo_seguro:
                tarifarios = obtener_tarifario(tipo_seguro)
                contexto_adicional += f"\n\nTarifarios de {tipo_seguro}:\n{json.dumps(tarifarios, indent=2, ensure_ascii=False)}"

        if "siniestro" in pregunta_lower:
            import re

            match = re.search(r"SIN\d+", pregunta_usuario)
            if match:
                id_sin = match.group()
                siniestro = obtener_siniestro(id_sin)
                if siniestro:
                    contexto_adicional += f"\n\nDetalles del siniestro {id_sin}:\n{json.dumps(siniestro, indent=2, ensure_ascii=False)}"
            else:
                siniestros = listar_siniestros()
                contexto_adicional += f"\n\nSiniestros disponibles:\n{json.dumps(siniestros, indent=2, ensure_ascii=False)}"

        if "politica" in pregunta_lower or "auditoria" in pregunta_lower or "criterio" in pregunta_lower:
            politicas = obtener_politicas()
            contexto_adicional += f"\n\nPoliticas de auditoria:\n{json.dumps(politicas, indent=2, ensure_ascii=False)}"

        return pregunta_usuario + contexto_adicional

    def limpiar_historial(self):
        self.historial = []

    def obtener_historial(self) -> list:
        return self.historial


def crear_agente() -> AgenteAuditoria:
    return AgenteAuditoria()
