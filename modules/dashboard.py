"""
Suzanna's Business Dashboard Module

Password-protected dashboard for managing doTERRA business operations,
clients, team members, and marketing tools.
"""

import streamlit as st
import pandas as pd
import json
import os
from datetime import datetime
from typing import Dict, List, Optional
import logging
from .utils import (
    load_json,
    save_json,
    get_whatsapp_link,
    get_doterra_shop_link,
    sanitize_phone,
    generate_qr_code
)

logger = logging.getLogger(__name__)

# Configuration
DEFAULT_PASSWORD = "nosotras2024"
CLIENTS_FILE = "data/clients.json"
TEAM_FILE = "data/team.json"
EVENTS_FILE = "data/events.json"
DOTERRA_REFERRAL_ID = "8205768"
DOTERRA_QUICK_CLAIMS_PDF = "assets/docs/doTERRA_Quick_Claims_Guide.pdf"
DOCS_UPLOAD_DIR = "assets/docs/"


def check_authentication() -> bool:
    """
    Check if user is authenticated via session state.

    Returns:
        True if authenticated, False otherwise
    """
    if "dashboard_auth" not in st.session_state:
        st.session_state.dashboard_auth = False

    return st.session_state.dashboard_auth


def render_auth_form():
    """
    Render the authentication form.

    Returns:
        True if user entered correct password
    """
    st.markdown("### 🔐 Acceso al Dashboard")
    st.write("Por favor, ingresa tu contraseña para acceder al dashboard de negocio")

    password = st.text_input(
        "Contraseña",
        type="password",
        placeholder="Ingresa tu contraseña",
        key="dashboard_password_input"
    )

    col1, col2 = st.columns(2)
    with col1:
        if st.button("Ingresar", key="auth_submit"):
            if password == DEFAULT_PASSWORD:
                st.session_state.dashboard_auth = True
                st.success("¡Acceso concedido!")
                st.rerun()
            elif password:
                st.error("Contraseña incorrecta")
            else:
                st.warning("Por favor, ingresa una contraseña")

    with col2:
        st.write("")  # Spacing


def render_dashboard():
    """
    Main dashboard render function.

    Displays all dashboard sections if user is authenticated.
    """
    # Check authentication
    if not check_authentication():
        render_auth_form()
        return

    # Dashboard header with logout
    col1, col2 = st.columns([3, 1])
    with col1:
        st.title("💼 Dashboard de Negocio - Suzanna")
    with col2:
        if st.button("🚪 Salir", key="logout"):
            st.session_state.dashboard_auth = False
            st.rerun()

    # Tabs for different sections
    tabs = st.tabs([
        "📊 Resumen",
        "📄 Documentos",
        "👥 Clientes",
        "👨‍💼 Equipo",
        "📅 Eventos",
        "📢 Marketing"
    ])

    with tabs[0]:
        render_business_summary()

    with tabs[1]:
        render_documentation()

    with tabs[2]:
        render_client_management()

    with tabs[3]:
        render_team_tracking()

    with tabs[4]:
        render_events_calendar()

    with tabs[5]:
        render_marketing_tools()


def render_business_summary():
    """Render the Business Summary section."""
    st.header("📊 Resumen del Negocio")

    col1, col2, col3, col4 = st.columns(4)

    with col1:
        # In a real app, connect to doTERRA API
        st.metric(
            label="Total Clientes",
            value=24,
            delta=3,
            delta_color="normal"
        )

    with col2:
        st.metric(
            label="Consultas Este Mes",
            value=12,
            delta=2,
            delta_color="normal"
        )

    with col3:
        st.metric(
            label="Volumen Personal (PV)",
            value=450,
            delta=50,
            delta_color="normal"
        )

    with col4:
        st.metric(
            label="Meta Mensual",
            value="95%",
            delta=5,
            delta_color="normal"
        )

    st.divider()

    # Info box
    st.info(
        "ℹ️ **Nota:** Para ver datos reales, conecta tu cuenta de doTERRA. "
        "Actualmente se muestran datos de ejemplo."
    )

    # Sample recent activity
    st.subheader("Actividad Reciente")
    activity_data = {
        "Fecha": ["2026-03-26", "2026-03-25", "2026-03-24"],
        "Evento": [
            "Nuevo cliente: María García",
            "Consulta sobre Lavender",
            "Orden completada: $150 USD"
        ],
        "Estado": ["✓ Completado", "En progreso", "✓ Completado"]
    }
    st.dataframe(pd.DataFrame(activity_data), use_container_width=True)


