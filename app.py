"""
app.py - Interfaz de usuario con Streamlit (estilo Claude)
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

# ── CSS completo estilo Claude ──────────────────────────────────────────────
st.markdown(
    """
<style>
/* ─── Google Fonts ─── */
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');

/* ─── Variables globales ─── */
:root {
    --bg-main: #f4f1eb;
    --bg-sidebar: #ffffff;
    --bg-card: #ffffff;
    --bg-input: #ffffff;
    --border-light: rgba(148, 163, 184, 0.18);
    --border-input: #d4cdc4;
    --text-primary: #1a1a1a;
    --text-secondary: #64748b;
    --text-muted: #94a3b8;
    --accent-orange: #c4704b;
    --accent-orange-hover: #b35f3a;
    --accent-warm: #e8ddd3;
    --shadow-sm: 0 1px 3px rgba(0,0,0,0.06);
    --shadow-md: 0 4px 16px rgba(0,0,0,0.06);
    --shadow-lg: 0 8px 32px rgba(0,0,0,0.08);
    --radius-sm: 8px;
    --radius-md: 14px;
    --radius-lg: 22px;
    --radius-xl: 28px;
}

/* ─── Base ─── */
html, body, [class*="css"], .stApp {
    font-family: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif !important;
}

.stApp {
    background: var(--bg-main);
}

/* ─── Sidebar ─── */
section[data-testid="stSidebar"] {
    background: var(--bg-sidebar);
    border-right: 1px solid var(--border-light);
    padding-top: 10px;
}

section[data-testid="stSidebar"] .stMarkdown h3 {
    font-size: 1.05rem;
    font-weight: 600;
    color: var(--text-primary);
    margin-bottom: 4px;
}

section[data-testid="stSidebar"] .stButton > button {
    background: transparent;
    border: 1px solid var(--border-light);
    border-radius: var(--radius-sm);
    color: var(--text-primary);
    font-family: 'Inter', sans-serif;
    font-size: 0.88rem;
    font-weight: 500;
    padding: 8px 14px;
    text-align: left;
    transition: all 0.2s ease;
    width: 100%;
}

section[data-testid="stSidebar"] .stButton > button:hover {
    background: var(--accent-warm);
    border-color: var(--border-input);
}

/* Nav items en sidebar */
.sidebar-nav-item {
    display: flex;
    align-items: center;
    gap: 10px;
    padding: 9px 12px;
    border-radius: var(--radius-sm);
    color: var(--text-primary);
    font-size: 0.92rem;
    font-weight: 500;
    cursor: pointer;
    transition: background 0.15s ease;
    text-decoration: none;
}

.sidebar-nav-item:hover {
    background: #f5f3ef;
}

.sidebar-nav-icon {
    font-size: 1.1rem;
    width: 22px;
    text-align: center;
    opacity: 0.7;
}

.sidebar-section-label {
    font-size: 0.72rem;
    font-weight: 600;
    color: var(--text-muted);
    text-transform: uppercase;
    letter-spacing: 0.08em;
    padding: 18px 12px 6px;
}

.sidebar-history-item {
    display: block;
    padding: 7px 12px;
    border-radius: var(--radius-sm);
    color: var(--text-secondary);
    font-size: 0.85rem;
    cursor: pointer;
    transition: background 0.15s ease;
    white-space: nowrap;
    overflow: hidden;
    text-overflow: ellipsis;
    text-decoration: none;
}

.sidebar-history-item:hover {
    background: #f5f3ef;
    color: var(--text-primary);
}

/* ─── Header / Greeting ─── */
.claude-greeting {
    text-align: center;
    padding: 60px 20px 30px;
}

.claude-greeting-icon {
    display: inline-block;
    width: 48px;
    height: 48px;
    margin-bottom: 4px;
    vertical-align: middle;
}

.claude-greeting h1 {
    font-family: 'Inter', sans-serif;
    font-size: 2.2rem;
    font-weight: 400;
    color: var(--text-primary);
    margin: 0;
    letter-spacing: -0.02em;
}

.claude-greeting h1 span.icon-flower {
    font-size: 2.2rem;
    margin-right: 8px;
    vertical-align: middle;
}

/* ─── Input Container (Chat Box) ─── */
.chat-input-container {
    max-width: 680px;
    margin: 0 auto 18px;
    background: var(--bg-card);
    border: 1px solid var(--border-input);
    border-radius: var(--radius-lg);
    box-shadow: var(--shadow-md);
    overflow: hidden;
}

