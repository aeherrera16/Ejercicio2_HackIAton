"""
app.py - Interfaz de usuario con Streamlit (estilo minimalista centrado)
"""

import io
import json
import os
import uuid
from datetime import datetime
import streamlit as st
from PIL import Image
from pypdf import PdfReader
from agente import crear_agente, MAX_ADJUNTOS

# ── Persistencia de conversaciones ──────────────────────────────────────────
CONVERSATIONS_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "conversaciones.json")


def _cargar_conversaciones() -> list:
    """Carga las conversaciones guardadas del archivo JSON."""
    if not os.path.exists(CONVERSATIONS_FILE):
        return []
    try:
        with open(CONVERSATIONS_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    except (json.JSONDecodeError, IOError):
        return []


def _guardar_conversaciones(conversaciones: list):
    """Guarda las conversaciones en el archivo JSON."""
    try:
        with open(CONVERSATIONS_FILE, "w", encoding="utf-8") as f:
            json.dump(conversaciones, f, ensure_ascii=False, indent=2)
    except IOError:
        pass


def _guardar_conversacion_actual():
    """Guarda o actualiza la conversación actual en el archivo."""
    if not st.session_state.historial:
        return

    conversaciones = _cargar_conversaciones()
    conv_id = st.session_state.get("conv_id")

    # Resumen: primera pregunta del usuario
    primera_pregunta = next(
        (m["content"] for m in st.session_state.historial if m["role"] == "user"), "Sin título"
    )
    resumen = primera_pregunta[:60] + "..." if len(primera_pregunta) > 60 else primera_pregunta

    conv_data = {
        "id": conv_id,
        "resumen": resumen,
        "fecha": datetime.now().strftime("%Y-%m-%d %H:%M"),
        "historial": st.session_state.historial,
    }

    # Actualizar si ya existe, o agregar nueva
    encontrada = False
    for i, c in enumerate(conversaciones):
        if c["id"] == conv_id:
            conversaciones[i] = conv_data
            encontrada = True
            break

    if not encontrada:
        conversaciones.insert(0, conv_data)

    # Mantener máximo 20 conversaciones
    conversaciones = conversaciones[:20]
    _guardar_conversaciones(conversaciones)

st.set_page_config(
    page_title="Auditor IA - Seguros",
    page_icon="A",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ── CSS completo estilo minimalista gris ─────────────────────────────────────
st.markdown(
    """
<style>
/* ─── Google Fonts ─── */
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');

:root {
    --bg-main: #f0f0f0;
    --bg-sidebar: #e8e8e8;
    --bg-card: #ffffff;
    --bg-input: #ffffff;
    --bg-input-area: #f5f5f5;
    --border-light: rgba(0, 0, 0, 0.08);
    --border-input: #d0d0d0;
    --text-primary: #1a1a1a;
    --text-secondary: #555555;
    --text-muted: #888888;
    --accent-primary: #2b2b2b;
    --accent-hover: #444444;
    --accent-subtle: #e0e0e0;
    --shadow-sm: 0 1px 3px rgba(0,0,0,0.04);
    --shadow-md: 0 4px 20px rgba(0, 0, 0, 0.06);
    --shadow-lg: 0 8px 40px rgba(0, 0, 0, 0.08);
    --shadow-input: 0 2px 16px rgba(0, 0, 0, 0.08);
    --radius-sm: 10px;
    --radius-md: 16px;
    --radius-lg: 24px;
    --radius-xl: 32px;
    --radius-full: 999px;
}

html, body, [class*="css"], .stApp {
    font-family: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif !important;
    color: var(--text-primary);
}

/* ─── Fondo principal gris elegante ─── */
.stApp {
    background:
        radial-gradient(ellipse 1400px 700px at 50% 0%, rgba(255, 255, 255, 0.6), transparent 60%),
        linear-gradient(180deg, #f2f2f2 0%, #ebebeb 40%, #e6e6e6 100%);
}

/* ─── Bottom container (Streamlit chat input area) ─── */
.stBottom,
.stBottom > div,
[data-testid="stBottom"],
[data-testid="stBottom"] > div {
    background: transparent !important;
    border-top: none !important;
    box-shadow: none !important;
}

[data-testid="stBottomBlockContainer"],
.stBottom [data-testid="stBottomBlockContainer"] {
    background: transparent !important;
    padding-top: 0px !important;
    padding-bottom: 18px !important;
    border-top: none !important;
}

/* ─── Sidebar ─── */
section[data-testid="stSidebar"] {
    background: linear-gradient(180deg, #fafafa 0%, #f3f3f3 100%);
    border-right: 1px solid rgba(0,0,0,0.06);
    padding-top: 0;
    box-shadow: 2px 0 20px rgba(0,0,0,0.03);
}

section[data-testid="stSidebar"] > div {
    background: transparent !important;
    padding-top: 20px;
    padding-bottom: 40px;
    display: flex;
    flex-direction: column;
    min-height: calc(100vh - 20px);
}

/* Sidebar brand */
.sidebar-brand {
    display: flex;
    align-items: center;
    gap: 12px;
    padding: 10px 4px 20px;
}

.sidebar-brand-icon {
    width: 40px;
    height: 40px;
    background: linear-gradient(135deg, #2b2b2b 0%, #4a4a4a 100%);
    border-radius: 12px;
    display: flex;
    align-items: center;
    justify-content: center;
    color: white;
    font-weight: 700;
    font-size: 1.15rem;
    font-family: 'Inter', sans-serif;
    flex-shrink: 0;
    box-shadow: 0 2px 8px rgba(0,0,0,0.15);
}

.sidebar-brand-text {
    font-family: 'Inter', sans-serif;
    font-size: 1.1rem;
    font-weight: 700;
    color: var(--text-primary);
    letter-spacing: -0.02em;
}

.sidebar-brand-sub {
    font-family: 'Inter', sans-serif;
    font-size: 0.72rem;
    font-weight: 400;
    color: var(--text-muted);
    letter-spacing: 0.01em;
    margin-top: 1px;
}

section[data-testid="stSidebar"] .stMarkdown h3 {
    font-family: 'Inter', sans-serif;
    font-size: 1.05rem;
    font-weight: 700;
    color: var(--text-primary);
    letter-spacing: -0.02em;
    margin-bottom: 4px;
}

/* New conversation button — first button in sidebar */
section[data-testid="stSidebar"] .stButton:first-of-type > button {
    background: linear-gradient(135deg, #2b2b2b 0%, #3d3d3d 100%);
    border: none;
    border-radius: 12px;
    color: #ffffff;
    font-family: 'Inter', sans-serif;
    font-size: 0.84rem;
    font-weight: 500;
    padding: 11px 16px;
    text-align: center;
    transition: all 0.25s ease;
    width: 100%;
    box-shadow: 0 2px 8px rgba(0,0,0,0.12);
    letter-spacing: 0.01em;
}

section[data-testid="stSidebar"] .stButton:first-of-type > button:hover {
    background: linear-gradient(135deg, #3d3d3d 0%, #555555 100%);
    transform: translateY(-1px);
    box-shadow: 0 4px 16px rgba(0,0,0,0.18);
}

/* Conversation history buttons */
section[data-testid="stSidebar"] .stButton:not(:first-of-type) > button {
    background: rgba(255, 255, 255, 0.6);
    border: 1px solid rgba(0, 0, 0, 0.06);
    border-radius: 10px;
    color: var(--text-secondary);
    font-family: 'Inter', sans-serif;
    font-size: 0.8rem;
    font-weight: 400;
    padding: 8px 12px;
    text-align: left;
    transition: all 0.2s ease;
    width: 100%;
    box-shadow: none;
}

section[data-testid="stSidebar"] .stButton:not(:first-of-type) > button:hover {
    background: rgba(255, 255, 255, 0.9);
    border-color: rgba(0,0,0,0.1);
    color: var(--text-primary);
    transform: translateX(2px);
}

.sidebar-section-label {
    font-size: 0.68rem;
    font-weight: 600;
    color: var(--text-muted);
    text-transform: uppercase;
    letter-spacing: 0.1em;
    padding: 18px 4px 8px;
    margin: 0;
}

.sidebar-divider {
    border: none;
    border-top: 1px solid rgba(0,0,0,0.06);
    margin: 12px 0 6px;
}

/* Empty state in sidebar */
.sidebar-empty {
    text-align: center;
    padding: 36px 16px;
    color: var(--text-muted);
    font-size: 0.82rem;
    font-family: 'Inter', sans-serif;
    line-height: 1.5;
}

.sidebar-empty-icon {
    font-size: 2rem;
    margin-bottom: 10px;
    opacity: 0.35;
}

/* Sidebar footer */
.sidebar-footer {
    position: fixed;
    bottom: 15px;
    left: 18px;
    text-align: left;
    font-family: 'Inter', sans-serif;
    font-size: 0.65rem;
    font-weight: 400;
    color: #a0a0a0;
    line-height: 1.4;
    letter-spacing: 0.01em;
    z-index: 999;
}

/* ─── Greeting centrado ─── */
.greeting-container {
    display: flex;
    flex-direction: column;
    align-items: center;
    justify-content: center;
    min-height: calc(100vh - 160px);
    padding: 0 20px 60px;
    animation: fadeInUp 0.6s ease-out;
}

.greeting-container h1 {
    font-family: 'Inter', sans-serif;
    font-size: 2.2rem;
    font-weight: 700;
    color: var(--text-primary);
    margin: 0 0 2px 0;
    letter-spacing: -0.03em;
    text-align: center;
    line-height: 1.25;
}

.greeting-container .greeting-subtitle {
    font-family: 'Inter', sans-serif;
    font-size: 2.2rem;
    font-weight: 700;
    color: var(--text-primary);
    margin: 0 0 28px 0;
    letter-spacing: -0.03em;
    text-align: center;
    line-height: 1.25;
}

/* System description */
.system-description {
    max-width: 520px;
    text-align: center;
    font-family: 'Inter', sans-serif;
    font-size: 0.85rem;
    font-weight: 400;
    color: var(--text-muted);
    line-height: 1.6;
    padding: 16px 20px;
    background: rgba(255, 255, 255, 0.5);
    border-radius: 14px;
    border: 1px solid rgba(0, 0, 0, 0.05);
}

/* ─── Chat messages ─── */
/* Mensajes del asistente: a la izquierda */
.stChatMessage {
    max-width: 740px;
    margin-left: 0;
    margin-right: auto;
}

/* Mensajes del usuario: a la derecha */
.stChatMessage[data-testid="stChatMessage"]:has([data-testid="stChatMessageAvatarUser"]) {
    margin-left: auto;
    margin-right: 0;
}

.stChatMessage [data-testid="stChatMessageContent"] {
    background: var(--bg-card);
    border: 1px solid var(--border-light);
    border-radius: var(--radius-md);
    padding: 14px 16px;
    box-shadow: var(--shadow-md);
}

.stChatMessage [data-testid="stMarkdownContainer"] p,
.stChatMessage [data-testid="stMarkdownContainer"] li,
.stChatMessage [data-testid="stMarkdownContainer"] strong,
.stChatMessage [data-testid="stMarkdownContainer"] em,
.stChatMessage [data-testid="stMarkdownContainer"] code {
    font-family: 'Inter', sans-serif !important;
    line-height: 1.65;
    font-size: 0.95rem;
}

.audit-note {
    color: var(--text-primary);
    font-size: 0.95rem;
    line-height: 1.7;
    font-family: 'Inter', sans-serif !important;
}

.audit-note strong {
    color: var(--text-primary);
    font-weight: 600;
}

/* ─── Model badge ─── */
.model-badge {
    display: inline-flex;
    align-items: center;
    gap: 6px;
    background: var(--accent-primary);
    color: #ffffff;
    font-size: 0.75rem;
    font-weight: 600;
    padding: 5px 14px;
    border-radius: var(--radius-full);
    letter-spacing: 0.01em;
}

/* ─── Chat input area ─── */
div[data-testid="stChatInput"] {
    max-width: 620px;
    margin: 0 auto;
}

div[data-testid="stChatInput"] > div {
    border-radius: var(--radius-xl) !important;
    border: 1px solid rgba(0, 0, 0, 0.10) !important;
    background: var(--bg-card) !important;
    box-shadow: var(--shadow-input) !important;
    padding: 2px 4px !important;
    transition: box-shadow 0.2s ease, border-color 0.2s ease;
}

div[data-testid="stChatInput"] > div:focus-within {
    border-color: rgba(0, 0, 0, 0.20) !important;
    box-shadow: 0 4px 24px rgba(0, 0, 0, 0.10) !important;
}

div[data-testid="stChatInput"] textarea {
    font-family: 'Inter', sans-serif !important;
    font-size: 0.93rem !important;
    color: var(--text-primary) !important;
}

div[data-testid="stChatInput"] textarea::placeholder {
    color: var(--text-muted) !important;
    font-weight: 400;
}

/* ─── File uploader ─── */
div[data-testid="stFileUploader"] {
    max-width: 660px;
    margin: 0 auto;
}

div[data-testid="stFileUploader"] > div {
    border-radius: var(--radius-md) !important;
    border-color: var(--border-input) !important;
}

/* ─── Misc ─── */
.stMarkdown, .stMarkdown p {
    font-family: 'Inter', sans-serif !important;
}

.stAlert {
    max-width: 740px;
    margin-left: auto;
    margin-right: auto;
    border-radius: var(--radius-md) !important;
}

.stSpinner {
    max-width: 740px;
    margin-left: auto;
    margin-right: auto;
}

/* ─── Terms line ─── */
.terms-line {
    text-align: center;
    font-size: 0.72rem;
    color: var(--text-muted);
    margin-top: 6px;
    margin-bottom: 0;
    font-family: 'Inter', sans-serif;
    letter-spacing: 0.01em;
}

.terms-line a {
    color: var(--text-secondary);
    text-decoration: underline;
    text-underline-offset: 2px;
}

/* ─── Hide Streamlit deploy button & header ─── */
header[data-testid="stHeader"] {
    background: transparent !important;
    backdrop-filter: none !important;
    height: 0 !important;
    min-height: 0 !important;
    overflow: hidden !important;
}

.stDeployButton {
    display: none !important;
}

footer { visibility: hidden; }
#MainMenu { visibility: hidden; }

/* ─── Reduce top padding of main content ─── */
.stMainBlockContainer,
block-container {
    padding-top: 1rem !important;
}

/* ─── Animations ─── */
@keyframes fadeInUp {
    from { opacity: 0; transform: translateY(18px); }
    to   { opacity: 1; transform: translateY(0); }
}

.stChatMessage {
    animation: fadeInUp 0.35s ease-out;
}

/* ─── Scrollbar ─── */
::-webkit-scrollbar { width: 6px; }
::-webkit-scrollbar-track { background: transparent; }
::-webkit-scrollbar-thumb {
    background: #c0c0c0;
    border-radius: 3px;
}
::-webkit-scrollbar-thumb:hover { background: #a0a0a0; }

/* ─── Responsive ─── */
@media (max-width: 900px) {
    .greeting-container h1,
    .greeting-container .greeting-subtitle {
        font-size: 1.8rem;
    }

    .stChatMessage,
    div[data-testid="stChatInput"],
    div[data-testid="stFileUploader"],
    .stAlert,
    .stSpinner {
        max-width: 92vw;
    }
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
if "conv_id" not in st.session_state:
    st.session_state.conv_id = str(uuid.uuid4())
if "conversaciones_guardadas" not in st.session_state:
    st.session_state.conversaciones_guardadas = _cargar_conversaciones()


# ── Helpers ─────────────────────────────────────────────────────────────────
def _saludo_hora() -> str:
    from datetime import datetime
    hora = datetime.now().hour
    if hora < 12:
        return "Buenos días"
    elif hora < 18:
        return "Buenas tardes"
    return "Buenas noches"


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


# ── Sidebar ─────────────────────────────────────────────────────────────────
with st.sidebar:
    # Brand with icon
    st.markdown(
        """
        <div class="sidebar-brand">
            <div class="sidebar-brand-icon">A</div>
            <div>
                <div class="sidebar-brand-text">Auditor IA</div>
                <div class="sidebar-brand-sub">Asistente de auditoría</div>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    # New conversation / clear button
    if st.button("Nueva conversación", use_container_width=True):
        # Guardar conversación actual antes de limpiar
        _guardar_conversacion_actual()
        st.session_state.agente.limpiar_historial()
        st.session_state.historial = []
        st.session_state.adjuntos = []
        st.session_state.ultimo_input = None
        st.session_state.consulta_seleccionada = None
        st.session_state.conv_id = str(uuid.uuid4())
        st.session_state.conversaciones_guardadas = _cargar_conversaciones()
        st.rerun()

    st.markdown("<hr class='sidebar-divider'>", unsafe_allow_html=True)

    # Recents - cargar conversaciones guardadas
    st.markdown("<div class='sidebar-section-label'>Recientes</div>", unsafe_allow_html=True)

    conversaciones = st.session_state.conversaciones_guardadas
    hay_conversaciones = False

    # Mostrar conversación actual si tiene historial
    if st.session_state.historial:
        consultas_previas = [m["content"] for m in st.session_state.historial if m["role"] == "user"]
        if consultas_previas:
            primera = consultas_previas[0]
            resumen = primera if len(primera) <= 50 else primera[:47] + "..."
            st.markdown(f"<div style='font-size:0.7rem;color:#aaa;padding:2px 4px 0;'>Ahora</div>", unsafe_allow_html=True)
            if st.button(f"● {resumen}", key="conv_actual", use_container_width=True):
                pass  # Ya estamos en esta conversación
            hay_conversaciones = True

    # Mostrar conversaciones guardadas
    for idx, conv in enumerate(conversaciones):
        if conv["id"] == st.session_state.conv_id:
            continue  # No duplicar la actual
        hay_conversaciones = True
        fecha = conv.get("fecha", "")
        resumen = conv.get("resumen", "Sin título")
        resumen_corto = resumen if len(resumen) <= 50 else resumen[:47] + "..."
        st.markdown(f"<div style='font-size:0.7rem;color:#aaa;padding:2px 4px 0;'>{fecha}</div>", unsafe_allow_html=True)
        if st.button(resumen_corto, key=f"conv_{idx}", use_container_width=True):
            # Cargar esta conversación
            st.session_state.historial = conv["historial"]
            st.session_state.conv_id = conv["id"]
            st.session_state.agente.limpiar_historial()
            st.session_state.agente.historial = conv["historial"].copy()
            st.session_state.consulta_seleccionada = None
            st.rerun()

    if not hay_conversaciones:
        st.markdown(
            """
            <div class="sidebar-empty">
                <div class="sidebar-empty-icon">💬</div>
                Tus conversaciones aparecerán aquí
            </div>
            """,
            unsafe_allow_html=True,
        )

    # Footer del sidebar
    st.markdown(
        """
        <div class="sidebar-footer">
            <div>Equipo Chifle y Medio</div>
            <div>Kris y Anahy</div>
        </div>
        """,
        unsafe_allow_html=True,
    )

# ── Main Area ───────────────────────────────────────────────────────────────
hay_historial = len(st.session_state.historial) > 0

# ── Greeting (only shown when chat is empty) ────────────────────────────────
if not hay_historial:
    saludo = _saludo_hora()
    st.markdown(
        f"""
        <div class="greeting-container">
            <h1>{saludo}</h1>
            <p class="greeting-subtitle">¿Qué te gustaría preguntar hoy?</p>
            <div class="system-description">
                Sistema de auditoría automática de documentación y facturas enviadas por el taller a la Aseguradora.
                Verifica que los insumos y honorarios cobrados correspondan al tarifario acordado y a la siniestralidad
                reportada, detectando discrepancias o cobros duplicados antes de que un humano revise la cuenta.
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

# ── Chat History ────────────────────────────────────────────────────────────
if hay_historial:
    for mensaje in st.session_state.historial:
        if mensaje["role"] == "user":
            with st.chat_message("user"):
                st.markdown(mensaje["content"])
        else:
            with st.chat_message("assistant"):
                st.markdown(
                    f"<div class='audit-note'>{mensaje['content']}</div>",
                    unsafe_allow_html=True,
                )

# ── Selected query notice ──────────────────────────────────────────────────
if st.session_state.consulta_seleccionada:
    st.info(f"Consulta seleccionada: {st.session_state.consulta_seleccionada}")

# ── Chat Input ──────────────────────────────────────────────────────────────
entrada = st.chat_input(
    "Pregunta lo que quieras",
    accept_file="multiple",
    file_type=["pdf", "jpg", "jpeg", "png"],
)


# ── Process input ──────────────────────────────────────────────────────────
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
            st.markdown(
                f"<div class='audit-note'>{respuesta}</div>",
                unsafe_allow_html=True,
            )

    st.session_state.historial = st.session_state.agente.obtener_historial()
    _guardar_conversacion_actual()
    st.session_state.conversaciones_guardadas = _cargar_conversaciones()
    st.rerun()
    st.session_state.ultimo_input = usuario_input
    st.session_state.adjuntos = st.session_state.adjuntos[:MAX_ADJUNTOS]