def render_documentation():
    """Render the Documentation section."""
    st.header("📄 Documentación Importante")

    col1, col2 = st.columns([2, 1])

    with col1:
        st.subheader("Documentos Disponibles")

        # Quick Claims Guide
        if os.path.exists(DOTERRA_QUICK_CLAIMS_PDF):
            with open(DOTERRA_QUICK_CLAIMS_PDF, "rb") as pdf_file:
                st.download_button(
                    label="📥 Descargar: doTERRA Quick Claims Guide",
                    data=pdf_file,
                    file_name="doTERRA_Quick_Claims_Guide.pdf",
                    mime="application/pdf"
                )
        else:
            st.warning("Archivo Quick Claims Guide no disponible")

        st.divider()

        # List uploaded documents
        st.subheader("Mis Documentos")

        os.makedirs(DOCS_UPLOAD_DIR, exist_ok=True)
        doc_files = [f for f in os.listdir(DOCS_UPLOAD_DIR) if f.endswith((".pdf", ".docx", ".txt"))]

        if doc_files:
            for doc_file in doc_files:
                doc_path = os.path.join(DOCS_UPLOAD_DIR, doc_file)
                file_size = os.path.getsize(doc_path) / 1024  # KB

                col1, col2 = st.columns([3, 1])
                with col1:
                    st.write(f"📄 {doc_file} ({file_size:.1f} KB)")
                with col2:
                    with open(doc_path, "rb") as f:
                        st.download_button(
                            label="📥",
                            data=f,
                            file_name=doc_file,
                            key=f"download_{doc_file}"
                        )
        else:
            st.caption("No hay documentos cargados aún")

    with col2:
        st.subheader("Cargar Documento")
        uploaded_file = st.file_uploader(
            "Sube un documento",
            type=["pdf", "docx", "txt"],
            key="doc_uploader"
        )

        if uploaded_file:
            os.makedirs(DOCS_UPLOAD_DIR, exist_ok=True)
            file_path = os.path.join(DOCS_UPLOAD_DIR, uploaded_file.name)

            with open(file_path, "wb") as f:
                f.write(uploaded_file.getbuffer())

            st.success(f"✓ {uploaded_file.name} guardado")
            st.rerun()


