"""
Nosotras Naturales - Spanish-language doTERRA Wellness Web App
Created by Suzanna Valles
doTERRA Wellness Advocate ID: 8205768
WhatsApp: +593 98 494 9487
Instagram: @nosotrasnaturales
"""

import streamlit as st
import json
import os
from pathlib import Path
from datetime import datetime

# ============================================
# PAGE CONFIGURATION
# ============================================

st.set_page_config(
    page_title="Nosotras Naturales - Bienestar con doTERRA",
    page_icon="🌿",
    layout="wide",
    initial_sidebar_state="expanded",
    menu_items={
        "About": "Nosotras Naturales - Tu guía natural de bienestar con aceites esenciales dōTERRA"
    }
)

# ============================================
# CONSTANTS
# ============================================

# Brand Information
ADVOCATE_ID = "8205768"
WHATSAPP_NUMBER = "593984949487"
WHATSAPP_DISPLAY = "+593 98 494 9487"
INSTAGRAM_HANDLE = "@nosotrasnaturales"
DOTERRA_STORE_URL = "https://www.doterra.com/EC/es_EC"
DOTERRA_SHOP_URL = f"https://www.doterra.com/EC/es_EC/shop?referralId={ADVOCATE_ID}"

# Color Palette
COLORS = {
    "primary_green": "#7C9070",
    "warm_beige": "#D4C5A9",
    "terracotta": "#C67B4F",
    "cream_bg": "#FDF8F0",
    "dark_brown": "#3D3229",
    "light_sage": "#E8EDE5",
    "accent_gold": "#B8965A",
    "white": "#FFFFFF",
    "whatsapp_green": "#25D366"
}

# FDA Disclaimer
FDA_DISCLAIMER = """
**Aviso Legal:** Estas declaraciones no han sido evaluadas por la Administración de Alimentos y Medicamentos (FDA).
Estos productos no tienen el propósito de diagnosticar, tratar, curar o evitar ninguna enfermedad.
Consulta a un profesional de la salud antes de usar cualquier producto.
"""

# ============================================
# UTILITY FUNCTIONS
# ============================================

@st.cache_resource
def load_css():
    """Load custom CSS from assets/style.css"""
    css_path = Path("assets/style.css")
    if css_path.exists():
        with open(css_path, "r", encoding="utf-8") as f:
            st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)

@st.cache_data
def load_products():
    """Load products from data/products.json"""
    products_path = Path("data/products.json")
    if products_path.exists():
        with open(products_path, "r", encoding="utf-8") as f:
            return json.load(f)
    return []

@st.cache_data
def load_symptom_flow():
    """Load symptom checker flow from data/symptom_flow.json"""
    symptom_path = Path("data/symptom_flow.json")
    if symptom_path.exists():
        with open(symptom_path, "r", encoding="utf-8") as f:
            return json.load(f)
    return {}

def get_whatsapp_link(message=""):
    """Generate WhatsApp contact link"""
    if message:
        return f"https://wa.me/{WHATSAPP_NUMBER}?text={message.replace(' ', '%20')}"
    return f"https://wa.me/{WHATSAPP_NUMBER}"

def display_whatsapp_button():
    """Display floating WhatsApp button"""
    whatsapp_html = f"""
    <a href="https://wa.me/{WHATSAPP_NUMBER}?text=Hola%20Suzanna"
       class="whatsapp-button"
       target="_blank"
       title="Contactar por WhatsApp">
        <span class="whatsapp-icon">💬</span>
    </a>
    """
    st.markdown(whatsapp_html, unsafe_allow_html=True)

def display_disclaimer():
    """Display FDA disclaimer banner"""
    st.markdown(
        f"""
        <div class="disclaimer">
            <div class="disclaimer-title">⚠️ Aviso Importante</div>
            <div class="disclaimer-text">{FDA_DISCLAIMER}</div>
        </div>
        """,
        unsafe_allow_html=True
    )

def initialize_session_state():
    """Initialize session state variables"""
    if "page" not in st.session_state:
        st.session_state.page = "home"
    if "symptom_flow_active" not in st.session_state:
        st.session_state.symptom_flow_active = False
    if "current_symptom_question" not in st.session_state:
        st.session_state.current_symptom_question = None
    if "selected_answers" not in st.session_state:
        st.session_state.selected_answers = []
    if "dashboard_authenticated" not in st.session_state:
        st.session_state.dashboard_authenticated = False

# ============================================
# PAGE COMPONENTS
# ============================================

