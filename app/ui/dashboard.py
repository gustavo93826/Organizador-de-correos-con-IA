"""Interfaz Streamlit: bandeja organizada por categoría/prioridad, con
resumen visible y borrador de respuesta editable.

Consume la API de FastAPI vía HTTP -- no accede a la base de
datos directamente, para mantener una única fuente de verdad.

Uso:
    uv run streamlit run app/ui/dashboard.py
"""
import os

import requests
import streamlit as st

API_BASE_URL = os.getenv("API_BASE_URL", "http://127.0.0.1:8000")

EMOJI_PRIORIDAD = {"alta": "🔴", "media": "🟡", "baja": "🟢", None: "⚪"}

st.set_page_config(page_title="Organizador de correos con IA", layout="wide")
st.title("📬 Organizador de correos con IA")


def obtener_emails(categoria, prioridad, estado) -> list[dict]:
    params = {k: v for k, v in {"categoria": categoria, "prioridad": prioridad, "estado": estado}.items() if v}
    respuesta = requests.get(f"{API_BASE_URL}/emails", params=params, timeout=10)
    respuesta.raise_for_status()
    return respuesta.json()


def obtener_detalle(email_id: int) -> dict:
    respuesta = requests.get(f"{API_BASE_URL}/emails/{email_id}", timeout=10)
    respuesta.raise_for_status()
    return respuesta.json()


def guardar_borrador(email_id: int, texto: str) -> None:
    respuesta = requests.patch(
        f"{API_BASE_URL}/emails/{email_id}/borrador", json={"borrador": texto}, timeout=10
    )
    respuesta.raise_for_status()


def reprocesar(email_id: int) -> None:
    respuesta = requests.post(f"{API_BASE_URL}/emails/{email_id}/reprocesar", timeout=10)
    respuesta.raise_for_status()


# --- Filtros en la barra lateral ---
st.sidebar.header("Filtros")
categoria = st.sidebar.selectbox(
    "Categoría",
    ["", "trabajo", "personal", "facturas", "promociones", "spam", "otros"],
    format_func=lambda v: "Todas" if v == "" else v.capitalize(),
)
prioridad = st.sidebar.selectbox(
    "Prioridad",
    ["", "alta", "media", "baja"],
    format_func=lambda v: "Todas" if v == "" else v.capitalize(),
)
estado = st.sidebar.selectbox(
    "Estado",
    ["completado", "", "pendiente", "procesando", "error"],
    format_func=lambda v: "Todos" if v == "" else v.capitalize(),
)

if st.sidebar.button("🔄 Actualizar"):
    st.rerun()

# --- Cuerpo principal ---
try:
    emails = obtener_emails(categoria or None, prioridad or None, estado or None)
except requests.exceptions.ConnectionError:
    st.error(
        "No se pudo conectar con la API. ¿Está corriendo? "
        "`uv run uvicorn app.main:app --reload`"
    )
    st.stop()

if not emails:
    st.info("No hay correos que coincidan con estos filtros.")
    st.stop()

st.caption(f"{len(emails)} correo(s) encontrado(s)")

for item in emails:
    detalle = obtener_detalle(item["id"])
    emoji = EMOJI_PRIORIDAD.get(detalle["prioridad"], "⚪")

    titulo = f"{emoji} {detalle['asunto']} — {detalle['remitente']}"
    with st.expander(titulo):
        col_info, col_estado = st.columns([3, 1])
        with col_info:
            st.write(f"**Categoría:** {detalle['categoria'] or '—'}")
            st.write(f"**Resumen:** {detalle['resumen'] or '(sin resumen aún)'}")
        with col_estado:
            st.write(f"**Estado:** {detalle['estado_procesamiento']}")

        borrador_editado = st.text_area(
            "Borrador de respuesta",
            value=detalle["borrador_respuesta"] or "",
            key=f"borrador_{detalle['id']}",
            height=120,
        )

        col1, col2 = st.columns(2)
        with col1:
            if st.button("💾 Guardar borrador", key=f"guardar_{detalle['id']}"):
                guardar_borrador(detalle["id"], borrador_editado)
                st.success("Borrador actualizado.")
        with col2:
            if st.button("🔁 Reprocesar con IA", key=f"reprocesar_{detalle['id']}"):
                reprocesar(detalle["id"])
                st.info("Reprocesamiento iniciado en segundo plano.")
                st.rerun()