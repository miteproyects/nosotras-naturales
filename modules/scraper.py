"""
doTERRA Country Page Scraper Module

Scrapes promotional content from doTERRA country pages for South America
and displays them in a Streamlit interface.
"""

import requests
from bs4 import BeautifulSoup
import json
import os
from datetime import datetime, timedelta
import logging
from typing import Dict, List, Optional, Tuple
import streamlit as st
from .utils import load_json, save_json

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# doTERRA Country Configuration
DOTERRA_COUNTRIES = {
    "Ecuador": {"code": "EC", "lang": "es_EC", "flag": "🇪🇨"},
    "Colombia": {"code": "CO", "lang": "es_CO", "flag": "🇨🇴"},
    "Peru": {"code": "PE", "lang": "es_PE", "flag": "🇵🇪"},
    "Chile": {"code": "CL", "lang": "es_CL", "flag": "🇨🇱"},
    "Argentina": {"code": "AR", "lang": "es_AR", "flag": "🇦🇷"},
    "Bolivia": {"code": "BO", "lang": "es_BO", "flag": "🇧🇴"},
    "Mexico": {"code": "MX", "lang": "es_MX", "flag": "🇲🇽"},
    "Brazil": {"code": "BR", "lang": "pt_BR", "flag": "🇧🇷"},
    "Costa Rica": {"code": "CR", "lang": "es_CR", "flag": "🇨🇷"},
    "Guatemala": {"code": "GT", "lang": "es_GT", "flag": "🇬🇹"},
    "Paraguay": {"code": "PY", "lang": "es_PY", "flag": "🇵🇾"},
    "Uruguay": {"code": None, "lang": None, "flag": "🇺🇾", "available": False},
    "Venezuela": {"code": None, "lang": None, "flag": "🇻🇪", "available": False},
}

CACHE_FILE = "data/country_cache.json"
CACHE_DURATION_HOURS = 24
DOTERRA_REFERRAL_ID = "8205768"
REQUEST_TIMEOUT = 10
USER_AGENT = (
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
    "(KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
)


def get_doterra_url(country_code: str, lang_code: str) -> str:
    """
    Build the doTERRA URL for a specific country.

    Args:
        country_code: Country code (e.g., 'EC')
        lang_code: Language code (e.g., 'es_EC')

    Returns:
        Full doTERRA URL
    """
    return f"https://www.doterra.com/{country_code}/{lang_code}"


def is_cache_valid(cache_path: str, hours: int = CACHE_DURATION_HOURS) -> bool:
    """
    Check if cache file exists and is not older than specified hours.

    Args:
        cache_path: Path to cache file
        hours: Maximum age in hours

    Returns:
        True if cache is valid, False otherwise
    """
    if not os.path.exists(cache_path):
        return False

    file_time = datetime.fromtimestamp(os.path.getmtime(cache_path))
    return datetime.now() - file_time < timedelta(hours=hours)


