"""
agente.py - Lógica del agente de IA con Google Gemini

Este archivo contiene el "cerebro" del sistema, donde se configura
el agente de IA y se definen las herramientas que puede utilizar.
"""

import os
import json
import io
from dotenv import load_dotenv
import google.generativeai as genai
from google.api_core.exceptions import ResourceExhausted
from PIL import Image
from database import (
    obtener_tarifario,
    obtener_siniestro,
    listar_siniestros,
    obtener_politicas
)

# Cargar variables de entorno
load_dotenv()

# Configurar API de Gemini
# Leer la API key desde .env o desde Streamlit secrets si estamos en Streamlit Cloud
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
try:
    # si el módulo streamlit está disponible en runtime, preferir st.secrets
    import streamlit as _st
    if not GEMINI_API_KEY and "GEMINI_API_KEY" in _st.secrets:
        GEMINI_API_KEY = _st.secrets["GEMINI_API_KEY"]
except Exception:
    # no estamos en Streamlit o no hay st.secrets disponibles
    pass

if not GEMINI_API_KEY:
    raise ValueError("❌ Error: No se encontró GEMINI_API_KEY en el archivo .env o en Streamlit secrets")

genai.configure(api_key=GEMINI_API_KEY)

# Información sobre herramientas disponibles (para contexto del modelo)
HERRAMIENTAS_DISPONIBLES = """
Herramientas disponibles:
1. obtener_tarifario(tipo_seguro: str) - Obtiene tarifarios para 'auto' o 'hogar'
2. obtener_siniestro(id_siniestro: str) - Obtiene detalles de un siniestro (ej: SIN001)
3. listar_siniestros() - Lista todos los siniestros disponibles
4. obtener_politicas() - Obtiene las políticas de auditoría
"""

MAX_ADJUNTOS = 3
MAX_PDF_CHARS = 12000
MAX_IMAGE_SIDE = 1400



def procesar_herramienta(nombre_herramienta: str, parametros: dict):
    """
    Procesa las llamadas a herramientas del agente.
    
    Args:
        nombre_herramienta: Nombre de la herramienta a ejecutar
        parametros: Parámetros para la herramienta
        
    Returns:
        Resultado de la herramienta
    """
    if nombre_herramienta == "obtener_tarifario":
        return obtener_tarifario(parametros.get("tipo_seguro"))
    elif nombre_herramienta == "obtener_siniestro":
        return obtener_siniestro(parametros.get("id_siniestro"))
    elif nombre_herramienta == "listar_siniestros":
        return listar_siniestros()
    elif nombre_herramienta == "obtener_politicas":
        return obtener_politicas()
    else:
        return {"error": f"Herramienta no encontrada: {nombre_herramienta}"}


