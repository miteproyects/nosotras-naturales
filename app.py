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

def create_product_card(product, match_percentage=None, recommendation_reason=None):
    """Create comprehensive HTML card showing ALL product info like an expert would"""
    price_display = f"${product.get('precio_usd', 'N/A')}"
    pv_display = product.get('pv', '')
    match_html = f'<div class="match-badge">{match_percentage}% Compatible</div>' if match_percentage else ''
    reason_html = f'<div class="recommendation-reason">{recommendation_reason}</div>' if recommendation_reason else ''
    comprar_link = DOTERRA_SHOP_URL
    consult_msg = f"Hola Suzanna! 👋 Me interesa {product['nombre']} ({product.get('nombre_en', '')}). ¿Me puedes dar más información y ayudarme a hacer mi pedido?"
    consult_link = whatsapp_link(consult_msg)

    # ALL benefits, not just 3
    benefits_html = ''.join([f'<li>{b}</li>' for b in product.get('beneficios', [])])

    # ALL three usage methods
    uso_aromatico = product.get('uso_aromatico', '')
    uso_topico = product.get('uso_topico', '')
    uso_interno = product.get('uso_interno', '')

    usage_sections = ''
    if uso_aromatico:
        usage_sections += f'<div class="usage-item"><span class="usage-icon">🌬️</span><strong>Aromático:</strong> {uso_aromatico}</div>'
    if uso_topico:
        usage_sections += f'<div class="usage-item"><span class="usage-icon">✋</span><strong>Tópico:</strong> {uso_topico}</div>'
    if uso_interno:
        usage_sections += f'<div class="usage-item"><span class="usage-icon">💧</span><strong>Interno:</strong> {uso_interno}</div>'

    # Categories as badges
    cat_badges = ''.join([f'<span class="cat-badge">{cat.replace("_", " ").title()}</span>' for cat in product.get('categoria', [])[:4]])

    html = f"""
    <div class="product-card">
        {match_html}
        <div class="product-image">
            <img src="{product['imagen_url']}" alt="{product['nombre']}">
        </div>
        <div class="product-info">
            <h3>{product['nombre']} <span style="color: #999; font-size: 14px; font-weight: 400;">({product.get('nombre_en', '')})</span></h3>
            {reason_html}
            <div style="display: flex; align-items: baseline; gap: 15px; margin-bottom: 12px;">
                <span class="product-price">{price_display}</span>
                <span style="color: #999; font-size: 13px;">PV: {pv_display}</span>
            </div>
            <div class="cat-badges">{cat_badges}</div>
            <p class="product-description">{product['descripcion']}</p>
            <div class="product-benefits">
                <strong>Beneficios Clave:</strong>
                <ul>{benefits_html}</ul>
            </div>
            <div class="product-usage-section">
                <strong style="color: var(--primary); display: block; margin-bottom: 8px;">Formas de Uso:</strong>
                {usage_sections}
            </div>
            <div class="product-buttons">
                <a href="{comprar_link}" class="btn-primary" target="_blank">🛒 Comprar en doTERRA</a>
                <a href="{consult_link}" class="btn-whatsapp" target="_blank">💬 Consultar con Suzanna</a>
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

def calculate_product_matches(selected_tags, products, category_id=None):
    """
    Expert-level product matching algorithm.
    Uses ALL product data: sintomas_relacionados, categoria, beneficios, descripcion.
    ALWAYS returns at least 3 products - never leaves the user without a recommendation.
    """
    scores = []
    selected_set = set(selected_tags)

    # Map symptom flow category IDs to product category keywords
    category_to_product_cats = {
        'digestivo': ['digestion', 'bienestar_digestivo', 'comodidad_digestiva', 'enzimas_digestivas', 'bienestar_intestinal', 'salud_intestinal', 'asimilacion'],
        'sueno': ['sueño', 'relajacion', 'bienestar_emocional', 'sistema_nervioso', 'equilibrio_emocional'],
        'tension': ['relajacion', 'bienestar_emocional', 'equilibrio_emocional', 'sistema_nervioso', 'grounding', 'estabilidad', 'masaje'],
        'muscular': ['comodidad_muscular', 'comodidad_articular', 'comodidad_ocasional', 'masaje', 'movimiento', 'recuperacion', 'bienestar_inflamatorio'],
        'respiratorio': ['respiracion', 'bienestar_respiratorio', 'respiro_claro', 'limpieza_aire', 'proteccion'],
        'piel': ['piel', 'autocuidado', 'proteccion_exterior'],
        'femenino': ['salud_femenina', 'comodidad_mensual', 'equilibrio_hormonal', 'bienestar_emocional'],
        'energia': ['energia', 'enfoque', 'concentracion', 'claridad_mental', 'bienestar_cerebral', 'animo', 'animo_positivo', 'elevacion'],
        'inmunitario': ['bienestar_inmunologico', 'defensa_natural', 'respuesta_defensiva', 'proteccion_diaria', 'proteccion', 'bienestar_completo'],
    }

    relevant_cats = set(category_to_product_cats.get(category_id, []))

    for product in products:
        score = 0
        reasons = []

        # 1. Direct symptom tag matches (highest weight: 30 pts each)
        product_symptoms = set(product.get('sintomas_relacionados', []))
        symptom_matches = product_symptoms.intersection(selected_set)
        if symptom_matches:
            score += len(symptom_matches) * 30
            reasons.append(f"Coincide con {len(symptom_matches)} de tus síntomas")

        # 2. Category match (15 pts each matching category)
        product_cats = set(product.get('categoria', []))
        cat_matches = product_cats.intersection(relevant_cats)
        if cat_matches:
            score += len(cat_matches) * 15
            reasons.append(f"Especializado en {', '.join(cat_matches)}")

        # 3. Keyword match in description & benefits (5 pts each)
        desc_lower = product.get('descripcion', '').lower()
        benefits_text = ' '.join(product.get('beneficios', [])).lower()
        all_text = desc_lower + ' ' + benefits_text

        keyword_groups = {
            'digestivo': ['digestiv', 'estomac', 'intestin', 'abdomen', 'gastrointestinal'],
            'sueno': ['sueño', 'dormir', 'descanso', 'reparador', 'nocturno', 'relajante'],
            'tension': ['tensión', 'estrés', 'calma', 'relajación', 'tranquilidad', 'equilibrio emocional', 'ansiedad'],
            'muscular': ['muscul', 'articul', 'dolor', 'masaje', 'movimiento', 'recuper', 'inflam'],
            'respiratorio': ['respirat', 'pulmón', 'nasal', 'bronq', 'vías', 'pecho', 'despej'],
            'piel': ['piel', 'cutáne', 'facial', 'arruga', 'juvenil', 'hidrat', 'impureza'],
            'femenino': ['femenin', 'hormon', 'menstr', 'ciclo', 'mujer', 'mensual'],
            'energia': ['energía', 'vitalidad', 'enfoque', 'mental', 'concentr', 'vigor', 'rendimiento'],
            'inmunitario': ['inmun', 'defens', 'protec', 'purific', 'antioxid', 'resist'],
        }

        keywords = keyword_groups.get(category_id, [])
        for kw in keywords:
            if kw in all_text:
                score += 5
                break  # Only count once per product for keyword match

        # 4. Bonus for versatile products (multi-use: aromatic + topical + internal)
        uses_count = sum(1 for key in ['uso_aromatico', 'uso_topico', 'uso_interno'] if product.get(key))
        if uses_count >= 3:
            score += 3

        if score > 0:
            percentage = min(int((score / max(score, 60)) * 100), 98)  # Cap at 98%
            scores.append({
                'product': product,
                'score': score,
                'percentage': percentage,
                'reasons': reasons
            })

    # Sort by score descending
    scores.sort(key=lambda x: x['score'], reverse=True)

    # ALWAYS return at least 3 products
    if len(scores) < 3:
        # Fill with best products from the category that weren't already matched
        existing_ids = {s['product']['id'] for s in scores}
        for product in products:
            if product['id'] not in existing_ids:
                product_cats = set(product.get('categoria', []))
                if product_cats.intersection(relevant_cats):
                    scores.append({
                        'product': product,
                        'score': 10,
                        'percentage': 65,
                        'reasons': ['Recomendado para esta categoría de bienestar']
                    })
                    existing_ids.add(product['id'])
            if len(scores) >= 3:
                break

    # If STILL less than 3 (very unlikely), add top general products
    if len(scores) < 3:
        existing_ids = {s['product']['id'] for s in scores}
        essentials = ['lavender', 'peppermint', 'lemon', 'frankincense', 'melaleuca', 'oregano']
        for eid in essentials:
            for product in products:
                if product['id'] == eid and eid not in existing_ids:
                    scores.append({
                        'product': product,
                        'score': 5,
                        'percentage': 60,
                        'reasons': ['Aceite esencial versátil recomendado por expertos']
                    })
                    existing_ids.add(eid)
                    break
            if len(scores) >= 3:
                break

    return scores[:3]

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
    """Home page — Guía de Bienestar is front and center"""

    # Combined hero banner with CTA
    st.markdown("""
    <div class="hero" style="padding: 48px 20px 40px; margin-bottom: 28px;">
        <div class="hero-content">
            <h1 style="font-size: 2.4rem; margin-bottom: 20px; letter-spacing: -0.5px;">🌿 Nosotras Naturales</h1>
            <div style="width: 50px; height: 3px; background: rgba(255,255,255,0.5); border-radius: 2px; margin: 0 auto 22px;"></div>
            <h2 style="color: white; font-size: 1.65rem; margin-bottom: 10px; font-weight: 700; text-shadow: 0 1px 8px rgba(0,0,0,0.10);">
                Cuéntanos, ¿cómo te sientes hoy?
            </h2>
            <p style="color: rgba(255,255,255,0.92); font-size: 1.05rem; max-width: 500px; margin: 0 auto; line-height: 1.7;">
                Toca el área que quieres mejorar. En <strong style="color: #fff; background: rgba(255,255,255,0.18); padding: 1px 8px; border-radius: 10px;">menos de 2 minutos</strong>
                descubrirás los aceites esenciales ideales para ti.
            </p>
        </div>
    </div>
    """, unsafe_allow_html=True)

    # Category cards — 3 per row, entire card is clickable (no separate button)
    cols = st.columns(3)
    col_idx = 0

    for category in symptom_flow['categories']:
        with cols[col_idx % 3]:
            # The button IS the card — styled to look like the category card
            if st.button(
                f"{category.get('icono', '🌿')}\n\n**{category['nombre']}**\n\n{category['descripcion']}",
                key=f"home_cat_{category['id']}",
                use_container_width=True
            ):
                st.session_state.current_category = category['id']
                first_question = category['preguntas'][0]
                st.session_state.current_question = first_question['id']
                st.session_state.question_history = [first_question['id']]
                st.session_state.selected_tags = []
                st.session_state.symptom_flow_started = True
                st.session_state.page = 'guia_bienestar'
                st.rerun()

        col_idx += 1

    # ==========================================
    # SECONDARY SECTIONS — Below the fold
    # ==========================================
    st.markdown("<div style='margin-top: 40px;'></div>", unsafe_allow_html=True)
    st.markdown("---")

    # Why doTERRA — compact
    st.markdown("<h3 style='text-align: center; margin: 25px 0 15px;'>¿Por qué doTERRA?</h3>", unsafe_allow_html=True)

    col1, col2, col3 = st.columns(3)
    with col1:
        st.markdown("""
        <div class="feature-card" style="padding: 20px;">
            <div style="font-size: 28px; margin-bottom: 8px;">🌾</div>
            <h4 style="font-size: 1rem;">100% Puro</h4>
            <p style="font-size: 13px;">Grado terapéutico, sin aditivos</p>
        </div>
        """, unsafe_allow_html=True)
    with col2:
        st.markdown("""
        <div class="feature-card" style="padding: 20px;">
            <div style="font-size: 28px; margin-bottom: 8px;">🔬</div>
            <h4 style="font-size: 1rem;">Ciencia</h4>
            <p style="font-size: 13px;">Respaldado por investigación</p>
        </div>
        """, unsafe_allow_html=True)
    with col3:
        st.markdown("""
        <div class="feature-card" style="padding: 20px;">
            <div style="font-size: 28px; margin-bottom: 8px;">💚</div>
            <h4 style="font-size: 1rem;">Natural</h4>
            <p style="font-size: 13px;">Bienestar holístico integral</p>
        </div>
        """, unsafe_allow_html=True)

    # Quick links
    st.markdown("<div style='margin-top: 20px;'></div>", unsafe_allow_html=True)

    col1, col2, col3, col4 = st.columns(4)
    with col1:
        if st.button("📦 Catálogo", use_container_width=True, key="nav_catalog"):
            st.session_state.page = 'productos'
            st.rerun()
    with col2:
        st.markdown(f'<a href="{DOTERRA_SHOP_URL}" target="_blank" class="btn-primary" style="display: block; text-align: center; padding: 10px; font-size: 13px;">🛍️ Comprar</a>',
                   unsafe_allow_html=True)
    with col3:
        if st.button("💼 Únete", use_container_width=True, key="nav_opportunity"):
            st.session_state.page = 'unete_al_equipo'
            st.rerun()
    with col4:
        if st.button("🌸 Nosotras", use_container_width=True, key="nav_about"):
            st.session_state.page = 'sobre_nosotras'
            st.rerun()


def page_guia_bienestar():
    """Symptom checker page - Ubie style"""

    if not st.session_state.symptom_flow_started:
        # If user navigated here from sidebar without selecting a category,
        # show categories here too
        st.markdown("""
        <div style="text-align: center; padding: 20px 20px 10px;">
            <h2 style="color: #3D3229; font-size: 2rem; margin-bottom: 8px; font-weight: 700;">
                Cuéntanos, ¿cómo te sientes hoy?
            </h2>
            <p style="color: #666; font-size: 16px; max-width: 550px; margin: 0 auto; line-height: 1.7;">
                Toca el área que quieres mejorar. En <strong style="color: #7C9070;">menos de 2 minutos</strong>
                descubrirás los aceites esenciales ideales para ti.
            </p>
        </div>
        """, unsafe_allow_html=True)

        cols = st.columns(3)
        col_idx = 0

        for category in symptom_flow['categories']:
            with cols[col_idx % 3]:
                if st.button(
                    f"{category.get('icono', '🌿')}\n\n**{category['nombre']}**\n\n{category['descripcion']}",
                    key=f"cat_{category['id']}",
                    use_container_width=True
                ):
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
    """Expert results page with personalized product recommendations"""
    # Get the category name for the header
    category_name = ""
    category_icon = "🌿"
    for cat in symptom_flow['categories']:
        if cat['id'] == st.session_state.current_category:
            category_name = cat['nombre']
            category_icon = cat.get('icono', '🌿')
            break

    st.markdown(f"""
    <div class="hero" style="padding: 35px 20px; margin-bottom: 30px;">
        <div class="hero-content">
            <h1 style="font-size: 2.2rem;">Tu Plan de Bienestar Personalizado</h1>
            <p>{category_icon} Basado en tu evaluación de <strong>{category_name}</strong></p>
            <p class="subtitle" style="font-size: 14px;">Recomendaciones seleccionadas por nuestra experta en aceites esenciales</p>
        </div>
    </div>
    """, unsafe_allow_html=True)

    # Expert intro message
    st.markdown(f"""
    <div style="background: white; border-radius: 12px; padding: 20px; margin-bottom: 25px; border-left: 5px solid #7C9070; box-shadow: 0 2px 10px rgba(0,0,0,0.05);">
        <p style="font-size: 15px; color: #3D3229; margin: 0;">
            <strong>👩‍⚕️ Recomendación de Suzanna:</strong> Basándome en tus respuestas, he seleccionado los 3 productos
            doTERRA que mejor se adaptan a tus necesidades de <strong>{category_name.lower()}</strong>.
            Cada producto ha sido cuidadosamente evaluado considerando su composición, beneficios específicos
            y métodos de aplicación más efectivos para tu caso.
        </p>
    </div>
    """, unsafe_allow_html=True)

    # Calculate matches using the expert algorithm
    top_products = calculate_product_matches(
        st.session_state.selected_tags,
        products_data,
        st.session_state.current_category
    )

    # Display recommendations with expert ranking
    rank_labels = ["🥇 Recomendación Principal", "🥈 Excelente Alternativa", "🥉 Complemento Ideal"]

    for idx, match_data in enumerate(top_products):
        rank_label = rank_labels[idx] if idx < len(rank_labels) else f"Recomendación #{idx+1}"
        st.markdown(f"<h3 style='color: #7C9070; margin: 25px 0 10px;'>{rank_label}</h3>", unsafe_allow_html=True)

        # Build recommendation reason
        reasons = match_data.get('reasons', [])
        reason_text = ' · '.join(reasons) if reasons else f'Recomendado para {category_name.lower()}'

        st.markdown(
            create_product_card(
                match_data['product'],
                match_data['percentage'],
                reason_text
            ),
            unsafe_allow_html=True
        )

    # Expert tip section
    st.markdown(f"""
    <div style="background: linear-gradient(135deg, #F0E8D8, #FDF8F0); border-radius: 12px; padding: 25px; margin: 30px 0; border: 1px solid #D4C5A9;">
        <h4 style="color: #3D3229; margin-top: 0;">💡 Consejo de Experta</h4>
        <p style="color: #555; font-size: 14px; margin-bottom: 10px;">
            Para mejores resultados, te recomiendo combinar el <strong>uso aromático</strong> (difusor) con la
            <strong>aplicación tópica</strong> diluida. La constancia es clave — usa los aceites durante al menos
            2-3 semanas para experimentar todos sus beneficios.
        </p>
        <p style="color: #555; font-size: 14px; margin: 0;">
            ¿Tienes dudas sobre cuál elegir? Suzanna puede ayudarte a crear un plan personalizado
            según tu presupuesto y necesidades específicas.
        </p>
    </div>
    """, unsafe_allow_html=True)

    # CTA to contact Suzanna
    wa_msg = f"Hola Suzanna! 👋 Acabo de completar la guía de bienestar de {category_name} en Nosotras Naturales y me gustaría tu asesoría personalizada sobre los productos recomendados."
    wa_link = whatsapp_link(wa_msg)
    st.markdown(f"""
    <div style="text-align: center; margin: 20px 0;">
        <a href="{wa_link}" target="_blank" style="display: inline-block; background: #25D366; color: white;
           padding: 15px 40px; border-radius: 10px; text-decoration: none; font-weight: 700; font-size: 16px;
           box-shadow: 0 4px 15px rgba(37,211,102,0.3); transition: all 0.3s;">
            💬 Hablar con Suzanna sobre mi plan de bienestar
        </a>
    </div>
    """, unsafe_allow_html=True)

    render_fda_disclaimer()

    # Action buttons
    col1, col2, col3 = st.columns([1, 1, 1])
    with col1:
        if st.button("🔄 Nueva Evaluación", use_container_width=True, key="restart_symptom"):
            st.session_state.symptom_flow_started = False
            st.session_state.current_category = None
            st.session_state.current_question = None
            st.session_state.selected_tags = []
            st.session_state.question_history = []
            st.session_state.page = 'guia_bienestar'
            st.rerun()
    with col2:
        if st.button("📦 Ver Catálogo Completo", use_container_width=True, key="go_catalog"):
            st.session_state.page = 'productos'
            st.rerun()
    with col3:
        if st.button("🏠 Ir al Inicio", use_container_width=True, key="go_home"):
            st.session_state.page = 'inicio'
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
# HORIZONTAL TOP NAV BAR
# ============================================

# Hide the default Streamlit sidebar completely
st.markdown("""
<style>
    /* ===== HIDE SIDEBAR COMPLETELY ===== */
    [data-testid="stSidebar"],
    [data-testid="collapsedControl"],
    button[kind="header"] {
        display: none !important;
        visibility: hidden !important;
        width: 0 !important;
        min-width: 0 !important;
    }
    /* Make main content full-width */
    [data-testid="stAppViewBlockContainer"] {
        max-width: 1100px;
        padding-left: 1rem;
        padding-right: 1rem;
    }