def page_home():
    """Home page (Inicio)"""

    # Hero Section
    st.markdown(
        """
        <h1 style="text-align: center; margin-bottom: 0.5rem;">🌿 Nosotras Naturales</h1>
        <p style="text-align: center; font-size: 1.3rem; color: #7C9070; margin-bottom: 2rem;">
        Tu guía natural de bienestar con aceites esenciales dōTERRA
        </p>
        """,
        unsafe_allow_html=True
    )

    # Main CTA Button
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        if st.button("🤔 ¿Cómo te sientes hoy?", key="home_symptom_btn", use_container_width=True):
            st.session_state.page = "symptom_checker"
            st.rerun()

    st.markdown("<div style='margin: 2rem 0;'></div>", unsafe_allow_html=True)

    # Feature Cards Section
    st.markdown("<h2 style='text-align: center; border: none; padding: 0;'>Nuestros Servicios</h2>",
                unsafe_allow_html=True)

    col1, col2, col3 = st.columns(3, gap="medium")

    with col1:
        st.markdown(
            """
            <div class="card" style="text-align: center;">
                <h3 style="color: #7C9070; border: none;">📋 Guía Personalizada</h3>
                <p>Descubre qué aceites esenciales son perfectos para tus necesidades específicas
                con nuestro cuestionario inteligente de bienestar.</p>
            </div>
            """,
            unsafe_allow_html=True
        )

    with col2:
        st.markdown(
            """
            <div class="card" style="text-align: center;">
                <h3 style="color: #7C9070; border: none;">🌱 Productos Naturales</h3>
                <p>Explora nuestra selección curada de aceites esenciales de grado terapéutico
                certificados por doTERRA.</p>
            </div>
            """,
            unsafe_allow_html=True
        )

    with col3:
        st.markdown(
            """
            <div class="card" style="text-align: center;">
                <h3 style="color: #7C9070; border: none;">👩‍💼 Asesoría Personal</h3>
                <p>Conecta directamente con Suzanna para consultas personalizadas
                y recomendaciones específicas.</p>
            </div>
            """,
            unsafe_allow_html=True
        )

    st.markdown("<div style='margin: 3rem 0;'></div>", unsafe_allow_html=True)

    # Welcome Section
    st.markdown(
        """
        <div class="card">
            <h3>✨ Bienvenida a tu Viaje de Bienestar</h3>
            <p>
            En Nosotras Naturales, creemos en el poder de la naturaleza para apoyar tu bienestar integral.
            Con más de X años de experiencia como Wellness Advocate de doTERRA, estoy dedicada a ayudarte
            a descubrir cómo los aceites esenciales puros y de grado terapéutico pueden mejorar tu calidad de vida.
            </p>
            <p>
            Cada producto ha sido cuidadosamente seleccionado y probado para garantizar la máxima pureza y eficacia.
            Ya sea que busques mejorar tu sueño, aumentar tu energía, o simplemente crear un ambiente más armonioso,
            tenemos la solución perfecta para ti.
            </p>
        </div>
        """,
        unsafe_allow_html=True
    )

    st.markdown("<div style='margin: 2rem 0;'></div>", unsafe_allow_html=True)

    # Quick Links Section
    st.markdown("<h3>Accesos Rápidos</h3>", unsafe_allow_html=True)

    col1, col2, col3, col4 = st.columns(4)

    with col1:
        if st.button("📦 Ver Productos", key="home_products_btn", use_container_width=True):
            st.session_state.page = "products"
            st.rerun()

    with col2:
        if st.button("🌍 doTERRA América", key="home_latam_btn", use_container_width=True):
            st.session_state.page = "latam"
            st.rerun()

    with col3:
        if st.button("💼 Únete al Equipo", key="home_team_btn", use_container_width=True):
            st.session_state.page = "join_team"
            st.rerun()

    with col4:
        if st.button("💬 Contactar", key="home_contact_btn", use_container_width=True):
            st.markdown(get_whatsapp_link("Hola Suzanna, me interesa saber más sobre los productos"),
                       unsafe_allow_html=True)

    st.markdown("<div style='margin: 3rem 0;'></div>", unsafe_allow_html=True)

    # Disclaimer
    display_disclaimer()