def render_client_management():
    """Render the Client Management section."""
    st.header("👥 Gestión de Clientes")

    # Load clients
    clients = load_json(CLIENTS_FILE) or []

    # Add new client
    with st.expander("➕ Agregar Nuevo Cliente", expanded=False):
        with st.form("new_client_form"):
            col1, col2 = st.columns(2)

            with col1:
                nombre = st.text_input("Nombre completo")
                whatsapp = st.text_input("WhatsApp (formato: +XX XXXXXXXXX)")

            with col2:
                email = st.text_input("Correo electrónico")
                fecha_contacto = st.date_input("Fecha de contacto")

            productos_interes = st.multiselect(
                "Productos de interés",
                [
                    "Lavender",
                    "Peppermint",
                    "Frankincense",
                    "Lemon",
                    "DigestZen",
                    "Balance",
                    "On Guard",
                    "Otro"
                ]
            )

            notas = st.text_area("Notas")

            if st.form_submit_button("Guardar Cliente"):
                if nombre and (whatsapp or email):
                    new_client = {
                        "id": len(clients) + 1,
                        "nombre": nombre,
                        "whatsapp": sanitize_phone(whatsapp) if whatsapp else None,
                        "email": email,
                        "productos_interes": productos_interes,
                        "fecha_contacto": fecha_contacto.isoformat(),
                        "notas": notas,
                        "fecha_creacion": datetime.now().isoformat()
                    }
                    clients.append(new_client)
                    save_json(CLIENTS_FILE, clients)
                    st.success("✓ Cliente agregado")
                    st.rerun()
                else:
                    st.error("Por favor completa nombre y al menos WhatsApp o email")

    # Search and filter
    st.subheader("Clientes Registrados")

    col1, col2, col3 = st.columns([2, 1, 1])

    with col1:
        search_term = st.text_input("🔍 Buscar cliente por nombre")
    with col2:
        product_filter = st.selectbox(
            "Filtrar por producto",
            ["Todos", "Lavender", "Peppermint", "Frankincense", "Lemon", "DigestZen", "Balance", "On Guard"],
            key="product_filter_clients"
        )

    # Filter clients
    filtered_clients = clients
    if search_term:
        filtered_clients = [c for c in filtered_clients if search_term.lower() in c.get("nombre", "").lower()]
    if product_filter != "Todos":
        filtered_clients = [c for c in filtered_clients if product_filter in c.get("productos_interes", [])]

    # Display clients table
    if filtered_clients:
        for client in filtered_clients:
            with st.container(border=True):
                col1, col2, col3 = st.columns([2, 1, 1])

                with col1:
                    st.write(f"**{client['nombre']}**")
                    if client.get("email"):
                        st.caption(f"📧 {client['email']}")
                    if client.get("productos_interes"):
                        st.caption(f"Interesado en: {', '.join(client['productos_interes'])}")
                    if client.get("notas"):
                        st.caption(f"Notas: {client['notas']}")

                with col2:
                    if client.get("whatsapp"):
                        whatsapp_link = get_whatsapp_link(
                            client["whatsapp"],
                            f"Hola {client['nombre'].split()[0]}, te escribo desde Nosotras Naturales"
                        )
                        st.markdown(f"[💬 WhatsApp]({whatsapp_link})")

                with col3:
                    if st.button("🗑️ Eliminar", key=f"delete_client_{client['id']}"):
                        clients = [c for c in clients if c["id"] != client["id"]]
                        save_json(CLIENTS_FILE, clients)
                        st.success("Cliente eliminado")
                        st.rerun()
    else:
        st.info("No hay clientes registrados")

    # Client stats
    st.divider()
    st.subheader("Estadísticas")
    col1, col2, col3 = st.columns(3)

    with col1:
        st.metric("Total Clientes", len(clients))
    with col2:
        with_whatsapp = sum(1 for c in clients if c.get("whatsapp"))
        st.metric("Con WhatsApp", with_whatsapp)
    with col3:
        with_email = sum(1 for c in clients if c.get("email"))
        st.metric("Con Email", with_email)