class AgenteAuditoria:
    """Clase principal del agente de auditoría de seguros."""
    
    def __init__(self):
        """Inicializa el agente con el modelo de Gemini."""
        # Preparar el contexto del sistema con información de herramientas
        contexto_herramientas = f"""
{HERRAMIENTAS_DISPONIBLES}

INSTRUCCIONES PARA USAR LAS HERRAMIENTAS:
- Si el usuario pregunta por tarifarios, usa: obtener_tarifario(tipo_seguro)
- Si pregunta por un siniestro específico, usa: obtener_siniestro(id_siniestro)
- Si pregunta por todos los siniestros, usa: listar_siniestros()
- Si pregunta por políticas de auditoría, usa: obtener_politicas()
    - Si hay un archivo adjunto, analízalo directamente sin pedir ID.
    - Tu primera tarea con un adjunto es clasificarlo: si parece documentación de siniestro, factura, póliza, cotización, peritaje u otro tipo de documento.
    - Si el adjunto contiene facturas o documentación de taller, verifica si los insumos y honorarios coinciden con el tarifario y con la siniestralidad reportada.
    - Detecta discrepancias, cobros duplicados, montos fuera de tarifario o señales de que el archivo no corresponde a un siniestro.
    - Si no puedes leer bien el archivo, dilo explícitamente y explica qué información falta, pero no solicites un ID si ya hay un adjunto.

Nunca escribas llamadas de funciones literalmente en la respuesta final.
No devuelvas textos como obtener_tarifario('auto') o consultar herramienta: responde con el resultado y el análisis.
Si usas una herramienta, incorpora su información en una explicación natural y breve.

Cuando necesites una herramienta, primero menciona que la vas a consultar,
luego proporciona la respuesta con el resultado.
"""
        
        system_instruction = """Eres un auditor experto en seguros. Tu función es:
1. Analizar solicitudes de reclamos de seguros
2. Verificar la cobertura disponible en las pólizas
3. Consultar tarifarios y políticas de auditoría
4. Proporcionar recomendaciones sobre aprobación o rechazo de reclamos
5. Explicar de manera clara las decisiones en lenguaje accesible

Siempre sé profesional, imparcial y fundamenta tus análisis con datos.
    Cuando el usuario adjunte un archivo, debes analizar ese archivo como evidencia principal y responder si corresponde o no a un siniestro, junto con una breve justificación.
    Si te preguntan por limites de carga, responde que puedes analizar hasta 3 archivos por consulta y que aceptas PDF, JPG o PNG.
""" + contexto_herramientas
        
        self.modelo = genai.GenerativeModel(
            model_name="gemini-1.5-flash-latest",
            system_instruction=system_instruction
        )
        self.historial = []
    
    def analizar_reclamo(self, pregunta_usuario: str, adjuntos: list | None = None) -> str:
        """
        Analiza un reclamo usando el agente de IA.
        
        Args:
            pregunta_usuario: Pregunta o consulta del usuario
            adjuntos: Lista de adjuntos procesados desde la interfaz
            
        Returns:
            Respuesta del agente
        """
        # Procesar herramientas mencionadas en la pregunta
        respuesta_mejorada = self._procesar_peticion(pregunta_usuario)

        partes_generacion = self._construir_partes_generacion(respuesta_mejorada, adjuntos)
        
        # Agregar pregunta al historial
        self.historial.append({
            "role": "user",
            "content": pregunta_usuario
        })
        
        # Generar respuesta
        try:
            respuesta = self.modelo.generate_content(
                partes_generacion,
                generation_config=genai.types.GenerationConfig(
                    temperature=0.4,
                    max_output_tokens=1200
                )
            )
        except ResourceExhausted:
            return (
                "No pude completar el análisis porque se alcanzó el límite de cuota de Gemini. "
                "Intenta nuevamente en 1-2 minutos o reduce el tamaño/cantidad de adjuntos "
                "(por ejemplo un PDF más corto y una sola imagen)."
            )
        
        # Obtener texto de respuesta
        respuesta_texto = self._limpiar_respuesta(respuesta.text)
        
        # Agregar respuesta al historial
        self.historial.append({
            "role": "assistant",
            "content": respuesta_texto
        })
        
        return respuesta_texto

    def _limpiar_respuesta(self, texto: str) -> str:
        """
        Elimina referencias literales a llamadas de herramientas para que la salida
        sea solo el análisis final.
        """
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
        Construye las partes del prompt para soportar adjuntos PDF e imágenes.

        Args:
            texto_base: Texto principal de la consulta
            adjuntos: Lista de adjuntos procesados

        Returns:
            Lista de partes para generate_content
        """
        partes = [texto_base]

        if not adjuntos:
            return partes

        partes.append(
            "\n\nObjetivo del análisis: determinar si el archivo adjunto corresponde a un siniestro o a documentación relacionada (factura, póliza, cotización, peritaje, evidencia). "
            "No pidas ID. Si hay facturas, revisa si los conceptos cobrados parecen consistentes con un taller y con la siniestralidad reportada. "
            "Si detectas duplicados o cobros fuera de tarifario, indícalo."
        )

        for adjunto in adjuntos[:MAX_ADJUNTOS]:
            tipo = adjunto.get("tipo")
            nombre = adjunto.get("nombre", "archivo")

            if tipo == "pdf" and adjunto.get("texto"):
                texto_pdf = self._compactar_texto_pdf(adjunto["texto"])
                partes.append(f"\n\nAdjunto PDF: {nombre}\n{texto_pdf}")
            elif tipo == "imagen" and adjunto.get("imagen") is not None:
                partes.append(f"\n\nImagen adjunta: {nombre}")
                partes.append(self._optimizar_imagen(adjunto["imagen"]))

        return partes

    def _compactar_texto_pdf(self, texto: str) -> str:
        """Recorta texto de PDF para controlar consumo de tokens."""
        texto_limpio = (texto or "").strip()
        if len(texto_limpio) <= MAX_PDF_CHARS:
            return texto_limpio

        inicio = texto_limpio[:9000]
        fin = texto_limpio[-2500:]
        return (
            f"{inicio}\n\n[... contenido omitido para reducir tamaño ...]\n\n{fin}"
        )

    def _optimizar_imagen(self, imagen: Image.Image) -> Image.Image:
        """Reduce resolución de imagen antes de enviarla al modelo."""
        imagen_opt = imagen.copy()
        imagen_opt.thumbnail((MAX_IMAGE_SIDE, MAX_IMAGE_SIDE))
        return imagen_opt
    
    def _procesar_peticion(self, pregunta_usuario: str) -> str:
        """
        Procesa la petición del usuario y ejecuta herramientas si es necesario.
        
        Args:
            pregunta_usuario: Pregunta del usuario
            
        Returns:
            Pregunta mejorada con información de herramientas ejecutadas
        """
        pregunta_lower = pregunta_usuario.lower()
        contexto_adicional = ""
        
        # Detectar y ejecutar herramientas automáticamente
        if "tarifario" in pregunta_lower or "cobertura" in pregunta_lower or "prima" in pregunta_lower:
            # Detectar tipo de seguro
            tipo_seguro = "auto" if "auto" in pregunta_lower else "hogar" if "hogar" in pregunta_lower else None
            if tipo_seguro:
                tarifarios = obtener_tarifario(tipo_seguro)
                contexto_adicional += f"\n\n📋 Tarifarios de {tipo_seguro}:\n{json.dumps(tarifarios, indent=2, ensure_ascii=False)}"
        
        if "siniestro" in pregunta_lower:
            # Detectar ID del siniestro
            import re
            match = re.search(r'SIN\d+', pregunta_usuario)
            if match:
                id_sin = match.group()
                siniestro = obtener_siniestro(id_sin)
                if siniestro:
                    contexto_adicional += f"\n\n📄 Detalles del Siniestro {id_sin}:\n{json.dumps(siniestro, indent=2, ensure_ascii=False)}"
            else:
                # Si no hay ID específico, listar todos
                siniestros = listar_siniestros()
                contexto_adicional += f"\n\n📊 Siniestros disponibles:\n{json.dumps(siniestros, indent=2, ensure_ascii=False)}"
        
        if "política" in pregunta_lower or "auditoría" in pregunta_lower or "criterio" in pregunta_lower:
            politicas = obtener_politicas()
            contexto_adicional += f"\n\n⚖️ Políticas de Auditoría:\n{json.dumps(politicas, indent=2, ensure_ascii=False)}"
        
        return pregunta_usuario + contexto_adicional
    
    def limpiar_historial(self):
        """Limpia el historial de conversación."""
        self.historial = []
    
    def obtener_historial(self) -> list:
        """Retorna el historial de conversación."""
        return self.historial


# Función helper para usar en Streamlit
def crear_agente() -> AgenteAuditoria:
    """Factory function para crear el agente."""
    return AgenteAuditoria()