/* File preview inside the input area */
.file-preview-area {
    padding: 16px 18px 0;
}

.file-preview-card {
    display: inline-flex;
    align-items: center;
    gap: 10px;
    background: #fafaf8;
    border: 1px solid var(--border-light);
    border-radius: 12px;
    padding: 8px 12px;
    max-width: 200px;
}

.file-preview-thumb {
    width: 60px;
    height: 72px;
    background: #fff;
    border: 1px solid #e5e2dc;
    border-radius: 6px;
    display: flex;
    align-items: center;
    justify-content: center;
    overflow: hidden;
    position: relative;
}

.file-preview-thumb img {
    max-width: 100%;
    max-height: 100%;
    object-fit: cover;
}

.file-type-badge {
    position: absolute;
    bottom: 2px;
    left: 4px;
    background: #fff;
    border: 1px solid #e0ddd6;
    border-radius: 3px;
    font-size: 0.6rem;
    font-weight: 700;
    padding: 1px 4px;
    color: var(--text-secondary);
    text-transform: uppercase;
}

/* ─── Suggestion Chips ─── */
.suggestion-chips {
    display: flex;
    justify-content: center;
    gap: 10px;
    flex-wrap: wrap;
    padding: 0 20px 20px;
    max-width: 680px;
    margin: 0 auto;
}

.suggestion-chip {
    display: inline-flex;
    align-items: center;
    gap: 7px;
    background: var(--bg-card);
    border: 1px solid var(--border-input);
    border-radius: 20px;
    padding: 8px 18px;
    font-size: 0.88rem;
    font-weight: 500;
    color: var(--text-primary);
    cursor: pointer;
    transition: all 0.2s ease;
    text-decoration: none;
    font-family: 'Inter', sans-serif;
}

.suggestion-chip:hover {
    background: var(--accent-warm);
    border-color: var(--border-input);
    box-shadow: var(--shadow-sm);
}

.chip-icon {
    font-size: 1rem;
    opacity: 0.75;
}

/* ─── Chat Messages ─── */
.stChatMessage {
    max-width: 680px;
    margin-left: auto;
    margin-right: auto;
    font-family: 'Inter', sans-serif !important;
}

.stChatMessage [data-testid="stMarkdownContainer"] p,
.stChatMessage [data-testid="stMarkdownContainer"] li,
.stChatMessage [data-testid="stMarkdownContainer"] strong,
.stChatMessage [data-testid="stMarkdownContainer"] em,
.stChatMessage [data-testid="stMarkdownContainer"] code {
    font-family: 'Inter', sans-serif !important;
    line-height: 1.65;
}

.audit-note {
    color: #334155;
    font-size: 0.95rem;
    line-height: 1.65;
    font-family: 'Inter', sans-serif !important;
}

.audit-note p,
.audit-note li,
.audit-note strong,
.audit-note em,
.audit-note code,
.audit-note ol,
.audit-note ul {
    font-family: 'Inter', sans-serif !important;
}

/* ─── Model Selector Badge ─── */
.model-badge {
    display: inline-flex;
    align-items: center;
    gap: 5px;
    background: transparent;
    color: var(--text-secondary);
    font-size: 0.82rem;
    font-weight: 500;
    padding: 4px 0;
}

/* ─── Send Button ─── */
.send-btn {
    display: inline-flex;
    align-items: center;
    justify-content: center;
    width: 36px;
    height: 36px;
    background: var(--accent-orange);
    border: none;
    border-radius: 50%;
    color: #fff;
    cursor: pointer;
    transition: background 0.2s ease;
    font-size: 1.1rem;
}

.send-btn:hover {
    background: var(--accent-orange-hover);
}

/* ─── Chat input restyle ─── */
div[data-testid="stChatInput"] {
    max-width: 680px;
    margin: 0 auto;
}

div[data-testid="stChatInput"] > div {
    border-radius: var(--radius-lg) !important;
    border-color: var(--border-input) !important;
    box-shadow: var(--shadow-md) !important;
    background: var(--bg-card) !important;
}

div[data-testid="stChatInput"] textarea {
    font-family: 'Inter', sans-serif !important;
    font-size: 0.95rem;
}

/* ─── File Uploader restyle ─── */
div[data-testid="stFileUploader"] {
    max-width: 680px;
    margin: 0 auto;
}

div[data-testid="stFileUploader"] > div {
    border-radius: var(--radius-md) !important;
    border-color: var(--border-input) !important;
}