def page_symptom_checker():
    """Symptom Checker page (Guía de Bienestar)"""

    st.markdown("<h1>🌿 Guía de Bienestar Personalizada</h1>", unsafe_allow_html=True)

    st.markdown(
        """
        Responde algunas preguntas simples sobre cómo te sientes y te recomendaremos
        los productos de doTERRA más adecuados para ti.
        """,
        unsafe_allow_html=True
    )

    symptom_data = load_symptom_flow()

    if not symptom_data:
        st.warning("📖 El flujo de síntomas aún no está disponible. Por favor, contacta con Suzanna.")
        if st.button("Ir al Inicio", key="symptom_home_btn"):
            st.session_state.page = "home"
            st.rerun()
        return

    # Placeholder for symptom flow implementation
    categories = symptom_data.get("categories", [])

    st.markdown("<h3>Selecciona una categoría:</h3>", unsafe_allow_html=True)

    col_count = 2
    cols = st.columns(col_count)

    for idx, category in enumerate(categories):
        col = cols[idx % col_count]
        with col:
            category_name = category.get("nombre", "")
            category_icon = category.get("icono", "")
            category_desc = category.get("descripcion", "")

            st.markdown(
                f"""
                <div class="card" style="cursor: pointer; text-align: center;">
                    <h3>{category_icon} {category_name}</h3>
                    <p>{category_desc}</p>
                </div>
                """,
                unsafe_allow_html=True
            )

            if st.button("Explorar", key=f"explore_{category.get('id', '')}"):
                st.info(f"Guía para {category_name} en desarrollo. Por favor, contacta con Suzanna para asesoría personalizada.")

    st.markdown("<div style='margin: 2rem 0;'></div>", unsafe_allow_html=True)

    # Contact Suzanna CTA
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        st.markdown(
            f"""
            <div class="cta-card">
                <div class="cta-title">¿Necesitas Asesoría Personalizada?</div>
                <div class="cta-description">
                Contacta directamente con Suzanna para una recomendación personalizada basada en tus necesidades específicas.
                </div>
            </div>
            """,
            unsafe_allow_html=True
        )
        if st.button("💬 Contactar a Suzanna por WhatsApp", key="symptom_contact_btn", use_container_width=True):
            st.markdown(
                f'<a href="{get_whatsapp_link("Me gustaría una asesoría personalizada de bienestar")}" target="_blank">Abrir WhatsApp</a>',
                unsafe_allow_html=True
            )

    st.markdown("<div style='margin: 2rem 0;'></div>", unsafe_allow_html=True)

    if st.button("← Volver al Inicio", key="symptom_back_btn"):
        st.session_state.page = "home"
        st.rerun()


def page_products():
    """Products page (Productos)"""

    st.markdown("<h1>📦 Productos doTERRA</h1>", unsafe_allow_html=True)

    products = load_products()

    if not products:
        st.error("❌ No se pudieron cargar los productos. Por favor, intenta más tarde.")
        if st.button("← Volver al Inicio", key="products_home_btn"):
            st.session_state.page = "home"
            st.rerun()
        return

    # Extract unique categories
    all_categories = set()
    for product in products:
        categories = product.get("categoria", [])
        all_categories.update(categories)
    all_categories = sorted(list(all_categories))

    # Sidebar Filters
    st.sidebar.markdown("<h3>🔍 Filtros</h3>", unsafe_allow_html=True)

    # Category filter
    selected_categories = st.sidebar.multiselect(
        "Categorías",
        options=all_categories,
        default=[]
    )

    # Price range filter
    prices = [p.get("precio_usd", 0) for p in products]
    min_price, max_price = st.sidebar.slider(
        "Rango de Precio (USD)",
        min_value=int(min(prices)) if prices else 0,
        max_value=int(max(prices)) if prices else 100,
        value=(int(min(prices)) if prices else 0, int(max(prices)) if prices else 100),
        step=5
    )

    # Search filter
    search_term = st.sidebar.text_input(
        "Buscar producto",
        placeholder="Ej: Lavanda, Menta..."
    )

    # Apply filters
    filtered_products = products

    if selected_categories:
        filtered_products = [
            p for p in filtered_products
            if any(cat in selected_categories for cat in p.get("categoria", []))
        ]

    filtered_products = [
        p for p in filtered_products
        if min_price <= p.get("precio_usd", 0) <= max_price
    ]

    if search_term:
        search_lower = search_term.lower()
        filtered_products = [
            p for p in filtered_products
            if search_lower in p.get("nombre", "").lower()
            or search_lower in p.get("descripcion", "").lower()
        ]

    # Display results count
    st.markdown(f"**Mostrando {len(filtered_products)} de {len(products)} productos**", unsafe_allow_html=True)

    st.markdown("<div style='margin: 1.5rem 0;'></div>", unsafe_allow_html=True)

    # Product Grid
    cols_per_row = 3
    for idx, product in enumerate(filtered_products):
        if idx % cols_per_row == 0:
            cols = st.columns(cols_per_row, gap="medium")

        col = cols[idx % cols_per_row]

        with col:
            product_id = product.get("id", "")
            product_name = product.get("nombre", "Sin nombre")
            product_desc = product.get("descripcion", "")
            product_price = product.get("precio_usd", 0)
            product_pv = product.get("pv", 0)

            # Truncate description
            if len(product_desc) > 100:
                product_desc = product_desc[:100] + "..."

            product_html = f"""
            <div class="product-card">
                <div class="product-image" style="background: linear-gradient(135deg, #E8EDE5 0%, #FDF8F0 100%); display: flex; align-items: center; justify-content: center;">
                    <span style="font-size: 3rem;">🌿</span>
                </div>
                <div class="product-info">
                    <div class="product-title">{product_name}</div>
                    <div class="product-description">{product_desc}</div>
                    <div class="product-price">${product_price:.2f}</div>
                    <div class="price-badge">PV: {product_pv}</div>
                </div>
            </div>
            """

            st.markdown(product_html, unsafe_allow_html=True)

            # Action buttons
            col_a, col_b = st.columns(2)

            with col_a:
                if st.button("🛒 Comprar", key=f"buy_{product_id}", use_container_width=True):
                    st.markdown(
                        f'<a href="{DOTERRA_SHOP_URL}" target="_blank">Ir a doTERRA</a>',
                        unsafe_allow_html=True
                    )

            with col_b:
                if st.button("💬 Consultar", key=f"consult_{product_id}", use_container_width=True):
                    st.markdown(
                        f'<a href="{get_whatsapp_link(f"Me interesa el producto: {product_name}")}" target="_blank">WhatsApp</a>',
                        unsafe_allow_html=True
                    )

    st.markdown("<div style='margin: 3rem 0;'></div>", unsafe_allow_html=True)

    # Back button
    if st.button("← Volver al Inicio", key="products_back_btn"):
        st.session_state.page = "home"
        st.rerun()

    display_disclaimer()


