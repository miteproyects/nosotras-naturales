"""
Nosotras Naturales - REDESIGNED doTERRA Wellness Web App
Modern, clean UI with Ubie-style symptom checker
Created by Suzanna Valles
doTERRA Wellness Advocate ID: 8205768
WhatsApp: +593 98 494 9487
Instagram: @nosotrasnaturales
"""

import streamlit as st
import json
import os
import urllib.parse
from datetime import datetime

# ============================================
# PAGE CONFIGURATION
# ============================================

st.set_page_config(
    page_title="Nosotras Naturales - doTERRA",
    page_icon="🌿",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# ============================================
# CONSTANTS
# ============================================

ADVOCATE_ID = "8205768"
WHATSAPP_NUMBER = "593984949487"
DOTERRA_SHOP_URL = f"https://www.doterra.com/EC/es_EC/shop?referralId={ADVOCATE_ID}"
INSTAGRAM_URL = "https://www.instagram.com/nosotrasnaturales"
DASHBOARD_PASSWORD = "nosotras2024"

# ============================================
# LOAD CSS & DATA
# ============================================

def load_css():
    """Load custom CSS"""
    css_path = "assets/style.css"
    if os.path.exists(css_path):
        with open(css_path, encoding="utf-8") as f:
            st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)

@st.cache_data
def load_products():
    """Load products from JSON"""
    with open("data/products.json", "r", encoding="utf-8") as f:
        return json.load(f)

@st.cache_data
def load_symptom_flow():
    """Load symptom flow from JSON"""
    with open("data/symptom_flow.json", "r", encoding="utf-8") as f:
        return json.load(f)

load_css()
products_data = load_products()
symptom_flow = load_symptom_flow()

# ============================================
# UTILITY FUNCTIONS
# ============================================

def whatsapp_link(message):
    """Create WhatsApp link with URL-encoded message"""
    encoded = urllib.parse.quote(message)
    return f"https://wa.me/{WHATSAPP_NUMBER}?text={encoded}"

def create_product_card(product, match_percentage=None):
    """Create HTML card for a product"""
    price_display = f"${product.get('precio_usd', 'N/A')}"
    match_html = f'<div class="match-badge">{match_percentage}% Match</div>' if match_percentage else ''
    comprar_link = DOTERRA_SHOP_URL
    consult_msg = f"Hola Suzanna! 👋 Me gustaría conocer más sobre {product['nombre']}. ¿Puedes ayudarme?"
    consult_link = whatsapp_link(consult_msg)

    benefits_html = ''.join([f'<li>{b}</li>' for b in product.get('beneficios', [])[:3]])

    html = f"""
    <div class="product-card">
        {match_html}
        <div class="product-image">
            <img src="{product['imagen_url']}" alt="{product['nombre']}">
        </div>
        <div class="product-info">
            <h3>{product['nombre']}</h3>
            <p class="product-price">{price_display}</p>
            <p class="product-description">{product['descripcion']}</p>
            <div class="product-benefits">
                <strong>Beneficios:</strong>
                <ul>{benefits_html}</ul>
            </div>
            <div class="product-usage">
                <p><strong>Uso Aromático:</strong> {product.get('uso_aromatico', 'N/A')}</p>
            </div>
            <div class="product-buttons">
                <a href="{comprar_link}" class="btn-primary" target="_blank">Comprar</a>
                <a href="{consult_link}" class="btn-whatsapp" target="_blank">Consultar con Suzanna</a>
            </div>
        </div>
    </div>
    """
    return html

def get_current_question(flow_data, category_id, question_id):
    """Get a specific question from the symptom flow"""
    for category in flow_data['categories']:
        if category['id'] == category_id:
            for question in category['preguntas']:
                if question['id'] == question_id:
                    return question
    return None

def calculate_product_matches(selected_tags, products):
    """Calculate match scores for products based on tags"""
    matches = {}

    for product in products:
        product_symptoms = set(product.get('sintomas_relacionados', []))
        selected_tags_set = set(selected_tags)
        common = product_symptoms.intersection(selected_tags_set)

        if common:
            match_percentage = int((len(common) / max(len(selected_tags_set), len(product_symptoms))) * 100)
            matches[product['id']] = {
                'product': product,
                'percentage': match_percentage
            }

    sorted_matches = sorted(matches.items(), key=lambda x: x[1]['percentage'], reverse=True)
    return sorted_matches[:3]

