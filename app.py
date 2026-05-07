"""
app.py - Interfaz de usuario con Streamlit
"""

import io
import streamlit as st
from PIL import Image
from pypdf import PdfReader
from agente import crear_agente, MAX_ADJUNTOS

st.set_page_config(
    page_title="Auditor IA - Seguros",
    page_icon="A",
    layout="wide",
    initial_sidebar_state="expanded",
)

st.markdown(
    """
<style>
    html, body, [class*="css"], .stApp {
        font-family: "Aptos", "Segoe UI", Arial, sans-serif;
    }
    .stMarkdown, .stMarkdown p, .stMarkdown li, .stCaption, .stText, .stChatMessage, .stChatMessage p, .stChatMessage li {
        font-family: "Aptos", "Segoe UI", Arial, sans-serif;
    }
    .main-title {
        color: #1f77b4;
        text-align: center;
        margin-bottom: 30px;
        font-weight: 700;
        letter-spacing: -0.02em;
    }
    .info-box {
        background-color: #e3f2fd;
        padding: 15px;
        border-radius: 8px;
        border-left: 4px solid #1f77b4;
        margin-bottom: 15px;
    }
    .audit-note {
        color: #334155;
        font-size: 0.98rem;
        line-height: 1.55;
    }
</style>
""",
    unsafe_allow_html=True,
)

if "agente" not in st.session_state:
    st.session_state.agente = crear_agente()
if "historial" not in st.session_state:
    st.session_state.historial = []
if "adjuntos" not in st.session_state:
    st.session_state.adjuntos = []
if "ultimo_input" not in st.session_state:
    st.session_state.ultimo_input = None


def procesar_adjunto(archivo):
    """Convierte un archivo cargado en una estructura utilizable por el agente."""
    nombre = archivo.name
    extension = nombre.rsplit(".", 1)[-1].lower()

    if extension == "pdf":
        lector = PdfReader(io.BytesIO(archivo.getvalue()))
        texto_paginas = []
        imagenes_pdf = []

        for pagina in lector.pages:
            texto = pagina.extract_text() or ""
            if texto.strip():
                texto_paginas.append(texto.strip())

            for imagen_pdf in getattr(pagina, "images", []):
                if len(imagenes_pdf) >= 2:
                    break
                try:
                    imagen = Image.open(io.BytesIO(imagen_pdf.data))
                    if imagen.mode not in ("RGB", "L"):
                        imagen = imagen.convert("RGB")
                    imagenes_pdf.append(imagen)
                except Exception:
                    continue

        return {
            "nombre": nombre,
            "tipo": "pdf",
            "texto": "\n\n".join(texto_paginas).strip() or "[El PDF no contiene texto extraible.]",
            "imagenes_pdf": imagenes_pdf,
        }

    if extension in ["jpg", "jpeg", "png"]:
        imagen = Image.open(io.BytesIO(archivo.getvalue()))
        return {
            "nombre": nombre,
            "tipo": "imagen",
            "imagen": imagen,
        }

    return None


st.markdown("<h1 class='main-title'>Auditor de Seguros - Agente IA</h1>", unsafe_allow_html=True)

with st.sidebar:
    st.header("Configuracion")
    st.markdown(
        """
    ### Funciones disponibles
    - Analizar reclamos de seguros
    - Consultar tarifarios
    - Verificar coberturas
    - Obtener politicas de auditoria
    """
    )

    if st.button("Limpiar historial", use_container_width=True):
        st.session_state.agente.limpiar_historial()
        st.session_state.historial = []
        st.success("Historial limpiado")

    st.divider()
    st.markdown(
        """
    ### Ejemplos de preguntas
    - "Cuales son las coberturas disponibles para seguros de auto?"
    - "Analiza el siniestro SIN001"
    - "Deberia aprobarse un reclamo de $50,000?"
    """
    )

col1, col2 = st.columns([2, 1])

with col1:
    st.subheader("Chat con el Auditor")

    archivos = st.file_uploader(
        "Adjuntar archivos",
        type=["pdf", "jpg", "jpeg", "png"],
        accept_multiple_files=True,
        help=(
            "Adjunta PDFs o imagenes para analizarlos junto con tu consulta. "
            f"Maximo {MAX_ADJUNTOS} archivos."
        ),
    )

    if archivos:
        adjuntos_procesados = []
        if len(archivos) > MAX_ADJUNTOS:
            st.warning(f"Se usaran solo los primeros {MAX_ADJUNTOS} archivos.")

        for archivo in archivos[:MAX_ADJUNTOS]:
            adjunto = procesar_adjunto(archivo)
            if adjunto is not None:
                adjuntos_procesados.append(adjunto)

        st.session_state.adjuntos = adjuntos_procesados

    if st.session_state.adjuntos:
        st.caption("Archivos cargados:")
        for adjunto in st.session_state.adjuntos:
            st.write(f"- {adjunto['nombre']}")

    for mensaje in st.session_state.historial:
        if mensaje["role"] == "user":
            with st.chat_message("user"):
                st.markdown(mensaje["content"])
        else:
            with st.chat_message("assistant"):
                st.markdown(mensaje["content"])

    usuario_input = st.chat_input("Escribe tu pregunta aqui...")

    if usuario_input and usuario_input != st.session_state.ultimo_input:
        with st.chat_message("user"):
            st.markdown(usuario_input)
            if st.session_state.adjuntos:
                st.caption("Adjuntos usados en esta consulta:")
                for adjunto in st.session_state.adjuntos:
                    st.write(f"- {adjunto['nombre']}")

        with st.chat_message("assistant"):
            with st.spinner("Analizando..."):
                respuesta = st.session_state.agente.analizar_reclamo(
                    usuario_input,
                    st.session_state.adjuntos,
                )
                st.markdown(f"<div class='audit-note'>{respuesta}</div>", unsafe_allow_html=True)

        st.session_state.historial = st.session_state.agente.obtener_historial()
        st.session_state.ultimo_input = usuario_input

with col2:
    st.subheader("Adjuntos")
    st.markdown('<div class="info-box"><strong>Archivos listos para analisis</strong></div>', unsafe_allow_html=True)

    if st.session_state.adjuntos:
        for adjunto in st.session_state.adjuntos:
            with st.expander(adjunto["nombre"]):
                st.write(f"Tipo: {adjunto['tipo']}")
                if adjunto["tipo"] == "pdf":
                    st.text_area(
                        "Texto extraido",
                        adjunto.get("texto", ""),
                        height=220,
                        label_visibility="collapsed",
                        key=f"texto_panel_{adjunto['nombre']}",
                    )
                    if adjunto.get("imagenes_pdf"):
                        st.caption("Imagenes extraidas del PDF:")
                        for img in adjunto["imagenes_pdf"]:
                            st.image(img, use_container_width=True)
                elif adjunto["tipo"] == "imagen":
                    st.image(adjunto["imagen"], use_container_width=True)
    else:
        st.caption("No hay archivos adjuntos cargados todavia.")

    st.divider()
    st.markdown("### Sugerencias")
    st.write("- Sube un PDF con el reclamo o poliza")
    st.write("- Sube una imagen del documento o evidencia")
    st.write("- Luego escribe tu consulta en el chat")

st.divider()
c1, c2 = st.columns(2)
with c1:
    st.caption("Sistema de Auditoria de Seguros")
with c2:
    st.caption("Powered by Llama 4 Scout")