def page_latam():
    """doTERRA Latinoamérica page"""

    st.markdown("<h1>🌎 doTERRA América Latina</h1>", unsafe_allow_html=True)

    st.markdown(
        """
        Explora nuestros productos y oportunidades en toda América Latina.
        doTERRA está comprometida con traer los mejores aceites esenciales
        de grado terapéutico a toda la región.
        """,
        unsafe_allow_html=True
    )

    st.markdown("<div style='margin: 2rem 0;'></div>", unsafe_allow_html=True)

    # Country cards
    countries = [
        {
            "flag": "🇪🇨",
            "name": "Ecuador",
            "details": "Tu tienda local",
            "url": f"{DOTERRA_STORE_URL}/shop?referralId={ADVOCATE_ID}"
        },
        {
            "flag": "🇵🇪",
            "name": "Perú",
            "details": "Bienestar natural",
            "url": "https://www.doterra.com/PE/es_PE/shop"
        },
        {
            "flag": "🇨🇴",
            "name": "Colombia",
            "details": "Aceites esenciales puros",
            "url": "https://www.doterra.com/CO/es_CO/shop"
        },
        {
            "flag": "🇧🇴",
            "name": "Bolivia",
            "details": "Productos certificados",
            "url": "https://www.doterra.com/BO/es_BO/shop"
        },
    ]

    col_count = 2
    cols = st.columns(col_count, gap="medium")

    for idx, country in enumerate(countries):
        col = cols[idx % col_count]
        with col:
            st.markdown(
                f"""
                <div class="country-card">
                    <div class="country-flag">{country['flag']}</div>
                    <div class="country-name">{country['name']}</div>
                    <div class="country-details">{country['details']}</div>
                </div>
                """,
                unsafe_allow_html=True
            )

            if st.button("Visitar Tienda", key=f"visit_{country['name']}", use_container_width=True):
                st.markdown(f'<a href="{country["url"]}" target="_blank">Ir a {country["name"]}</a>',
                           unsafe_allow_html=True)

    st.markdown("<div style='margin: 2rem 0;'></div>", unsafe_allow_html=True)

    # Join Team CTA
    st.markdown(
        """
        <div class="cta-card">
            <div class="cta-title">¿Quieres ser parte de este movimiento?</div>
            <div class="cta-description">
            Únete a miles de Wellness Advocates en América Latina que están transformando
            sus vidas a través de doTERRA.
            </div>
        </div>
        """,
        unsafe_allow_html=True
    )

    if st.button("Conocer Oportunidades de Negocio", key="latam_business_btn", use_container_width=True):
        st.session_state.page = "join_team"
        st.rerun()

    st.markdown("<div style='margin: 2rem 0;'></div>", unsafe_allow_html=True)

    if st.button("← Volver al Inicio", key="latam_back_btn"):
        st.session_state.page = "home"
        st.rerun()