def render_fda_disclaimer():
    """Render FDA compliance disclaimer"""
    disclaimer = """
    <div class="fda-disclaimer">
        <p><strong>Aviso Importante:</strong> Estos productos no están destinados a diagnosticar, tratar, curar o prevenir ninguna enfermedad.
        Las declaraciones sobre estos productos no han sido evaluadas por organismos de salud. Consulte con un profesional de la salud antes de usar si está
        embarazada, amamantando, tomando medicamentos o tiene condiciones de salud preexistentes.</p>
    </div>
    """
    st.markdown(disclaimer, unsafe_allow_html=True)

def render_whatsapp_float():
    """Render floating WhatsApp button"""
    whatsapp_html = """
    <div class="whatsapp-float">
        <a href="https://wa.me/593984949487" target="_blank" title="Contactar por WhatsApp">
            <svg width="24" height="24" viewBox="0 0 24 24" fill="white">
                <path d="M17.472 14.382c-.297-.149-1.758-.867-2.03-.967-.273-.099-.471-.148-.67.15-.197.297-.767.966-.94 1.164-.173.199-.347.223-.644.075-.297-.15-1.255-.463-2.39-1.475-.883-.788-1.48-1.761-1.653-2.059-.173-.297-.018-.458.13-.606.134-.133.298-.347.446-.52.149-.174.198-.298.298-.497.099-.198.05-.371-.025-.52-.075-.149-.669-1.612-.916-2.207-.242-.579-.487-.5-.67-.51-.173-.008-.371-.01-.57-.01-.198 0-.52.074-.792.372-.272.297-1.04 1.016-1.04 2.479 0 1.462 1.065 2.875 1.213 3.074.149.198 2.096 3.2 5.076 4.487.709.306 1.262.489 1.694.625.712.227 1.36.195 1.871.118.571-.085 1.758-.719 2.006-1.413.248-.694.248-1.289.173-1.413-.074-.124-.272-.198-.57-.347m-5.421-7.403h-.004a9.87 9.87 0 00-9.746 9.798c0 2.718.738 5.33 2.146 7.591L2.885 23.68l8.29-2.161a9.885 9.885 0 004.748 1.212h.005c5.435 0 9.85-4.414 9.85-9.85 0-2.631-1.039-5.1-2.927-6.965-1.888-1.865-4.39-2.89-7.032-2.89z"/>
            </svg>
        </a>
    </div>
    """
    st.markdown(whatsapp_html, unsafe_allow_html=True)

# ============================================
# SESSION STATE INITIALIZATION
# ============================================

if 'page' not in st.session_state:
    st.session_state.page = 'inicio'
if 'symptom_flow_started' not in st.session_state:
    st.session_state.symptom_flow_started = False
if 'current_category' not in st.session_state:
    st.session_state.current_category = None
if 'current_question' not in st.session_state:
    st.session_state.current_question = None
if 'selected_tags' not in st.session_state:
    st.session_state.selected_tags = []
if 'question_history' not in st.session_state:
    st.session_state.question_history = []
if 'dashboard_authenticated' not in st.session_state:
    st.session_state.dashboard_authenticated = False

# ============================================
# PAGE FUNCTIONS
# ============================================

