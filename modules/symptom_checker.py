"""
Symptom Checker Module - Ubie-style conversational symptom checker for doTERRA essential oils.
Provides interactive wellness category selection, progressive questioning, and personalized product recommendations.
"""

import streamlit as st
import json
from typing import Dict, List, Set, Tuple
import urllib.parse


# ============================================================================
# TAG MATCHING & RESULT LOGIC
# ============================================================================

def find_best_result(accumulated_tags: List[Set[str]], resultados: Dict) -> Tuple[str, Dict]:
    """
    Find the best matching result based on accumulated tags.
    Uses set intersection scoring to match tag combinations.

    Args:
        accumulated_tags: List of tag sets from each answer
        resultados: Dict mapping tag combinations to results

    Returns:
        (key, result_data) tuple, or (None, {}) if no match found
    """
    if not accumulated_tags:
        return None, {}

    # Flatten and combine all tags
    all_tags = set()
    for tag_set in accumulated_tags:
        all_tags.update(tag_set)

    best_match = None
    best_score = 0

    for result_key, result_data in resultados.items():
        # Split the key by '+' to get individual tag components
        result_tags = set(result_key.split('+'))

        # Calculate intersection score
        intersection = all_tags.intersection(result_tags)
        score = len(intersection)

        if score > best_score:
            best_score = score
            best_match = (result_key, result_data)

    return best_match if best_match else (None, {})


def get_question_by_id(categories: List[Dict], question_id: str) -> Dict:
    """
    Retrieve a question object by its ID from the categories structure.

    Args:
        categories: List of category dictionaries
        question_id: The ID of the question to find

    Returns:
        Question dictionary or empty dict if not found
    """
    for category in categories:
        for question in category.get('preguntas', []):
            if question['id'] == question_id:
                return question
    return {}


def get_category_by_id(categories: List[Dict], category_id: str) -> Dict:
    """
    Retrieve a category object by its ID.

    Args:
        categories: List of category dictionaries
        category_id: The ID of the category to find

    Returns:
        Category dictionary or empty dict if not found
    """
    for category in categories:
        if category['id'] == category_id:
            return category
    return {}


# ============================================================================
# STREAMLIT UI COMPONENTS
# ============================================================================

def render_category_cards(categories: List[Dict]) -> str:
    """
    Render 9 wellness category cards in a 3x3 grid.

    Args:
        categories: List of category dictionaries with id, nombre, icono, descripcion

    Returns:
        Selected category ID or None
    """
    st.markdown("### Selecciona tu área de bienestar")
    st.markdown(
        "Elige la categoría que mejor describe tus necesidades de salud y bienestar.",
        help="Puedes cambiar de categoría en cualquier momento"
    )

    # Create 3x3 grid
    cols = st.columns(3)
    selected_category = None

    for idx, category in enumerate(categories):
        col_idx = idx % 3

        with cols[col_idx]:
            # Create styled card button
            button_key = f"cat_btn_{category['id']}"

            # Use columns to create a bordered card effect
            card_col = st.container(border=True)
            with card_col:
                st.markdown(
                    f"<div style='text-align: center; padding: 20px;'>"
                    f"<div style='font-size: 48px; margin-bottom: 10px;'>{category['icono']}</div>"
                    f"<div style='font-size: 18px; font-weight: bold; margin-bottom: 8px;'>{category['nombre']}</div>"
                    f"<div style='font-size: 13px; color: #666;'>{category['descripcion']}</div>"
                    f"</div>",
                    unsafe_allow_html=True
                )

                if st.button(
                    "Seleccionar",
                    key=button_key,
                    use_container_width=True,
                    type="primary"
                ):
                    selected_category = category['id']
                    st.session_state.selected_category = category['id']
                    st.session_state.current_step = "questions"
                    st.session_state.current_question_id = category['preguntas'][0]['id']
                    st.session_state.answers = []
                    st.session_state.accumulated_tags = []

        # Add a spacer row for better visual organization
        if col_idx == 2 and idx < len(categories) - 1:
            st.divider()

    return selected_category


