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
    .stApp {
        background: #f4f1eb;
    }
    html, body, [class*="css"], .stApp {
        font-family: "Aptos", "Segoe UI", Arial, sans-serif;
    }
    .stMarkdown, .stMarkdown p, .stMarkdown li, .stCaption, .stText, .stChatMessage, .stChatMessage p, .stChatMessage li {
        font-family: "Aptos", "Segoe UI", Arial, sans-serif;
    }
    .audit-note,
    .audit-note p,
    .audit-note li,
    .audit-note strong,
    .audit-note em,
    .audit-note code,
    .audit-note ol,
    .audit-note ul {
        font-family: "Aptos", "Segoe UI", Arial, sans-serif !important;
        line-height: 1.6;
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
    .claude-panel {
        background: rgba(255, 255, 255, 0.72);
        border: 1px solid rgba(148, 163, 184, 0.22);
        border-radius: 18px;
        box-shadow: 0 10px 28px rgba(15, 23, 42, 0.05);
        backdrop-filter: blur(10px);
    }
    .history-item {
        background: rgba(255, 255, 255, 0.72);
        border: 1px solid rgba(148, 163, 184, 0.18);
        border-radius: 14px;
        padding: 10px 12px;
        margin-bottom: 10px;
        font-size: 0.92rem;
        color: #334155;
    }
    .history-item small {
        color: #64748b;
        display: block;
        margin-top: 4px;
    }
    .brand-title {
        font-size: 1.9rem;
        font-weight: 700;
        text-align: center;
        margin: 18px 0 8px;
        color: #1f2937;
        letter-spacing: -0.03em;
    }
    .brand-subtitle {
        text-align: center;
        color: #64748b;
        margin-bottom: 18px;
    }
    .stChatMessage [data-testid="stMarkdownContainer"] p,
    .stChatMessage [data-testid="stMarkdownContainer"] li,
    .stChatMessage [data-testid="stMarkdownContainer"] strong,
    .stChatMessage [data-testid="stMarkdownContainer"] em,
    .stChatMessage [data-testid="stMarkdownContainer"] code {
        font-family: "Aptos", "Segoe UI", Arial, sans-serif !important;
        line-height: 1.6;
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
if "consulta_seleccionada" not in st.session_state:
    st.session_state.consulta_seleccionada = None


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


st.markdown("<div class='brand-title'>Auditor de Seguros - Agente IA</div>", unsafe_allow_html=True)
st.markdown("<div class='brand-subtitle'>Auditoría automática de facturas, documentación y siniestralidad reportada</div>", unsafe_allow_html=True)

left_col, main_col = st.columns([0.28, 0.72], gap="large")

with left_col:
    st.markdown("<div class='claude-panel' style='padding:16px;'>", unsafe_allow_html=True)
    st.markdown("### Historial")

    if st.button("Limpiar historial", use_container_width=True):
        st.session_state.agente.limpiar_historial()
        st.session_state.historial = []
        st.session_state.adjuntos = []
        st.session_state.ultimo_input = None
        st.session_state.consulta_seleccionada = None
        st.rerun()

    consultas_previas = [m["content"] for m in st.session_state.historial if m["role"] == "user"]

    if consultas_previas:
        for indice, consulta in enumerate(reversed(consultas_previas[-8:]), start=1):
            resumen = consulta if len(consulta) <= 70 else consulta[:67] + "..."
            if st.button(f"{indice}. {resumen}", key=f"hist_{indice}", use_container_width=True):
                st.session_state.consulta_seleccionada = consulta
    else:
        st.caption("Aun no tienes consultas guardadas.")

    st.divider()
    st.markdown("### Guía rápida")
    st.write("- Sube PDF, JPG o PNG")
    st.write("- Escribe tu consulta")
    st.write("- El agente compara contra el tarifario de referencia")
    st.markdown("</div>", unsafe_allow_html=True)

with main_col:
    st.markdown("<div class='claude-panel' style='padding:18px 18px 10px;'>", unsafe_allow_html=True)

    for mensaje in st.session_state.historial:
        if mensaje["role"] == "user":
            with st.chat_message("user"):
                st.markdown(mensaje["content"])
        else:
            with st.chat_message("assistant"):
                st.markdown(f"<div class='audit-note'>{mensaje['content']}</div>", unsafe_allow_html=True)

    if st.session_state.consulta_seleccionada:
        st.info(f"Consulta seleccionada del historial: {st.session_state.consulta_seleccionada}")

    entrada = st.chat_input(
        "Escribe tu pregunta y adjunta archivos...",
        accept_file="multiple",
        file_type=["pdf", "jpg", "jpeg", "png"],
    )

    if entrada:
        if isinstance(entrada, str):
            usuario_input = entrada.strip()
            archivos = []
        else:
            usuario_input = (getattr(entrada, "text", None) or entrada.get("text") or "").strip()
            archivos = list(getattr(entrada, "files", None) or entrada.get("files", []) or [])

        if archivos:
            adjuntos_procesados = []
            if len(archivos) > MAX_ADJUNTOS:
                st.warning(f"Se usarán solo los primeros {MAX_ADJUNTOS} archivos.")

            for archivo in archivos[:MAX_ADJUNTOS]:
                adjunto = procesar_adjunto(archivo)
                if adjunto is not None:
                    adjuntos_procesados.append(adjunto)

            st.session_state.adjuntos = adjuntos_procesados

        if not usuario_input:
            st.warning("Escribe una pregunta para poder analizar los adjuntos.")
            st.stop()

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
                st.markdown(respuesta)

        st.session_state.historial = st.session_state.agente.obtener_historial()
        st.session_state.ultimo_input = usuario_input
        st.session_state.adjuntos = st.session_state.adjuntos[:MAX_ADJUNTOS]

    st.markdown("</div>", unsafe_allow_html=True)