def scrape_country_page(country_name: str, country_info: Dict) -> Dict:
    """
    Scrape a doTERRA country page for promotional content.

    Args:
        country_name: Name of the country
        country_info: Dictionary with code, lang, flag info

    Returns:
        Dictionary with scraped data or error information
    """
    if not country_info.get("code"):
        return {
            "country": country_name,
            "available": False,
            "error": "País no disponible actualmente",
            "url": None,
        }

    country_code = country_info["code"]
    lang_code = country_info["lang"]
    url = get_doterra_url(country_code, lang_code)

    result = {
        "country": country_name,
        "url": url,
        "flag": country_info.get("flag", ""),
        "available": True,
        "scraped_at": datetime.now().isoformat(),
        "title": None,
        "promo_text": None,
        "featured_products": [],
        "images": [],
        "error": None,
    }

    try:
        headers = {"User-Agent": USER_AGENT}
        response = requests.get(url, headers=headers, timeout=REQUEST_TIMEOUT)
        response.raise_for_status()

        soup = BeautifulSoup(response.content, "html.parser")

        # Extract page title
        title_tag = soup.find("h1")
        if title_tag:
            result["title"] = title_tag.get_text(strip=True)

        # Look for promotional banners and text
        promo_elements = soup.find_all(["div", "section"], class_=["promo", "banner", "featured", "hero"])
        promo_texts = []
        for elem in promo_elements[:3]:  # Limit to first 3
            text = elem.get_text(strip=True)
            if text and len(text) > 10:
                promo_texts.append(text[:150])

        if promo_texts:
            result["promo_text"] = " | ".join(promo_texts)

        # Extract featured product sections
        product_sections = soup.find_all(["div", "article"], class_=["product", "featured-product"])
        for product in product_sections[:5]:  # Limit to 5 products
            product_name = product.find(["h2", "h3", "span"])
            if product_name:
                result["featured_products"].append(product_name.get_text(strip=True)[:100])

        # Extract images
        images = soup.find_all("img")
        for img in images[:3]:  # Limit to 3 images
            img_url = img.get("src") or img.get("data-src")
            if img_url and ("doterra" in img_url.lower() or "product" in img_url.lower()):
                if not img_url.startswith("http"):
                    img_url = f"https://www.doterra.com{img_url}" if img_url.startswith("/") else f"https://www.doterra.com/{img_url}"
                result["images"].append(img_url)

        logger.info(f"Successfully scraped {country_name}")

    except requests.exceptions.Timeout:
        result["error"] = "Timeout: La página tardó demasiado en cargar"
        result["available"] = False
        logger.warning(f"Timeout scraping {country_name}")
    except requests.exceptions.ConnectionError:
        result["error"] = "Conexión rechazada. doTERRA puede bloquear los bots"
        result["available"] = False
        logger.warning(f"Connection error scraping {country_name}")
    except requests.exceptions.HTTPError as e:
        result["error"] = f"Error HTTP: {e.response.status_code}"
        result["available"] = False
        logger.warning(f"HTTP error scraping {country_name}: {e}")
    except Exception as e:
        result["error"] = f"Error inesperado: {str(e)[:100]}"
        result["available"] = False
        logger.error(f"Error scraping {country_name}: {str(e)}")

    return result


def scrape_all_countries(force_refresh: bool = False) -> Dict[str, Dict]:
    """
    Scrape all available doTERRA country pages.

    Args:
        force_refresh: If True, ignore cache and scrape all pages

    Returns:
        Dictionary with country data
    """
    # Check cache
    if not force_refresh and is_cache_valid(CACHE_FILE):
        cached_data = load_json(CACHE_FILE)
        if cached_data:
            logger.info("Using cached data")
            return cached_data

    logger.info("Scraping all country pages...")
    results = {}

    for country_name, country_info in DOTERRA_COUNTRIES.items():
        results[country_name] = scrape_country_page(country_name, country_info)

    # Save to cache
    os.makedirs(os.path.dirname(CACHE_FILE), exist_ok=True)
    save_json(CACHE_FILE, results)

    return results


def get_country_data(country_name: str, force_refresh: bool = False) -> Dict:
    """
    Get data for a specific country.

    Args:
        country_name: Name of the country
        force_refresh: Force refresh from server

    Returns:
        Country data dictionary
    """
    all_data = scrape_all_countries(force_refresh=force_refresh)
    return all_data.get(country_name, {})


def get_doterra_shop_link(country_code: str, referral_id: str = DOTERRA_REFERRAL_ID) -> str:
    """
    Generate a doTERRA shop link with referral ID.

    Args:
        country_code: Country code
        referral_id: Suzanna's referral ID

    Returns:
        Full shop URL with referral
    """
    base_url = f"https://www.doterra.com/{country_code}"
    return f"{base_url}?referralId={referral_id}"