def page_join_team():
    """Join the Team page (Únete al Equipo)"""

    st.markdown("<h1>💼 Únete al Equipo de Nosotras Naturales</h1>", unsafe_allow_html=True)

    st.markdown(
        """
        ¿Te apasiona el bienestar natural? ¿Quieres ayudar a otros mientras construyes
        un negocio rentable? Únete a nuestra creciente comunidad de Wellness Advocates de doTERRA.
        """,
        unsafe_allow_html=True
    )

    st.markdown("<div style='margin: 2rem 0;'></div>", unsafe_allow_html=True)

    # Benefits Section
    st.markdown("<h3>✨ Beneficios de ser un Wellness Advocate</h3>", unsafe_allow_html=True)

    benefits = [
        ("💰", "Ingresos Flexible", "Gana comisiones generosas en cada venta"),
        ("🎁", "Descuentos Especiales", "Obtén descuentos de 25-30% en todos los productos"),
        ("📚", "Capacitación Completa", "Acceso a materiales de entrenamiento y webinars"),
        ("👥", "Comunidad de Apoyo", "Únete a un equipo de mujeres empoderadas"),
        ("🌍", "Alcance Global", "Vende en cualquier lugar con el programa doTERRA"),
        ("🚀", "Crecimiento Ilimitado", "Construye tu propio equipo y gana bonificaciones"),
    ]

    col_count = 3
    cols = st.columns(col_count, gap="medium")

    for idx, (icon, title, desc) in enumerate(benefits):
        col = cols[idx % col_count]
        with col:
            st.markdown(
                f"""
                <div class="card" style="text-align: center;">
                    <h4 style="border: none; color: #3D3229;">{icon} {title}</h4>
                    <p>{desc}</p>
                </div>
                """,
                unsafe_allow_html=True
            )

    st.markdown("<div style='margin: 2rem 0;'></div>", unsafe_allow_html=True)

    # Enrollment Info
    st.markdown("<h3>📋 Cómo Comenzar</h3>", unsafe_allow_html=True)

    steps = [
        ("1️⃣", "Selecciona tu Kit Inicial", "Elige entre nuestros kits curados de bienvenida"),
        ("2️⃣", "Completa el Registro", "Regístrate como Wellness Advocate de doTERRA"),
        ("3️⃣", "Recibe tu Paquete", "Tu kit llega a tu puerta en 5-7 días hábiles"),
        ("4️⃣", "Comienza a Vender", "Comparte productos y gana comisiones"),
    ]

    for icon, title, desc in steps:
        st.markdown(
            f"""
            <div class="card">
                <h4 style="border: none;">{icon} {title}</h4>
                <p>{desc}</p>
            </div>
            """,
            unsafe_allow_html=True
        )

    st.markdown("<div style='margin: 2rem 0;'></div>", unsafe_allow_html=True)

    # Contact CTA
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        st.markdown(
            f"""
            <div class="cta-card">
                <div class="cta-title">¿Listo para Comenzar?</div>
                <div class="cta-description">
                Contacta a Suzanna para más información sobre cómo unirte a nuestro equipo
                y comenzar tu viaje como Wellness Advocate de doTERRA.
                </div>
            </div>
            """,
            unsafe_allow_html=True
        )

        if st.button("💬 Solicitar Información", key="join_contact_btn", use_container_width=True):
            st.markdown(
                f'<a href="{get_whatsapp_link("Me interesa ser Wellness Advocate de doTERRA")}" target="_blank">Abrir WhatsApp</a>',
                unsafe_allow_html=True
            )

    st.markdown("<div style='margin: 2rem 0;'></div>", unsafe_allow_html=True)

    if st.button("← Volver al Inicio", key="join_back_btn"):
        st.session_state.page = "home"
        st.rerun()


