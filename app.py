"""
app.py - Interfaz de usuario con Streamlit

Este archivo contiene la "cara" del sistema, donde los usuarios
interactúan con el agente de auditoría de seguros.
"""

import io
import streamlit as st
from PIL import Image
from pypdf import PdfReader
from agente import crear_agente

# Configuración de la página
st.set_page_config(
    page_title="Auditor IA - Seguros",
    page_icon="🔍",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Estilos CSS personalizados
st.markdown("""
<style>
    .main-title {
        color: #1f77b4;
        text-align: center;
        margin-bottom: 30px;
    }
    .info-box {
        background-color: #e3f2fd;
        padding: 15px;
        border-radius: 8px;
        border-left: 4px solid #1f77b4;
        margin-bottom: 15px;
    }
    .success-box {
        background-color: #e8f5e9;
        padding: 15px;
        border-radius: 8px;
        border-left: 4px solid #4caf50;
        margin-bottom: 15px;
    }
    .warning-box {
        background-color: #fff3e0;
        padding: 15px;
        border-radius: 8px;
        border-left: 4px solid #ff9800;
        margin-bottom: 15px;
    }
</style>
""", unsafe_allow_html=True)

# Inicializar sesión
if "agente" not in st.session_state:
    st.session_state.agente = crear_agente()
if "historial" not in st.session_state:
    st.session_state.historial = []
if "adjuntos" not in st.session_state:
    st.session_state.adjuntos = []


def procesar_adjunto(archivo):
    """Convierte un archivo cargado en una estructura utilizable por el agente."""
    nombre = archivo.name
    extension = nombre.rsplit(".", 1)[-1].lower()

    if extension == "pdf":
        lector = PdfReader(io.BytesIO(archivo.getvalue()))
        texto_paginas = []

        for pagina in lector.pages:
            texto = pagina.extract_text() or ""
            if texto.strip():
                texto_paginas.append(texto.strip())

        return {
            "nombre": nombre,
            "tipo": "pdf",
            "texto": "\n\n".join(texto_paginas).strip() or "[El PDF no contiene texto extraíble.]",
        }

    if extension in ["jpg", "jpeg", "png"]:
        imagen = Image.open(io.BytesIO(archivo.getvalue()))
        return {
            "nombre": nombre,
            "tipo": "imagen",
            "imagen": imagen,
        }

    return None

# Header
st.markdown("<h1 class='main-title'>🔍 Auditor de Seguros - Agente IA</h1>", unsafe_allow_html=True)

# Sidebar
with st.sidebar:
    st.header("⚙️ Configuración")

    archivos = st.file_uploader(
        "Adjuntar archivos",
        type=["pdf", "jpg", "jpeg", "png"],
        accept_multiple_files=True,
        help="Adjunta PDFs o imágenes para analizarlos junto con tu consulta.",
    )

    adjuntos_procesados = []
    if archivos:
        for archivo in archivos:
            adjunto = procesar_adjunto(archivo)
            if adjunto is not None:
                adjuntos_procesados.append(adjunto)

        st.session_state.adjuntos = adjuntos_procesados

        st.caption("Archivos cargados:")
        for adjunto in adjuntos_procesados:
            st.write(f"• {adjunto['nombre']}")
    
    st.markdown("""
    ### 📋 Funciones disponibles:
    - Analizar reclamos de seguros
    - Consultar tarifarios
    - Verificar coberturas
    - Obtener políticas de auditoría
    """)
    
    if st.button("🗑️ Limpiar historial", use_container_width=True):
        st.session_state.agente.limpiar_historial()
        st.session_state.historial = []
        st.success("✅ Historial limpiado")
    
    st.divider()
    
    st.markdown("""
    ### 💡 Ejemplos de preguntas:
    - "¿Cuáles son las coberturas disponibles para seguros de auto?"
    - "Analiza el siniestro SIN001"
    - "¿Debería aprobarse un reclamo de $50,000?"
    """)

# Contenido principal
col1, col2 = st.columns([2, 1])

with col1:
    st.subheader("💬 Chat con el Auditor")
    
    # Mostrar historial
    for i, mensaje in enumerate(st.session_state.historial):
        if mensaje["role"] == "user":
            with st.chat_message("user"):
                st.write(mensaje["content"])
        else:
            with st.chat_message("assistant"):
                st.write(mensaje["content"])
    
    # Input del usuario
    usuario_input = st.chat_input("Escribe tu pregunta aquí...")
    
    if usuario_input:
        # Mostrar pregunta del usuario
        with st.chat_message("user"):
            st.write(usuario_input)

            if st.session_state.adjuntos:
                st.caption("Adjuntos usados en esta consulta:")
                for adjunto in st.session_state.adjuntos:
                    st.write(f"• {adjunto['nombre']}")
        
        # Obtener respuesta del agente
        with st.chat_message("assistant"):
            with st.spinner("🤔 Analizando..."):
                respuesta = st.session_state.agente.analizar_reclamo(
                    usuario_input,
                    st.session_state.adjuntos,
                )
                st.write(respuesta)
        
        # Guardar en historial de sesión
        st.session_state.historial = st.session_state.agente.obtener_historial()

with col2:
    st.subheader("📎 Adjuntos")

    st.markdown('<div class="info-box">', unsafe_allow_html=True)
    st.markdown("### Archivos listos para análisis")
    st.markdown('</div>', unsafe_allow_html=True)

    if st.session_state.adjuntos:
        for adjunto in st.session_state.adjuntos:
            with st.expander(adjunto["nombre"]):
                st.write(f"**Tipo:** {adjunto['tipo']}")
                if adjunto["tipo"] == "pdf":
                    st.text_area(
                        "Texto extraído",
                        adjunto.get("texto", ""),
                        height=220,
                        label_visibility="collapsed",
                        key=f"texto_{adjunto['nombre']}"
                    )
                elif adjunto["tipo"] == "imagen":
                    st.image(adjunto["imagen"], use_container_width=True)
    else:
        st.caption("No hay archivos adjuntos cargados todavía.")

    st.divider()
    st.markdown("### Sugerencias")
    st.write("• Sube un PDF con el reclamo o póliza")
    st.write("• Sube una imagen del documento o evidencia")
    st.write("• Luego escribe tu consulta en el chat")

# Footer
st.divider()
col1, col2, col3 = st.columns(3)

with col1:
    st.caption("📊 Sistema de Auditoría de Seguros")
with col2:
    st.caption("Powered by Google Gemini")
with col3:
    st.caption("v1.0.0")