def render_country_promotions():
    """
    Render the country promotions interface in Streamlit.

    Displays:
    - Grid of country cards with flags
    - Click to view country details
    - Last updated timestamps
    - Refresh button
    - Error handling and visit buttons
    """
    st.header("🌎 Promociones doTERRA por País")

    col1, col2, col3 = st.columns([2, 1, 1])
    with col1:
        st.write("Explora promociones y productos destacados en cada país de Sudamérica")

    with col3:
        if st.button("🔄 Actualizar", key="refresh_countries"):
            st.session_state.force_refresh = True

    force_refresh = st.session_state.get("force_refresh", False)

    # Load country data
    with st.spinner("Cargando información de países..."):
        country_data = scrape_all_countries(force_refresh=force_refresh)
        if force_refresh:
            st.session_state.force_refresh = False
            st.rerun()

    # Display country cards in a grid
    cols = st.columns(4)

    for idx, (country_name, data) in enumerate(country_data.items()):
        col = cols[idx % 4]

        with col:
            # Country card
            card_key = f"country_select_{country_name}"

            # Create a button that looks like a card
            flag = data.get("flag", "")
            status = "✓" if data.get("available", False) else "⚠️"

            if st.button(
                f"{flag} {country_name}\n{status}",
                key=card_key,
                use_container_width=True,
            ):
                st.session_state.selected_country = country_name
                st.rerun()

    # Display selected country details
    selected_country = st.session_state.get("selected_country")

    if selected_country:
        st.divider()
        country_info = country_data.get(selected_country, {})

        # Country header
        col1, col2 = st.columns([3, 1])
        with col1:
            st.subheader(f"{country_info.get('flag', '')} {selected_country}")
        with col2:
            if st.button("✕ Cerrar", key="close_country"):
                st.session_state.selected_country = None
                st.rerun()

        # Check for errors
        if country_info.get("error"):
            st.warning(f"⚠️ {country_info['error']}")
            st.info("Visita la tienda directamente:")
            col1, col2 = st.columns(2)
            with col1:
                country_code = DOTERRA_COUNTRIES[selected_country].get("code")
                if country_code:
                    shop_url = get_doterra_shop_link(country_code)
                    st.markdown(f"[🛍️ Visitar tienda doTERRA]({shop_url})")
        else:
            # Display country content
            col1, col2 = st.columns([3, 1])

            with col1:
                if country_info.get("title"):
                    st.write(f"**{country_info['title']}**")

            with col2:
                if country_info.get("scraped_at"):
                    scraped_time = datetime.fromisoformat(country_info["scraped_at"])
                    time_str = scraped_time.strftime("%d/%m %H:%M")
                    st.caption(f"Actualizado: {time_str}")

            # Promo text
            if country_info.get("promo_text"):
                st.info(country_info["promo_text"])

            # Featured products
            if country_info.get("featured_products"):
                st.subheader("Productos Destacados")
                for product in country_info["featured_products"]:
                    st.write(f"• {product}")

            # Images
            if country_info.get("images"):
                st.subheader("Galería")
                cols = st.columns(3)
                for idx, img_url in enumerate(country_info["images"]):
                    with cols[idx % 3]:
                        try:
                            st.image(img_url, use_column_width=True)
                        except:
                            st.caption("Imagen no disponible")

            # Visit shop button
            country_code = DOTERRA_COUNTRIES[selected_country].get("code")
            if country_code:
                shop_url = get_doterra_shop_link(country_code)
                st.markdown(
                    f'<a href="{shop_url}" target="_blank"><button style="width:100%; padding:10px; background-color:#16a85f; color:white; border:none; border-radius:5px; cursor:pointer;">🛍️ Visitar Tienda doTERRA</button></a>',
                    unsafe_allow_html=True
                )


def run_daily_scrape():
    """
    Run the daily scrape task.

    This function is designed to be called by an external scheduler
    (e.g., APScheduler, cron job, or Streamlit task).

    Returns:
        Dictionary with scrape results and status
    """
    logger.info("Starting daily scrape task...")

    try:
        results = scrape_all_countries(force_refresh=True)

        successful = sum(1 for data in results.values() if data.get("available"))
        failed = len(results) - successful

        status = {
            "status": "success",
            "timestamp": datetime.now().isoformat(),
            "countries_scraped": len(results),
            "successful": successful,
            "failed": failed,
            "message": f"Scraped {successful}/{len(results)} countries successfully"
        }

        logger.info(status["message"])
        return status

    except Exception as e:
        error_msg = f"Daily scrape failed: {str(e)}"
        logger.error(error_msg)
        return {
            "status": "error",
            "timestamp": datetime.now().isoformat(),
            "message": error_msg
        }


if __name__ == "__main__":
    # For testing
    results = scrape_all_countries(force_refresh=True)
    for country, data in results.items():
        print(f"\n{country}:")
        print(f"  Available: {data.get('available')}")
        print(f"  Title: {data.get('title')}")
        print(f"  Error: {data.get('error')}")