def render_team_tracking():
    """Render the Team Tracking section."""
    st.header("👨‍💼 Seguimiento de Equipo")

    # Load team members
    team = load_json(TEAM_FILE) or []

    # Add new team member
    with st.expander("➕ Agregar Miembro del Equipo", expanded=False):
        with st.form("new_team_form"):
            col1, col2 = st.columns(2)

            with col1:
                nombre = st.text_input("Nombre completo")
                rango = st.selectbox(
                    "Rango",
                    ["Distribuidor", "Líder", "Ejecutivo", "Oro", "Platino"]
                )

            with col2:
                pv = st.number_input("Volumen Personal (PV)", min_value=0, step=10)
                estado = st.selectbox("Estado", ["Activo", "Inactivo", "En pausa"])

            fecha_inscripcion = st.date_input("Fecha de inscripción")
            notas = st.text_area("Notas adicionales")

            if st.form_submit_button("Guardar Miembro"):
                if nombre:
                    new_member = {
                        "id": len(team) + 1,
                        "nombre": nombre,
                        "rango": rango,
                        "pv": int(pv),
                        "estado": estado,
                        "fecha_inscripcion": fecha_inscripcion.isoformat(),
                        "notas": notas,
                        "fecha_creacion": datetime.now().isoformat()
                    }
                    team.append(new_member)
                    save_json(TEAM_FILE, team)
                    st.success("✓ Miembro agregado")
                    st.rerun()
                else:
                    st.error("Por favor ingresa un nombre")

    # Display team
    st.subheader("Miembros del Equipo")

    if team:
        # Team table
        team_df = pd.DataFrame([
            {
                "Nombre": m["nombre"],
                "Rango": m["rango"],
                "PV": m["pv"],
                "Estado": m["estado"],
                "Inscripción": m["fecha_inscripcion"][:10]
            }
            for m in team
        ])

        st.dataframe(team_df, use_container_width=True)

        # Individual team member cards
        for member in team:
            with st.container(border=True):
                col1, col2, col3 = st.columns([2, 1, 1])

                with col1:
                    st.write(f"**{member['nombre']}**")
                    st.caption(f"Rango: {member['rango']}")
                    if member.get("notas"):
                        st.caption(f"Notas: {member['notas']}")

                with col2:
                    st.metric("PV", member["pv"])
                    status_color = "🟢" if member["estado"] == "Activo" else "🔴" if member["estado"] == "Inactivo" else "🟡"
                    st.write(f"{status_color} {member['estado']}")

                with col3:
                    if st.button("✏️ Editar", key=f"edit_team_{member['id']}"):
                        st.session_state[f"edit_team_{member['id']}"] = True

                    if st.button("🗑️ Eliminar", key=f"delete_team_{member['id']}"):
                        team = [m for m in team if m["id"] != member["id"]]
                        save_json(TEAM_FILE, team)
                        st.success("Miembro eliminado")
                        st.rerun()
    else:
        st.info("No hay miembros del equipo registrados")

    # Team stats
    st.divider()
    st.subheader("Estadísticas del Equipo")
    col1, col2, col3 = st.columns(3)

    with col1:
        st.metric("Total Miembros", len(team))
    with col2:
        total_pv = sum(m["pv"] for m in team)
        st.metric("PV Total", total_pv)
    with col3:
        activos = sum(1 for m in team if m["estado"] == "Activo")
        st.metric("Miembros Activos", activos)


def render_events_calendar():
    """Render the Events Calendar section."""
    st.header("📅 Próximas Actividades")

    # Load events
    events = load_json(EVENTS_FILE) or []

    # Add new event
    with st.expander("➕ Agregar Evento", expanded=False):
        with st.form("new_event_form"):
            col1, col2 = st.columns(2)

            with col1:
                titulo = st.text_input("Título del evento")
                tipo_evento = st.selectbox(
                    "Tipo de evento",
                    ["Clase Online", "Reunión Equipo", "Evento doTERRA", "Seguimiento Cliente", "Otro"]
                )

            with col2:
                fecha = st.date_input("Fecha")
                hora = st.time_input("Hora")

            descripcion = st.text_area("Descripción")
            ubicacion = st.text_input("Ubicación (opcional)")

            if st.form_submit_button("Guardar Evento"):
                if titulo and fecha:
                    new_event = {
                        "id": len(events) + 1,
                        "titulo": titulo,
                        "tipo": tipo_evento,
                        "fecha": fecha.isoformat(),
                        "hora": str(hora),
                        "descripcion": descripcion,
                        "ubicacion": ubicacion,
                        "fecha_creacion": datetime.now().isoformat()
                    }
                    events.append(new_event)
                    save_json(EVENTS_FILE, events)
                    st.success("✓ Evento agregado")
                    st.rerun()
                else:
                    st.error("Por favor completa título y fecha")

    # Display events
    st.subheader("Eventos Próximos")

    # Sort events by date
    sorted_events = sorted(events, key=lambda e: e.get("fecha", ""))

    if sorted_events:
        for event in sorted_events:
            with st.container(border=True):
                col1, col2, col3 = st.columns([2, 1, 1])

                with col1:
                    st.write(f"**{event['titulo']}**")
                    st.caption(f"📍 {event['tipo']}")
                    if event.get("ubicacion"):
                        st.caption(f"Ubicación: {event['ubicacion']}")
                    if event.get("descripcion"):
                        st.caption(f"Descripción: {event['descripcion']}")

                with col2:
                    st.write(f"📅 {event['fecha']}")
                    st.write(f"⏰ {event['hora']}")

                with col3:
                    if st.button("🗑️ Eliminar", key=f"delete_event_{event['id']}"):
                        events = [e for e in events if e["id"] != event["id"]]
                        save_json(EVENTS_FILE, events)
                        st.success("Evento eliminado")
                        st.rerun()
    else:
        st.info("No hay eventos programados")