</style>
""", unsafe_allow_html=True)

nav_options = {
    "🏠 Inicio": "inicio",
    "🌿 Guía": "guia_bienestar",
    "📦 Productos": "productos",
    "🌎 Latinoamérica": "latam",
    "💼 Únete": "unete_al_equipo",
    "🌸 Nosotras": "sobre_nosotras",
    "👩‍💼 Dashboard": "dashboard",
}

# Reverse map to find the label for the current page
page_to_label = {v: k for k, v in nav_options.items()}
# Pages not in nav (resultado_sintomas) default to Guía highlight
current_label = page_to_label.get(st.session_state.page, "🌿 Guía")

selected_label = st.radio(
    "nav",
    options=list(nav_options.keys()),
    index=list(nav_options.keys()).index(current_label) if current_label in nav_options else 0,
    horizontal=True,
    label_visibility="collapsed",
    key="top_nav_radio"
)

# Navigate when selection changes (only if user explicitly clicked a different tab)
selected_page = nav_options[selected_label]
if selected_page != st.session_state.page and selected_page != page_to_label.get(st.session_state.page, ""):
    # Don't redirect if current page is resultado_sintomas and Guía is highlighted
    if not (st.session_state.page == 'resultado_sintomas' and selected_page == 'guia_bienestar'):
        st.session_state.page = selected_page
        if selected_page not in ('guia_bienestar', 'resultado_sintomas'):
            st.session_state.symptom_flow_started = False
            st.session_state.current_category = None
            st.session_state.current_question = None
            st.session_state.selected_tags = []
            st.session_state.question_history = []
        st.rerun()

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