def page_community():
    """Nosotras Naturales Community page"""

    st.markdown("<h1>🌸 Nosotras Naturales - Nuestra Comunidad</h1>", unsafe_allow_html=True)

    st.markdown(
        """
        Somos una comunidad de mujeres dedicadas al bienestar natural y la construcción
        de un futuro próspero para nosotras y nuestras familias.
        """,
        unsafe_allow_html=True
    )

    st.markdown("<div style='margin: 2rem 0;'></div>", unsafe_allow_html=True)

    # Social Links
    st.markdown("<h3>Conéctate Con Nosotros</h3>", unsafe_allow_html=True)

    col1, col2, col3 = st.columns(3)

    with col1:
        if st.button("📱 Instagram @nosotrasnaturales", key="community_instagram_btn", use_container_width=True):
            st.markdown('https://www.instagram.com/nosotrasnaturales', unsafe_allow_html=True)

    with col2:
        if st.button("💬 WhatsApp +593 98 494 9487", key="community_whatsapp_btn", use_container_width=True):
            st.markdown(f'<a href="{get_whatsapp_link()}" target="_blank">Abrir WhatsApp</a>',
                       unsafe_allow_html=True)

    with col3:
        if st.button("🌐 Visita doTERRA", key="community_doterra_btn", use_container_width=True):
            st.markdown(f'<a href="{DOTERRA_STORE_URL}" target="_blank">Visitar</a>',
                       unsafe_allow_html=True)

    st.markdown("<div style='margin: 2rem 0;'></div>", unsafe_allow_html=True)

    # Community Content
    st.markdown("<h3>📖 Nuestros Valores</h3>", unsafe_allow_html=True)

    col1, col2 = st.columns(2)

    with col1:
        st.markdown(
            """
            <div class="card">
                <h4 style="border: none;">🌱 Autenticidad</h4>
                <p>Recomendamos solo productos en los que creemos y hemos probado personalmente.</p>
            </div>
            """,
            unsafe_allow_html=True
        )
        st.markdown(
            """
            <div class="card">
                <h4 style="border: none;">💪 Empoderamiento</h4>
                <p>Apoyamos a cada mujer en su viaje hacia la independencia y el éxito.</p>
            </div>
            """,
            unsafe_allow_html=True
        )

    with col2:
        st.markdown(
            """
            <div class="card">
                <h4 style="border: none;">❤️ Comunidad</h4>
                <p>Juntas somos más fuertes. Celebramos nuestros logros y nos apoyamos mutuamente.</p>
            </div>
            """,
            unsafe_allow_html=True
        )
        st.markdown(
            """
            <div class="card">
                <h4 style="border: none;">🌍 Sostenibilidad</h4>
                <p>Comprometidas con prácticas sustentables y el bienestar del planeta.</p>
            </div>
            """,
            unsafe_allow_html=True
        )

    st.markdown("<div style='margin: 2rem 0;'></div>", unsafe_allow_html=True)

    if st.button("← Volver al Inicio", key="community_back_btn"):
        st.session_state.page = "home"
        st.rerun()


def page_dashboard():
    """Suzanna's Dashboard (Dashboard de Suzanna) - Password Protected"""

    st.markdown("<h1>👩‍💼 Dashboard de Suzanna</h1>", unsafe_allow_html=True)

    if not st.session_state.dashboard_authenticated:
        st.warning("⚠️ Acceso Restringido")

        password = st.text_input("Ingresa la contraseña:", type="password")

        if password:
            # Simple password check (in production, use proper authentication)
            if password == "doterra2024":
                st.session_state.dashboard_authenticated = True
                st.success("✓ Acceso concedido")
                st.rerun()
            else:
                st.error("❌ Contraseña incorrecta")

        if st.button("← Volver al Inicio", key="dashboard_back_btn"):
            st.session_state.page = "home"
            st.rerun()
        return

    # Dashboard Content
    col1, col2, col3, col4 = st.columns(4)

    with col1:
        st.metric(label="Productos", value="50+", delta="En catálogo")

    with col2:
        st.metric(label="Clientes", value="150+", delta="Activos")

    with col3:
        st.metric(label="Advocate ID", value="8205768", delta=ADVOCATE_ID)

    with col4:
        st.metric(label="Región", value="Ecuador", delta="América Latina")

    st.markdown("<div style='margin: 2rem 0;'></div>", unsafe_allow_html=True)

    # Admin Actions
    st.markdown("<h3>Acciones de Administración</h3>", unsafe_allow_html=True)

    col1, col2 = st.columns(2)

    with col1:
        if st.button("📊 Ver Analytics", key="dashboard_analytics_btn", use_container_width=True):
            st.info("Analytics dashboard en desarrollo")

    with col2:
        if st.button("👥 Gestionar Clientes", key="dashboard_clients_btn", use_container_width=True):
            st.info("Gestor de clientes en desarrollo")

    st.markdown("<div style='margin: 2rem 0;'></div>", unsafe_allow_html=True)

    # Contact Info Section
    st.markdown("<h3>📋 Información de Contacto</h3>", unsafe_allow_html=True)

    st.markdown(
        f"""
        **ID de Wellness Advocate:** {ADVOCATE_ID}

        **WhatsApp:** {WHATSAPP_DISPLAY}

        **Instagram:** {INSTAGRAM_HANDLE}

        **Tienda doTERRA:** {DOTERRA_STORE_URL}
        """,
        unsafe_allow_html=True
    )

    st.markdown("<div style='margin: 2rem 0;'></div>", unsafe_allow_html=True)

    col1, col2 = st.columns(2)

    with col1:
        if st.button("Cerrar Sesión", key="dashboard_logout_btn", use_container_width=True):
            st.session_state.dashboard_authenticated = False
            st.session_state.page = "home"
            st.rerun()

    with col2:
        if st.button("← Volver al Inicio", key="dashboard_back_btn_2"):
            st.session_state.page = "home"
            st.rerun()