def render_progress_bar(current_step: int, total_steps: int):
    """
    Render a progress bar showing current step progress.

    Args:
        current_step: Current question number (1-indexed)
        total_steps: Total number of questions
    """
    progress = (current_step - 1) / (total_steps - 1) if total_steps > 1 else 1.0

    col1, col2 = st.columns([4, 1])
    with col1:
        st.progress(progress, text=f"Paso {current_step} de {total_steps}")
    with col2:
        st.caption(f"{int(progress * 100)}%")


def render_question(question: Dict, step_num: int, total_steps: int) -> str:
    """
    Render a question with clickable option cards.

    Args:
        question: Question dictionary with texto and opciones
        step_num: Current step number
        total_steps: Total number of steps

    Returns:
        The selected option's "siguiente" value or None
    """
    render_progress_bar(step_num, total_steps)

    st.markdown(f"### {question['texto']}")

    selected_next = None

    # Render options as clickable cards in a 2-column layout
    opciones = question.get('opciones', [])
    cols_per_row = 2 if len(opciones) <= 4 else 1

    for idx, opcion in enumerate(opciones):
        if idx % cols_per_row == 0:
            cols = st.columns(cols_per_row)

        col_idx = idx % cols_per_row

        with cols[col_idx]:
            card = st.container(border=True)
            with card:
                # Center the text and make it clickable
                st.markdown(
                    f"<div style='text-align: left; padding: 10px;'>{opcion['texto']}</div>",
                    unsafe_allow_html=True
                )

                button_key = f"opt_btn_{question['id']}_{idx}"
                if st.button(
                    "Seleccionar opción",
                    key=button_key,
                    use_container_width=True,
                    type="secondary"
                ):
                    # Store the answer
                    st.session_state.answers.append({
                        'question_id': question['id'],
                        'option_text': opcion['texto'],
                        'tags': opcion.get('tags', [])
                    })

                    # Accumulate tags
                    st.session_state.accumulated_tags.append(set(opcion.get('tags', [])))

                    # Determine next step
                    siguiente = opcion.get('siguiente')
                    if siguiente == 'resultado':
                        st.session_state.current_step = 'results'
                    else:
                        st.session_state.current_question_id = siguiente

                    st.rerun()

    return selected_next


