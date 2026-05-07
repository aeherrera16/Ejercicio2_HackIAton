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

# Configurar API de OpenRouter
OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY")
try:
    import streamlit as _st

    if not OPENROUTER_API_KEY and "OPENROUTER_API_KEY" in _st.secrets:
        OPENROUTER_API_KEY = _st.secrets["OPENROUTER_API_KEY"]
except Exception:
    pass

if not OPENROUTER_API_KEY:
    raise ValueError("Error: No se encontro OPENROUTER_API_KEY en .env o Streamlit secrets")

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


class AgenteAuditoria:
    """Clase principal del agente de auditoria de seguros."""

    def __init__(self):
        contexto_herramientas = f"""
{HERRAMIENTAS_DISPONIBLES}

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
            "Eres un auditor experto en seguros. Analiza reclamos, verifica coberturas, "
            "consulta politicas/tarifarios y da recomendaciones claras. "
            "Cuando recibas adjuntos, usalos como evidencia principal. "
            "Puedes analizar hasta 3 archivos por consulta (PDF/JPG/PNG).\n\n"
            + contexto_herramientas
        )

        self.api_url = "https://openrouter.ai/api/v1/chat/completions"
        self.headers = {
            "Authorization": f"Bearer {OPENROUTER_API_KEY}",
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
        """Llama al modelo de OpenRouter con contenido multimodal."""
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
            detalle = ""
            try:
                detalle = resp.text
            except Exception:
                pass
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
        return resultado or texto.strip()

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
            "No pidas ID. Si hay facturas, revisa coherencia y posibles cobros fuera de tarifario."
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