def page_about():
    """About Suzanna page (Sobre Suzanna)"""

    st.markdown("<h1>👤 Sobre Suzanna</h1>", unsafe_allow_html=True)

    col1, col2 = st.columns([1, 2], gap="large")

    with col1:
        st.markdown(
            """
            <div style="text-align: center;">
                <div style="width: 150px; height: 150px; border-radius: 50%;
                           background: linear-gradient(135deg, #7C9070 0%, #B8965A 100%);
                           margin: 0 auto 1.5rem; display: flex; align-items: center;
                           justify-content: center; color: white; font-size: 3rem;">
                    👩‍💼
                </div>
            </div>
            """,
            unsafe_allow_html=True
        )

    with col2:
        st.markdown(
            """
            <h3>Suzanna Valles</h3>
            <p><strong>Wellness Advocate de doTERRA</strong></p>
            <p><strong>ID:</strong> 8205768</p>
            <p><strong>Ubicación:</strong> Ecuador</p>
            <p><strong>Especialidad:</strong> Bienestar Holístico con Aceites Esenciales</p>
            """,
            unsafe_allow_html=True
        )

    st.markdown("<div style='margin: 2rem 0;'></div>", unsafe_allow_html=True)

    # Bio Section
    st.markdown("<h3>Mi Historia</h3>", unsafe_allow_html=True)

    st.markdown(
        """
        Mi viaje con el bienestar natural comenzó cuando descubrí el poder transformador
        de los aceites esenciales de grado terapéutico. Desde entonces, he dedicado mi vida
        a compartir estos productos extraordinarios con mujeres en toda América Latina.

        Como Wellness Advocate certificada de doTERRA, estoy comprometida con proporcionar
        educación de calidad, recomendaciones personalizadas y apoyo continuo a cada cliente.
        Creo que el bienestar es un derecho, no un lujo, y que cada persona merece acceso a
        productos de la más alta calidad.

        A través de Nosotras Naturales, he creado una comunidad de mujeres apasionadas que
        comparten mi visión: transformar vidas a través de la naturaleza, una gota a la vez.
        """,
        unsafe_allow_html=True
    )

    st.markdown("<div style='margin: 2rem 0;'></div>", unsafe_allow_html=True)

    # Mission Section
    st.markdown("<h3>🎯 Nuestra Misión</h3>", unsafe_allow_html=True)

    st.markdown(
        """
        Empoderar a mujeres ecuatorianas y latinoamericanas a través de:

        - 🌿 **Educación en Bienestar:** Proporcionar conocimiento profundo sobre aceites esenciales
        - 💪 **Oportunidades Económicas:** Crear caminos para la independencia financiera
        - 👥 **Comunidad Solidaria:** Construir redes de apoyo mutuo y crecimiento
        - 🌍 **Impacto Sostenible:** Promover prácticas responsables con el ambiente
        """,
        unsafe_allow_html=True
    )

    st.markdown("<div style='margin: 2rem 0;'></div>", unsafe_allow_html=True)

    # Social Links
    st.markdown("<h3>Conéctate Conmigo</h3>", unsafe_allow_html=True)

    col1, col2, col3 = st.columns(3)

    with col1:
        st.markdown(
            f"""
            <a href="https://www.instagram.com/nosotrasnaturales" target="_blank" style="text-decoration: none;">
                <button style="width: 100%; padding: 0.8rem; background-color: #E4405F; color: white; border: none; border-radius: 8px; cursor: pointer; font-weight: 600;">
                    📱 Instagram
                </button>
            </a>
            """,
            unsafe_allow_html=True
        )

    with col2:
        st.markdown(
            f"""
            <a href="{get_whatsapp_link('Hola Suzanna')}" target="_blank" style="text-decoration: none;">
                <button style="width: 100%; padding: 0.8rem; background-color: #25D366; color: white; border: none; border-radius: 8px; cursor: pointer; font-weight: 600;">
                    💬 WhatsApp
                </button>
            </a>
            """,
            unsafe_allow_html=True
        )

    with col3:
        st.markdown(
            f"""
            <a href="{DOTERRA_STORE_URL}" target="_blank" style="text-decoration: none;">
                <button style="width: 100%; padding: 0.8rem; background-color: #7C9070; color: white; border: none; border-radius: 8px; cursor: pointer; font-weight: 600;">
                    🛒 Tienda
                </button>
            </a>
            """,
            unsafe_allow_html=True
        )

    st.markdown("<div style='margin: 2rem 0;'></div>", unsafe_allow_html=True)

    if st.button("← Volver al Inicio", key="about_back_btn"):
        st.session_state.page = "home"
        st.rerun()