def render_results(
    products_data: List[Dict],
    accumulated_tags: List[Set[str]],
    resultado_data: Dict,
    category: Dict,
    whatsapp_number: str = "593984949487"
) -> None:
    """
    Render personalized product recommendations with descriptions, benefits, and CTAs.

    Args:
        products_data: List of product dictionaries
        accumulated_tags: List of tag sets from answers
        resultado_data: Result data containing products_recomendados, mensaje, consejo
        category: Selected category dictionary
        whatsapp_number: WhatsApp contact number (default Suzanna)
    """
    # Create a products lookup dictionary
    products_by_id = {p['id']: p for p in products_data}

    st.markdown("### 🎯 Recomendaciones Personalizadas")

    # Display personalized message
    if resultado_data.get('mensaje'):
        st.info(resultado_data['mensaje'])

    # Display products
    productos_ids = resultado_data.get('productos_recomendados', [])

    if productos_ids:
        st.markdown("#### Productos Recomendados")

        # Create columns for product display (2 per row)
        cols = st.columns(2)

        for idx, product_id in enumerate(productos_ids):
            product = products_by_id.get(product_id)

            if not product:
                continue

            col = cols[idx % 2]

            with col:
                # Product card with border
                card = st.container(border=True)
                with card:
                    # Product header with emoji placeholder
                    emoji_map = {
                        'lavender': '💜',
                        'peppermint': '🌿',
                        'lemon': '🍋',
                        'melaleuca': '🌳',
                        'frankincense': '✨',
                        'rosemary': '🪴',
                        'oregano': '🌱',
                        'teatree': '🍃',
                        'wildorange': '🍊',
                        'intune': '🧠',
                        'metapwr': '⚡',
                        'elevation': '🚀',
                        'onguard': '🛡️',
                    }

                    emoji = emoji_map.get(product_id, '💎')

                    st.markdown(
                        f"<div style='font-size: 36px; text-align: center; margin-bottom: 10px;'>{emoji}</div>",
                        unsafe_allow_html=True
                    )

                    st.markdown(f"**{product['nombre']}**")
                    st.caption(product.get('nombre_en', ''))

                    # Descripcion - estructura-función language (FDA compliant)
                    st.markdown(f"_{product['descripcion']}_")

                    # Benefits as pills
                    if product.get('beneficios'):
                        st.markdown("**Beneficios:**")
                        beneficios_html = " ".join(
                            [f"<span style='display: inline-block; background-color: #e8f5e9; padding: 4px 8px; border-radius: 12px; margin: 2px; font-size: 12px;'>{b}</span>"
                             for b in product['beneficios'][:3]]
                        )
                        st.markdown(beneficios_html, unsafe_allow_html=True)

                    # Price
                    st.markdown(f"### ${product['precio_usd']:.2f} USD")

                    # Buy button
                    col1, col2 = st.columns(2)
                    with col1:
                        st.markdown(
                            f"<a href='https://www.doterra.com/EC/es_EC/shop?referralId=8205768' target='_blank' style='text-decoration: none;'>"
                            f"<button style='width: 100%; padding: 8px; background-color: #1f77b4; color: white; border: none; border-radius: 4px; cursor: pointer;'>"
                            f"Comprar en doTERRA</button></a>",
                            unsafe_allow_html=True
                        )

                    with col2:
                        # Consultar button with pre-filled message
                        consulta_message = f"Hola Suzanna! 👋 Exploré la categoría '{category.get('nombre', 'bienestar')}' y me recomendaron '{product['nombre']}'. ¿Puedes ayudarme con más detalles?"
                        encoded_message = urllib.parse.quote(consulta_message)
                        st.markdown(
                            f"<a href='https://wa.me/{whatsapp_number}?text={encoded_message}' target='_blank' style='text-decoration: none;'>"
                            f"<button style='width: 100%; padding: 8px; background-color: #25D366; color: white; border: none; border-radius: 4px; cursor: pointer;'>"
                            f"WhatsApp</button></a>",
                            unsafe_allow_html=True
                        )

    # Display advice/consejo
    if resultado_data.get('consejo'):
        st.markdown("#### 💡 Consejo Experto")
        st.info(resultado_data['consejo'])

    # FDA Disclaimer
    st.markdown("---")
    st.markdown(
        "<div style='background-color: #fff3cd; padding: 15px; border-radius: 4px; font-size: 12px;'>"
        "<strong>Aviso Importante:</strong> Estos productos no están diseñados para diagnosticar, tratar, curar o prevenir ninguna enfermedad. "
        "Los resultados pueden variar según el individuo. Consulte con un profesional de salud calificado antes de usar si está embarazada, "
        "amamantando, tomando medicamentos o tiene una condición de salud existente."
        "</div>",
        unsafe_allow_html=True
    )

    # CTA for WhatsApp consultation
    st.markdown("---")
    st.markdown("#### 🤝 Consulta Personalizada")

    summary_message = (
        f"Hola Suzanna! 👋\n\n"
        f"He completado la evaluación de '{category.get('nombre', 'bienestar')}' en tu plataforma.\n\n"
        f"Mis síntomas principales:\n"
    )

    for i, answer in enumerate(st.session_state.get('answers', []), 1):
        summary_message += f"{i}. {answer['option_text']}\n"

    summary_message += (
        f"\n¿Cuál sería tu recomendación completa para mi situación?"
    )

    encoded_summary = urllib.parse.quote(summary_message)

    col1, col2 = st.columns([2, 1])
    with col1:
        st.markdown(
            f"<a href='https://wa.me/{whatsapp_number}?text={encoded_summary}' target='_blank' style='text-decoration: none;'>"
            f"<button style='width: 100%; padding: 12px; background-color: #25D366; color: white; border: none; border-radius: 4px; cursor: pointer; font-size: 16px;'>"
            f"Consulta con Suzanna por WhatsApp</button></a>",
            unsafe_allow_html=True
        )


def render_back_button() -> bool:
    """
    Render a back button to return to previous question.

    Returns:
        True if back button was clicked, False otherwise
    """
    if len(st.session_state.answers) > 0:
        if st.button("← Volver a la pregunta anterior", use_container_width=False):
            return True
    return False