def render_marketing_tools():
    """Render the Marketing Tools section."""
    st.header("📢 Herramientas de Marketing")

    tabs = st.tabs(["🔗 Enlaces", "📝 Plantillas", "🎯 QR Code"])

    with tabs[0]:
        st.subheader("Enlaces Importantes")

        col1, col2 = st.columns(2)

        with col1:
            st.write("**Mi Tienda doTERRA**")
            referral_link = get_doterra_shop_link("EC", DOTERRA_REFERRAL_ID)  # Default to Ecuador
            st.code(referral_link, language="url")
            st.markdown(f"[🛍️ Abrir tienda]({referral_link})")

        with col2:
            st.write("**Material de Marketing doTERRA**")
            st.markdown("[📚 Digital Marketing Kit](https://www.doterra.com/US/en/marketing-resources)")
            st.markdown("[🎬 Videos de Productos](https://www.doterra.com/US/en/videos)")

    with tabs[1]:
        st.subheader("Plantillas de Redes Sociales")

        templates = [
            {
                "titulo": "Presentación Lavender",
                "contenido": """✨ ¿Sabías que Lavender es mucho más que un aroma relajante?

🌿 Lavender ayuda a:
• Calmar la mente y el cuerpo
• Mejorar la calidad del sueño
• Apoyar la piel saludable

💜 Disponible en múltiples presentaciones:
✓ Aceite esencial puro
✓ Touch (diluido)
✓ Productos de cuidado personal

¿Quieres aprender más? Contáctame 💬"""
            },
            {
                "titulo": "Oferta Especial",
                "contenido": """🎉 ¡OFERTA ESPECIAL ESTA SEMANA!

Obtén 20% de descuento en tu primera compra de doTERRA.

✨ Productos destacados:
• Lavender - Relajación
• Peppermint - Energía
• Frankincense - Bienestar

¡Aprovecha esta oportunidad! Solo válido esta semana.

Haz tu pedido hoy 👇"""
            },
            {
                "titulo": "Beneficios doTERRA",
                "contenido": """💡 ¿Por qué elegir doTERRA?

🌍 Sourcing ético - Ingredientes de la más alta calidad
✅ Probado en laboratorio - Pureza garantizada
🏆 Estándar Cptg - Control de calidad superior
🌱 Soporte agrícola - Ayudamos a agricultores

Únete a miles de personas que ya confían en doTERRA.

¡Contáctame para más información! 💬"""
            }
        ]

        for template in templates:
            with st.container(border=True):
                st.write(f"**{template['titulo']}**")
                st.text_area(
                    "Contenido",
                    value=template["contenido"],
                    height=150,
                    key=f"template_{template['titulo']}"
                )

                col1, col2 = st.columns(2)
                with col1:
                    if st.button("📋 Copiar", key=f"copy_{template['titulo']}"):
                        st.success("Copiado a portapapeles")

    with tabs[2]:
        st.subheader("Generador de QR Code")
        st.write("Genera un código QR para tu enlace de referencia")

        referral_link = get_doterra_shop_link("EC", DOTERRA_REFERRAL_ID)

        try:
            qr_image = generate_qr_code(referral_link)
            st.image(qr_image, caption="Tu código QR de referencia")

            # Download button
            st.download_button(
                label="📥 Descargar QR Code",
                data=qr_image,
                file_name="referral_qr.png",
                mime="image/png"
            )
        except Exception as e:
            st.error(f"Error generando QR: {str(e)}")

        st.divider()
        st.write("**Usa este código QR en:**")
        st.write("• Posts de redes sociales")
        st.write("• Materiales impresos")
        st.write("• Tu firma de email")
        st.write("• Mensajes de WhatsApp")


if __name__ == "__main__":
    render_dashboard()