/* ─── Streamlit overrides ─── */
.stMarkdown, .stMarkdown p {
    font-family: 'Inter', sans-serif !important;
}

/* Hide default Streamlit footer */
footer { visibility: hidden; }
#MainMenu { visibility: hidden; }

/* Divider */
.sidebar-divider {
    border: none;
    border-top: 1px solid var(--border-light);
    margin: 12px 0;
}

/* Empty chat state */
.empty-chat-notice {
    text-align: center;
    color: var(--text-muted);
    font-size: 0.85rem;
    padding: 30px 0 0;
}

/* Animations */
@keyframes fadeInUp {
    from { opacity: 0; transform: translateY(12px); }
    to   { opacity: 1; transform: translateY(0); }
}

.claude-greeting {
    animation: fadeInUp 0.5s ease-out;
}

.suggestion-chips {
    animation: fadeInUp 0.6s ease-out 0.1s both;
}

/* Scrollbar styling */
::-webkit-scrollbar { width: 6px; }
::-webkit-scrollbar-track { background: transparent; }
::-webkit-scrollbar-thumb {
    background: #d4cdc4;
    border-radius: 3px;
}
::-webkit-scrollbar-thumb:hover { background: #b8b0a5; }

/* ─── Stacked buttons for suggestions ─── */
.stButton > button[kind="secondary"] {
    background: var(--bg-card) !important;
    border: 1px solid var(--border-input) !important;
    border-radius: 20px !important;
    padding: 8px 18px !important;
    font-size: 0.88rem !important;
    font-weight: 500 !important;
    color: var(--text-primary) !important;
    font-family: 'Inter', sans-serif !important;
    transition: all 0.2s ease !important;
}

.stButton > button[kind="secondary"]:hover {
    background: var(--accent-warm) !important;
    border-color: var(--border-input) !important;
}

/* ─── Info/Warning boxes ─── */
.stAlert {
    max-width: 680px;
    margin-left: auto;
    margin-right: auto;
    border-radius: var(--radius-md) !important;
}

/* ─── Spinner ─── */
.stSpinner {
    max-width: 680px;
    margin-left: auto;
    margin-right: auto;
}
</style>
""",
    unsafe_allow_html=True,
)

# ── Session State ───────────────────────────────────────────────────────────
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
    # Brand / Title
    st.markdown("### Auditor IA")

    st.markdown("<hr class='sidebar-divider'>", unsafe_allow_html=True)

    # Clear history button
    if st.button("Limpiar historial", use_container_width=True):
        st.session_state.agente.limpiar_historial()
        st.session_state.historial = []
        st.session_state.adjuntos = []
        st.session_state.ultimo_input = None
        st.session_state.consulta_seleccionada = None
        st.rerun()

    # Recents
    consultas_previas = [m["content"] for m in st.session_state.historial if m["role"] == "user"]

    if consultas_previas:
        st.markdown("<div class='sidebar-section-label'>Recientes</div>", unsafe_allow_html=True)
        for indice, consulta in enumerate(reversed(consultas_previas[-8:]), start=1):
            resumen = consulta if len(consulta) <= 55 else consulta[:52] + "..."
            if st.button(resumen, key=f"hist_{indice}", use_container_width=True):
                st.session_state.consulta_seleccionada = consulta
    else:
        st.markdown("<div class='sidebar-section-label'>Recientes</div>", unsafe_allow_html=True)
        st.caption("Aún no tienes consultas guardadas.")


# ── Main Area ───────────────────────────────────────────────────────────────
hay_historial = len(st.session_state.historial) > 0

# ── Greeting (only shown when chat is empty) ────────────────────────────────
if not hay_historial:
    saludo = _saludo_hora()
    st.markdown(
        f"""
        <div class="claude-greeting">
            <h1>{saludo}, Anahy</h1>
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
    "¿En qué puedo ayudarte hoy?",
    accept_file="multiple",
    file_type=["pdf", "jpg", "jpeg", "png"],
)



# ── Model badge ─────────────────────────────────────────────────────────────
if not hay_historial:
    st.markdown(
        """
        <div style="text-align:center; padding: 10px 0 30px;">
            <span class="model-badge">Llama 4 Scout · OpenRouter</span>
        </div>
        """,
        unsafe_allow_html=True,
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
    st.session_state.ultimo_input = usuario_input
    st.session_state.adjuntos = st.session_state.adjuntos[:MAX_ADJUNTOS]