# ============================================================================
# MAIN RENDER FUNCTION
# ============================================================================

def render_symptom_checker(products_data: List[Dict], symptom_flow_data: Dict) -> None:
    """
    Main render function for the symptom checker.
    Orchestrates the flow: category selection → progressive questions → results.

    Args:
        products_data: List of product dictionaries from products.json
        symptom_flow_data: Symptom flow structure from symptom_flow.json
    """

    # Initialize session state
    if 'current_step' not in st.session_state:
        st.session_state.current_step = "categories"
    if 'selected_category' not in st.session_state:
        st.session_state.selected_category = None
    if 'answers' not in st.session_state:
        st.session_state.answers = []
    if 'accumulated_tags' not in st.session_state:
        st.session_state.accumulated_tags = []
    if 'current_question_id' not in st.session_state:
        st.session_state.current_question_id = None

    categories = symptom_flow_data.get('categories', [])

    # ========================================================================
    # STEP 1: Category Selection
    # ========================================================================
    if st.session_state.current_step == "categories":
        st.title("✨ Buscador de Bienestar")
        st.markdown(
            "Descubre los aceites esenciales doTERRA que mejor se adaptan a tus necesidades. "
            "Responde algunas preguntas simples para obtener recomendaciones personalizadas."
        )
        st.divider()

        render_category_cards(categories)

    # ========================================================================
    # STEP 2-6: Progressive Questions
    # ========================================================================
    elif st.session_state.current_step == "questions":
        selected_category = get_category_by_id(
            categories,
            st.session_state.selected_category
        )

        st.title(f"{selected_category['icono']} {selected_category['nombre']}")
        st.markdown(selected_category['descripcion'])
        st.divider()

        # Get current question
        current_question = get_question_by_id(
            categories,
            st.session_state.current_question_id
        )

        if current_question:
            # Calculate question number
            question_list = selected_category.get('preguntas', [])
            current_step_num = next(
                (i + 1 for i, q in enumerate(question_list) if q['id'] == current_question['id']),
                1
            )
            total_steps = len(question_list)

            # Render back button
            render_back_button()

            # Render question
            render_question(current_question, current_step_num, total_steps)

    # ========================================================================
    # FINAL: Results & Recommendations
    # ========================================================================
    elif st.session_state.current_step == "results":
        selected_category = get_category_by_id(
            categories,
            st.session_state.selected_category
        )

        st.title(f"{selected_category['icono']} Tu Plan de Bienestar Personalizado")
        st.divider()

        # Find best matching result
        result_key, resultado_data = find_best_result(
            st.session_state.accumulated_tags,
            selected_category.get('resultados', {})
        )

        if resultado_data:
            render_results(
                products_data,
                st.session_state.accumulated_tags,
                resultado_data,
                selected_category
            )
        else:
            st.warning(
                "No pudimos encontrar una recomendación exacta. "
                "Por favor, ponte en contacto con Suzanna para una consulta personalizada."
            )

        st.divider()

        # Navigation buttons
        col1, col2, col3 = st.columns(3)

        with col1:
            if st.button("← Volver al Inicio", use_container_width=True):
                st.session_state.current_step = "categories"
                st.session_state.selected_category = None
                st.session_state.answers = []
                st.session_state.accumulated_tags = []
                st.session_state.current_question_id = None
                st.rerun()

        with col2:
            if st.button("Explorar Otra Categoría", use_container_width=True):
                st.session_state.current_step = "categories"
                st.session_state.selected_category = None
                st.session_state.answers = []
                st.session_state.accumulated_tags = []
                st.session_state.current_question_id = None
                st.rerun()

        with col3:
            st.markdown(
                f"<a href='https://www.doterra.com/EC/es_EC/shop?referralId=8205768' target='_blank' style='text-decoration: none;'>"
                f"<button style='width: 100%; padding: 10px; background-color: #1f77b4; color: white; border: none; border-radius: 4px; cursor: pointer;'>"
                f"Ver Tienda doTERRA</button></a>",
                unsafe_allow_html=True
            )