def page_inicio():
    """Home page with hero and CTAs"""
    st.markdown("""
    <div class="hero">
        <div class="hero-content">
            <h1>Bienvenida a Nosotras Naturales</h1>
            <p>Aceites esenciales doTERRA de grado terapéutico para tu bienestar</p>
            <p class="subtitle">Descubre el poder de la naturaleza con Suzanna Valles</p>
        </div>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("")

    # Main CTA
    col1, col2, col3 = st.columns([1, 1.5, 1])
    with col2:
        st.markdown("""
        <div style="text-align: center; padding: 25px; background: linear-gradient(135deg, #7C9070 0%, #B8965A 100%);
                    border-radius: 15px; color: white; margin: 20px 0;">
            <h3 style="margin-top: 0; color: white;">¿Cómo te sientes hoy?</h3>
            <p style="color: white;">Descubre cuáles productos doTERRA son perfectos para ti</p>
        </div>
        """, unsafe_allow_html=True)

        if st.button("▶ Iniciar Guía de Bienestar", key="cta_wellness", use_container_width=True):
            st.session_state.page = 'guia_bienestar'
            st.session_state.symptom_flow_started = True
            st.rerun()

    st.markdown("---")

    # Feature cards
    st.markdown("<h2 style='text-align: center; margin: 40px 0;'>¿Por qué doTERRA?</h2>", unsafe_allow_html=True)

    col1, col2, col3 = st.columns(3)

    with col1:
        st.markdown("""
        <div class="feature-card">
            <div class="feature-icon">🌾</div>
            <h4>100% Puro</h4>
            <p>Aceites esenciales de grado terapéutico, sin aditivos ni rellenos</p>
        </div>
        """, unsafe_allow_html=True)

    with col2:
        st.markdown("""
        <div class="feature-card">
            <div class="feature-icon">🔬</div>
            <h4>Probado Científicamente</h4>
            <p>Formulaciones respaldadas por investigación y pruebas de calidad</p>
        </div>
        """, unsafe_allow_html=True)

    with col3:
        st.markdown("""
        <div class="feature-card">
            <div class="feature-icon">💚</div>
            <h4>Bienestar Natural</h4>
            <p>Apoyo holístico para tu salud y bienestar emocional</p>
        </div>
        """, unsafe_allow_html=True)

    st.markdown("---")

    # Quick actions
    st.markdown("<h2 style='text-align: center; margin: 40px 0;'>Explora Más</h2>", unsafe_allow_html=True)

    col1, col2, col3, col4 = st.columns(4)

    with col1:
        if st.button("📚 Catálogo", use_container_width=True, key="nav_catalog"):
            st.session_state.page = 'productos'
            st.rerun()

    with col2:
        st.markdown(f'<a href="{DOTERRA_SHOP_URL}" target="_blank" class="btn-primary" style="display: block; text-align: center; padding: 10px;">🛍️ Comprar</a>',
                   unsafe_allow_html=True)

    with col3:
        if st.button("💼 Oportunidad", use_container_width=True, key="nav_opportunity"):
            st.session_state.page = 'unete_al_equipo'
            st.rerun()

    with col4:
        if st.button("ℹ️ Sobre Nosotras", use_container_width=True, key="nav_about"):
            st.session_state.page = 'sobre_nosotras'
            st.rerun()


def page_guia_bienestar():
    """Symptom checker page - Ubie style"""
    st.markdown("<h1>Guía de Bienestar</h1>", unsafe_allow_html=True)
    st.markdown("<p class='subtitle'>Encuentra los productos doTERRA perfectos para ti</p>", unsafe_allow_html=True)

    if not st.session_state.symptom_flow_started:
        # Landing screen
        st.markdown("""
        <div style="text-align: center; padding: 40px 20px;">
            <h2>¿Cómo te sientes hoy?</h2>
            <p style="font-size: 16px; color: #666; margin: 20px 0;">
                Responde algunas preguntas simples para descubrir qué productos doTERRA
                pueden apoyar tu bienestar natural.
            </p>
        </div>
        """, unsafe_allow_html=True)

        st.markdown("<h3 style='text-align: center; margin: 40px 0;'>Elige una categoría:</h3>", unsafe_allow_html=True)

        # Show categories as cards
        cols = st.columns(3)
        col_idx = 0

        for category in symptom_flow['categories']:
            with cols[col_idx % 3]:
                st.markdown("""
                <style>
                    .category-btn { cursor: pointer; }
                    .category-btn:hover { opacity: 0.8; }
                </style>
                """, unsafe_allow_html=True)

                st.markdown(f"""
                <div class="category-card">
                    <div style="font-size: 40px; margin-bottom: 10px;">{category.get('icono', '🌿')}</div>
                    <h4>{category['nombre']}</h4>
                    <p style="font-size: 14px; color: #666;">{category['descripcion']}</p>
                </div>
                """, unsafe_allow_html=True)

                if st.button(f"Explorar {category['nombre']}", key=f"cat_{category['id']}", use_container_width=True):
                    st.session_state.current_category = category['id']
                    first_question = category['preguntas'][0]
                    st.session_state.current_question = first_question['id']
                    st.session_state.question_history = [first_question['id']]
                    st.session_state.selected_tags = []
                    st.session_state.symptom_flow_started = True
                    st.rerun()

            col_idx += 1

    else:
        # Question flow
        if st.session_state.current_category and st.session_state.current_question:
            category = None
            for cat in symptom_flow['categories']:
                if cat['id'] == st.session_state.current_category:
                    category = cat
                    break

            if category:
                current_q = get_current_question(symptom_flow, st.session_state.current_category, st.session_state.current_question)

                if current_q:
                    # Progress bar
                    progress = min(len(st.session_state.question_history) / 5, 1.0)
                    st.progress(progress, f"Pregunta {len(st.session_state.question_history)} de ~5")

                    # Question title
                    st.markdown(f"<h3>{current_q['texto']}</h3>", unsafe_allow_html=True)

                    # Options as buttons
                    for i, option in enumerate(current_q['opciones']):
                        col1, col2, col3 = st.columns([1, 2, 1])
                        with col2:
                            if st.button(option['texto'], key=f"opt_{i}", use_container_width=True):
                                st.session_state.selected_tags.extend(option.get('tags', []))
                                next_question_id = option.get('siguiente')

                                if next_question_id == 'resultado':
                                    st.session_state.page = 'resultado_sintomas'
                                    st.rerun()
                                else:
                                    st.session_state.current_question = next_question_id
                                    st.session_state.question_history.append(next_question_id)
                                    st.rerun()

                    # Back button
                    col1, col2, col3 = st.columns([1, 2, 1])
                    with col1:
                        if st.button("← Atrás", key="back_btn"):
                            if len(st.session_state.question_history) > 1:
                                st.session_state.question_history.pop()
                                st.session_state.current_question = st.session_state.question_history[-1]
                                st.rerun()
                            else:
                                st.session_state.symptom_flow_started = False
                                st.rerun()


def page_resultado_sintomas():
    """Results page with recommended products"""
    st.markdown("<h1>Tu Recomendación Personalizada</h1>", unsafe_allow_html=True)

    top_products = calculate_product_matches(st.session_state.selected_tags, products_data)

    if top_products:
        st.markdown("<h3 style='text-align: center; margin: 30px 0;'>Top 3 Productos Recomendados</h3>", unsafe_allow_html=True)

        for idx, (product_id, match_data) in enumerate(top_products, 1):
            st.markdown(f"<h4>Recomendación #{idx}</h4>", unsafe_allow_html=True)
            st.markdown(create_product_card(match_data['product'], match_data['percentage']), unsafe_allow_html=True)
            st.markdown("---")
    else:
        st.info("No se encontraron productos que coincidan. Por favor, intenta de nuevo.")

    render_fda_disclaimer()

    col1, col2, col3 = st.columns(3)
    with col2:
        if st.button("🔄 Volver a Empezar", use_container_width=True, key="restart_symptom"):
            st.session_state.symptom_flow_started = False
            st.session_state.current_category = None
            st.session_state.current_question = None
            st.session_state.selected_tags = []
            st.session_state.question_history = []
            st.rerun()


def page_productos():
    """Product catalog page"""
    st.markdown("<h1>Catálogo de Productos</h1>", unsafe_allow_html=True)

    col1, col2 = st.columns([3, 1])
    with col1:
        search_term = st.text_input("🔍 Buscar productos...", placeholder="Ej: Lavanda, Menta...")
    with col2:
        categories = ["Todos"] + list(set([cat for p in products_data for cat in p.get('categoria', [])]))
        category_filter = st.selectbox("Categoría", options=categories, key="category_filter")

    filtered_products = products_data

    if search_term:
        filtered_products = [p for p in filtered_products
                            if search_term.lower() in p['nombre'].lower()
                            or search_term.lower() in p['descripcion'].lower()]

    if category_filter != "Todos":
        filtered_products = [p for p in filtered_products if category_filter in p.get('categoria', [])]

    if filtered_products:
        st.markdown(f"<p style='text-align: center; color: #666;'>{len(filtered_products)} productos encontrados</p>", unsafe_allow_html=True)

        cols = st.columns(3)
        for idx, product in enumerate(filtered_products):
            with cols[idx % 3]:
                st.markdown(create_product_card(product), unsafe_allow_html=True)
    else:
        st.info("No se encontraron productos que coincidan con tu búsqueda.")

    st.markdown("---")
    render_fda_disclaimer()


def page_unete_al_equipo():
    """Business opportunity page"""
    st.markdown("<h1>Únete al Equipo</h1>", unsafe_allow_html=True)
    st.markdown("<p class='subtitle'>Crea una oportunidad de negocio con doTERRA</p>", unsafe_allow_html=True)

    col1, col2 = st.columns([1, 1])

    with col1:
        st.markdown("""
        <div class="feature-card">
            <h3>¿Por qué unirse?</h3>
            <ul style="font-size: 14px;">
                <li>Comisiones atractivas y crecientes</li>
                <li>Productos de excelente calidad</li>
                <li>Soporte continuo del equipo</li>
                <li>Oportunidad de ganar desde casa</li>
                <li>Comunidad de emprendedoras</li>
                <li>Capacitación y recursos gratuitos</li>
            </ul>
        </div>
        """, unsafe_allow_html=True)

    with col2:
        st.markdown("""
        <div class="feature-card">
            <h3>¿Cómo funciona?</h3>
            <ol style="font-size: 14px;">
                <li><strong>Inscríbete</strong> como miembro preferente</li>
                <li><strong>Recibe</strong> tus aceites con descuento</li>
                <li><strong>Comparte</strong> con amigos y familia</li>
                <li><strong>Gana</strong> comisiones por tus ventas</li>
                <li><strong>Crece</strong> tu equipo y expandir ingresos</li>
                <li><strong>Disfruta</strong> beneficios exclusivos</li>
            </ol>
        </div>
        """, unsafe_allow_html=True)

    st.markdown("---")

    st.markdown("""
    <div style="text-align: center; padding: 30px; background: linear-gradient(135deg, #7C9070 0%, #B8965A 100%);
                border-radius: 15px; color: white; margin: 20px 0;">
        <h3 style="color: white;">¿Listo para comenzar?</h3>
        <p style="color: white;">Contacta a Suzanna Valles hoy mismo para más información</p>
    </div>
    """, unsafe_allow_html=True)

    col1, col2, col3 = st.columns(3)
    with col2:
        wa_msg = "¡Hola Suzanna! 👋 Me gustaría saber más sobre la oportunidad de negocio con doTERRA. ¿Puedes ayudarme?"
        wa_link = whatsapp_link(wa_msg)
        st.markdown(f'<a href="{wa_link}" target="_blank" class="btn-primary" style="display: block; text-align: center; padding: 12px; background: #25D366; color: white; text-decoration: none; border-radius: 8px; font-weight: bold; margin: 20px 0;">📱 Contactar por WhatsApp</a>',
                   unsafe_allow_html=True)


def page_sobre_nosotras():
    """About page"""
    st.markdown("<h1>Sobre Nosotras</h1>", unsafe_allow_html=True)

    col1, col2 = st.columns([1, 1])

    with col1:
        st.markdown("""
        <div style="background: #F0E8D8; padding: 20px; border-radius: 10px;">
            <h3>Suzanna Valles</h3>
            <p><strong>Embajadora doTERRA en Ecuador</strong></p>
            <p>Con más de 5 años de experiencia en aceites esenciales doTERRA, Suzanna se dedica a ayudar
            a las personas a descubrir el poder transformador de los productos naturales de grado terapéutico.</p>
            <p style="margin-top: 15px;">
                <strong>Misión:</strong> Llevar bienestar natural a cada hogar en Ecuador y Latinoamérica.
            </p>
            <p>
                <strong>Visión:</strong> Crear una comunidad de mujeres empoderadas que viven con salud,
                abundancia y propósito a través de doTERRA.
            </p>
        </div>
        """, unsafe_allow_html=True)

    with col2:
        st.markdown("""
        <div style="background: #F0E8D8; padding: 20px; border-radius: 10px;">
            <h3>¿Por qué Nosotras Naturales?</h3>
            <p>Creemos que la naturaleza tiene soluciones poderosas para el bienestar:</p>
            <ul>
                <li><strong>Pureza:</strong> Grado terapéutico, sin aditivos</li>
                <li><strong>Efectividad:</strong> Probado científicamente</li>
                <li><strong>Sostenibilidad:</strong> Producción ética y responsable</li>
                <li><strong>Accesibilidad:</strong> Precios competitivos</li>
                <li><strong>Comunidad:</strong> Apoyo continuo y educación</li>
            </ul>
        </div>
        """, unsafe_allow_html=True)

    st.markdown("---")

    st.markdown("<h3 style='text-align: center;'>Síguenos en Redes</h3>", unsafe_allow_html=True)
    col1, col2, col3 = st.columns(3)
    with col2:
        st.markdown(f'<a href="{INSTAGRAM_URL}" target="_blank" style="font-size: 18px; text-decoration: none; display: block; text-align: center;">📱 Instagram @nosotrasnaturales</a>',
                   unsafe_allow_html=True)


def page_dashboard():
    """Password-protected dashboard"""
    if not st.session_state.dashboard_authenticated:
        st.markdown("<h1>Dashboard de Suzanna</h1>", unsafe_allow_html=True)
        password = st.text_input("Contraseña:", type="password")

        if st.button("Acceder"):
            if password == DASHBOARD_PASSWORD:
                st.session_state.dashboard_authenticated = True
                st.rerun()
            else:
                st.error("❌ Contraseña incorrecta")
        return

    st.markdown("<h1>Dashboard de Suzanna</h1>", unsafe_allow_html=True)

    if st.button("🚪 Cerrar Sesión", key="logout"):
        st.session_state.dashboard_authenticated = False
        st.rerun()

    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("Productos", len(products_data))
    with col2:
        st.metric("Categorías", len(symptom_flow['categories']))
    with col3:
        st.metric("ID Advocada", ADVOCATE_ID)
    with col4:
        st.metric("Fecha", datetime.now().strftime("%d/%m/%Y"))

    st.markdown("---")

    st.markdown("<h3>Inventario de Productos</h3>", unsafe_allow_html=True)
    st.dataframe(
        [(p['nombre'], p['precio_usd'], p['pv'], ', '.join(p.get('categoria', [])))
         for p in products_data],
        columns=["Producto", "Precio USD", "PV", "Categorías"],
        use_container_width=True
    )

    st.markdown("---")
    st.markdown("<h3>Configuración</h3>", unsafe_allow_html=True)
    col1, col2 = st.columns(2)
    with col1:
        st.info(f"📱 **WhatsApp:** {WHATSAPP_NUMBER}")
    with col2:
        st.info(f"🎯 **ID Advocada:** {ADVOCATE_ID}")

def page_latam():
    """doTERRA Latinoamérica page"""
    st.markdown("<h1>doTERRA en América Latina</h1>", unsafe_allow_html=True)
    st.markdown("<p class='subtitle'>Explora los productos doTERRA disponibles en tu país</p>", unsafe_allow_html=True)

    countries = [
        {"flag": "🇪🇨", "name": "Ecuador", "code": "EC", "lang": "es_EC", "highlight": True},
        {"flag": "🇨🇴", "name": "Colombia", "code": "CO", "lang": "es_CO"},
        {"flag": "🇵🇪", "name": "Perú", "code": "PE", "lang": "es_PE"},
        {"flag": "🇨🇱", "name": "Chile", "code": "CL", "lang": "es_CL"},
        {"flag": "🇦🇷", "name": "Argentina", "code": "AR", "lang": "es_AR"},
        {"flag": "🇧🇴", "name": "Bolivia", "code": "BO", "lang": "es_BO"},
        {"flag": "🇲🇽", "name": "México", "code": "MX", "lang": "es_MX"},
        {"flag": "🇧🇷", "name": "Brasil", "code": "BR", "lang": "pt_BR"},
        {"flag": "🇨🇷", "name": "Costa Rica", "code": "CR", "lang": "es_CR"},
        {"flag": "🇬🇹", "name": "Guatemala", "code": "GT", "lang": "es_GT"},
        {"flag": "🇵🇾", "name": "Paraguay", "code": "PY", "lang": "es_PY"},
        {"flag": "🇺🇾", "name": "Uruguay", "code": "UY", "lang": "es_UY"},
    ]

    cols = st.columns(4)
    for idx, country in enumerate(countries):
        with cols[idx % 4]:
            url = f"https://www.doterra.com/{country['code']}/{country['lang']}"
            if country.get('highlight'):
                url = f"https://www.doterra.com/{country['code']}/{country['lang']}/shop?referralId={ADVOCATE_ID}"
            border = "3px solid #7C9070" if country.get('highlight') else "1px solid #D4C5A9"
            badge = '<span style="background: #7C9070; color: white; padding: 2px 8px; border-radius: 10px; font-size: 11px;">Tu país</span>' if country.get('highlight') else ''
            st.markdown(f"""
            <a href="{url}" target="_blank" style="text-decoration: none; color: inherit;">
                <div style="background: white; border: {border}; border-radius: 12px; padding: 20px; text-align: center; margin-bottom: 15px; transition: all 0.3s; cursor: pointer;">
                    <div style="font-size: 36px;">{country['flag']}</div>
                    <div style="font-weight: 700; color: #3D3229; margin: 8px 0;">{country['name']}</div>
                    {badge}
                </div>
            </a>
            """, unsafe_allow_html=True)

    st.markdown("---")
    st.markdown("""
    <div style="text-align: center; padding: 30px; background: linear-gradient(135deg, #7C9070, #B8965A); border-radius: 15px; color: white;">
        <h3 style="color: white;">¿Quieres ser parte de doTERRA?</h3>
        <p style="color: rgba(255,255,255,0.9);">Únete a la comunidad más grande de bienestar natural en América Latina</p>
    </div>
    """, unsafe_allow_html=True)

    col1, col2, col3 = st.columns(3)
    with col2:
        if st.button("💼 Únete al Equipo", use_container_width=True, key="latam_join"):
            st.session_state.page = 'unete_al_equipo'
            st.rerun()


# ============================================
# SIDEBAR NAVIGATION
# ============================================

with st.sidebar:
    st.markdown("""
    <div style="text-align: center; padding: 15px 0;">
        <h2 style="color: white; margin: 0;">🌿 Nosotras Naturales</h2>
        <p style="color: rgba(255,255,255,0.8); font-size: 13px; margin: 5px 0;">Bienestar Natural con doTERRA</p>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("---")

    nav_items = [
        ("🏠 Inicio", "inicio"),
        ("🌿 Guía de Bienestar", "guia_bienestar"),
        ("📦 Productos", "productos"),
        ("🌎 doTERRA Latinoamérica", "latam"),
        ("💼 Únete al Equipo", "unete_al_equipo"),
        ("🌸 Sobre Nosotras", "sobre_nosotras"),
        ("👩‍💼 Dashboard", "dashboard"),
    ]

    for label, page_key in nav_items:
        if st.button(label, key=f"nav_{page_key}", use_container_width=True):
            st.session_state.page = page_key
            # Reset symptom flow when navigating away
            if page_key != 'guia_bienestar' and page_key != 'resultado_sintomas':
                st.session_state.symptom_flow_started = False
                st.session_state.current_category = None
                st.session_state.current_question = None
                st.session_state.selected_tags = []
                st.session_state.question_history = []
            st.rerun()

    st.markdown("---")
    wa_link = whatsapp_link("Hola Suzanna! Me interesa saber más sobre doTERRA.")
    st.markdown(f"""
    <a href="{wa_link}" target="_blank" style="display: block; text-align: center; background: #25D366;
       color: white; padding: 10px; border-radius: 8px; text-decoration: none; font-weight: 600; font-size: 14px;">
       💬 WhatsApp Suzanna
    </a>
    """, unsafe_allow_html=True)


# ============================================
# MAIN APP LOGIC
# ============================================

# Render floating WhatsApp button
render_whatsapp_float()

# Page routing
page_map = {
    'inicio': page_inicio,
    'guia_bienestar': page_guia_bienestar,
    'resultado_sintomas': page_resultado_sintomas,
    'productos': page_productos,
    'unete_al_equipo': page_unete_al_equipo,
    'sobre_nosotras': page_sobre_nosotras,
    'latam': page_latam,
    'dashboard': page_dashboard,
}

if st.session_state.page in page_map:
    page_map[st.session_state.page]()
else:
    st.session_state.page = 'inicio'
    st.rerun()

# Footer
st.markdown("---")
st.markdown("""
<div style="text-align: center; padding: 20px; color: #999; font-size: 12px;">
    <p>Nosotras Naturales © 2024 | Aceites Esenciales doTERRA de Grado Terapéutico</p>
    <p>Para consultas: 📱 Contacta a Suzanna Valles por WhatsApp</p>
</div>
""", unsafe_allow_html=True)