# ============================================
# SIDEBAR NAVIGATION
# ============================================

def setup_sidebar():
    """Setup sidebar navigation"""

    with st.sidebar:
        # Logo/Brand
        st.markdown(
            """
            <div style="text-align: center; margin-bottom: 2rem;">
                <h2 style="color: white; border: none; margin-bottom: 0;">🌿 Nosotras Naturales</h2>
                <p style="color: rgba(255,255,255,0.8); font-size: 0.9rem; margin: 0;">
                    Bienestar Natural con doTERRA
                </p>
            </div>
            """,
            unsafe_allow_html=True
        )

        st.markdown("<div style='margin: 1.5rem 0;'></div>", unsafe_allow_html=True)

        # Navigation buttons
        nav_items = [
            ("🏠 Inicio", "home"),
            ("🌿 Guía de Bienestar", "symptom_checker"),
            ("📦 Productos", "products"),
            ("🌎 doTERRA Latinoamérica", "latam"),
            ("👩‍💼 Dashboard de Suzanna", "dashboard"),
            ("💼 Únete al Equipo", "join_team"),
            ("🌸 Nosotras Naturales", "community"),
            ("👤 Sobre Suzanna", "about"),
        ]

        for label, page_key in nav_items:
            if st.button(label, key=f"nav_{page_key}", use_container_width=True):
                st.session_state.page = page_key
                st.rerun()

        st.markdown("<div style='margin: 2rem 0;'></div>", unsafe_allow_html=True)

        # Contact Info
        st.markdown("<h4 style='color: white; text-align: center;'>📞 Contacto Directo</h4>", unsafe_allow_html=True)

        st.markdown(
            f"""
            <div style="background: rgba(255,255,255,0.1); border-radius: 8px; padding: 1rem; text-align: center;">
                <p style="color: white; margin: 0.5rem 0; font-size: 0.9rem;">
                    <strong>WhatsApp:</strong><br>
                    {WHATSAPP_DISPLAY}
                </p>
                <p style="color: white; margin: 0.5rem 0; font-size: 0.9rem;">
                    <strong>Instagram:</strong><br>
                    {INSTAGRAM_HANDLE}
                </p>
                <p style="color: white; margin: 0.5rem 0; font-size: 0.9rem;">
                    <strong>ID doTERRA:</strong><br>
                    {ADVOCATE_ID}
                </p>
            </div>
            """,
            unsafe_allow_html=True
        )

        st.markdown("<div style='margin: 2rem 0;'></div>", unsafe_allow_html=True)

        # Footer Info
        st.markdown(
            """
            <div style="text-align: center; font-size: 0.8rem; color: rgba(255,255,255,0.6);">
                <p>© 2024 Nosotras Naturales</p>
                <p>Tous droits réservés</p>
            </div>
            """,
            unsafe_allow_html=True
        )


# ============================================
# MAIN APPLICATION
# ============================================

def main():
    """Main application function"""

    # Load styles
    load_css()

    # Initialize session state
    initialize_session_state()

    # Setup sidebar navigation
    setup_sidebar()

    # Display WhatsApp button
    display_whatsapp_button()

    # Route to appropriate page
    page_map = {
        "home": page_home,
        "symptom_checker": page_symptom_checker,
        "products": page_products,
        "latam": page_latam,
        "join_team": page_join_team,
        "community": page_community,
        "dashboard": page_dashboard,
        "about": page_about,
    }

    current_page = st.session_state.page
    page_function = page_map.get(current_page, page_home)
    page_function()

    # Footer
    st.markdown("<div style='margin: 4rem 0 2rem 0;'></div>", unsafe_allow_html=True)
    st.markdown(
        """
        <footer style='text-align: center; color: #666; font-size: 0.9rem; border-top: 1px solid #D4C5A9; padding-top: 2rem;'>
            <p>Nosotras Naturales © 2024 | Wellness Advocate doTERRA ID: 8205768</p>
            <p>
                <a href='https://www.doterra.com/EC/es_EC' target='_blank' style='color: #7C9070; text-decoration: none;'>
                    Visita nuestra tienda doTERRA
                </a>
            </p>
        </footer>
        """,
        unsafe_allow_html=True
    )


if __name__ == "__main__":
    main()
