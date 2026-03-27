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
import re
import urllib.parse
from datetime import datetime
import requests
from bs4 import BeautifulSoup

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
DASHBOARD_PASSWORD = "Suzzana"

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
# PRODUCT DATA FILE PATH
# ============================================
PRODUCTS_JSON_PATH = os.path.join(os.path.dirname(__file__), "data", "products.json")

def save_products(data):
    """Save products data to JSON file."""
    with open(PRODUCTS_JSON_PATH, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

def scrape_doterra_product(url):
    """Scrape product data from a doTERRA product page URL.
    Returns dict with 'success' bool and 'data' dict or 'error' string.
    Extracts: imagen_url, precio_usd, precio_mayoreo, doterra_sku, pv, infografia_url, descripcion.
    """
    try:
        clean_url = url.split('?')[0]  # Remove tracking params
        headers = {
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Accept-Language': 'es-EC,es;q=0.9',
        }
        response = requests.get(clean_url, headers=headers, timeout=15)
        response.raise_for_status()

        soup = BeautifulSoup(response.text, 'lxml')
        data = {}
        data['doterra_url'] = clean_url

        # og:image for product photo
        og_img = soup.find('meta', {'property': 'og:image'})
        if og_img and og_img.get('content'):
            img_url = og_img['content']
            if not img_url.startswith('http'):
                img_url = 'https://www.doterra.com' + img_url
            data['imagen_url'] = img_url

        # Better image: look for 2x3 background-image divs (higher res product bottle)
        for div in soup.find_all('div', style=True):
            style = div.get('style', '')
            if 'background-image' in style and '2x3' in style:
                bg_match = re.search(r'url\(["\']?(.*?)["\']?\)', style)
                if bg_match:
                    img_url = bg_match.group(1)
                    if img_url.startswith('/'):
                        img_url = 'https://www.doterra.com' + img_url
                    data['imagen_url'] = img_url
                    break

        # Text content for prices and SKU
        page_text = soup.get_text()

        # Retail price: "Menudeo: $38.00"
        retail_match = re.search(r'Menudeo:\s*\$([\d,.]+)', page_text)
        if retail_match:
            data['precio_usd'] = float(retail_match.group(1).replace(',', ''))

        # Wholesale: "Mayoreo: $28.50"
        wholesale_match = re.search(r'Mayoreo:\s*\$([\d,.]+)', page_text)
        if wholesale_match:
            data['precio_mayoreo'] = float(wholesale_match.group(1).replace(',', ''))

        # SKU: "Artículo: 60202061"
        sku_match = re.search(r'Art[ií]culo:\s*(\d+)', page_text)
        if sku_match:
            data['doterra_sku'] = sku_match.group(1)

        # PV
        pv_match = re.search(r'PV:\s*([\d.]+)', page_text)
        if pv_match:
            data['pv'] = float(pv_match.group(1))

        # Infographic PDF link — look for "Ver infografía" or any infographic PDF
        for a in soup.find_all('a', href=True):
            href = a.get('href', '')
            if '.pdf' in href.lower() and ('infographic' in href.lower() or 'infografia' in href.lower()):
                if not href.startswith('http'):
                    href = 'https://media.doterra.com' + href
                data['infografia_url'] = href
                break

        # og:description as fallback description
        og_desc = soup.find('meta', {'property': 'og:description'})
        if og_desc and og_desc.get('content'):
            data['og_descripcion'] = og_desc['content']

        return {'success': True, 'data': data}

    except requests.exceptions.RequestException as e:
        return {'success': False, 'error': f'Error de red: {str(e)}'}
    except Exception as e:
        return {'success': False, 'error': f'Error: {str(e)}'}

# ============================================
# UTILITY FUNCTIONS
# ============================================

def whatsapp_link(message):
    """Create WhatsApp link with URL-encoded message"""
    encoded = urllib.parse.quote(message)
    return f"https://wa.me/{WHATSAPP_NUMBER}?text={encoded}"

def get_product_icon(product):
    """Return an emoji icon based on product type/category."""
    tipo = product.get('tipo', '').lower()
    nombre = product.get('nombre', '').lower()
    cats = ' '.join(product.get('categoria', []))
    if 'blend' in tipo or 'mezcla' in tipo:
        return '🌸'
    if 'roll-on' in tipo or 'rollon' in nombre:
        return '🫧'
    if any(x in cats for x in ['digestion', 'digestiv']):
        return '🍃'
    if any(x in cats for x in ['respiracion', 'respirat']):
        return '💨'
    if any(x in cats for x in ['sueño', 'relajacion']):
        return '🌙'
    if any(x in cats for x in ['energia', 'enfoque']):
        return '⚡'
    if any(x in cats for x in ['piel', 'autocuidado']):
        return '✨'
    if any(x in cats for x in ['inmunolog', 'defensa', 'proteccion']):
        return '🛡️'
    return '🌿'

def create_product_card(product, match_percentage=None, recommendation_reason=None, rank=None):
    """Create a clean, compact product card with all essential info.
    IMPORTANT: Only use div, span, and a tags — Streamlit's st.markdown breaks on
    img, details, summary, ul, li, p, strong, h3 etc. No f-string indentation (4+ spaces
    triggers markdown code blocks). Hardcode all colors (no CSS variables).
    """
    price_display = f"${product.get('precio_usd', 'N/A')}"
    pv_display = product.get('pv', '')
    comprar_link = DOTERRA_SHOP_URL
    consult_msg = f"Hola Suzanna! Me interesa {product['nombre']} ({product.get('nombre_en', '')}). ¿Me puedes dar más información?"
    consult_link = whatsapp_link(consult_msg)
    icon = get_product_icon(product)
    imagen_url = product.get('imagen_url', '')

    # Image: CSS background-image for real photos, emoji fallback
    if imagen_url and 'doterra.com/medias/' in imagen_url:
        image_html = f'<div style="width:80px;height:80px;background:url({imagen_url}) center/contain no-repeat;background-color:#f9f6f0;border-radius:12px;flex-shrink:0;"></div>'
    else:
        image_html = f'<div style="width:80px;height:80px;background:linear-gradient(135deg,#e8f0e4,#f0ead8);border-radius:12px;display:flex;align-items:center;justify-content:center;font-size:34px;">{icon}</div>'

    # Rank label
    rank_labels = {1: '🥇 Mejor opción', 2: '🥈 Excelente alternativa', 3: '🥉 También recomendado'}
    rank_html = f'<div style="font-size:12px;font-weight:700;color:#7C9070;margin-bottom:6px;">{rank_labels.get(rank, "")}</div>' if rank else ''

    # Match badge
    match_html = ''
    if match_percentage:
        match_html = f'<span style="background:linear-gradient(135deg,#7C9070,#B8965A);color:white;padding:4px 12px;border-radius:20px;font-size:12px;font-weight:600;">{match_percentage}%</span>'

    # Recommendation reason (sanitize underscores to prevent markdown interpretation)
    reason_text = recommendation_reason.replace('_', ' ') if recommendation_reason else ''
    reason_html = f'<div style="background:rgba(124,144,112,0.08);color:#7C9070;padding:8px 12px;border-radius:8px;font-size:13px;font-weight:500;margin-bottom:12px;border-left:3px solid #7C9070;">{reason_text}</div>' if reason_text else ''

    # Wholesale price
    precio_mayoreo = product.get('precio_mayoreo', '')
    mayoreo_html = f'<span style="color:#999;font-size:12px;text-decoration:line-through;">${precio_mayoreo}</span>' if precio_mayoreo else ''

    # Benefits as divs (no ul/li)
    benefits = product.get('beneficios', [])[:4]
    benefits_html = ''.join([f'<div style="color:#666;font-size:13px;padding:2px 0;">• {b}</div>' for b in benefits])

    # Usage method badges
    usos = []
    if product.get('uso_aromatico'):
        usos.append('<span style="display:inline-flex;align-items:center;gap:4px;font-size:12px;color:#777;background:#f5f0e6;padding:4px 10px;border-radius:6px;">🌬️ Aromático</span>')
    if product.get('uso_topico'):
        usos.append('<span style="display:inline-flex;align-items:center;gap:4px;font-size:12px;color:#777;background:#f5f0e6;padding:4px 10px;border-radius:6px;">✋ Tópico</span>')
    if product.get('uso_interno'):
        usos.append('<span style="display:inline-flex;align-items:center;gap:4px;font-size:12px;color:#777;background:#f5f0e6;padding:4px 10px;border-radius:6px;">💧 Interno</span>')
    usos_html = f'<div style="display:flex;gap:6px;flex-wrap:wrap;margin-bottom:12px;">{"".join(usos)}</div>' if usos else ''

    # Category badges (sanitize underscores)
    cat_badges = ''.join([f'<span style="background:#eee;color:#888;padding:2px 8px;border-radius:10px;font-size:11px;">{cat.replace("_", " ").title()}</span>' for cat in product.get('categoria', [])[:3]])

    # Detailed usage section (replaces details/summary with always-visible div)
    uso_details = []
    if product.get('uso_aromatico'):
        uso_details.append(f'<div style="margin-bottom:4px;"><span style="color:#7C9070;font-weight:700;">🌬️ Aromático:</span> {product["uso_aromatico"]}</div>')
    if product.get('uso_topico'):
        uso_details.append(f'<div style="margin-bottom:4px;"><span style="color:#7C9070;font-weight:700;">✋ Tópico:</span> {product["uso_topico"]}</div>')
    if product.get('uso_interno'):
        uso_details.append(f'<div style="margin-bottom:4px;"><span style="color:#7C9070;font-weight:700;">💧 Interno:</span> {product["uso_interno"]}</div>')
    details_section = ''
    if benefits or uso_details:
        details_section = (
            '<div style="margin-bottom:14px;padding:10px 14px;background:#faf8f5;border-radius:10px;border:1px solid #eee;">'
            '<div style="color:#7C9070;font-weight:600;font-size:14px;margin-bottom:8px;">Beneficios y usos</div>'
            f'{benefits_html}'
            f'<div style="margin-top:8px;font-size:13px;color:#666;line-height:1.7;">{"".join(uso_details)}</div>'
            '</div>'
        )

    # Sanitize description (replace underscores)
    descripcion = product['descripcion'].replace('_', ' ')

    # Build card — NO indentation, only div/span/a tags, hardcoded colors
    html = (
        '<div style="background:white;border-radius:16px;padding:24px;margin-bottom:18px;'
        'box-shadow:0 2px 12px rgba(60,50,41,0.07);border:1px solid rgba(0,0,0,0.04);">'
        '<div style="display:flex;align-items:flex-start;gap:18px;margin-bottom:14px;">'
        f'<div style="flex-shrink:0;">{image_html}</div>'
        '<div style="flex:1;min-width:0;">'
        f'{rank_html}'
        '<div style="display:flex;align-items:center;gap:10px;flex-wrap:wrap;">'
        f'<div style="margin:0;font-size:1.15rem;font-weight:700;color:#3D3229;">{product["nombre"]}</div>'
        f'<span style="color:#aaa;font-size:13px;">{product.get("nombre_en", "")}</span>'
        f'{match_html}'
        '</div>'
        '<div style="display:flex;align-items:baseline;gap:12px;margin-top:4px;">'
        f'<span style="font-size:1.4rem;font-weight:700;color:#C67B4F;">{price_display}</span>'
        f'{mayoreo_html}'
        f'<span style="color:#bbb;font-size:12px;">PV: {pv_display}</span>'
        '</div>'
        '</div>'
        '</div>'
        f'{reason_html}'
        f'<div style="color:#666;font-size:14px;line-height:1.6;margin-bottom:12px;">{descripcion}</div>'
        f'{usos_html}'
        f'<div style="display:flex;gap:6px;flex-wrap:wrap;margin-bottom:12px;">{cat_badges}</div>'
        f'{details_section}'
        '<div style="display:flex;gap:10px;">'
        f'<a href="{comprar_link}" target="_blank" style="flex:1;text-align:center;padding:11px 16px;'
        'background:linear-gradient(135deg,#7C9070,#B8965A);color:white;border-radius:10px;'
        'font-weight:600;font-size:14px;text-decoration:none;">🛒 Comprar</a>'
        f'<a href="{consult_link}" target="_blank" style="flex:1;text-align:center;padding:11px 16px;'
        'background:#25D366;color:white;border-radius:10px;font-weight:600;font-size:14px;'
        'text-decoration:none;">💬 Consultar</a>'
        '</div>'
        '</div>'
    )
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
# NAVIGATION HELPER — keeps radio in sync
# ============================================

# Map page keys to radio labels
PAGE_TO_RADIO = {
    'inicio': "🏠 Inicio",
    'guia_bienestar': "🌿 Guía",
    'resultado_sintomas': "🌿 Guía",
    'productos': "📦 Productos",
    'latam': "🌎 Latinoamérica",
    'unete_al_equipo': "💼 Únete",
    'sobre_nosotras': "🌸 Nosotras",
    'dashboard': "👩‍💼 Dashboard",
}

def navigate_to(page_key):
    """Navigate to a page. Sets a pending nav so radio syncs before render."""
    st.session_state.page = page_key
    st.session_state._pending_nav = PAGE_TO_RADIO.get(page_key, "🏠 Inicio")
    st.rerun()

# ============================================
# PAGE FUNCTIONS
# ============================================

def page_inicio():
    """Home page — Guía de Bienestar is front and center"""

    # Compact hero banner
    st.markdown("""
    <div class="hero">
        <div class="hero-content">
            <div style="display: flex; align-items: center; justify-content: center; gap: 16px; flex-wrap: wrap;">
                <div style="text-align: left;">
                    <h2 style="font-size: 1.35rem; margin: 0 0 4px; font-weight: 700;">Cuéntanos, ¿cómo te sientes hoy?</h2>
                    <p style="font-size: 0.88rem; margin: 0; opacity: 0.85;">
                        Elige un área abajo · En <strong style="background: rgba(255,255,255,0.15); padding: 1px 8px; border-radius: 8px;">2 min</strong> descubrirás tus aceites ideales
                    </p>
                </div>
            </div>
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
                navigate_to('guia_bienestar')

        col_idx += 1

    # ==========================================
    # SECONDARY SECTIONS — Below the fold
    # ==========================================
    st.markdown("""
    <div style="margin-top: 48px; text-align: center;">
        <h3 style="color: var(--text); font-size: 1.4rem; margin-bottom: 6px;">¿Por qué doTERRA?</h3>
        <p style="color: #999; font-size: 14px; margin-bottom: 20px;">Calidad que puedes sentir en cada gota</p>
    </div>
    """, unsafe_allow_html=True)

    col1, col2, col3 = st.columns(3)
    with col1:
        st.markdown("""
        <div class="feature-card" style="padding: 22px; text-align: center; border-left: none; border-top: 3px solid var(--primary);">
            <div style="font-size: 30px; margin-bottom: 10px;">🌾</div>
            <h4 style="font-size: 1rem; margin-bottom: 6px;">100% Puro</h4>
            <p style="font-size: 13px; color: #888;">Grado terapéutico CPTG, sin aditivos ni sintéticos</p>
        </div>
        """, unsafe_allow_html=True)
    with col2:
        st.markdown("""
        <div class="feature-card" style="padding: 22px; text-align: center; border-left: none; border-top: 3px solid var(--gold);">
            <div style="font-size: 30px; margin-bottom: 10px;">🔬</div>
            <h4 style="font-size: 1rem; margin-bottom: 6px;">Ciencia</h4>
            <p style="font-size: 13px; color: #888;">Respaldado por investigación y pruebas rigurosas</p>
        </div>
        """, unsafe_allow_html=True)
    with col3:
        st.markdown("""
        <div class="feature-card" style="padding: 22px; text-align: center; border-left: none; border-top: 3px solid var(--terracotta);">
            <div style="font-size: 30px; margin-bottom: 10px;">💚</div>
            <h4 style="font-size: 1rem; margin-bottom: 6px;">Natural</h4>
            <p style="font-size: 13px; color: #888;">Bienestar holístico e integral para tu cuerpo</p>
        </div>
        """, unsafe_allow_html=True)


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
                                    navigate_to('resultado_sintomas')
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
        # Build recommendation reason
        reasons = match_data.get('reasons', [])
        reason_text = ' · '.join(reasons) if reasons else f'Recomendado para {category_name.lower()}'

        st.markdown(
            create_product_card(
                match_data['product'],
                match_data['percentage'],
                reason_text,
                rank=idx + 1
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
            navigate_to('guia_bienestar')
    with col2:
        if st.button("📦 Ver Catálogo Completo", use_container_width=True, key="go_catalog"):
            navigate_to('productos')
    with col3:
        if st.button("🏠 Ir al Inicio", use_container_width=True, key="go_home"):
            navigate_to('inicio')


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
    st.caption("Pega el link de cada producto de doTERRA Ecuador y haz clic en Guardar para actualizar la información automáticamente.")

    # Search/filter
    search_term = st.text_input("🔍 Buscar producto:", placeholder="Escribe el nombre del producto...", key="dash_search")

    filtered = products_data
    if search_term:
        term = search_term.lower()
        filtered = [p for p in products_data if term in p['nombre'].lower() or term in p.get('nombre_en', '').lower()]

    st.markdown(f"<p style='color: #888; font-size: 14px;'>Mostrando {len(filtered)} de {len(products_data)} productos</p>", unsafe_allow_html=True)

    # Initialize session state for scrape messages
    if 'scrape_msg' not in st.session_state:
        st.session_state.scrape_msg = {}

    # Editable product cards in dashboard
    for p in filtered:
        pid = p['id']
        img_url = p.get('imagen_url', '')
        mayoreo = p.get('precio_mayoreo', '')
        mayoreo_str = f" | Mayoreo: ${mayoreo}" if mayoreo else ""
        sku = p.get('doterra_sku', '')
        cats = ', '.join([c.replace('_', ' ') for c in p.get('categoria', [])[:3]])
        infografia = p.get('infografia_url', '')
        current_url = p.get('doterra_url', '')

        with st.expander(f"{'✅' if current_url else '⚠️'} {p['nombre']} ({p.get('nombre_en', '')}) — ${p.get('precio_usd', 'N/A')}", expanded=False):
            # Product info header with image
            col_img, col_info = st.columns([1, 4])
            with col_img:
                if img_url and 'doterra.com' in img_url:
                    st.markdown(
                        f'<div style="width:70px;height:70px;background:url({img_url}) center/contain no-repeat;background-color:#f9f6f0;border-radius:10px;"></div>',
                        unsafe_allow_html=True
                    )
                else:
                    st.markdown('<div style="width:70px;height:70px;display:flex;align-items:center;justify-content:center;font-size:28px;background:#f5f0e6;border-radius:10px;">📦</div>', unsafe_allow_html=True)
            with col_info:
                st.markdown(f"**SKU:** {sku} &nbsp;|&nbsp; **PV:** {p.get('pv', '')} &nbsp;|&nbsp; **Menudeo:** ${p.get('precio_usd', 'N/A')} &nbsp;|&nbsp; **Mayoreo:** ${mayoreo or 'N/A'}")
                st.markdown(f"**Categorías:** {cats}")

            # Editable URL input
            new_url = st.text_input(
                "Link de doTERRA Ecuador:",
                value=current_url,
                placeholder="https://www.doterra.com/EC/es_EC/p/...",
                key=f"url_{pid}"
            )

            # Action buttons row
            col_save, col_pdf, col_status = st.columns([1, 1, 2])

            with col_save:
                if st.button("💾 Guardar y Actualizar", key=f"save_{pid}"):
                    if new_url and 'doterra.com' in new_url:
                        with st.spinner(f"Actualizando {p['nombre']}..."):
                            result = scrape_doterra_product(new_url)
                            if result['success']:
                                scraped = result['data']
                                # Update product in products_data (in memory)
                                for prod in products_data:
                                    if prod['id'] == pid:
                                        prod['doterra_url'] = scraped.get('doterra_url', new_url.split('?')[0])
                                        if scraped.get('imagen_url'):
                                            prod['imagen_url'] = scraped['imagen_url']
                                        if scraped.get('precio_usd'):
                                            prod['precio_usd'] = scraped['precio_usd']
                                        if scraped.get('precio_mayoreo'):
                                            prod['precio_mayoreo'] = scraped['precio_mayoreo']
                                        if scraped.get('doterra_sku'):
                                            prod['doterra_sku'] = scraped['doterra_sku']
                                        if scraped.get('pv'):
                                            prod['pv'] = scraped['pv']
                                        if scraped.get('infografia_url'):
                                            prod['infografia_url'] = scraped['infografia_url']
                                        break
                                # Save to file
                                try:
                                    save_products(products_data)
                                    # Clear cache so next reload picks up changes
                                    load_products.clear()
                                    fields_updated = ', '.join(scraped.keys())
                                    st.session_state.scrape_msg[pid] = ('success', f"Actualizado: {fields_updated}")
                                except Exception as e:
                                    st.session_state.scrape_msg[pid] = ('error', f"Error al guardar: {e}")
                            else:
                                st.session_state.scrape_msg[pid] = ('error', result['error'])
                        st.rerun()
                    elif new_url:
                        st.warning("El link debe ser de doterra.com")
                    else:
                        # Just save the URL field even if empty (to clear it)
                        for prod in products_data:
                            if prod['id'] == pid:
                                prod.pop('doterra_url', None)
                                break
                        save_products(products_data)
                        load_products.clear()

            with col_pdf:
                if infografia:
                    st.markdown(
                        f'<a href="{infografia}" target="_blank" style="display:inline-block;padding:8px 16px;background:#7C9070;color:white;border-radius:8px;text-decoration:none;font-size:14px;font-weight:600;">📄 Infografía PDF</a>',
                        unsafe_allow_html=True
                    )
                else:
                    st.markdown('<span style="color:#bbb;font-size:13px;">Sin infografía</span>', unsafe_allow_html=True)

            with col_status:
                # Show scrape result message
                if pid in st.session_state.scrape_msg:
                    msg_type, msg_text = st.session_state.scrape_msg[pid]
                    if msg_type == 'success':
                        st.success(f"✅ {msg_text}")
                    else:
                        st.error(f"❌ {msg_text}")

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
            navigate_to('unete_al_equipo')


# ============================================
# HORIZONTAL TOP NAV BAR
# ============================================

# Hide the default Streamlit sidebar completely
st.markdown("""
<style>
    /* ===== HIDE SIDEBAR, HEADER, DEPLOY BUTTON ===== */
    [data-testid="stSidebar"],
    [data-testid="collapsedControl"],
    button[kind="header"],
    header[data-testid="stHeader"],
    .stDeployButton,
    #MainMenu {
        display: none !important;
        visibility: hidden !important;
        height: 0 !important;
        width: 0 !important;
        overflow: hidden !important;
        position: absolute !important;
    }

    /* ===== NUKE ALL TOP SPACING — every Streamlit wrapper ===== */
    html, body, [data-testid="stAppViewContainer"],
    .stApp, [data-testid="stAppViewBlockContainer"],
    .main, .block-container, section[data-testid="stMain"],
    section[data-testid="stMain"] > div {
        padding-top: 0 !important;
        margin-top: 0 !important;
    }
    [data-testid="stAppViewBlockContainer"] {
        max-width: 100% !important;
        padding: 0 !important;
    }
    /* ONLY the top-level vertical block gets gap: 0 (for nav flush to top).
       Inner vertical blocks keep normal spacing for content. */
    [data-testid="stAppViewBlockContainer"] > [data-testid="stVerticalBlock"] {
        gap: 0 !important;
    }
    /* First few wrapper divs (style injection + radio) — no top space */
    [data-testid="stAppViewBlockContainer"] > [data-testid="stVerticalBlock"] > div:first-child,
    [data-testid="stAppViewBlockContainer"] > [data-testid="stVerticalBlock"] > div:nth-child(2),
    [data-testid="stAppViewBlockContainer"] > [data-testid="stVerticalBlock"] > div:nth-child(3) {
        padding-top: 0 !important;
        margin-top: 0 !important;
    }
    /* Restore normal spacing inside content areas */
    .main-content-wrapper [data-testid="stVerticalBlock"] {
        gap: 1rem !important;
    }
    /* Element container around radio */
    [data-testid="stElementContainer"]:has([data-testid="stRadio"]) {
        padding: 0 !important;
        margin: 0 !important;
        width: 100% !important;
    }
    /* Content below nav gets centered padding */
    .main-content-wrapper {
        max-width: 1100px;
        margin: 0 auto;
        padding: 20px 1.5rem 0;
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

def on_nav_change():
    """Callback when user clicks a radio nav item."""
    selected = st.session_state.top_nav_radio
    page_key = nav_options.get(selected, 'inicio')
    if page_key != st.session_state.page:
        st.session_state.page = page_key
        if page_key not in ('guia_bienestar', 'resultado_sintomas'):
            st.session_state.symptom_flow_started = False
            st.session_state.current_category = None
            st.session_state.current_question = None
            st.session_state.selected_tags = []
            st.session_state.question_history = []

# Apply pending navigation (from navigate_to) BEFORE radio renders
if '_pending_nav' in st.session_state:
    st.session_state.top_nav_radio = st.session_state._pending_nav
    del st.session_state._pending_nav
elif 'top_nav_radio' not in st.session_state:
    st.session_state.top_nav_radio = PAGE_TO_RADIO.get(st.session_state.page, "🏠 Inicio")

st.radio(
    "nav",
    options=list(nav_options.keys()),
    horizontal=True,
    label_visibility="collapsed",
    key="top_nav_radio",
    on_change=on_nav_change
)

# ============================================
# MAIN APP LOGIC (wrapped in centered container)
# ============================================

st.markdown('<div class="main-content-wrapper">', unsafe_allow_html=True)

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

st.markdown('</div>', unsafe_allow_html=True)

# Footer
wa_footer = whatsapp_link("Hola Suzanna! Me interesa saber más sobre doTERRA.")
st.markdown(f"""
<div style="background: linear-gradient(135deg, #3D3229 0%, #5a4a3a 100%); padding: 30px 20px; margin-top: 40px; text-align: center;">
    <p style="color: rgba(255,255,255,0.6); font-size: 12px; margin-bottom: 8px;">
        Nosotras Naturales © 2024 · Aceites Esenciales doTERRA de Grado Terapéutico
    </p>
    <a href="{wa_footer}" target="_blank"
       style="color: #25D366; font-size: 13px; font-weight: 600; text-decoration: none;">
       📱 Contacta a Suzanna Valles por WhatsApp
    </a>
</div>
""", unsafe_allow_html=True)
