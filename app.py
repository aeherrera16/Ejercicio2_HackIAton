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
@import url('https://fonts.googleapis.com/css2?family=Space+Grotesk:wght@400;500;600;700&family=Source+Sans+3:wght@400;500;600&display=swap');

:root {
    --bg-main: #f6f0e8;
    --bg-sidebar: #f6f0e8;
    --bg-card: #ffffff;
    --bg-input: #ffffff;
    --border-light: rgba(36, 38, 40, 0.12);
    --border-input: #d7cdbf;
    --text-primary: #1f2328;
    --text-secondary: #5c6570;
    --text-muted: #8f98a3;
    --accent-coral: #e46f4a;
    --accent-coral-hover: #cf5c3a;
    --accent-ink: #182029;
    --accent-sand: #efe4d6;
    --shadow-sm: 0 1px 3px rgba(0,0,0,0.06);
    --shadow-md: 0 10px 30px rgba(17, 24, 39, 0.10);
    --shadow-lg: 0 22px 60px rgba(17, 24, 39, 0.16);
    --radius-sm: 10px;
    --radius-md: 16px;
    --radius-lg: 24px;
    --radius-xl: 32px;
}

html, body, [class*="css"], .stApp {
    font-family: 'Source Sans 3', 'Segoe UI', sans-serif !important;
    color: var(--text-primary);
}

.stApp {
    background:
        radial-gradient(1200px 600px at 80% -10%, rgba(228, 111, 74, 0.18), transparent 55%),
        radial-gradient(900px 500px at -10% 10%, rgba(24, 32, 41, 0.12), transparent 55%),
        linear-gradient(180deg, #f9f3eb 0%, #f4ede3 55%, #f2eadf 100%);
}

section[data-testid="stSidebar"] {
    background:
        linear-gradient(180deg, rgba(255, 255, 255, 0.2), rgba(244, 236, 225, 0.65)),
        var(--bg-sidebar);
    border-right: none;
    padding-top: 18px;
    box-shadow: 18px 0 40px rgba(24, 32, 41, 0.08);
}

section[data-testid="stSidebar"] > div {
    background: transparent !important;
}

section[data-testid="stSidebar"] .stMarkdown h3 {
    font-family: 'Space Grotesk', sans-serif;
    font-size: 1.1rem;
    font-weight: 600;
    color: var(--accent-ink);
    letter-spacing: -0.01em;
    margin-bottom: 4px;
}

section[data-testid="stSidebar"] .stButton > button {
    background: var(--bg-card);
    border: 1px solid var(--border-light);
    border-radius: var(--radius-sm);
    color: var(--text-primary);
    font-family: 'Source Sans 3', sans-serif;
    font-size: 0.9rem;
    font-weight: 600;
    padding: 9px 14px;
    text-align: left;
    transition: all 0.2s ease;
    width: 100%;
    box-shadow: var(--shadow-sm);
}

section[data-testid="stSidebar"] .stButton > button:hover {
    background: var(--accent-sand);
    border-color: var(--border-input);
    transform: translateY(-1px);
}

.sidebar-section-label {
    font-size: 0.7rem;
    font-weight: 700;
    color: var(--text-muted);
    text-transform: uppercase;
    letter-spacing: 0.12em;
    padding: 20px 12px 6px;
}

.sidebar-divider {
    border: none;
    border-top: 1px solid var(--border-light);
    margin: 12px 0 8px;
}

.claude-greeting {
    text-align: center;
    padding: 70px 20px 36px;
}

.claude-greeting h1 {
    font-family: 'Space Grotesk', sans-serif;
    font-size: 2.6rem;
    font-weight: 600;
    color: var(--accent-ink);
    margin: 0;
    letter-spacing: -0.02em;
}

.claude-greeting::after {
    content: "";
    display: block;
    margin: 18px auto 0;
    width: 120px;
    height: 3px;
    border-radius: 999px;
    background: linear-gradient(90deg, transparent, var(--accent-coral), transparent);
}

.stChatMessage {
    max-width: 740px;
    margin-left: auto;
    margin-right: auto;
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
    font-family: 'Source Sans 3', sans-serif !important;
    line-height: 1.65;
    font-size: 0.98rem;
}

.audit-note {
    color: #2d3741;
    font-size: 0.98rem;
    line-height: 1.7;
    font-family: 'Source Sans 3', sans-serif !important;
}

.audit-note strong {
    color: var(--accent-ink);
}

.model-badge {
    display: inline-flex;
    align-items: center;
    gap: 6px;
    background: var(--accent-ink);
    color: #f8f5f0;
    font-size: 0.8rem;
    font-weight: 600;
    padding: 6px 14px;
    border-radius: 999px;
    letter-spacing: 0.02em;
}

div[data-testid="stChatInput"] {
    max-width: 740px;
    margin: 0 auto;
}

div[data-testid="stChatInput"] > div {
    border-radius: var(--radius-lg) !important;
    border-color: var(--border-input) !important;
    box-shadow: var(--shadow-lg) !important;
    background: var(--bg-card) !important;
}

div[data-testid="stChatInput"] textarea {
    font-family: 'Source Sans 3', sans-serif !important;
    font-size: 1rem;
}

div[data-testid="stChatInput"] button {
    background: var(--accent-ink) !important;
    border: none !important;
    color: #f8f5f0 !important;
    border-radius: 999px !important;
    box-shadow: var(--shadow-sm) !important;
}

div[data-testid="stChatInput"] button:hover {
    background: var(--accent-coral) !important;
}

div[data-testid="stChatInput"] button svg {
    fill: #f8f5f0 !important;
}

div[data-testid="stFileUploader"] {
    max-width: 740px;
    margin: 0 auto;
}

div[data-testid="stFileUploader"] > div {
    border-radius: var(--radius-md) !important;
    border-color: var(--border-input) !important;
}

.stMarkdown, .stMarkdown p {
    font-family: 'Source Sans 3', sans-serif !important;
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

footer { visibility: hidden; }
#MainMenu { visibility: hidden; }

@keyframes fadeInUp {
    from { opacity: 0; transform: translateY(12px); }
    to   { opacity: 1; transform: translateY(0); }
}

.claude-greeting {
    animation: fadeInUp 0.55s ease-out;
}

.stChatMessage {
    animation: fadeInUp 0.35s ease-out;
}

::-webkit-scrollbar { width: 6px; }
::-webkit-scrollbar-track { background: transparent; }
::-webkit-scrollbar-thumb {
    background: #c7b9a7;
    border-radius: 3px;
}
::-webkit-scrollbar-thumb:hover { background: #b2a291; }

@media (max-width: 900px) {
    .claude-greeting h1 {
        font-size: 2rem;
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
