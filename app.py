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
DASHBOARD_PASSWORD = "Suzanna"

# ============================================
# DOTERRA COUNTRY AVAILABILITY (ALL categories scraped March 2026)
# ============================================
DOTERRA_COUNTRIES = {
    'EC': {'name': 'Ecuador', 'locale': 'es_EC', 'flag': '🇪🇨'},
    'CO': {'name': 'Colombia', 'locale': 'es_CO', 'flag': '🇨🇴'},
    'CL': {'name': 'Chile', 'locale': 'es_CL', 'flag': '🇨🇱'},
    'CR': {'name': 'Costa Rica', 'locale': 'es_CR', 'flag': '🇨🇷'},
    'MX': {'name': 'México', 'locale': 'es_MX', 'flag': '🇲🇽'},
    'GT': {'name': 'Guatemala', 'locale': 'es_GT', 'flag': '🇬🇹'},
    'BR': {'name': 'Brasil', 'locale': 'pt_BR', 'flag': '🇧🇷'},
    'BO': {'name': 'Bolivia', 'locale': 'es_BO', 'flag': '🇧🇴'},
    'US': {'name': 'USA', 'locale': 'en', 'flag': '🇺🇸'},
}

def get_product_country_url(slug, country_code):
    """Build doTERRA product URL for a given country, resolving slug aliases."""
    c = DOTERRA_COUNTRIES.get(country_code)
    if not c:
        return None
    # Use the actual slug that exists in that country's set
    country_set = COUNTRY_PRODUCTS.get(country_code, set())
    resolved_slug = slug
    if slug not in country_set:
        # Try aliases
        aliases = SLUG_ALIASES.get(slug, set())
        for alt in aliases:
            if alt in country_set:
                resolved_slug = alt
                break
        else:
            # Try reverse aliases
            for primary, alt_set in SLUG_ALIASES.items():
                if slug in alt_set and primary in country_set:
                    resolved_slug = primary
                    break
    return f"https://www.doterra.com/{country_code}/{c['locale']}/p/{resolved_slug}"

# Product ID → doTERRA slug mapping (products.json uses short IDs, doTERRA uses slugs)
PRODUCT_SLUG_MAP = {
    'adaptiv_blend': 'adaptiv-oil',
    'air_x': 'air-x-oil',
    'alpha_crs': 'alpha-crs',
    'amber_bottles': 'amber-dram-bottles-12-pack',
    'aromatouch_blend': 'aromatouch-oil',
    'aromatouch_kit': 'aromatouch-technique-kit',
    'athletes_kit': 'athletes-kit',
    'balance_blend': 'doterra-balance-oil',
    'basil': 'basil-oil',
    'beginners_trio': 'beginners-trio-kit',
    'bergamot': 'bergamot-oil',
    'black_pepper': 'black-pepper-oil',
    'black_spruce': 'black-spruce-oil',
    'body_butter': 'spa-replenishing-body-butter',
    'body_mist': 'hydrating-body-mist-with-beautiful-blend',
    'brave_kids': 'doterra-brave-oil',
    'breathe_blend': 'breathe-oil',
    'breathe_drops': 'breathe-drops',
    'breathe_stick': 'breathe-stick',
    'brevi_marble_diffuser': 'brevi-marble-diffuser',
    'cap_stickers': 'storage-essential-oil-cap-stickers',
    'cardamom': 'cardamom-oil',
    'cassia': 'cassia-oil',
    'cedarwood': 'cedarwood-oil',
    'celery_seed': 'celery-seed-oil',
    'cheer_blend': 'cheer-oil',
    'cilantro': 'cilantro-oil',
    'cinnamon': 'cinnamon-oil',
    'citronella': 'citronella-oil',
    'citrus_bliss': 'citrus-bliss-oil',
    'citrus_bliss_bath_bar': 'citrus-bliss-invigorating-bath-bar',
    'citrus_bliss_hand_lotion': 'spa-citrus-bliss-hand-lotion',
    'clary_sage': 'clary-sage-oil',
    'clarycalm_blend': 'clary-calm-roll-on',
    'clove': 'clove-oil',
    'console_blend': 'console-oil',
    'copaiba': 'copaiba-oil',
    'copaiba_softgels': 'copaiba-softgels',
    'coriander': 'coriander-oil',
    'correct_x': 'correct-x',
    'cypress': 'cypress-oil',
    'daily_nutrient_pack': 'supplements-daily-vitality-daily-nutrient-pack',
    'davana': 'davana-touch-oil',
    'deep_blue': 'deep-blue-oil',
    'deep_blue_polyphenol': 'deep-blue-polyphenol-complex',
    'deep_blue_rub': 'deep-blue-rub',
    'deep_blue_stick': 'deep-blue-stick',
    'digestzen': 'zengest-oil',
    'digestzen_terrazyme': 'digestzen-terrazyme',
    'doterra_on_guard': 'on-guard-oil',
    'elevation_blend': 'elevation-oil',
    'emotional_aromatherapy_kit': 'emotional-aromatherapy-kit',
    'eucalyptus': 'eucalyptus-oil',
    'family_essentials_kit': 'family-essentials-kit',
    'felt_oil_bag': 'felt-oil-bag',
    'forgive_blend': 'forgive-oil',
    'fractionated_coconut': 'fractionated-coconut-oil',
    'fractionated_coconut_carrier': 'fractionated-coconut-oil',
    'frankincense': 'frankincense-oil',
    'geranium': 'geranium-oil',
    'ginger': 'ginger-oil',
    'grapefruit': 'grapefruit-oil',
    'guaiacwood': 'guaiacwood-oil',
    'hair_conditioner': 'hair-care-daily-conditioner',
    'hair_leave_in': 'hair-care-leave-in-conditioner',
    'hair_shampoo': 'hair-care-protecting-shampoo',
    'hand_wash_dispenser': 'amber-foaming-hand-wash-dispenser',
    'hd_clear': 'hd-clear-oil',
    'helichrysum': 'helichrysum-oil',
    'home_essentials_kit': 'home-essentials-enrollment-kit',
    'introductory_kit': 'introductory-kit',
    'intune_blend': 'intune-oil-roll-on',
    'island_rock_diffuser': 'island-rock-diffuser-2pk',
    'jasmine': 'jasmine-touch',
    'juniper_berry': 'juniper-berry-oil',
    'keychain_8_vial': 'storage-gray-8-vial-keychain',
    'kids_collection': 'kids-collection',
    'koala_diffuser': 'koala-diffuser',
    'lavender': 'lavender-oil',
    'lemon': 'lemon-oil',
    'lemon_eucalyptus': 'lemon-eucalyptus-oil',
    'lemongrass': 'lemongrass-oil',
    'lifelong_vitality_pack': 'life-long-vitality-pack',
    'lime': 'lime-oil',
    'lotus_display': 'lotus-wood-display',
    'madagascar_vanilla': 'madagascar-vanilla-oil',
    'marjoram': 'marjoram-oil',
    'melaleuca': 'melaleuca-oil',
    'meo_pal': 'meo-pal',
    'metapwr_advantage': 'metapwr-advantage',
    'metapwr_blend': 'metapwr-oil',
    'motivate_blend': 'motivate-oil',
    'myrrh': 'myrrh-oil',
    'natural_deodorant': 'natural-deodorant-with-doterra-balance',
    'on_guard_beadlets': 'on-guard-beadlets',
    'on_guard_foaming_wash': 'on-guard-foaming-hand-wash',
    'on_guard_softgels': 'on-guard-softgels',
    'on_guard_toothpaste': 'on-guard-natural-whitening-toothpaste',
    'oregano': 'oregano-oil',
    'osmanthus': 'osmanthus-touch-oil',
    'passion_blend': 'passion-oil',
    'pasttense_blend': 'pasttense-oil-roll-on',
    'patchouli': 'patchouli-oil',
    'pb_assist_plus': 'pb-assist',
    'peace_blend': 'peace-oil',
    'peppermint': 'peppermint-oil',
    'petal_diffuser': 'petal-diffuser',
    'petitgrain': 'petitgrain-oil',
    'purify_blend': 'purify-oil',
    'pursue_blend': 'pursue-oil',
    'roll_on_stand': 'ready-roll-on-stand',
    'roman_chamomile': 'roman-chamomile-oil',
    'rosemary': 'rosemary-oil',
    'serenity_blend': 'serenity-oil',
    'shinrin_yoku': 'shinrin-yoku-oil',
    'siberian_fir': 'siberian-fir-oil',
    'skin_care_kit': 'essential-skin-care-kit',
    'skin_facial_cleanser': 'essential-skin-care-facial-cleanser',
    'skin_hydrating_cream': 'essential-skin-care-hydrating-cream',
    'skin_moisturizer': 'essential-skin-care-moisturizer',
    'skin_scrub': 'essential-skin-care-invigorating-scrub',
    'skin_serum': 'essential-skin-care-tightening-serum',
    'skin_toner': 'essential-skin-care-pore-reducing-toner',
    'spa_body_wash': 'spa-body-wash',
    'spa_hand_lotion': 'spa-hand-and-body-lotion',
    'spanish_sage': 'spanish-sage-oil',
    'spearmint': 'spearmint-oil',
    'stronger_kids': 'doterra-stronger-oil',
    'supermint_toothpaste': 'supermint-toothpaste',
    'tangerine': 'tangerine-oil',
    'terrashield_blend': 'terrashield-oil',
    'thyme': 'thyme-oil',
    'toppers_10': 'toppers-10-ml',
    'toppers_5_15': 'toppers-5-and-15-ml',
    'turmeric': 'turmeric-oil',
    'turmeric_capsules': 'turmeric-duo-caps',
    'veggie_caps': 'usage-internal-veggie-caps',
    'vetiver': 'vetiver-oil',
    'wild_orange': 'wild-orange-oil',
    'wintergreen': 'wintergreen-oil',
    'ylang_ylang': 'ylang-ylang-oil',
    'zendocrine_blend': 'zendocrine-oil',
}

def _get_product_slug(product):
    """Get the doTERRA slug for a product (from doterra_url or PRODUCT_SLUG_MAP)."""
    url = product.get('doterra_url', '')
    if '/p/' in url:
        return url.split('/p/')[-1].split('?')[0]
    return PRODUCT_SLUG_MAP.get(product.get('id', ''), product.get('id', '').replace('_', '-') + '-oil')

# Scraped product availability per country — ALL categories (doTERRA slug sets, March 2026)
COUNTRY_PRODUCTS = {
    'BR': {"adaptiv-oil","adaptiv-pastilhas","adaptiv-touch-oil","air-x-oil","aromatouch-diffused-kit-2020","aromatouch-kit","aromatouch-mini-kit","aromatouch-oil-blend","basil-oil","basil-oil-flavor","bergamot-oil","bergamot-oil-flavor","black-pepper-oil","black-pepper-oil-flavor","black-spruce-oil","br-convention-backpack-2020","brasil-living-collection","breu-branco-oil","build-guide-10-pack","build-your-legacy","cardamom-oil-flavor","cassia-oil","cassia-oil-flavor","cedarwood-oil","celery-seed-oil-flavor","cilantro-oil","cilantro-oil-flavor","cinnamon-bark-oil-flavor","citronella-oil","citrus-bliss-oil","citrus-bloom-touch-oil","clary-sage-oil","clary-sage-oil-flavor","clarycalm-oil","class-in-a-box","clove-oil","clove-oil-flavor","copaiba-oil","copaiba-oil-flavor","copaiba-touch-oil","coriander-oil","coriander-oil-flavor","correct-x","costa-brio-oil","cypress-oil","daily-conditioner","daily-nutrient-pack","ddr-prime-oil","ddr-prime-pastilha","deep-blue-stick","doterra-balance-oil","doterra-beauty-power-collagen-elixir","doterra-brave-oil","doterra-breathe-balm-stick","doterra-breathe-oil","doterra-breathe-touch","doterra-calmer-oil","doterra-cheer-oil","doterra-cheer-touch-oil","doterra-console-oil","doterra-console-touch-oil","doterra-dawn-humidifier","doterra-deep-blue-oil","doterra-deep-blue-rub","doterra-deep-blue-rub-travel-size","doterra-deep-blue-touch","doterra-early-care-kit","doterra-elevation-oil","doterra-emotional-aromatherapy-kit","doterra-forgive-oil","doterra-forgive-touch-oil","doterra-frankincense-touch","doterra-hygge-oil","doterra-intro-kit","doterra-kids-kit","doterra-lavender-touch","doterra-lifeshot","doterra-malama-oil","doterra-melaleuca-touch","doterra-metapwr-fiber-up-sachets-30-ct","doterra-metapwr-oil-flavor","doterra-metapwr-pastilha","doterra-motivate-oil","doterra-motivate-touch-oil","doterra-oil-collector","doterra-oregano-touch","doterra-passion-oil","doterra-passion-touch-oil","doterra-peace-oil","doterra-peace-touch-oil","doterra-peppermint-touch","doterra-pur-homme-edp","doterra-pure-femme-edp","doterra-rescuer-oil","doterra-serenity-oil","doterra-spa-body-butter","doterra-steady-oil","doterra-stronger-oil","doterra-tamer-oil","doterra-thinker-oil","doterra-zengest-oil","douglas-fir-oil","erva-baleeira-oil","essential-culinary","essential-culinary-luri-toledo-recipe-book","essential-culinary-no-recipe-book","essential-oil-capstickers","eucalyptus-oil","eucalyptus-oil-blend","fast-track-kit","fennel-oil","fennel-oil-flavor","forest-bathing-oil","fractionated-coconut-oil","frankincense-oil","frankincense-oil-flavor","geranium-oil","geranium-oil-flavor","ginger-oil","ginger-oil-flavor","grapefruit-oil","grapefruit-oil-flavor","green-mandarin-oil","gua-sha-beauty-collection","guaiacwood-oil","hawaiian-sandalwood","hd-clear-oil","healthy-simple-guide-10-pack","helichrysum-oil","helichrysum-touch-oil","home-essentials-pebble","home-essentials-petal","hope-touch-oil","intune-oil","jasmine-touch-oil","juniper-berry-oil","juniper-berry-oil-flavor","kit-doterra-emotional-aromatherapy-touch","launch-guide-10-pack","lavender-fields-body-splash","lavender-oil","lavender-oil-flavor","lead-guide-10-pack","leave-in-conditioner","lemon-eucalyptus-oil","lemon-oil","lemon-oil-flavor","lemongrass-oil","lemongrass-oil-flavor","lifeshot-genesis","lime-oil","lime-oil-flavor","live-guide-10-pack","madagascar-vanilla-oil-flavor","marjoram-oil","marjoram-oil-flavor","melaleuca-tea-tree-oil","melissa-oil","multiply-guide","myrrh-oil","myrrh-oil-flavor","myst-wall-diffuser","natural-solutions-flyer-pack","on-guard-beadlet","on-guard-oil","on-guard-oil-flavor","on-guard-pastilha","on-guard-toothpaste","on-guard-toothpaste-travel-pack","onguard-touch","oregano-oil","oregano-oil-flavor","paper-bags-medium","paper-bags-small","pasttense-oil","patchouli-oil","patchouli-oil-flavor","pebble-diffuser-collection","peppermint-beadlet","peppermint-oil","peppermint-oil-flavor","petal-diffuser-2","petitgrain-oil","petitgrain-oil-flavor","pink-pepper-oil-flavor","price-list-pack","product-guide-10-pack","product-guide-5-pack","protecting-shampoo","purify-oil","roman-chamomile-oil","rose-touch-oil","rosemary-oil","rosemary-oil-flavor","salubelle-oil","share-guide-10-pack","siberian-fir-oil","siberian-fir-oil-flavor","spa-bath-ritual-book","spa-body-wash","spa-citrus-bliss-hand-lotion","spa-essentials-kit","spa-exfoliating-body-scrub","spa-hand-and-body-lotion","spearmint-oil","spearmint-oil-flavor","spikenard-oil","sunny-citrus-oil","supermint-beadlets","supermint-oil","tangerine-oil","tangerine-oil-flavor","terrashield-oil","terrashield-oil-spray","thyme-oil","thyme-oil-flavor","train-guide-10-pack","turmeric-oil-flavor","turmeric-pastilha","verage-cleanser","verage-hydrating-cream","verage-mineral-moisturizer","verage-moisturizer","verage-toner","vetiver-oil","vetiver-oil-flavor","vetiver-touch-oil","vm-complex","whisper-touch-oil","wild-orange-oil","wild-orange-oil-flavor","wintergreen-oil","wooden-box-with-doterra-logo","xeo-mega","yarrow-pom-active-duo-oil","yarrow-pom-oil","ylang-ylang-oil","ylang-ylang-oil-flavor","zendocrine-oil","zendocrine-oil-flavor","zendocrine-pastilha","zengest-oil-flavor","zengest-pastilha","zengest-touch-oil"},
    'CL': {"adaptiv-touch-oil","arborvitae-oil","aromatouch-enrollment-kit","aromatouch-oil","aromatouch-oil-5ml","aromatouch-technique-kit","basil-oil","beginners-trio-kit","bergamot-oil","breathe-drops","breathe-stick","cap-stickers","cardamom-oil","carry-in-style-oil-case","cassia-oil","cedarwood-oil","change-it-up-oil-holder","cilantro-oil","cinnamon-oil","citronella-oil","citrus-bliss-hand-lotion","clary-calm-roll-on","clary-sage-oil","clove-oil","copaiba-oil","coriander-oil","correct-x","curso-de-la-tecnica-aroma-touch-cl","cypress-oil","deep-blue-oil","deep-blue-rub","deep-blue-stick","diffusing-stone-necklace-warm-tones","doterra-adaptiv-oil","doterra-balance-oil","doterra-balance-oil-5ml","doterra-braver-oil","doterra-breathe-oil","doterra-breathe-oil-5ml","doterra-breathe-touch-oil","doterra-calmer-oil","doterra-citrus-bliss-oil","doterra-ddr-prime","doterra-kids-collection","doterra-rescuer-oil","doterra-steady-oil","doterra-stronger-oil","doterra-tamer-oil","doterra-thinker-oil","doterra-whisper-touch-oil","easy-travel-silicone-tube-set","essential-skin-care-facial-cleanser","essential-skin-care-hydrating-cream","essential-skin-care-kit","essential-skin-care-moisturizer","essential-skin-care-pore-reducing-toner","essential-skin-care-tightening-serum","eucalyptus-oil","family-essentials-enrollment-kit","family-essentials-kit","fennel-oil","fractionated-coconut-oil","frankincense-cosmetic-oil-5ml","frankincense-oil","frankincense-oil-5ml","frankincense-stick-naio-wood","geranium-oil","ginger-oil","grapefruit-oil","hd-clear-oil","helichrysum-oil","home-essentials-enrollment-kit","introductory-kit","intune-oil","juniper-berry-oil","laluz-diffuser","lavender-oil","lavender-oil-5ml","lavender-peace-oil","lavender-touch-oil","lemon-eucalyptus-oil","lemon-oil","lemon-oil-5ml","lemongrass-oil","lime-oil","madagascar-vanilla-oil","marjoram-oil","metapwr-beadlets","metapwr-oil","myrrh-oil","on-guard-and-2-pk-hand-wash-dispenser","on-guard-beadlets","on-guard-cleaner-concentrate","on-guard-drops","on-guard-foaming-hand-wash","on-guard-food-oil-5ml","on-guard-hand-wash-dispenser","on-guard-mouthwash","on-guard-natural-whitening-toothpaste","on-guard-oil","on-guard-oil-5ml","on-guard-sanitizing-mist","on-guard-touch-oil","oregano-oil","oregano-oil-5ml","patchouli-oil","pebble-diffuser","peppermint-beadlets","peppermint-oil","peppermint-oil-5ml","petal-diffuser","petitgrain-oil","pure-fresh-oil","roman-chamomile-oil","rosemary-oil","round-storage-case-organizer","salon-essentials-duo","salon-essentials-leave-in-conditioner","salon-essentials-protecting-shampoo","salon-essentials-smoothing-conditioner","salon-essentials-trio","scent-my-shower-passive-diffuser","serenity-valerian-stick","shinrin-yoku-oil","siberian-fir-oil","simple-solutions-enrollment-kit","sloth-diffuser","spa-hand-and-body-lotion","spa-hand-and-body-lotion-3-pack","spa-moisturizing-bath-bar","spa-moisturizing-bath-bar-3-pack","spa-rose-hand-lotion","spearmint-oil","storage-gray-8-vial-keychain","storage-logo-engraved-wooden-box","supermint-oil","supermint-toothpaste","tangerine-oil","tea-tree-oil","tea-tree-oil-5ml","terrashield-oil","terrashield-spray","thyme-oil","turmeric-oil","usage-internal-veggie-caps","vetiver-oil","wild-orange-oil","wild-orange-oil-5ml","wintergreen-oil","yarrow-pom-oil","ylang-ylang-oil","zendocrine-oil","zengest-oil","zengest-oil-5ml"},
    'CO': {"abode-oil","adaptiv-oil","adaptiv-touch-oil","air-x-oil","aromatouch-enrollment-kit","aromatouch-oil","aromatouch-oil-5ml","aromatouch-technique-kit","baby-collection","baby-diaper-cream","baby-hair-and-body-wash","baby-lotion","balance-oil","basil-oil","beginners-trio-kit","bergamot-oil","breathe-oil","breathe-oil-5ml","breathe-vapor-stick","cardamom-oil","cassia-oil","cedarwood-oil","celery-seed-oil","cheer-oil","cilantro-oil","cinnamon-bark-oil","citronella-oil","citrus-bliss-oil","citrus-bloom-oil","clary-sage-oil","clarycalm-oil","clove-oil","console-oil","copaiba-oil","copaiba-touch-oil","coriander-oil","curso-de-la-tecnica-aroma-touch-co","cypress-oil","daily-nutrition-pack","deep-blue-oil","deep-blue-touch-oil","doterra-balance-oil","doterra-balance-oil-5ml","doterra-balance-touch-oil","doterra-brave-oil","doterra-breathe-touch-oil","doterra-calmer-oil","doterra-deep-blue-rub","doterra-deep-blue-stick","doterra-emotional-aromatherapy-diffused","doterra-emotional-aromatherapy-kit","doterra-essential-oil-specialist-certification-co","doterra-metapwr-beadlets","doterra-metapwr-oil","doterra-pure-fresh-oil","doterra-rescuer-oil","doterra-steady-oil","doterra-stronger-oil","doterra-supermint-beadlets","doterra-supermint-oil","doterra-supermint-toothpaste","doterra-supermint-touch-oil","doterra-tamer-oil","doterra-thinker-oil","dram-bottles-12-pack","elevation-oil","essential-citrus-diffused-enrollment-kit","essential-citrus-enrollment-kit","essential-skin-care-anti-aging-moisturizer","essential-skin-care-facial-cleanser","essential-skin-care-hydrating-cream","essential-skin-care-invigorating-scrub","essential-skin-care-kit","essential-skin-care-pore-reducing-toner","essential-skin-care-tightening-serum","eucalyptus-oil","family-essentials-kit","family-essentials-meta-pwr-oil","fennel-oil","forgive-oil","fractionated-coconut-oil","frankincense-oil","frankincense-oil-5ml","frankincense-stick-naio-wood","geranium-oil","ginger-oil","grapefruit-oil","guaiacwood-oil","hair-care-daily-conditioner","hair-care-daily-conditioner-2-pack","hair-care-leave-in-conditioner","hair-care-leave-in-conditioner-2-pack","hair-care-protecting-shampoo","hair-care-protecting-shampoo-2-pack","hair-care-shampoo-and-conditioner","hair-care-shampoo-with-daily-and-leave-in-conditioner","haircare-salon-essentials-root-to-tip-serum","hd-clear-oil","helichrysum-oil","home-essentials-kit","hydrating-body-mist-with-beautiful-blend","introductory-kit","intune-roll-on-oil","juniper-berry-oil","kids-collection","kids-collection-enrollment-kit","laluz-diffuser","lavender-oil","lavender-oil-5ml","lavender-touch-oil","lemon-eucalyptus-oil","lemon-oil","lemon-oil-5ml","lemongrass-oil","lime-oil","lotus-wood-display","madagascar-vanilla-oil","marjoram-oil","melaleuca-oil","microplex-vmz","motivate-oil","myrrh-oil","natural-deodorant-infused-with-doterra-balance-essential-oil","on-guard-beadlets","on-guard-drops","on-guard-natural-whitening-toothpaste","on-guard-oil","on-guard-oil-5ml","on-guard-sanitizing-mist","onguard-oil","onguard-touch-oil","oregano-oil","oregano-oil-5ml","passion-oil","pasttense-roll-on-oil","patchouli-oil","peace-oil","pebble-diffuser","peppermint-beadlets","peppermint-oil","peppermint-oil-5ml","peppermint-touch-oil","petal-diffuser","petitgrain-oil","pursue-oil","ready-roll-on-stand","roam-diffuser","roman-chamomile-oil","rosemary-oil","serenity-oil","serenity-valerian-stick","shinrin-yoku-oil","siberian-fir-oil","simple-solutions-enrollment-kit","smart-and-sassy-oil","spa-body-butter","spa-body-scrub","spa-hand-and-body-lotion","spa-hand-and-body-lotion-3-pack","spanish-sage-oil","spearmint-oil","storage-essential-oil-cap-stickers","storage-gray-8-vial-keychain","sun-care-body-lotion","sun-care-body-spray","sun-care-duo","supplements-xeo-mega","tangerine-oil","tea-tree-oil","tea-tree-oil-5ml","tea-tree-touch-oil","terrashield-oil","terrashield-spray-oil","thyme-oil","toppers-10-ml","toppers-5-and-15-ml","travel-kit-empty-bottles","turmeric-oil","usage-internal-veggie-caps","volo-diffuser-onyx","whisper-touch-oil","wild-orange-oil","wild-orange-oil-5ml","wintergreen-oil","yarrow-pom-oil","ylang-ylang-oil","zendocrine-oil","zengest-oil","zengest-oil-5ml","zengest-touch-roll-on-oil"},
    'CR': {"10-ml-amber-roller-bottle-6-pack","30-ml-sprayer-bottle-3-pack","5-ml-amber-bottle-6-pack","abode-foaming-hand-wash","abode-hand-wash-dispenser","abode-liquid-dish-soap-dispenser","abode-liquid-dish-wash","abode-multisurface-spray-dispenser","abode-oil","adaptiv-oil","adaptiv-touch-oil","adobe-multi-surface-cleaner","air-x-oil","alpha-crs","amber-dram-bottles-12-pack","aromatouch-enrollment-kit","aromatouch-oil","aromatouch-oil-5ml","aromatouch-technique-kit","balance-oil","balance-oil-5ml","basil-oil","bergamot-oil","breathe-oil","breathe-oil-5ml","breathe-respiratory-drops","breathe-touch-oil","breathe-vapor-stick","cardamom-oil","cedarwood-oil","cheer-oil","cinnamon-bark-oil","citronella-oil","citrus-bliss-invigorating-bath-bar","citrus-bliss-oil","citrus-bloom-hand-wash-and-pump","citrus-bloom-lotion","citrus-bloom-oil","clary-calm-roll-on","clary-sage-oil","clove-oil","collections-beginners-trio-kit","console-oil","conviertete-en-un-profesional-de-ventas-de-tu-negocio-doterra","copaiba-oil","copaiba-softgels","copaiba-touch-oil","correct-x","curso-de-la-tecnica-aroma-touch-cr","cypress-oil","daily-vitality-daily-nutrient-pack","davana-touch-oil","ddr-prime-oil","ddr-prime-softgels","deep-blue-oil","deep-blue-polyphenol-complex","deep-blue-rub","deep-blue-stick","digestzen-blend-softgels","doterra-brave-oil","doterra-calmer-oil","doterra-greens","doterra-introductory-kit","doterra-on-guard-foaming-hand-wash-2pk","doterra-onguard-foaming-hand-wash-dispenser","doterra-onguard-foaming-hand-wash-dispenser-3pk","doterra-rescuer-oil","doterra-serenity-bath-bar","doterra-serenity-bath-bar-3-pack","doterra-serenity-softgels","doterra-serenity-touch-oil","doterra-spa-basics-kit","doterra-spa-body-scrub","doterra-spa-body-wash","doterra-spa-citrus-bliss-hand-lotion","doterra-spa-detoxifying-mud-mask","doterra-spa-hand-and-body-lotion","doterra-spa-hand-and-body-lotion-3-pack","doterra-spa-lip-balm-3-pack","doterra-spa-lip-balm-herbal","doterra-spa-luxury-kit","doterra-spa-moisturizing-bath-bar","doterra-spa-replenishing-body-butter","doterra-steady-oil","doterra-stronger-oil","doterra-tamer-oil","doterra-thinker-oil","doterra-total-spa-kit","duo-doterra-sun","enrollment-kits-athlete","essential-supplements-kit","essentials-petal-kit","eucalyptus-oil","family-essentials-kit","family-essentials-kit-with-diffuser","forgive-oil","fractionated-coconut-oil","frankincense-oil","frankincense-oil-5ml","frankincese-stick-naio-wood","geranium-oil","ginger-drops","ginger-oil","grapefruit-oil","guaiacwood-oil","hair-care-daily-conditioner","hair-care-duo","hair-care-leave-in-conditioner","hair-care-mini-travel-kit","hair-care-protecting-shampoo","hair-care-trio","hd-clear-oil","helichrysum-oil","home-essentials-kit","hydrating-body-mist-with-beautiful-blend","hygge-blend-oil","immortelle-roll-on","intro-kit-6-pack","intune-roll-on","jasmine-touch-oil","juniper-berry-oil","kids-collection","kids-collection-enrollment-kit","kit-emotional-aromatherapy","koala-diffuser-holiday","laluz-diffuser","lavender-oil","lavender-oil-5ml","lemon-eucalyptus-oil","lemon-oil","lemon-oil-5ml","lemongrass-oil","life-long-vitality-pack","lime-oil","lrp-kit-daily-habits","lrp-kit-relief-and-revive","madagascar-vanilla-oil","marjoram-oil","melaleuca-oil","melaleuca-oil-5ml","melaleuca-touch-oil","metapwr-advantage","metapwr-assist","metapwr-beadlets","metapwr-mito-2-max","metapwr-oil","metapwr-softgels","metapwr-system","microplex-vmz","mood-management-kit","motivate-oil","myrrh-oil","natural-deodorant-with-doterra-balance","on-guard-beadlets","on-guard-cleaner-concentrate","on-guard-foaming-hand-wash","on-guard-laundry-detergent","on-guard-mouthwash","on-guard-natural-whitening-toothpaste","on-guard-oil","on-guard-oil-5ml","on-guard-protecting-throat-drops","on-guard-protective-blend-softgel","on-guard-sanitizing-mist","on-guard-touch-oil","onguard-foaming-hand-wash-with-2-dispensers","oregano-oil","oregano-oil-5ml","oregano-touch-oil","osmanthus-oil","passion-oil","pasttense-roll-on","pb-assist","pb-assist-jr","pb-core-caps","peace-oil","pebble-diffuser","peppermint-beadlet","peppermint-oil","peppermint-oil-5ml","peppermint-softgels","peppermint-touch-oil","petal-diffuser","petitgrain-oil","phytoestrogen-complex","pipettes-50-pk","purify-oil","roman-chamomile-oil","rose-hydrosol","rose-touch-oil","rosemary-oil","serenity-kit","serenity-oil","serenity-stick-valerian","shinrin-yoku","siberian-fir-oil","simple-solutions-enrollment-kit","skin-care-anti-aging-moisturizer","skin-care-facial-cleanser","skin-care-hydrating-cream","skin-care-pore-reducing-toner","skin-care-system","skin-care-tightening-serum","smart-and-sassy-oil","spa-rose-hand-lotion","spanish-sage-oil","spearmint-oil","storage-essential-oil-cap-stickers","storage-logo-engraved-wooden-box","sun-after-sun-spray","sun-care-face-body-lotion","sunscreen-spray","supermint-beadlets","supermint-oil","supermint-toothpaste","supermint-touch-oil","supplements-digestzen-terrazyme","supplements-gx-assist","supplements-mito-2-max","sweet-fennel-oil","tangerine-oil","terrashield-oil","terrashield-spray-oil","thyme-oil","touch-lavender-oil","triease-softgels","trio-doterra-sun","turmeric-oil","usage-internal-veggie-caps","vetiver-oil","volo-marble-diffuser","volo-onyx-diffuser","whisper-touch-oil","wild-orange-oil","wild-orange-oil-5ml","wintergreen-oil","xeo-mega","yarrow-pom-oil","ylang-ylang-oil","zendocrine-oil","zendocrine-softgels","zengest-oil","zengest-oil-5ml","zengest-touch-oil"},
    'EC': {"abode-cleaner-concentrate","abode-cleaner-concentrate-dispenser","abode-duo-cleaner-concentrate-and-dispenser","abode-oil","adaptiv-oil","adaptiv-touch-oil","air-x-oil","alpha-crs","amber-dram-bottles-12-pack","amber-foaming-hand-wash-dispenser","aromatouch-enrollment-kit","aromatouch-oil","aromatouch-oil-5ml","aromatouch-technique-kit","athletes-kit","balance-oil-5ml","basil-oil","beginners-trio-kit","bergamot-oil","black-spruce-oil","breathe-drops","breathe-oil","breathe-oil-5ml","breathe-stick","breathe-touch-oil","brevi-marble-diffuser","cardamom-oil","cassia-oil","cedarwood-oil","celery-seed-oil","cheer-oil","cilantro-oil","cinnamon-oil","citronella-oil","citrus-bliss-invigorating-bath-bar","citrus-bliss-oil","citrus-bloom-oil","clary-calm-roll-on","clary-sage-oil","clove-oil","console-oil","copaiba-oil","copaiba-touch-oil","coriander-oil","curso-de-la-tecnica-aroma-touch-ec","cypress-oil","davana-touch-oil","deep-blue-oil","deep-blue-polyphenol-complex","deep-blue-rub","deep-blue-stick","deep-blue-touch-oil","doterra-balance-oil","doterra-balance-oil-5ml","doterra-balance-touch-oil","doterra-brave-oil","doterra-calmer-oil","doterra-cheer-touch","doterra-essential-oil-specialist-certification-ec","doterra-ginger-drops","doterra-pure-fresh-oil","doterra-rescuer-oil","doterra-steady-oil","doterra-stronger-oil","doterra-tamer-oil","doterra-thinker-oil","elevation-oil","emotional-aromatherapy-diffused-kit","emotional-aromatherapy-kit","essential-citrus-diffused-enrollment-kit","essential-citrus-enrollment-kit","essential-skin-care-facial-cleanser","essential-skin-care-hydrating-cream","essential-skin-care-invigorating-scrub","essential-skin-care-kit","essential-skin-care-moisturizer","essential-skin-care-pore-reducing-toner","essential-skin-care-tightening-serum","eucalyptus-oil","family-essentials-kit","family-essentials-meta-pwr-oil","felt-oil-bag","forgive-oil","fractionated-coconut-oil","frankincense-oil","frankincense-oil-5ml","frankincense-touch-oil","geranium-oil","ginger-oil","grapefruit-oil","guaiacwood-oil","hair-care-daily-conditioner","hair-care-daily-conditioner-2-pack","hair-care-leave-in-conditioner","hair-care-leave-in-conditioner-2-pack","hair-care-protecting-shampoo","hair-care-protecting-shampoo-2-pack","hair-care-shampoo-and-conditioner","hair-care-shampoo-with-daily-and-leave-in-conditioner","hd-clear-oil","helichrysum-oil","home-essentials-enrollment-kit","hydrating-body-mist-with-beautiful-blend","introductory-kit","intune-oil-roll-on","island-rock-diffuser-2pk","jasmine-touch","juniper-berry-oil","kids-collection","kids-collection-enrollment-kit","koala-diffuser","laluz-diffuser","lavender-oil","lavender-oil-5ml","lavender-touch-oil","lemon-eucalyptus-oil","lemon-oil","lemon-oil-5ml","lemongrass-oil","life-long-vitality-pack","lime-oil","lotus-wood-display","madagascar-vanilla-oil","marjoram-oil","melaleuca-oil","melaleuca-oil-5ml","melaleuca-touch-oil","meo-pal","metapwr-beadlets","metapwr-oil","microplex-vmz","motivate-oil","myrrh-oil","natural-deodorant-with-doterra-balance","on-guard-beadlets","on-guard-drops","on-guard-foaming-hand-wash","on-guard-natural-whitening-toothpaste","on-guard-oil","on-guard-oil-5ml","on-guard-sanitizing-mist","on-guard-touch-oil","oregano-oil","oregano-oil-5ml","osmanthus-touch-oil","passion-oil","pasttense-oil-roll-on","patchouli-oil","peace-oil","pebble-diffuser","peppermint-oil","peppermint-oil-5ml","peppermint-touch-oil","petal-diffuser","petitgrain-oil","pursue-oil","ready-roll-on-stand","roman-chamomile-oil","rosemary-oil","salubelle-oil","serenity-bath-bar","serenity-oil","serenity-valerian-stick","shinrin-yoku-oil","siberian-fir-oil","simple-solutions-enrollment-kit","smart-and-sassy-oil","spa-body-wash","spa-citrus-bliss-hand-lotion","spa-hand-and-body-lotion","spa-hand-and-body-lotion-3-pack","spa-replenishing-body-butter","spanish-sage-oil","spearmint-oil","storage-essential-oil-cap-stickers","storage-gray-8-vial-keychain","sun-care-body-lotion","sun-care-body-spray","sun-care-duo","supermint-beadlets","supermint-oil","supermint-toothpaste","supermint-touch-oil","supplements-daily-vitality-daily-nutrient-pack","supplements-xeo-mega","tangerine-oil","terrashield-oil","terrashield-spray-oil","thyme-oil","toppers-10-ml","toppers-5-and-15-ml","travel-kit-empty-bottles","turmeric-oil","usage-internal-veggie-caps","wild-orange-oil","wild-orange-oil-5ml","wintergreen-oil","yarrow-pom-oil","ylang-ylang-oil","zendocrine-oil","zengest-oil","zengest-oil-5ml","zengest-touch-oil"},
    'GT': {"10-ml-amber-roller-bottle-6-pack","5-ml-amber-bottle-6-pack","abode-foaming-hand-wash","abode-hand-wash-dispenser","abode-liquid-dish-soap-dispenser","abode-liquid-dish-wash","abode-multisurface-spray-dispenser","abode-oil","adaptiv-oil","adaptiv-touch-oil","adobe-multi-surface-cleaner","air-x-oil","alpha-crs","arborvitae-oil","aromatouch-enrollment-kit","aromatouch-kit","aromatouch-oil","aromatouch-oil-5ml","athletes-kit","balance-oil","balance-oil-5ml","basil-oil","beginners-trio-kit","bergamot-oil","breathe-oil","breathe-oil-5ml","breathe-respiratory-drops","breathe-stick","caja-de-madera-con-logo","cardamom-oil","cassia-oil","cedarwood-oil","cheer-oil","cinnamon-oil","citronella-oil","citrus-bliss-invigorating-bath-bar","citrus-bliss-invigorating-bath-bar-3-pack","citrus-bliss-oil","citrus-bloom-oil","clary-calm-roll-on-oil","clary-sage-oil","clove-oil","copaiba-oil","copaiba-softgels","copaiba-touch-oil","coriander-oil","correct-x","curso-de-la-tecnica-aroma-touch-gt","cypress-oil","daily-nutrient-pack","davana-touch-oil","deep-blue-oil","deep-blue-polyphenol","deep-blue-rub","deep-blue-stick","digestzen-gx-assist","digestzen-oil","digestzen-oil-5ml","digestzen-terrazyme","doterra-balance-touch-oil","doterra-brave-oil","doterra-calmer-oil","doterra-ddr-prime-oil","doterra-ginger-drops","doterra-greens","doterra-rescuer-oil","doterra-spa-basics-kit","doterra-spa-body-scrub","doterra-spa-body-wash","doterra-spa-hand-and-body-lotion","doterra-spa-hand-and-body-lotion-3-pack","doterra-spa-lip-balm-herbal","doterra-spa-replenishing-body-butter","doterra-steady-oil","doterra-stronger-oil","doterra-tamer-oil","doterra-thinker-oil","duo-doterra-sun","elevation-oil","essential-supplements-kit","essentials-bag-set","essentials-petal-kit","eucalyptus-oil","family-essentials-kit","family-essentials-kit-with-diffuser","fractionated-coconut-oil","frankincense-oil","frankincense-oil-5ml","frankincese-stick-naio-wood","geranium-oil","ginger-oil","grapefruit-oil","guaiacwood-oil","hair-care-daily-conditioner","hair-care-duo","hair-care-leave-in-conditioner","hair-care-mini-travel-kit","hair-care-protecting-shampoo","hair-care-trio","hawaiian-sandalwood-oil","hd-clear-oil","home-essentials-kit","hydrating-body-mist-with-beautiful-blend","hygge-blend-oil","immortelle-oil-roll-on","in-tune-oil","intro-kit","intro-kit-6-pack","jasmine-touch-oil","juniper-berry-oil","kids-collection","kids-collection-enrollment-kit","kit-metapwr","koala-diffuser-holiday","laluz-diffuser","lavender-oil","lavender-oil-5ml","lavender-peace-bath-bar","lavender-peace-bath-bar-3-pack","lavender-peace-duo","lavender-peace-oil","lavender-peace-stick","lavender-peace-touch-oil","lemon-eucalyptus-oil","lemon-oil","lemon-oil-5ml","lemongrass-oil","lifelong-vitality-pack","lime-oil","lotus-wood-display","lrp-kit-daily-habits","lrp-kit-immune-support","madagascar-vanilla-oil","marjoram-oil","melaleuca-oil","melaleuca-oil-5ml","metapwr-assist","metapwr-beadlets","metapwr-oil","metapwr-softgels","mexican-cooking-blend","microplex-vmz","mood-management-kit","motivate-oil","myrrh-oil","natural-deodorant-with-doterra-balance","on-guard-foaming-dispenser-3-pack","on-guard-foaming-hand-wash","on-guard-foaming-hand-wash-with-two-dispensers","on-guard-laundry-detergent","on-guard-mouthwash","on-guard-natural-whitening-toothpaste","on-guard-oil","on-guard-oil-5ml","on-guard-oil-beadlets","on-guard-protecting-throat-drops","on-guard-sanitizing-mist","onguard-foaming-hand-wash-two-pack","oregano-oil","oregano-oil-5ml","pasttense-oil-roll-on","patchouli-oil","peace-oil","pebble-diffuser","peppermint-beadlets","peppermint-oil","peppermint-oil-5ml","peppermint-softgels","petal-diffuser","phytoestrogen-complex","pipettes-50-pk","planilla-de-etiquetes-para-aceites","purify-oil","pursue-oil","roam-diffuser","roman-chamomile-oil","rose-touch-oil","rosemary-oil","shinrin-yoku-oil","siberian-fir-oil","simple-solutions-enrollment-kit","skin-care-anti-aging-moisturizer","skin-care-facial-cleanser","skin-care-hydrating-cream","skin-care-pore-reducing-toner","skin-care-system","skin-care-tightening-serum","sloth-diffuser","spa-moisturizing-bath-bar","spa-rose-hand-lotion","spanish-sage-oil","sun-after-sun-spray","sun-care-face-body-lotion","sunscreen-spray","supermint-beadlets","supermint-oil","supermint-toothpaste","supermint-touch-oil","supplements-bone-nutrient","sweet-fennel-oil","tangerine-oil","terrashield-oil","terrashield-spray-oil","thyme-oil","trio-doterra-sun","tropical-cooking-blend","turmeric-oil","ultra-fine-continuous-mist-sprayer","usage-internal-veggie-caps","vetiver-oil","wellness-kit-respiratory","whisper-touch-oil","wild-orange-oil","wild-orange-oil-5ml","womens-health-kit","xeo-mega","yarrow-pom-oil","ylang-ylang-oil","zendocrine-oil"},
    'MX': {"abod-dish-washer-and-bottle","abode-hand-wash-concentrade-and-bottle","abode-multipurpose-concentrate","abode-oil","adaptiv-oil","adaptiv-touch-oil","adobe-citrus-bloom-hand-wash-concentrate","adobe-liquid-dish-soap","air-repair-oil","amber-dram-bottles","amber-hand-wash-dispenser","arborvitae-oil","aromatouch-oil","aromatouch-technique-kit","aromatouch-training-enrollment-kit","athletes-kit-8-pack","ba","baby-diaper-cream","baby-hair-and-body-wash","baby-lotion","balance-bath-bar","balance-deodorant","balance-oil","basic-enrollment-kit","basil-oil","bear-diffuser","bear-diffuser-tangerine-oil","beautiful-touch-oil","bergamot-mint-oil","bergamot-oil","birch-oil","black-pepper-oil","black-spruce-oil","blue-lotus-touch-oil","blue-tansy-oil","body-mineral-sunscreen-spray","boys-kit-with-bear-diffuser","cananga-oil","caraway-oil-5ml","cardamom-oil","cassia-oil","cedarwood-oil","celery-seed-oil","cheer-touch-oil","cilantro-oil","cinnamon-bark-oil","citronella-oil","citrus-bliss-oil","citrus-bloom-oil","citrus-bloom-touch-oil","clary-sage-oil","clarycalm-oil","clementine-oil","clip-diffuser-ravintsara-oil","clove-oil","console-touch-oil","copaiba-kof-2022","copaiba-oil","copaiba-softgels","copaiba-touch-oil","coriander-oil","correct-x","curso-de-la-tecnica-aroma-touch","cypress-oil","daily-conditioner","damiana-touch-oil","ddr-prime","ddr-prime-oil","deep-blue-oil","deep-blue-roll-on","deep-blue-rub","deep-blue-softgels","deep-blue-stick","digestzen-oil","digestzen-touch-oil","doterra-affirm-oil","doterra-anchor-oil","doterra-arise-oil","doterra-baby-collection","doterra-balance-touch-oil","doterra-brave-oil","doterra-brave-oil-5ml","doterra-calmer-oil","doterra-calmer-oil-5ml","doterra-cheer-5ml","doterra-console-oil","doterra-forgive-oil","doterra-hope-oil","doterra-lilac-case","doterra-motivate-oil","doterra-mugs-purple","doterra-passion-oil","doterra-peace-oil","doterra-rescuer-oil","doterra-rescuer-oil-5ml","doterra-spa-body-butter","doterra-spa-refreshing-body-wash","doterra-spa-serenity-bath-bar","doterra-steady-oil","doterra-steady-oil-5ml","doterra-stronger-oil","doterra-stronger-oil-5ml","doterra-tamer-oil","doterra-tamer-oil-5ml","doterra-thinker-oil","doterra-thinker-oil-5ml","doterra-touch-kit","dual-deluxe-bag","easy-air-drops","easy-air-oil","easy-air-stick","easy-air-touch","easy-air-vapor-stick","elevation-oil","emotion-management-enrollment-kit","emotional-aromatherapy-kit","eo-mega-essential-oil-omega-complex","essential-oil-cap-stickers","essential-oil-stacking-box","essential-oil-waist-bag","essential-skin-care-anti-aging-moisturizer","essential-skin-care-brightening-gel","essential-skin-care-eye-cream","essential-skin-care-facial-cleanser","essential-skin-care-hydrating-cream","essential-skin-care-invigorating-scrub","essential-skin-care-tightening-serum","eucalyptus-oil","eucalyptus-oil-blend","evolve-gala-blend-oil","face-and-body-mineral-sunscreen-lotion","fiber","forgive-touch-oil","fractionated-coconut-oil","frankincense-oil","frankincense-touch-oil","frankincese-stick-naio-wood","geranium-oil","ginger-oil","girls-kit-with-kitty-diffuser","grapefruit-oil","green-mandarin-oil","guaiacwood-oil","hair-care-beauty-kof","hair-care-travel-set-empty","hand-and-body-lotion","hand-and-body-lotion-3-pack","hand-soap-dispenser","hard-roll-on-case","harvest-spice-oil","hawaiian-sandalwood-oil","hd-clear-facial-lotion","hd-clear-roll-on","helichrysum-oil","helichrysum-touch-oil","hinoki-oil","holiday-joy-oil","holiday-peace-oil","home-","home-essentials-kit","home-essentials-plus-enrollment-kit","hygge-oil","immunity-kit","influence-guide","inspire-guide","introductory-enrollment-packet","introductory-kit","island-mint-oil","jasmine-oil-2","jasmine-touch-oil","juniper-berry-oil","keychain-grey","kitty-diffuser","koala-diffuser","koala-diffuser-lavender-oil","laluz-diffuser","laluz-diffuser-clementine-oil","laurel-leaf-oil","lavender-oil","lavender-touch-oil","leave-in-conditioner","lemon-eucalyptus-oil","lemon-oil","lemongrass-oil","lifelong-vitality-pack-llv","lime-oil","lip-balm-herbal","lip-balm-tropical","liquid-soap-dispenser","live-guide","llv-with-eo-mega","love-oils-case","madagascar-vanilla-oil","magnolia-oil","magnolia-touch-oil","malama-oil","marjoram-oil","melissa-oil","metapwr-advantage","metapwr-advantage-2-pack","metapwr-assist","metapwr-beadlets","metapwr-gum","metapwr-kit","metapwr-oil","metapwr-softgels","microplex-vmz","midnight-forest-oil","mightymint-beadlets","mightymint-oil","mightymint-toothpaste","mightymint-touch-oil","mind-mood-kit","moisturizing-bath-bar","motivate-touch-oil","myrrh-oil","myrrh-touch","natural-habits-enrollment-kit","natural-reset-enrollment-kit","natural-solutions-plus-enrollment-kit","neck-back-wrap","neoprene-bag-navy-blue","neoprene-bag-orange","neoprene-bag-sky-blue","neroli-oil","neroli-touch-oil","niaouli-oil","non-woven-bag","northern-escape-oil","on-guard-chewable-tablets","on-guard-detergent","on-guard-drops","on-guard-foaming-hand-wash","on-guard-hand-wash-concetrate","on-guard-oil","on-guard-oil-beadlet","on-guard-sanitizing-mist","on-guard-toothpaste","on-guard-touch","onguard-cleaner-concentrate","onguard-foaming-hand-wash-two-pack","onguard-foaming-hand-wash-with-two-dispensers","onguard-natural-whitening-toothpaste-samples","onguard-softgels","ontask-oil-roll-on","oregano-oil","oregano-touch-oil","osmanthus-touch-oil","palmarosa-oil","palmarose-oil","passion-touch-oil","pasttense-oil-roll-on","patchouli-oil","pb-core-caps","pebble-diffuser","pebble-diffuser-sunny-citrus-oil","peppermint-beadlets","peppermint-oil","peppermint-softgels","peppermint-touch-oil","petal-diffuser","petitgrain-oil","pink-pepper-oil","pore-reducing-toner","portable-phone-charger","product-guide","product-guide-10-pack","protecting-shampoo","purify-oil","ravintsara-oil","roll-on-box","roman-chamomile-oil","rose-hand-lotion","rose-oil","rose-touch-oil","rose-train-case","rosemary-oil","sales-guide","sales-guide-10-pack","salon-essentials-root-to-tip-serum","salubelle-oil","sandalwood-oil","serenity-blend-oil","serenity-oil","serenity-stick-valerian","shinrin-yoku-15ml","siberian-fir-oil","silicone-oil-organizer","spa-hydrating-body-mist","spanish-sage-oil","spearmint-oil","strengths-guide","summer-savory-oil","sun-care-stick","sun-face-sunscreen-moisturizer","sunny-citrus-oil","supplements-alpha-crs","supplements-digestzen-terrazyme","supplements-gx-assist","supplements-xeo-mega","sweet-fennel-oil","tangerine-oil","tea-tree-oil","tea-tree-touch-oil","terracota-diffuser","terrashield-oil","terrashield-oil-spray","thyme-oil","triease-softgels","tulsi-holy-basil-oil","turmeric-duo-caps","turmeric-oil","usage-internal-veggie-caps","vanilla-chai-oil","verage-facial-cleanser","verage-facial-toner","verage-moisturizer","verage-salubelle-hydrating-system","verage-skin-care-collection","vertical-sliding-oil-case","vetiver-oil","vetiver-touch","vmg-eo-mega","vmg-whole-food-nutrient-complex","volo-diffuser-marble-black-spruce-oil","volo-diffuser-onyx","volo-diffuser-onyx-northern-escape-oil","volo-marble-diffuser","whisper-touch-oil","wild-orange-oil","wintergreen-oil","wooden-box-with-logo","yarrow-pom-oil","yarrow-pom-serum","ylang-ylang-oil","yoga-collection","yule-log-oil","zedocrine-oil"},
    'BO': {"foundational-wellness-bundle"},
}

COUNTRY_CATEGORIES = {
    "BR": ["accessories","body-care","collections","doterra-hair-care","doterra-metapwr","doterra-spa","enrollment-kits","kits-collections","limited-time-offers","natural-flavorings","personal-care","personal-care-verage","proprietary-blends","sales-aids","single-oils","supplements-foods"],
    "CL": ["accessories","breathe-products","collections","deep-blue-products","diffusers","enrollment-kits","essential-skin-care","food-flavoring","kits-collections","new-products","on-guard-products","personal-care","proprietary-blends","salon-essentials","single-oils","skin-care-hd-clear","spa"],
    "CO": ["accessories","baby-collection","breathe-products","collections","deep-blue-products","diffusers","doterra-touch-oils","enrollment-kits","essential-skin-care","hair-care","hd-clear","kits-collections","new-products","on-guard-products","personal-care","proprietary-blends","single-oils","spa-products","supplements","zengest-products"],
    "CR": ["abode","accessories","breathe-products","collections","deep-blue-products","diffusers","doterra-spa-products","doterra-sun","enrollment-kits","hair-care-products","hd-clear-products","kits-collections","loyalty-reward-kits","metapwr-products","natural-products","new-products","on-guard-products","personal-care","proprietary-blends","serenity-products","single-oils","skin-care","storage","touch-products","wellness","zengest-products"],
    "EC": ["abode-products","accessories","breathe-products","collections","deep-blue-products","diffusers","doterra-touch-products","enrollment-kits","essential-skin-care","hair-care","kits-collections","new-products","on-guard-products","personal-care","proprietary-blends","single-oils","skin-care-hd-clear","spa","supplements"],
    "GT": ["abode","accessories","breathe-products","collections","deep-blue-products","diffusers","doterra-spa","doterra-sun","enrollment-kits","hd-clear-skin-care","kits-collections","lavender-peace-products","literature","loyalty-reward-kits","metapwr","new-products","on-guard-products","personal-care","phytotherapeutic-products","proprietary-blends","salon-essentials-hair-care","single-oils","skin-care","storage","supplements","verage-skin-care"],
    "MX": ["accessories","baby-collection","body-care","collections","daily-vitality","deep-blue-products","diffusers","digestzen-products","doterra-spa","easy-air-products","enrollment-kits","essential-skin-care","hd-clear","kits-collections","literature","metapwr-products","monthly-discounts","new-releases","on-guard-products","personal-care","productos-abode","proprietary-blends","salon-essentials-hair-care","serenity-products","single-oils","specialized-supplements","sun-care","supplements","verage-skin-care","while-supplies-last","yarrow-pom-skin-care"],
}

# doTERRA uses different slug variants per country (e.g. "adaptiv-oil" vs "doterra-adaptiv-oil")
# This map defines known aliases: primary_slug → set of alternative slugs seen in other countries
SLUG_ALIASES = {
    'adaptiv-oil': {'doterra-adaptiv-oil'},
    'breathe-oil': {'doterra-breathe-oil', 'easy-air-oil', 'doterra-breathe-touch-oil'},
    'citrus-bliss-oil': {'doterra-citrus-bliss-oil'},
    'deep-blue-oil': {'doterra-deep-blue-oil'},
    'elevation-oil': {'doterra-elevation-oil'},
    'serenity-oil': {'doterra-serenity-oil', 'lavender-peace-oil', 'serenity-blend-oil', 'doterra-serenity-oil'},
    'doterra-balance-oil': {'balance-oil'},
    'aromatouch-oil': {'aromatouch-oil-blend'},
    'zengest-oil': {'digestzen-oil', 'doterra-zengest-oil'},
    'clary-calm-roll-on': {'clarycalm-oil', 'clary-calm-roll-on-oil'},
    'metapwr-oil': {'doterra-metapwr-oil', 'doterra-metapwr-oil-flavor'},
    'deep-blue-polyphenol-complex': {'deep-blue-polyphenol'},
    'zendocrine-oil': {'zedocrine-oil'},
    'on-guard-oil': {'onguard-oil'},
    'intune-oil-roll-on': {'intune-oil', 'intune-roll-on-oil', 'intune-roll-on', 'in-tune-oil'},
    'pasttense-oil-roll-on': {'pasttense-oil', 'pasttense-roll-on', 'pasttense-roll-on-oil', 'past-tense-oil'},
    'melaleuca-oil': {'tea-tree-oil', 'melaleuca-tea-tree-oil', 'tea-tree-oil-5ml'},
    'life-long-vitality-pack': {'lifelong-vitality-pack', 'lifelong-vitality-pack-llv'},
    'home-essentials-enrollment-kit': {'home-essentials-kit', 'home-essentials-pebble', 'home-essentials-petal'},
    'copaiba-softgels': set(),
    'digestzen-terrazyme': {'supplements-digestzen-terrazyme', 'terrazyme'},
    'pb-assist': {'pb-assist-jr', 'pb-core-caps'},
    'on-guard-softgels': {'on-guard-protective-blend-softgel', 'onguard-softgels'},
    'cheer-oil': {'doterra-cheer-oil', 'doterra-cheer-5ml'},
    'console-oil': {'doterra-console-oil'},
    'forgive-oil': {'doterra-forgive-oil'},
    'motivate-oil': {'doterra-motivate-oil'},
    'peace-oil': {'doterra-peace-oil'},
    'passion-oil': {'doterra-passion-oil'},
    'purify-oil': {'purify-oil'},
    'terrashield-oil': {'terrashield-spray', 'terrashield-spray-oil', 'terrashield-oil-spray'},
    'deep-blue-rub': {'doterra-deep-blue-rub', 'doterra-deep-blue-rub-travel-size'},
    'deep-blue-stick': {'doterra-deep-blue-stick'},
    'breathe-stick': {'breathe-vapor-stick', 'doterra-breathe-balm-stick', 'easy-air-stick', 'easy-air-vapor-stick'},
    'on-guard-foaming-hand-wash': {'doterra-on-guard-foaming-hand-wash-2pk', 'on-guard-hand-wash-concetrate', 'onguard-foaming-hand-wash-two-pack'},
    'on-guard-natural-whitening-toothpaste': {'on-guard-toothpaste'},
    'spa-hand-and-body-lotion': {'hand-and-body-lotion', 'doterra-spa-hand-and-body-lotion'},
    'spa-replenishing-body-butter': {'doterra-spa-replenishing-body-butter', 'spa-body-butter', 'doterra-spa-body-butter'},
    'correct-x': set(),
    'supermint-toothpaste': {'doterra-supermint-toothpaste', 'mightymint-toothpaste'},
    'natural-deodorant-with-doterra-balance': {'natural-deodorant-infused-with-doterra-balance-essential-oil', 'balance-deodorant'},
    'doterra-brave-oil': {'doterra-brave-oil-5ml', 'doterra-braver-oil'},
    'doterra-stronger-oil': {'doterra-stronger-oil-5ml'},
    'alpha-crs': {'supplements-alpha-crs'},
    'metapwr-advantage': {'metapwr-advantage-2-pack'},
    'on-guard-beadlets': {'on-guard-beadlet', 'on-guard-oil-beadlets', 'on-guard-oil-beadlet'},
    'breathe-drops': {'breathe-respiratory-drops', 'easy-air-drops'},
    'hair-care-protecting-shampoo': {'protecting-shampoo', 'salon-essentials-protecting-shampoo'},
    'hair-care-daily-conditioner': {'daily-conditioner', 'salon-essentials-smoothing-conditioner'},
    'hair-care-leave-in-conditioner': {'leave-in-conditioner', 'salon-essentials-leave-in-conditioner'},
    'spa-citrus-bliss-hand-lotion': {'citrus-bliss-hand-lotion', 'doterra-spa-citrus-bliss-hand-lotion'},
    'spa-body-wash': {'doterra-spa-body-wash', 'doterra-spa-refreshing-body-wash'},
    'hydrating-body-mist-with-beautiful-blend': {'spa-hydrating-body-mist'},
}

def _product_available_in(product, country_code):
    """Check if a product is available in a given country, handling slug variants."""
    slug = _get_product_slug(product)
    country_set = COUNTRY_PRODUCTS.get(country_code, set())
    if slug in country_set:
        return True
    # Check known aliases
    aliases = SLUG_ALIASES.get(slug, set())
    if aliases & country_set:
        return True
    # Check reverse aliases (if our slug is an alias of another primary)
    for primary, alt_set in SLUG_ALIASES.items():
        if slug in alt_set and primary in country_set:
            return True
    return False


def verify_product_urls(product, countries=None):
    """
    Live-check doTERRA URLs via HEAD requests for a single product.
    Returns dict: {country_code: {'status': int, 'ok': bool, 'url': str}}
    """
    slug = _get_product_slug(product)
    if countries is None:
        countries = [c for c in DOTERRA_COUNTRIES if c != 'BO']
    results = {}
    for code in countries:
        url = get_product_country_url(slug, code)
        if not url:
            results[code] = {'status': 0, 'ok': False, 'url': url}
            continue
        try:
            resp = requests.head(url, timeout=8, allow_redirects=True)
            # doTERRA returns 200 for valid products, 404 or redirects for invalid
            ok = resp.status_code == 200
            results[code] = {'status': resp.status_code, 'ok': ok, 'url': url}
        except requests.RequestException:
            results[code] = {'status': 0, 'ok': False, 'url': url}
    return results


def verify_all_products(products_data):
    """
    Verify all products across all countries. Returns dict:
    {product_id: {country_code: {'status': int, 'ok': bool, 'url': str}}}
    """
    all_results = {}
    countries = [c for c in DOTERRA_COUNTRIES if c != 'BO']
    for p in products_data:
        pid = p['id']
        all_results[pid] = verify_product_urls(p, countries)
    return all_results


# ============================================
# LOAD CSS & DATA
# ============================================

def load_css():
    """Load custom CSS"""
    css_path = "assets/style.css"
    if os.path.exists(css_path):
        with open(css_path, encoding="utf-8") as f:
            st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)

def load_products():
    """Load products from JSON (no cache to ensure fresh data after updates)"""
    _path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "data", "products.json")
    with open(_path, "r", encoding="utf-8") as f:
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
RECRUITMENT_JSON_PATH = os.path.join(os.path.dirname(__file__), "data", "recruitment.json")

def save_products(data):
    """Save products data to JSON file."""
    with open(PRODUCTS_JSON_PATH, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

def _load_recruitment_data():
    """Load recruitment pipeline data."""
    try:
        with open(RECRUITMENT_JSON_PATH, "r", encoding="utf-8") as f:
            return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        return {"pipeline": [], "team_members": [], "content_calendar": [], "settings": {"weekly_prospecting_goal": 10, "weekly_followup_goal": 5, "monthly_enrollment_goal": 2}}

def _save_recruitment_data(data):
    """Save recruitment pipeline data."""
    with open(RECRUITMENT_JSON_PATH, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

def _ensure_ecuador_spanish_url(url):
    """Convert any doTERRA URL to the Ecuador Spanish version for consistent scraping.
    E.g., doterra.com/US/en/p/lavender-oil -> doterra.com/EC/es_EC/p/lavender-oil
    """
    clean = url.split('?')[0]
    # Match pattern: /XX/xx_XX/p/slug or /XX/xx/p/slug
    slug_match = re.search(r'/p/([\w-]+)', clean)
    if slug_match:
        slug = slug_match.group(1)
        return f'https://www.doterra.com/EC/es_EC/p/{slug}'
    return clean

def scrape_doterra_product(url):
    """Scrape product data from a doTERRA product page URL.
    Returns dict with 'success' bool and 'data' dict or 'error' string.
    Auto-detects language: fetches both English and Spanish versions.
    Extracts: imagen_url, precio_usd, precio_mayoreo, doterra_sku, pv,
              infografia_url, nombre, nombre_en, descripcion.
    """
    try:
        clean_url = url.split('?')[0]
        # Always fetch the Ecuador Spanish page for prices/descriptions
        es_url = _ensure_ecuador_spanish_url(clean_url)
        headers = {
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Accept-Language': 'es-EC,es;q=0.9',
        }
        response = requests.get(es_url, headers=headers, timeout=15)
        response.raise_for_status()

        soup = BeautifulSoup(response.text, 'lxml')
        data = {}
        data['doterra_url'] = es_url

        # ---- Extract product names from page title ----
        # Pattern: "Aceite de Lavanda | Lavender Oil | Aceites esenciales dōTERRA"
        og_title = soup.find('meta', {'property': 'og:title'})
        title_text = og_title['content'] if og_title and og_title.get('content') else ''
        if not title_text:
            title_tag = soup.find('title')
            title_text = title_tag.text if title_tag else ''

        if '|' in title_text:
            parts = [p.strip() for p in title_text.split('|')]
            if len(parts) >= 2:
                data['nombre'] = parts[0]  # Spanish name
                # English name: remove common suffixes like "Oil", "Blend" context
                en_name = parts[1].replace('Aceites esenciales dōTERRA', '').strip()
                if en_name:
                    data['nombre_en'] = en_name

        # ---- og:image for product photo ----
        og_img = soup.find('meta', {'property': 'og:image'})
        if og_img and og_img.get('content'):
            img_url = og_img['content']
            if not img_url.startswith('http'):
                img_url = 'https://www.doterra.com' + img_url
            data['imagen_url'] = img_url

        # Better image: look for 2x3 background-image divs (higher res)
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

        # ---- Text content for prices and SKU ----
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

        # ---- Infographic PDF link ----
        for a in soup.find_all('a', href=True):
            href = a.get('href', '')
            if '.pdf' in href.lower() and ('infographic' in href.lower() or 'infografia' in href.lower()):
                if not href.startswith('http'):
                    href = 'https://media.doterra.com' + href
                data['infografia_url'] = href
                break

        # Also search raw HTML text for PDF URLs (JS-rendered links)
        if 'infografia_url' not in data:
            pdf_matches = re.findall(r'https?://media\.doterra\.com[^\s"\'<>]*infographic[^\s"\'<>]*\.pdf', response.text, re.IGNORECASE)
            if not pdf_matches:
                pdf_matches = re.findall(r'https?://media\.doterra\.com[^\s"\'<>]*infografia[^\s"\'<>]*\.pdf', response.text, re.IGNORECASE)
            if pdf_matches:
                data['infografia_url'] = pdf_matches[0]

        # Fallback: construct infographic URL from slug pattern
        # doTERRA pattern: media.doterra.com/cr-otg/es/presentations/infographic-{slug}.pdf
        if 'infografia_url' not in data:
            slug_for_pdf = re.search(r'/p/([\w-]+)', es_url)
            if slug_for_pdf:
                raw_slug = slug_for_pdf.group(1)
                # Remove common suffixes like "-oil", "-blend", "-touch" for the PDF name
                pdf_slug = re.sub(r'-(oil|blend|touch|essential|aceite|mezcla)$', '', raw_slug, flags=re.IGNORECASE)
                # Try multiple doTERRA media CDN patterns
                fallback_urls = [
                    f'https://media.doterra.com/cr-otg/es/presentations/infographic-{pdf_slug}.pdf',
                    f'https://media.doterra.com/us/en/presentations/infographic-{pdf_slug}.pdf',
                    f'https://media.doterra.com/cr-otg/es/presentations/infographic-{raw_slug}.pdf',
                    f'https://media.doterra.com/us/en/presentations/infographic-{raw_slug}.pdf',
                ]
                for fb_url in fallback_urls:
                    try:
                        check = requests.head(fb_url, headers=headers, timeout=5, allow_redirects=True)
                        if check.status_code == 200:
                            data['infografia_url'] = fb_url
                            break
                    except Exception:
                        continue

        # ---- Additional image sources ----
        # Try to find product image from img tags (some doTERRA pages use these)
        if 'imagen_url' not in data:
            for img in soup.find_all('img', src=True):
                src = img.get('src', '')
                if 'doterra.com' in src and ('product' in src.lower() or 'medias' in src.lower()):
                    if not src.startswith('http'):
                        src = 'https://www.doterra.com' + src
                    data['imagen_url'] = src
                    break

        # Try to find image from JSON-LD structured data
        if 'imagen_url' not in data:
            for script in soup.find_all('script', type='application/ld+json'):
                try:
                    import json
                    ld = json.loads(script.string or '{}')
                    if isinstance(ld, dict) and ld.get('image'):
                        img_val = ld['image']
                        if isinstance(img_val, list):
                            img_val = img_val[0]
                        if isinstance(img_val, str) and img_val:
                            data['imagen_url'] = img_val
                            break
                except Exception:
                    continue

        # ---- Description (Spanish from og:description) ----
        og_desc = soup.find('meta', {'property': 'og:description'})
        if og_desc and og_desc.get('content'):
            data['descripcion'] = og_desc['content']

        # ---- Also try to get the English page for English description ----
        slug_match = re.search(r'/p/([\w-]+)', es_url)
        if slug_match:
            slug = slug_match.group(1)
            en_url = f'https://www.doterra.com/US/en/p/{slug}'
            try:
                en_headers = dict(headers)
                en_headers['Accept-Language'] = 'en-US,en;q=0.9'
                en_resp = requests.get(en_url, headers=en_headers, timeout=10)
                if en_resp.status_code == 200:
                    en_soup = BeautifulSoup(en_resp.text, 'lxml')
                    en_og_title = en_soup.find('meta', {'property': 'og:title'})
                    if en_og_title and en_og_title.get('content'):
                        en_parts = [p.strip() for p in en_og_title['content'].split('|')]
                        if en_parts:
                            data['nombre_en'] = en_parts[0]  # English name from US page
                    en_og_desc = en_soup.find('meta', {'property': 'og:description'})
                    if en_og_desc and en_og_desc.get('content'):
                        data['descripcion_en'] = en_og_desc['content']
            except Exception:
                pass  # English page fetch is optional — don't fail the whole scrape

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
    # Type-based icons first
    if tipo == 'difusor':
        return '🌫️'
    if tipo == 'accesorio':
        return '🔧'
    if tipo == 'cuidado_personal':
        return '🧴'
    if tipo == 'cuidado_piel':
        return '✨'
    if tipo == 'cuidado_cabello':
        return '💇'
    if tipo == 'kit':
        return '📦'
    if tipo == 'suplemento':
        return '💊'
    if 'blend' in tipo or 'mezcla' in tipo:
        return '🌸'
    if 'roll-on' in tipo or 'rollon' in nombre:
        return '🫧'
    # Category-based icons
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
    if any(x in cats for x in ['muscular', 'articular']):
        return '💪'
    if any(x in cats for x in ['femenin', 'hormonal']):
        return '🌺'
    return '🌿'

def render_product_card(product, mode="catalog", match_percentage=None, recommendation_reason=None, rank=None):
    """SINGLE SOURCE OF TRUTH for all product card rendering.
    mode: "catalog" (website), "recommendation" (after questionnaire), "dashboard" (admin)
    Uses only div/span/a tags. No indentation. Hardcoded colors. CSS class tooltips for usage icons.
    """
    price_display = f"${product.get('precio_usd', 'N/A')}"
    pv_display = product.get('pv', '')
    icon = get_product_icon(product)
    imagen_url = product.get('imagen_url', '')
    sku = product.get('doterra_sku', '')
    infografia = product.get('infografia_url', '')
    is_active = product.get('active', True)

    # ---- Image ----
    if imagen_url and 'doterra.com' in imagen_url:
        image_html = f'<div style="width:80px;height:80px;background:url({imagen_url}) center/contain no-repeat;background-color:#f9f6f0;border-radius:12px;flex-shrink:0;"></div>'
    else:
        image_html = f'<div style="width:80px;height:80px;background:linear-gradient(135deg,#e8f0e4,#f0ead8);border-radius:12px;display:flex;align-items:center;justify-content:center;font-size:34px;">{icon}</div>'

    # ---- Usage method circle icons (A, T, I) with CSS tooltips ----
    uso_icons = []
    if product.get('uso_aromatico'):
        tooltip_text = product['uso_aromatico'][:60]
        uso_icons.append(f'<div class="uso-icon uso-A"><span class="uso-tooltip">Aromático: {tooltip_text}</span>A</div>')
    if product.get('uso_topico'):
        tooltip_text = product['uso_topico'][:60]
        uso_icons.append(f'<div class="uso-icon uso-T"><span class="uso-tooltip">Tópico: {tooltip_text}</span>T</div>')
    if product.get('uso_interno'):
        tooltip_text = product['uso_interno'][:60]
        uso_icons.append(f'<div class="uso-icon uso-I"><span class="uso-tooltip">Interno: {tooltip_text}</span>I</div>')
    uso_icons_html = f'<div style="display:flex;gap:6px;align-items:center;">{"".join(uso_icons)}</div>' if uso_icons else ''

    # ---- Rank (recommendation mode only) ----
    rank_html = ''
    if mode == "recommendation" and rank:
        rank_labels = {1: '🥇 Mejor opción', 2: '🥈 Excelente alternativa', 3: '🥉 También recomendado'}
        rank_html = f'<div style="font-size:12px;font-weight:700;color:#7C9070;margin-bottom:6px;">{rank_labels.get(rank, "")}</div>'

    # ---- Match badge (recommendation mode only) ----
    match_html = ''
    if mode == "recommendation" and match_percentage:
        match_html = f'<span style="background:linear-gradient(135deg,#7C9070,#B8965A);color:white;padding:4px 12px;border-radius:20px;font-size:12px;font-weight:600;">{match_percentage}%</span>'

    # ---- Recommendation reason ----
    reason_html = ''
    if mode == "recommendation" and recommendation_reason:
        reason_text = recommendation_reason.replace('_', ' ')
        reason_html = f'<div style="background:rgba(124,144,112,0.08);color:#7C9070;padding:8px 12px;border-radius:8px;font-size:13px;font-weight:500;margin-bottom:12px;border-left:3px solid #7C9070;">{reason_text}</div>'

    # ---- Dashboard status badges ----
    status_badges = ''
    if mode == "dashboard":
        active_badge = '<span style="background:#e8f5e9;color:#2e7d32;padding:2px 8px;border-radius:10px;font-size:11px;font-weight:600;">Activo</span>' if is_active else '<span style="background:#ffebee;color:#c62828;padding:2px 8px;border-radius:10px;font-size:11px;font-weight:600;">Inactivo</span>'
        stock = product.get('stock', 99)
        stock_badge = f'<span style="background:#fff8e1;color:#f57f17;padding:2px 8px;border-radius:10px;font-size:11px;">Stock: {stock}</span>' if stock < 10 else ''
        stripe_badge = '<span style="background:#e8eaf6;color:#283593;padding:2px 8px;border-radius:10px;font-size:11px;">Stripe ✓</span>' if product.get('stripe_price_id') else ''
        status_badges = f'<div style="display:flex;gap:6px;align-items:center;margin-bottom:4px;">{active_badge}{stock_badge}{stripe_badge}</div>'

    # ---- Prices ----
    precio_mayoreo = product.get('precio_mayoreo', '')
    mayoreo_html = f'<span style="color:#999;font-size:12px;text-decoration:line-through;">${precio_mayoreo}</span>' if precio_mayoreo else ''

    # ---- Benefits ----
    benefits = product.get('beneficios', [])[:4]
    benefits_html = ''.join([f'<div style="color:#666;font-size:13px;padding:2px 0;">• {b}</div>' for b in benefits])

    # ---- Category badges ----
    cat_badges = ''.join([f'<span style="background:#eee;color:#888;padding:2px 8px;border-radius:10px;font-size:11px;">{cat.replace("_", " ").title()}</span>' for cat in product.get('categoria', [])[:3]])

    # ---- Details section (benefits + detailed usage) ----
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

    # ---- Description ----
    descripcion = product.get('descripcion', '').replace('_', ' ')

    # ---- Infographic button (dashboard and catalog) ----
    infog_btn = ''
    if infografia:
        infog_btn = (
            f'<a href="{infografia}" target="_blank" style="display:inline-flex;align-items:center;gap:6px;padding:8px 14px;'
            'background:#f5f0e6;color:#7C9070;border-radius:8px;text-decoration:none;font-size:13px;font-weight:600;">📄 Infografía PDF</a>'
        )

    # ---- Action buttons (catalog and recommendation: buy/consult; dashboard: infographic) ----
    actions_html = ''
    if mode in ("catalog", "recommendation"):
        comprar_link = product.get('doterra_url', DOTERRA_SHOP_URL)
        consult_msg = f"Hola Suzanna! Me interesa {product['nombre']} ({product.get('nombre_en', '')}). ¿Me puedes dar más información?"
        consult_link = whatsapp_link(consult_msg)
        actions_html = (
            '<div style="display:flex;gap:10px;">'
            f'<a href="{comprar_link}" target="_blank" style="flex:1;text-align:center;padding:11px 16px;'
            'background:linear-gradient(135deg,#7C9070,#B8965A);color:white;border-radius:10px;'
            'font-weight:600;font-size:14px;text-decoration:none;">🛒 Comprar</a>'
            f'<a href="{consult_link}" target="_blank" style="flex:1;text-align:center;padding:11px 16px;'
            'background:#25D366;color:white;border-radius:10px;font-weight:600;font-size:14px;'
            'text-decoration:none;">💬 Consultar</a>'
            '</div>'
        )
    elif mode == "dashboard":
        actions_html = f'<div style="display:flex;gap:10px;align-items:center;">{infog_btn}</div>' if infog_btn else ''

    # ---- Card border style ----
    border = 'border:1px solid rgba(0,0,0,0.04);' if (mode != "dashboard" or is_active) else 'border:1px solid #ffcdd2;'
    opacity = 'opacity:0.6;' if (mode == "dashboard" and not is_active) else ''

    # ---- SKU line (dashboard only shows extra detail) ----
    sku_html = f'<span style="color:#ccc;font-size:11px;">SKU: {sku}</span>' if mode == "dashboard" and sku else ''

    # ---- Dashboard inline action bar (inside card) ----
    dash_action_bar = ''
    if mode == "dashboard":
        dash_action_bar = (
            '<div class="dash-action-bar">'
            '<div class="dash-action-bar-inner">'
            f'{infog_btn}'
            '<div class="dash-action-placeholder"></div>'
            '</div>'
            '</div>'
        )

    # ---- Build card ----
    card_bottom = f'{actions_html}' if mode != "dashboard" else dash_action_bar

    html = (
        f'<div style="background:white;border-radius:16px;padding:24px;margin-bottom:0;'
        f'box-shadow:0 2px 12px rgba(60,50,41,0.07);{border}{opacity}'
        f'{"padding-bottom:12px;" if mode == "dashboard" else ""}">'
        f'{status_badges}'
        '<div style="display:flex;align-items:flex-start;gap:18px;margin-bottom:14px;">'
        f'<div style="flex-shrink:0;">{image_html}</div>'
        '<div style="flex:1;min-width:0;">'
        f'{rank_html}'
        '<div style="display:flex;align-items:center;gap:10px;flex-wrap:wrap;">'
        f'<div style="margin:0;font-size:1.15rem;font-weight:700;color:#3D3229;">{product["nombre"]}</div>'
        f'<span style="color:#aaa;font-size:13px;">{product.get("nombre_en", "")}</span>'
        f'{match_html}'
        f'{uso_icons_html}'
        '</div>'
        '<div style="display:flex;align-items:baseline;gap:12px;margin-top:4px;">'
        f'<span style="font-size:1.4rem;font-weight:700;color:#C67B4F;">{price_display}</span>'
        f'{mayoreo_html}'
        f'<span style="color:#bbb;font-size:12px;">PV: {pv_display}</span>'
        f'{sku_html}'
        '</div>'
        '</div>'
        '</div>'
        f'{reason_html}'
        f'<div style="color:#666;font-size:14px;line-height:1.6;margin-bottom:12px;">{descripcion}</div>'
        f'<div style="display:flex;gap:6px;flex-wrap:wrap;margin-bottom:12px;">{cat_badges}</div>'
        f'{details_section}'
        f'{card_bottom}'
        '</div>'
    )
    return html


# Backward-compatible aliases
def create_product_card(product, match_percentage=None, recommendation_reason=None, rank=None):
    """Alias for render_product_card in recommendation mode."""
    return render_product_card(product, mode="recommendation", match_percentage=match_percentage,
                               recommendation_reason=recommendation_reason, rank=rank)

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
                st.markdown(render_product_card(product, mode="catalog"), unsafe_allow_html=True)
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


def _render_dashboard_product_card(product):
    """Render a product card in the dashboard — uses the unified render_product_card()."""
    st.markdown(render_product_card(product, mode="dashboard"), unsafe_allow_html=True)


def _product_edit_form(product, key_prefix, is_new=False):
    """Render an edit form for a product. Returns updated product dict.
    Includes Stripe-ready fields for seamless checkout integration.
    """
    ALL_CATEGORIES = [
        'sueño', 'relajacion', 'piel', 'bienestar_emocional', 'digestion',
        'bienestar_digestivo', 'energia', 'enfoque', 'concentracion',
        'respiracion', 'bienestar_respiratorio', 'proteccion', 'defensa_natural',
        'bienestar_inmunologico', 'bienestar_muscular', 'bienestar_articular',
        'bienestar_femenino', 'bienestar_celular', 'bienestar_cerebral',
        'bienestar_cardiovascular', 'bienestar_general',
        'limpieza', 'purificacion', 'meditacion', 'enraizamiento',
        'insectos', 'metabolismo', 'circulacion', 'nauseas', 'cabello',
        'romance', 'duelo', 'estrés', 'niños', 'deporte', 'masaje',
        'familia', 'hogar', 'difusor', 'accesorio', 'portador',
        'cuidado_personal', 'cuidado_piel', 'cuidado_cabello',
        'salud_bucal', 'nutricion', 'anti_envejecimiento',
        'spa', 'kit', 'accesorio_suplemento',
    ]
    ALL_TIPOS = ['aceite_individual', 'mezcla', 'suplemento', 'kit', 'cuidado_personal', 'cuidado_piel', 'cuidado_cabello', 'difusor', 'accesorio']

    # ---- Tab layout for organized editing ----
    tab_basic, tab_content, tab_store = st.tabs(["📦 Producto", "📝 Contenido", "🛒 Tienda y Stripe"])

    with tab_basic:
        col1, col2 = st.columns(2)
        with col1:
            nombre = st.text_input("Nombre (Español):", value=product.get('nombre', ''), key=f"{key_prefix}_nombre")
            nombre_en = st.text_input("Name (English):", value=product.get('nombre_en', ''), key=f"{key_prefix}_nombre_en")
            tipo = st.selectbox("Tipo:", ALL_TIPOS, index=ALL_TIPOS.index(product.get('tipo', 'aceite_individual')) if product.get('tipo') in ALL_TIPOS else 0, key=f"{key_prefix}_tipo")
            if is_new:
                pid = st.text_input("ID (único, sin espacios):", value='', placeholder="ej: lavender, deep_blue", key=f"{key_prefix}_id")
            else:
                pid = product.get('id', '')
                st.text_input("ID:", value=pid, disabled=True, key=f"{key_prefix}_id")

        with col2:
            sku = st.text_input("SKU (doTERRA):", value=product.get('doterra_sku', ''), key=f"{key_prefix}_sku")
            imagen_url = st.text_input("URL Imagen:", value=product.get('imagen_url', ''), placeholder="https://www.doterra.com/medias/...", key=f"{key_prefix}_img")
            infografia_url = st.text_input("URL Infografía PDF:", value=product.get('infografia_url', ''), placeholder="https://media.doterra.com/.../infographic-....pdf", key=f"{key_prefix}_infog")

        # Image preview
        if imagen_url and 'doterra.com' in imagen_url:
            st.markdown(
                f'<div style="display:flex;align-items:center;gap:12px;padding:8px;background:#faf8f5;border-radius:8px;margin-top:8px;">'
                f'<div style="width:60px;height:60px;background:url({imagen_url}) center/contain no-repeat;background-color:#f9f6f0;border-radius:8px;flex-shrink:0;"></div>'
                f'<span style="color:#888;font-size:13px;">Vista previa de imagen</span>'
                f'</div>',
                unsafe_allow_html=True
            )

        # doTERRA link + auto-scrape
        st.markdown("---")
        col_url, col_scrape = st.columns([3, 1])
        with col_url:
            doterra_url = st.text_input("Link doTERRA Ecuador (auto-actualiza datos):", value=product.get('doterra_url', ''), placeholder="https://www.doterra.com/EC/es_EC/p/...", key=f"{key_prefix}_dturl")
        with col_scrape:
            st.markdown("<br>", unsafe_allow_html=True)
            scrape_clicked = st.button("🔄 Auto-llenar", key=f"{key_prefix}_scrape")

    with tab_content:
        st.markdown("**Descripción del producto**")
        col_desc_es, col_desc_en = st.columns(2)
        with col_desc_es:
            descripcion = st.text_area("Descripción (Español):", value=product.get('descripcion', ''), height=100, key=f"{key_prefix}_desc")
        with col_desc_en:
            descripcion_en = st.text_area("Description (English):", value=product.get('descripcion_en', ''), height=100, key=f"{key_prefix}_desc_en",
                                          help="Se llena automáticamente al usar Auto-llenar desde link doTERRA")

        # Categories as multiselect
        current_cats = product.get('categoria', [])
        categorias = st.multiselect("Categorías:", ALL_CATEGORIES, default=[c for c in current_cats if c in ALL_CATEGORIES], key=f"{key_prefix}_cats")

        # Benefits as editable text (one per line)
        beneficios_text = st.text_area("Beneficios (uno por línea):", value='\n'.join(product.get('beneficios', [])), height=100, key=f"{key_prefix}_bene")
        beneficios = [b.strip() for b in beneficios_text.split('\n') if b.strip()]

        # Usage methods
        uso_aromatico = st.text_input("Uso Aromático:", value=product.get('uso_aromatico', ''), key=f"{key_prefix}_usoA")
        uso_topico = st.text_input("Uso Tópico:", value=product.get('uso_topico', ''), key=f"{key_prefix}_usoT")
        uso_interno = st.text_input("Uso Interno:", value=product.get('uso_interno', ''), key=f"{key_prefix}_usoI")

        # Symptoms as editable text (one per line)
        sintomas_text = st.text_area("Síntomas relacionados (uno por línea):", value='\n'.join(product.get('sintomas_relacionados', [])), height=80, key=f"{key_prefix}_sint")
        sintomas = [s.strip() for s in sintomas_text.split('\n') if s.strip()]

    with tab_store:
        st.markdown('<div style="background:#f0f7ed;padding:12px 16px;border-radius:8px;margin-bottom:16px;">'
                    '<span style="color:#7C9070;font-weight:600;">Configuración de Tienda y Stripe</span>'
                    '<div style="color:#888;font-size:13px;margin-top:4px;">Estos campos conectan el producto con Stripe para pagos online.</div>'
                    '</div>', unsafe_allow_html=True)

        col_p1, col_p2 = st.columns(2)
        with col_p1:
            precio_usd = st.number_input("Precio Menudeo (USD):", value=float(product.get('precio_usd', 0)), min_value=0.0, step=0.5, key=f"{key_prefix}_precio")
            precio_mayoreo = st.number_input("Precio Mayoreo (USD):", value=float(product.get('precio_mayoreo', 0)), min_value=0.0, step=0.5, key=f"{key_prefix}_mayoreo")
            pv = st.number_input("PV:", value=float(product.get('pv', 0)), min_value=0.0, step=0.5, key=f"{key_prefix}_pv")
        with col_p2:
            active = st.toggle("Producto activo (visible en tienda)", value=product.get('active', True), key=f"{key_prefix}_active")
            stock = st.number_input("Stock disponible:", value=int(product.get('stock', 99)), min_value=0, step=1, key=f"{key_prefix}_stock")
            max_per_order = st.number_input("Máximo por pedido:", value=int(product.get('max_per_order', 10)), min_value=1, max_value=50, step=1, key=f"{key_prefix}_maxorder")

        st.markdown("**Stripe IDs** (se llenan automáticamente al sincronizar con Stripe)")
        col_s1, col_s2 = st.columns(2)
        with col_s1:
            stripe_product_id = st.text_input("Stripe Product ID:", value=product.get('stripe_product_id', ''), placeholder="prod_...", key=f"{key_prefix}_stripe_prod")
        with col_s2:
            stripe_price_id = st.text_input("Stripe Price ID:", value=product.get('stripe_price_id', ''), placeholder="price_...", key=f"{key_prefix}_stripe_price")

        # Shipping info
        st.markdown("**Envío**")
        col_w, col_sh = st.columns(2)
        with col_w:
            weight_g = st.number_input("Peso (gramos):", value=int(product.get('weight_g', 0)), min_value=0, step=10, key=f"{key_prefix}_weight")
        with col_sh:
            requires_shipping = st.toggle("Requiere envío", value=product.get('requires_shipping', True), key=f"{key_prefix}_shipping")

    # Handle auto-scrape (from tab_basic)
    if scrape_clicked and doterra_url and 'doterra.com' in doterra_url:
        with st.spinner("Obteniendo datos de doTERRA..."):
            result = scrape_doterra_product(doterra_url)
            if result['success']:
                scraped = result['data']
                st.success(f"✅ Datos obtenidos: {', '.join(scraped.keys())}")
                st.info("Haz clic en **Guardar** para aplicar los cambios.")
                st.session_state[f'{key_prefix}_scraped'] = scraped
                st.rerun()
            else:
                st.error(f"❌ {result['error']}")

    # Apply scraped data if available (from previous scrape click)
    scraped = st.session_state.pop(f'{key_prefix}_scraped', None)

    # Build the updated product dict (Stripe-ready, bilingual)
    updated = {
        'id': pid if is_new else product['id'],
        'nombre': scraped.get('nombre', nombre) if scraped and scraped.get('nombre') and not nombre else nombre,
        'nombre_en': scraped.get('nombre_en', nombre_en) if scraped and scraped.get('nombre_en') and not nombre_en else nombre_en,
        'tipo': tipo,
        'categoria': categorias,
        'imagen_url': scraped.get('imagen_url', imagen_url) if scraped else imagen_url,
        'precio_usd': scraped.get('precio_usd', precio_usd) if scraped else precio_usd,
        'pv': scraped.get('pv', pv) if scraped else pv,
        'descripcion': scraped.get('descripcion', descripcion) if scraped and scraped.get('descripcion') and not descripcion else descripcion,
        'descripcion_en': scraped.get('descripcion_en', descripcion_en) if scraped and scraped.get('descripcion_en') else descripcion_en,
        'beneficios': beneficios,
        'uso_aromatico': uso_aromatico,
        'uso_topico': uso_topico,
        'uso_interno': uso_interno,
        'sintomas_relacionados': sintomas,
        'doterra_sku': scraped.get('doterra_sku', sku) if scraped else sku,
        'precio_mayoreo': scraped.get('precio_mayoreo', precio_mayoreo) if scraped else precio_mayoreo,
        # Stripe-ready fields
        'active': active,
        'stock': stock,
        'max_per_order': max_per_order,
        'stripe_product_id': stripe_product_id,
        'stripe_price_id': stripe_price_id,
        'weight_g': weight_g,
        'requires_shipping': requires_shipping,
        'currency': 'usd',
    }
    if doterra_url:
        updated['doterra_url'] = doterra_url.split('?')[0]
    if scraped and scraped.get('infografia_url'):
        updated['infografia_url'] = scraped['infografia_url']
    elif infografia_url:
        updated['infografia_url'] = infografia_url
    # Preserve existing Stripe IDs if not explicitly changed
    if not stripe_product_id and product.get('stripe_product_id'):
        updated['stripe_product_id'] = product['stripe_product_id']
    if not stripe_price_id and product.get('stripe_price_id'):
        updated['stripe_price_id'] = product['stripe_price_id']

    return updated


def page_dashboard():
    """Password-protected dashboard with full product CRUD."""
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

    # ---- Header ----
    st.markdown("<h1>Dashboard de Suzanna</h1>", unsafe_allow_html=True)
    if st.button("🚪 Cerrar Sesión", key="logout"):
        st.session_state.dashboard_authenticated = False
        st.rerun()

    # ---- Quick stats bar ----
    active_count = sum(1 for p in products_data if p.get('active', True))
    stripe_count = sum(1 for p in products_data if p.get('stripe_price_id'))
    low_stock = sum(1 for p in products_data if p.get('stock', 99) < 10)

    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("Productos", len(products_data))
    with col2:
        st.metric("Activos", f"{active_count}/{len(products_data)}")
    with col3:
        st.metric("Stripe", stripe_count)
    with col4:
        st.metric("Stock Bajo", low_stock, delta=None if low_stock == 0 else f"-{low_stock}", delta_color="inverse")

    # ---- Initialize session state ----
    if 'dash_editing' not in st.session_state:
        st.session_state.dash_editing = None
    if 'dash_adding' not in st.session_state:
        st.session_state.dash_adding = False
    if 'dash_msg' not in st.session_state:
        st.session_state.dash_msg = None
    if 'verify_results' not in st.session_state:
        st.session_state.verify_results = {}  # {product_id: {country_code: {status, ok, url}}}
    if 'verify_timestamp' not in st.session_state:
        st.session_state.verify_timestamp = {}  # {product_id: datetime_str}
    if 'verify_running' not in st.session_state:
        st.session_state.verify_running = False
    if 'verify_bulk_running' not in st.session_state:
        st.session_state.verify_bulk_running = False
    # ---- Recruitment tab state ----
    if 'recruit_pipeline' not in st.session_state:
        st.session_state.recruit_pipeline = _load_recruitment_data().get('pipeline', [])
    if 'recruit_adding' not in st.session_state:
        st.session_state.recruit_adding = False
    if 'recruit_view' not in st.session_state:
        st.session_state.recruit_view = 'pipeline'

    # Show success/error message if any
    if st.session_state.dash_msg:
        msg_type, msg_text = st.session_state.dash_msg
        if msg_type == 'success':
            st.success(msg_text)
        else:
            st.error(msg_text)
        st.session_state.dash_msg = None

    # ============================================
    # HORIZONTAL TAB BAR
    # ============================================
    tab_productos, tab_recruit, tab_stripe, tab_config = st.tabs(["📦 Productos", "🚀 Reclutamiento", "💳 Stripe", "⚙️ Configuración"])

    # ============================================
    # TAB 1: PRODUCTOS
    # ============================================
    with tab_productos:
        # ---- Top action bar ----
        col_add, col_view = st.columns([1, 5])
        with col_add:
            if st.button("➕ Agregar Producto", key="add_new", type="primary"):
                st.session_state.dash_adding = True
                st.session_state.dash_editing = None

        # ---- Filter bar ----
        with st.expander("🔍 Filtros y Búsqueda", expanded=True):
            # Row 1: Search (full width)
            search_term = st.text_input("Buscar", placeholder="Escribe nombre, SKU, beneficio o palabra clave...", key="dash_search")

            # Row 2: Type + Status + Country
            fc1, fc2, fc3 = st.columns(3)
            with fc1:
                tipo_labels = {"Todos": "— Todos los tipos —", "aceite_individual": "🫧 Aceites Individuales", "mezcla": "🌸 Mezclas", "suplemento": "💊 Suplementos", "kit": "📦 Kits", "cuidado_personal": "🧴 Cuidado Personal", "cuidado_piel": "✨ Cuidado de Piel", "cuidado_cabello": "💇 Cabello", "difusor": "🌫️ Difusores", "accesorio": "🔧 Accesorios"}
                filter_tipo = st.selectbox("Tipo de Producto", list(tipo_labels.keys()), format_func=lambda x: tipo_labels[x], key="dash_filter_tipo")
            with fc2:
                status_options = {"Todos": "— Todos —", "Activos": "✅ Activos", "Inactivos": "⏸️ Inactivos", "Con Precio": "💰 Con Precio", "Sin Precio": "🚫 Sin Precio", "Con Imagen": "🖼️ Con Imagen", "Sin Imagen": "📷 Sin Imagen", "Stripe Conectado": "💳 Stripe ✓", "Stripe Pendiente": "💳 Stripe Pendiente"}
                filter_status = st.selectbox("Estado", list(status_options.keys()), format_func=lambda x: status_options[x], key="dash_filter_status")
            with fc3:
                country_options = {"Todos": "🌎 Todos los países"}
                for code, info in DOTERRA_COUNTRIES.items():
                    if code in COUNTRY_PRODUCTS and len(COUNTRY_PRODUCTS[code]) > 1:
                        count_c = len(COUNTRY_PRODUCTS[code])
                        country_options[code] = f"{info['flag']} {info['name']} ({count_c})"
                filter_country = st.selectbox("País doTERRA", list(country_options.keys()), format_func=lambda x: country_options[x], key="dash_filter_country")

            # Row 3: Categories + Sort
            fc4, fc5 = st.columns([3, 1])
            with fc4:
                all_cats = sorted(set(c for p in products_data for c in p.get('categoria', [])))
                cat_labels = {c: c.replace('_', ' ').title() for c in all_cats}
                filter_cats = st.multiselect("Categorías", all_cats, format_func=lambda x: cat_labels.get(x, x), key="dash_filter_cats")
            with fc5:
                sort_options = {"nombre": "Nombre A-Z", "nombre_desc": "Nombre Z-A", "precio_asc": "Precio ↑", "precio_desc": "Precio ↓", "tipo": "Por Tipo"}
                filter_sort = st.selectbox("Ordenar por", list(sort_options.keys()), format_func=lambda x: sort_options[x], key="dash_filter_sort")

        # ---- Apply filters ----
        filtered = list(products_data)
        if search_term:
            term = search_term.lower()
            filtered = [p for p in filtered if term in p['nombre'].lower() or term in p.get('nombre_en', '').lower() or term in p.get('doterra_sku', '') or term in p.get('descripcion', '').lower() or any(term in b.lower() for b in p.get('beneficios', []))]
        if filter_tipo != "Todos":
            filtered = [p for p in filtered if p.get('tipo') == filter_tipo]
        if filter_cats:
            filtered = [p for p in filtered if any(c in p.get('categoria', []) for c in filter_cats)]
        if filter_country != "Todos":
            filtered = [p for p in filtered if _product_available_in(p, filter_country)]
        if filter_status == "Activos":
            filtered = [p for p in filtered if p.get('active', True)]
        elif filter_status == "Inactivos":
            filtered = [p for p in filtered if not p.get('active', True)]
        elif filter_status == "Con Precio":
            filtered = [p for p in filtered if p.get('precio_usd', 0) > 0]
        elif filter_status == "Sin Precio":
            filtered = [p for p in filtered if not p.get('precio_usd', 0)]
        elif filter_status == "Con Imagen":
            filtered = [p for p in filtered if p.get('imagen_url')]
        elif filter_status == "Sin Imagen":
            filtered = [p for p in filtered if not p.get('imagen_url')]
        elif filter_status == "Stripe Conectado":
            filtered = [p for p in filtered if p.get('stripe_price_id')]
        elif filter_status == "Stripe Pendiente":
            filtered = [p for p in filtered if not p.get('stripe_price_id')]

        # Sort
        if filter_sort == "nombre":
            filtered.sort(key=lambda p: p['nombre'].lower())
        elif filter_sort == "nombre_desc":
            filtered.sort(key=lambda p: p['nombre'].lower(), reverse=True)
        elif filter_sort == "precio_asc":
            filtered.sort(key=lambda p: p.get('precio_usd', 0))
        elif filter_sort == "precio_desc":
            filtered.sort(key=lambda p: p.get('precio_usd', 0), reverse=True)
        elif filter_sort == "tipo":
            filtered.sort(key=lambda p: p.get('tipo', ''))

        # ---- Results summary with type badges ----
        type_counts = {}
        for p in filtered:
            t = p.get('tipo', 'otro')
            type_counts[t] = type_counts.get(t, 0) + 1
        badge_colors = {'aceite_individual': '#7C9070', 'mezcla': '#C67B4F', 'suplemento': '#3B82F6', 'kit': '#8B5CF6'}
        badge_labels = {'aceite_individual': 'Aceites', 'mezcla': 'Mezclas', 'suplemento': 'Suplementos', 'kit': 'Kits'}
        badges_html = ''.join(
            f'<span style="display:inline-block;padding:2px 10px;border-radius:12px;font-size:12px;font-weight:600;color:white;background:{badge_colors.get(t,"#888")};margin-right:6px;">{badge_labels.get(t,t)} ({c})</span>'
            for t, c in sorted(type_counts.items())
        )
        st.markdown(
            f'<div style="display:flex;align-items:center;gap:12px;padding:8px 0;">'
            f'<span style="font-weight:600;color:#3D3229;">{len(filtered)} de {len(products_data)} productos</span>'
            f'<span>{badges_html}</span></div>',
            unsafe_allow_html=True
        )

        # ---- Verification panel ----
        with st.expander("🔍 Verificador de Disponibilidad por País", expanded=False):
            st.markdown(
                '<div style="font-size:13px;color:#666;line-height:1.6;margin-bottom:12px;">'
                'Verifica en tiempo real la disponibilidad, precios y estado de los productos. '
                'Compara tu catálogo con los datos de doTERRA.com para detectar discrepancias.'
                '</div>',
                unsafe_allow_html=True
            )

            # --- Catalog Summary ---
            st.markdown("##### 📊 Resumen del Catálogo")
            summary_cols = st.columns(5)
            type_labels = {
                'aceite_individual': ('🫒', 'Aceites'),
                'mezcla': ('🧪', 'Mezclas'),
                'suplemento': ('💊', 'Suplementos'),
                'kit': ('📦', 'Kits'),
                'cuidado_personal': ('🧴', 'Cuidado Personal'),
                'cuidado_piel': ('✨', 'Piel'),
                'cuidado_cabello': ('💇', 'Cabello'),
                'difusor': ('🌫️', 'Difusores'),
                'accesorio': ('🔧', 'Accesorios'),
            }
            type_counts_cat = {}
            for p in products_data:
                t = p.get('tipo', 'otro')
                type_counts_cat[t] = type_counts_cat.get(t, 0) + 1

            for idx, (tipo, count) in enumerate(sorted(type_counts_cat.items(), key=lambda x: -x[1])):
                icon, label = type_labels.get(tipo, ('📦', tipo.replace('_', ' ').title()))
                col_idx = idx % 5
                with summary_cols[col_idx]:
                    st.metric(f"{icon} {label}", count)

            # --- Country Coverage ---
            st.markdown("##### 🌎 Cobertura por País")
            coverage_cols = st.columns(len([c for c in DOTERRA_COUNTRIES if c not in ('BO', 'US')]))
            for idx, (code, info) in enumerate([(c, DOTERRA_COUNTRIES[c]) for c in DOTERRA_COUNTRIES if c not in ('BO', 'US')]):
                avail_count = sum(1 for p in products_data if _product_available_in(p, code))
                total_in_country = len(COUNTRY_PRODUCTS.get(code, set()))
                with coverage_cols[idx]:
                    st.markdown(
                        f'<div style="text-align:center;padding:8px;background:#f8f9fa;border-radius:8px;">'
                        f'<div style="font-size:20px;">{info["flag"]}</div>'
                        f'<div style="font-weight:600;font-size:14px;">{info["name"]}</div>'
                        f'<div style="color:#16a34a;font-weight:600;">{avail_count}/{len(products_data)}</div>'
                        f'<div style="color:#888;font-size:11px;">de {total_in_country} en doTERRA</div>'
                        f'</div>',
                        unsafe_allow_html=True
                    )

            # --- Missing Products Detector ---
            st.markdown("##### 🔎 Productos No Incluidos en el Catálogo")
            st.markdown(
                '<div style="font-size:12px;color:#888;margin-bottom:8px;">'
                'Productos disponibles en doTERRA que no están en tu catálogo actual (filtrado por Ecuador).'
                '</div>',
                unsafe_allow_html=True
            )

            # Get all slugs from our catalog
            catalog_slugs = set()
            for p in products_data:
                slug = _get_product_slug(p)
                catalog_slugs.add(slug)
                # Also add known aliases
                aliases = SLUG_ALIASES.get(slug, set())
                catalog_slugs.update(aliases)
                for primary, alt_set in SLUG_ALIASES.items():
                    if slug in alt_set:
                        catalog_slugs.add(primary)

            ec_products = COUNTRY_PRODUCTS.get('EC', set())
            missing_from_catalog = sorted(ec_products - catalog_slugs)

            # Filter out obvious variants (5ml, touch, flavor versions of products we have)
            significant_missing = []
            for slug in missing_from_catalog:
                # Skip variants of products already in catalog
                is_variant = False
                base = slug.replace('-oil-5ml', '-oil').replace('-touch-oil', '-oil').replace('-oil-flavor', '-oil')
                if base in catalog_slugs:
                    is_variant = True
                if slug.endswith('-5ml') or slug.endswith('-flavor') or '-enrollment-' in slug:
                    is_variant = True
                if slug.startswith('curso-') or slug.startswith('doterra-essential-oil-specialist'):
                    is_variant = True
                if not is_variant:
                    significant_missing.append(slug)

            if significant_missing:
                st.markdown(
                    f'<div style="padding:8px 14px;background:#fffbeb;border-radius:8px;border-left:3px solid #f59e0b;margin-bottom:8px;">'
                    f'<span style="font-weight:600;color:#d97706;">⚠️ {len(significant_missing)} productos en Ecuador no incluidos en catálogo</span>'
                    f'</div>',
                    unsafe_allow_html=True
                )
                with st.container(height=200):
                    for slug in significant_missing:
                        st.markdown(
                            f'<div style="padding:3px 8px;font-size:12px;font-family:monospace;background:#f8f9fa;'
                            f'border-radius:4px;margin-bottom:2px;">'
                            f'<a href="https://www.doterra.com/EC/es_EC/p/{slug}" target="_blank">{slug}</a>'
                            f'</div>',
                            unsafe_allow_html=True
                        )
            else:
                st.markdown(
                    '<div style="padding:8px 14px;background:#f0fdf4;border-radius:8px;border-left:3px solid #22c55e;">'
                    '<span style="color:#16a34a;">✅ Tu catálogo cubre todos los productos significativos de Ecuador</span>'
                    '</div>',
                    unsafe_allow_html=True
                )

            # --- Live Verification ---
            st.markdown("##### 🔄 Verificación en Vivo")
            vcol1, vcol2 = st.columns([1, 3])
            with vcol1:
                if st.button("🔄 Verificar Todos", key="verify_all_btn", type="primary"):
                    st.session_state.verify_bulk_running = True
                    with st.spinner("Verificando disponibilidad de todos los productos..."):
                        results = verify_all_products(filtered)
                        now_str = datetime.now().strftime("%Y-%m-%d %H:%M")
                        for pid, res in results.items():
                            st.session_state.verify_results[pid] = res
                            st.session_state.verify_timestamp[pid] = now_str
                    st.session_state.verify_bulk_running = False
                    st.rerun()
            with vcol2:
                verified_count = len(st.session_state.verify_results)
                if verified_count > 0:
                    last_ts = max(st.session_state.verify_timestamp.values()) if st.session_state.verify_timestamp else "—"
                    st.markdown(
                        f'<div style="padding:8px 14px;background:#f0fdf4;border-radius:8px;border-left:3px solid #22c55e;">'
                        f'<span style="font-weight:600;color:#16a34a;">{verified_count} productos verificados</span>'
                        f'<span style="color:#888;margin-left:10px;font-size:12px;">Última verificación: {last_ts}</span>'
                        f'</div>',
                        unsafe_allow_html=True
                    )
                else:
                    st.markdown(
                        '<div style="padding:8px 14px;background:#f8f9fa;border-radius:8px;border-left:3px solid #ccc;">'
                        '<span style="color:#888;font-size:13px;">Aún no se ha verificado. Pulsa "Verificar Todos" para comprobar URLs en vivo.</span>'
                        '</div>',
                        unsafe_allow_html=True
                    )

            # Show summary of discrepancies if results exist
            if st.session_state.verify_results:
                discrepancies = []
                for p in filtered:
                    pid = p['id']
                    vr = st.session_state.verify_results.get(pid, {})
                    if not vr:
                        continue
                    for code in [c for c in DOTERRA_COUNTRIES if c not in ('BO', 'US')]:
                        scraped_avail = _product_available_in(p, code)
                        live_ok = vr.get(code, {}).get('ok', False)
                        if scraped_avail and not live_ok:
                            discrepancies.append((p['nombre'], DOTERRA_COUNTRIES[code]['flag'], DOTERRA_COUNTRIES[code]['name'], '📋 En datos pero ❌ URL inactiva'))
                        elif not scraped_avail and live_ok:
                            discrepancies.append((p['nombre'], DOTERRA_COUNTRIES[code]['flag'], DOTERRA_COUNTRIES[code]['name'], '❌ No en datos pero ✅ URL activa'))

                if discrepancies:
                    st.markdown(f'<div style="margin-top:12px;font-weight:600;color:#dc2626;">⚠️ {len(discrepancies)} discrepancia(s) encontrada(s):</div>', unsafe_allow_html=True)
                    for name, flag, country, desc in discrepancies[:30]:
                        st.markdown(
                            f'<div style="padding:4px 12px;background:#fef2f2;border-radius:6px;margin-bottom:4px;font-size:13px;border-left:3px solid #ef4444;">'
                            f'{flag} <strong>{name}</strong> — {country}: {desc}'
                            f'</div>',
                            unsafe_allow_html=True
                        )
                else:
                    st.markdown(
                        '<div style="margin-top:12px;padding:8px 14px;background:#f0fdf4;border-radius:8px;border-left:3px solid #22c55e;">'
                        '<span style="color:#16a34a;">✅ Sin discrepancias — datos y URLs coinciden</span>'
                        '</div>',
                        unsafe_allow_html=True
                    )

        # ---- Add New Product Form ----
        if st.session_state.dash_adding:
            st.markdown("---")
            st.markdown('<div style="background:#f0f7ed;padding:4px 16px;border-radius:10px;border-left:4px solid #7C9070;margin-bottom:12px;"><span style="font-weight:700;color:#7C9070;font-size:1.1rem;">➕ Nuevo Producto</span></div>', unsafe_allow_html=True)

            new_product = _product_edit_form({}, "new", is_new=True)

            col_save, col_cancel = st.columns([1, 1])
            with col_save:
                if st.button("✅ Crear Producto", key="save_new", type="primary"):
                    if not new_product['id'] or not new_product['nombre']:
                        st.error("ID y Nombre son obligatorios.")
                    elif any(p['id'] == new_product['id'] for p in products_data):
                        st.error(f"Ya existe un producto con ID '{new_product['id']}'.")
                    else:
                        products_data.append(new_product)
                        save_products(products_data)
                        # products reloaded on next run (no cache)
                        st.session_state.dash_adding = False
                        st.session_state.dash_msg = ('success', f"✅ Producto '{new_product['nombre']}' creado exitosamente.")
                        st.rerun()
            with col_cancel:
                if st.button("❌ Cancelar", key="cancel_new"):
                    st.session_state.dash_adding = False
                    st.rerun()
            st.markdown("---")

        # ---- Product cards (grid: 2 columns) ----
        if not filtered:
            st.info("No se encontraron productos con los filtros seleccionados.")
        else:
            cols = st.columns(2)
            for idx, p in enumerate(filtered):
                pid = p['id']
                is_editing = st.session_state.dash_editing == pid

                with cols[idx % 2]:
                    if not is_editing:
                        # ---- Product card wrapped in container with inline actions ----
                        card_container = st.container()
                        with card_container:
                            _render_dashboard_product_card(p)

                            # Country availability flags
                            product_slug = _get_product_slug(p)
                            vr = st.session_state.verify_results.get(pid, {})
                            vts = st.session_state.verify_timestamp.get(pid, '')
                            flag_links = []
                            avail_count = 0
                            for code, info in DOTERRA_COUNTRIES.items():
                                if code == 'BO':
                                    continue
                                is_avail = _product_available_in(p, code)
                                url = get_product_country_url(product_slug, code)
                                opacity = '1.0' if is_avail else '0.25'
                                pointer = 'pointer' if is_avail else 'default'

                                v_badge = ''
                                if vr and code in vr:
                                    live_ok = vr[code].get('ok', False)
                                    if is_avail and live_ok:
                                        v_badge = '<span style="font-size:8px;position:relative;top:-6px;">✅</span>'
                                    elif is_avail and not live_ok:
                                        v_badge = '<span style="font-size:8px;position:relative;top:-6px;">❌</span>'
                                    elif not is_avail and live_ok:
                                        v_badge = '<span style="font-size:8px;position:relative;top:-6px;">🟡</span>'

                                title = f"{info['name']} ✓" if is_avail else f"{info['name']} — no disponible"
                                if vr and code in vr:
                                    live_ok = vr[code].get('ok', False)
                                    status_code = vr[code].get('status', 0)
                                    title += f" | Verificado: {'✓ OK' if live_ok else f'✗ {status_code}'}"

                                if is_avail:
                                    flag_links.append(f'<a href="{url}" target="_blank" title="{title}" style="text-decoration:none;font-size:18px;opacity:{opacity};cursor:{pointer};">{info["flag"]}{v_badge}</a>')
                                    avail_count += 1
                                else:
                                    flag_links.append(f'<span title="{title}" style="font-size:18px;opacity:{opacity};cursor:{pointer};">{info["flag"]}{v_badge}</span>')

                            verify_label = f'<span style="font-size:10px;color:#16a34a;margin-left:6px;">verificado {vts}</span>' if vts else ''
                            st.markdown(
                                '<div style="display:flex;align-items:center;gap:3px;padding:6px 10px;background:#f8f6f2;border-radius:8px;'
                                'border:1px solid #eae6df;">'
                                f'<span style="font-size:11px;color:#888;margin-right:4px;">{avail_count} países:</span>'
                                + ''.join(flag_links) + verify_label +
                                '</div>',
                                unsafe_allow_html=True
                            )

                            # ---- Inline action toolbar divider ----
                            st.markdown(
                                '<div class="dash-action-divider" style="border-top:1px solid #eae6df;margin:8px -16px 4px -16px;padding-top:6px;"></div>',
                                unsafe_allow_html=True
                            )
                            bc1, bc2, bc3 = st.columns([1, 1, 1])
                            with bc1:
                                if st.button("✏️ Editar", key=f"edit_{pid}", use_container_width=True):
                                    st.session_state.dash_editing = pid
                                    st.session_state.dash_adding = False
                                    st.rerun()
                            with bc2:
                                if st.button("🗑️ Eliminar", key=f"del_{pid}", use_container_width=True):
                                    st.session_state[f'confirm_del_{pid}'] = True
                                    st.rerun()
                            with bc3:
                                if st.button("🔍 Verificar", key=f"verify_{pid}", use_container_width=True):
                                    with st.spinner("Verificando..."):
                                        result = verify_product_urls(p)
                                        st.session_state.verify_results[pid] = result
                                        st.session_state.verify_timestamp[pid] = datetime.now().strftime("%Y-%m-%d %H:%M")
                                    st.rerun()

                        # Confirm delete (outside card container)
                        if st.session_state.get(f'confirm_del_{pid}'):
                            st.warning(f"¿Eliminar **{p['nombre']}**?")
                            cy, cn = st.columns(2)
                            with cy:
                                if st.button("Sí", key=f"confirm_yes_{pid}", type="primary"):
                                    products_data[:] = [pr for pr in products_data if pr['id'] != pid]
                                    save_products(products_data)
                                    st.session_state.pop(f'confirm_del_{pid}', None)
                                    st.session_state.dash_msg = ('success', f"✅ '{p['nombre']}' eliminado.")
                                    st.rerun()
                            with cn:
                                if st.button("No", key=f"confirm_no_{pid}"):
                                    st.session_state.pop(f'confirm_del_{pid}', None)
                                    st.rerun()

                    # ---- Edit mode ----
                    else:
                        st.markdown('<div style="background:#fff8ee;padding:4px 16px;border-radius:10px;border-left:4px solid #C67B4F;margin-bottom:12px;">'
                                    f'<span style="font-weight:700;color:#C67B4F;font-size:1.1rem;">✏️ Editando: {p["nombre"]}</span></div>', unsafe_allow_html=True)

                        updated = _product_edit_form(p, f"edit_{pid}")

                        col_save, col_cancel = st.columns([1, 1])
                        with col_save:
                            if st.button("💾 Guardar", key=f"save_edit_{pid}", type="primary"):
                                for i, prod in enumerate(products_data):
                                    if prod['id'] == pid:
                                        products_data[i] = updated
                                        break
                                save_products(products_data)
                                # products reloaded on next run (no cache)
                                st.session_state.dash_editing = None
                                st.session_state.dash_msg = ('success', f"✅ '{updated['nombre']}' actualizado.")
                                st.rerun()
                        with col_cancel:
                            if st.button("❌ Cancelar", key=f"cancel_edit_{pid}"):
                                st.session_state.dash_editing = None
                                st.rerun()

                    st.markdown('<div style="margin-bottom:8px;"></div>', unsafe_allow_html=True)

    # ============================================
    # TAB 2: RECLUTAMIENTO — Team Building Strategy
    # ============================================
    with tab_recruit:
        # ---- Load data ----
        recruit_data = _load_recruitment_data()
        pipeline = recruit_data.get('pipeline', [])
        r_settings = recruit_data.get('settings', {})

        # ---- Header ----
        st.markdown(
            '<div style="background:linear-gradient(135deg,#1a1a2e 0%,#16213e 50%,#0f3460 100%);padding:28px 24px;border-radius:16px;margin-bottom:20px;">'
            '<div style="display:flex;align-items:center;gap:14px;margin-bottom:10px;">'
            '<span style="font-size:2rem;">🚀</span>'
            '<div>'
            '<div style="font-size:1.3rem;font-weight:700;color:#e2e8f0;">Constructor de Equipo doTERRA</div>'
            '<div style="font-size:13px;color:#94a3b8;margin-top:2px;">Recluta, entrena y escala tus piernas con personas que <b style="color:#fbbf24;">necesitan</b> el ingreso</div>'
            '</div>'
            '</div>'
            '</div>',
            unsafe_allow_html=True
        )

        # ---- Sub-tabs ----
        r_tab1, r_tab2, r_tab3, r_tab4, r_tab5 = st.tabs([
            "🎯 Estrategia", "📋 Pipeline", "📱 Contenido Social", "📊 Métricas", "📖 Guía Paso a Paso"
        ])

        # ==============================================
        # RECRUITMENT SUB-TAB 1: STRATEGY
        # ==============================================
        with r_tab1:
            st.markdown(
                '<div style="background:#fffbeb;padding:18px 20px;border-radius:12px;border-left:4px solid #f59e0b;margin-bottom:16px;">'
                '<div style="font-weight:700;color:#92400e;font-size:15px;margin-bottom:6px;">💡 El Problema Actual de Suzanna</div>'
                '<div style="color:#78350f;font-size:14px;line-height:1.7;">'
                'Tus piernas actuales son mujeres que <b>no necesitan el dinero</b> — tienen esposos que pagan todo o ya tienen recursos. '
                'Trabajan por entretenimiento, pero cuando tienen un mal día, se deprimen y paran. '
                '<b>No hay urgencia real.</b> Necesitas personas como Verónica: mamás que venden seguros porque necesitan '
                'flexibilidad Y el ingreso. Personas que no pueden ir a una oficina de 8 a 5 pero que <b>sí necesitan producir</b>.</div>'
                '</div>',
                unsafe_allow_html=True
            )

            # ---- Ideal Candidate Profile ----
            st.markdown(
                '<div style="background:white;padding:20px 24px;border-radius:14px;border:1px solid #e2e8f0;box-shadow:0 2px 8px rgba(0,0,0,0.04);margin-bottom:16px;">'
                '<div style="font-weight:700;color:#1e293b;font-size:16px;margin-bottom:14px;">🎯 Perfil de Candidata Ideal — Quito</div>'
                '<div style="display:grid;grid-template-columns:1fr 1fr;gap:12px;">'
                # Profile 1
                '<div style="background:#f0fdf4;padding:14px;border-radius:10px;border:1px solid #bbf7d0;">'
                '<div style="font-weight:600;color:#166534;font-size:13px;margin-bottom:6px;">🏆 PERFIL A: Mamá Emprendedora</div>'
                '<div style="color:#15803d;font-size:12.5px;line-height:1.6;">'
                '• Mamá soltera o con hijos pequeños<br>'
                '• No puede trabajar horario fijo 8-5<br>'
                '• Necesita $300-$800/mes extra REAL<br>'
                '• Tiene celular + internet + redes sociales<br>'
                '• Edad: 25-45 años<br>'
                '• Vive en Quito (Norte, Valles, Cumbayá)'
                '</div></div>'
                # Profile 2
                '<div style="background:#eff6ff;padding:14px;border-radius:10px;border:1px solid #bfdbfe;">'
                '<div style="font-weight:600;color:#1e40af;font-size:13px;margin-bottom:6px;">🥈 PERFIL B: Freelancer / Vendedora</div>'
                '<div style="color:#1d4ed8;font-size:12.5px;line-height:1.6;">'
                '• Ya vende algo (seguros, Avon, Tupperware, ropa)<br>'
                '• Entiende comisiones y venta directa<br>'
                '• Tiene red de contactos existente<br>'
                '• Busca diversificar ingresos<br>'
                '• Disciplinada con metas de venta<br>'
                '• Activa en WhatsApp y Facebook'
                '</div></div>'
                # Profile 3
                '<div style="background:#fdf4ff;padding:14px;border-radius:10px;border:1px solid #f0abfc;">'
                '<div style="font-weight:600;color:#86198f;font-size:13px;margin-bottom:6px;">🥉 PERFIL C: Profesional en Bienestar</div>'
                '<div style="color:#a21caf;font-size:12.5px;line-height:1.6;">'
                '• Instructora de yoga, nutricionista, terapeuta<br>'
                '• Ya tiene audiencia interesada en salud<br>'
                '• Credibilidad natural para aceites<br>'
                '• Puede integrar doTERRA a su práctica<br>'
                '• Red profesional en bienestar<br>'
                '• Instagram activo con contenido de salud'
                '</div></div>'
                # Anti-profile
                '<div style="background:#fef2f2;padding:14px;border-radius:10px;border:1px solid #fecaca;">'
                '<div style="font-weight:600;color:#991b1b;font-size:13px;margin-bottom:6px;">🚫 EVITAR: Perfil Sin Urgencia</div>'
                '<div style="color:#b91c1c;font-size:12.5px;line-height:1.6;">'
                '• Esposo paga todo, no necesita ingreso<br>'
                '• Lo hace "por hobby" o "para entretenerse"<br>'
                '• Se deprime fácil y para de trabajar<br>'
                '• No tiene presión económica real<br>'
                '• No ha vendido nada antes<br>'
                '• Solo quiere descuento personal'
                '</div></div>'
                '</div></div>',
                unsafe_allow_html=True
            )

            # ---- Where to Find Them ----
            st.markdown(
                '<div style="background:white;padding:20px 24px;border-radius:14px;border:1px solid #e2e8f0;box-shadow:0 2px 8px rgba(0,0,0,0.04);margin-bottom:16px;">'
                '<div style="font-weight:700;color:#1e293b;font-size:16px;margin-bottom:14px;">📍 Dónde Encontrarlas en Quito</div>'
                '<div style="display:grid;grid-template-columns:1fr 1fr 1fr;gap:10px;">'
                '<div style="background:#fefce8;padding:12px;border-radius:10px;text-align:center;">'
                '<div style="font-size:1.5rem;">📱</div>'
                '<div style="font-weight:600;font-size:13px;color:#713f12;">Facebook Groups</div>'
                '<div style="font-size:11.5px;color:#92400e;margin-top:4px;line-height:1.5;">"Mamás emprendedoras Quito"<br>"Trabajo desde casa Ecuador"<br>"Ventas directas Ecuador"</div>'
                '</div>'
                '<div style="background:#fefce8;padding:12px;border-radius:10px;text-align:center;">'
                '<div style="font-size:1.5rem;">🎵</div>'
                '<div style="font-weight:600;font-size:13px;color:#713f12;">TikTok / Instagram</div>'
                '<div style="font-size:11.5px;color:#92400e;margin-top:4px;line-height:1.5;">#mamáemprendedora<br>#trabajoflexible<br>#aceitesesenciales<br>#bienestarnatural</div>'
                '</div>'
                '<div style="background:#fefce8;padding:12px;border-radius:10px;text-align:center;">'
                '<div style="font-size:1.5rem;">🏫</div>'
                '<div style="font-weight:600;font-size:13px;color:#713f12;">En Persona</div>'
                '<div style="font-size:11.5px;color:#92400e;margin-top:4px;line-height:1.5;">Talleres de bienestar<br>Escuelas (grupos de mamás)<br>Gimnasios y estudios de yoga<br>Ferias de emprendimiento</div>'
                '</div>'
                '</div></div>',
                unsafe_allow_html=True
            )

            # ---- The Recruitment Funnel ----
            st.markdown(
                '<div style="background:white;padding:20px 24px;border-radius:14px;border:1px solid #e2e8f0;box-shadow:0 2px 8px rgba(0,0,0,0.04);">'
                '<div style="font-weight:700;color:#1e293b;font-size:16px;margin-bottom:14px;">🔄 Embudo de Reclutamiento (5 Etapas)</div>'
                '<div style="display:flex;gap:6px;align-items:stretch;">'
                # Stage 1
                '<div style="flex:1;background:linear-gradient(180deg,#dbeafe,#eff6ff);padding:12px 10px;border-radius:10px;text-align:center;">'
                '<div style="font-size:1.2rem;">🔍</div>'
                '<div style="font-weight:700;font-size:12px;color:#1e40af;">1. PROSPECTO</div>'
                '<div style="font-size:11px;color:#3b82f6;margin-top:4px;line-height:1.4;">Identificar candidata<br>Redes sociales, referidos<br><b>Meta: 10/semana</b></div>'
                '</div>'
                # Stage 2
                '<div style="flex:1;background:linear-gradient(180deg,#fef3c7,#fffbeb);padding:12px 10px;border-radius:10px;text-align:center;">'
                '<div style="font-size:1.2rem;">💬</div>'
                '<div style="font-weight:700;font-size:12px;color:#92400e;">2. CONTACTO</div>'
                '<div style="font-size:11px;color:#b45309;margin-top:4px;line-height:1.4;">Primer mensaje<br>Evaluar interés real<br><b>Meta: 5/semana</b></div>'
                '</div>'
                # Stage 3
                '<div style="flex:1;background:linear-gradient(180deg,#fed7aa,#fff7ed);padding:12px 10px;border-radius:10px;text-align:center;">'
                '<div style="font-size:1.2rem;">🫙</div>'
                '<div style="font-weight:700;font-size:12px;color:#9a3412;">3. MUESTRA</div>'
                '<div style="font-size:11px;color:#c2410c;margin-top:4px;line-height:1.4;">Enviar kit de muestra<br>Clase virtual 1:1<br><b>Conversión: 40%</b></div>'
                '</div>'
                # Stage 4
                '<div style="flex:1;background:linear-gradient(180deg,#bbf7d0,#f0fdf4);padding:12px 10px;border-radius:10px;text-align:center;">'
                '<div style="font-size:1.2rem;">🤝</div>'
                '<div style="font-weight:700;font-size:12px;color:#166534;">4. INSCRIPCIÓN</div>'
                '<div style="font-size:11px;color:#15803d;margin-top:4px;line-height:1.4;">Kit de inicio doTERRA<br>Setup de cuenta<br><b>Meta: 2/mes</b></div>'
                '</div>'
                # Stage 5
                '<div style="flex:1;background:linear-gradient(180deg,#e9d5ff,#faf5ff);padding:12px 10px;border-radius:10px;text-align:center;">'
                '<div style="font-size:1.2rem;">🌱</div>'
                '<div style="font-weight:700;font-size:12px;color:#6b21a8;">5. ACTIVACIÓN</div>'
                '<div style="font-size:11px;color:#7c3aed;margin-top:4px;line-height:1.4;">Primera venta propia<br>Entrenamiento 30 días<br><b>Retención: 70%</b></div>'
                '</div>'
                '</div></div>',
                unsafe_allow_html=True
            )

        # ==============================================
        # RECRUITMENT SUB-TAB 2: PIPELINE TRACKER
        # ==============================================
        with r_tab2:
            st.markdown(
                '<div style="font-weight:700;font-size:1.1rem;color:#1e293b;margin-bottom:12px;">📋 Tu Pipeline de Reclutamiento</div>',
                unsafe_allow_html=True
            )

            # ---- Pipeline Stats ----
            stages = ['prospecto', 'contacto', 'muestra', 'inscripcion', 'activa']
            stage_labels = {'prospecto': '🔍 Prospecto', 'contacto': '💬 Contacto', 'muestra': '🫙 Muestra', 'inscripcion': '🤝 Inscrita', 'activa': '🌱 Activa'}
            stage_colors = {'prospecto': '#3b82f6', 'contacto': '#f59e0b', 'muestra': '#f97316', 'inscripcion': '#22c55e', 'activa': '#8b5cf6'}
            counts = {s: len([p for p in pipeline if p.get('stage') == s]) for s in stages}

            stat_cols = st.columns(5)
            for i, s in enumerate(stages):
                with stat_cols[i]:
                    st.markdown(
                        f'<div style="background:white;padding:12px;border-radius:10px;text-align:center;border:2px solid {stage_colors[s]}20;box-shadow:0 1px 4px rgba(0,0,0,0.04);">'
                        f'<div style="font-size:1.5rem;font-weight:700;color:{stage_colors[s]};">{counts[s]}</div>'
                        f'<div style="font-size:11px;color:#64748b;font-weight:600;">{stage_labels[s]}</div>'
                        '</div>',
                        unsafe_allow_html=True
                    )

            st.markdown("")

            # ---- Add new prospect button ----
            if st.button("➕ Agregar Prospecto", key="add_prospect", use_container_width=True):
                st.session_state.recruit_adding = True

            if st.session_state.recruit_adding:
                with st.form("new_prospect_form"):
                    st.markdown("**Nueva Prospecto**")
                    rp_cols1 = st.columns(2)
                    with rp_cols1[0]:
                        rp_name = st.text_input("Nombre completo")
                    with rp_cols1[1]:
                        rp_phone = st.text_input("WhatsApp / Teléfono")
                    rp_cols2 = st.columns(2)
                    with rp_cols2[0]:
                        rp_source = st.selectbox("¿Dónde la encontraste?", [
                            "Facebook", "Instagram", "TikTok", "WhatsApp", "Referida", "Evento presencial", "Taller", "Otro"
                        ])
                    with rp_cols2[1]:
                        rp_profile = st.selectbox("Perfil", [
                            "🏆 Mamá Emprendedora", "🥈 Freelancer/Vendedora", "🥉 Profesional Bienestar", "Otro"
                        ])
                    rp_cols3 = st.columns(2)
                    with rp_cols3[0]:
                        rp_needs_income = st.selectbox("¿Necesita el ingreso?", ["Sí, urgente", "Sí, complementario", "No realmente"])
                    with rp_cols3[1]:
                        rp_experience = st.selectbox("Experiencia en ventas", ["Sí, venta directa", "Sí, otro tipo", "No tiene"])
                    rp_notes = st.text_area("Notas (situación, motivación, etc.)", height=80)

                    rp_sub_cols = st.columns(2)
                    with rp_sub_cols[0]:
                        submitted = st.form_submit_button("✅ Agregar al Pipeline", type="primary", use_container_width=True)
                    with rp_sub_cols[1]:
                        cancelled = st.form_submit_button("❌ Cancelar", use_container_width=True)

                    if submitted and rp_name:
                        new_prospect = {
                            "id": f"r_{datetime.now().strftime('%Y%m%d%H%M%S')}_{rp_name.lower().replace(' ', '_')[:10]}",
                            "name": rp_name,
                            "phone": rp_phone,
                            "source": rp_source,
                            "profile": rp_profile,
                            "needs_income": rp_needs_income,
                            "experience": rp_experience,
                            "notes": rp_notes,
                            "stage": "prospecto",
                            "created": datetime.now().strftime("%Y-%m-%d"),
                            "last_contact": "",
                            "next_action": "Primer contacto",
                            "score": 0
                        }
                        # Score the prospect
                        score = 0
                        if "Sí, urgente" in rp_needs_income:
                            score += 40
                        elif "Sí, complementario" in rp_needs_income:
                            score += 20
                        if "Sí, venta directa" in rp_experience:
                            score += 30
                        elif "Sí, otro tipo" in rp_experience:
                            score += 15
                        if "Mamá Emprendedora" in rp_profile:
                            score += 20
                        elif "Freelancer" in rp_profile:
                            score += 25
                        elif "Profesional" in rp_profile:
                            score += 20
                        new_prospect['score'] = min(score, 100)

                        pipeline.append(new_prospect)
                        recruit_data['pipeline'] = pipeline
                        _save_recruitment_data(recruit_data)
                        st.session_state.recruit_pipeline = pipeline
                        st.session_state.recruit_adding = False
                        st.session_state.dash_msg = ('success', f"✅ {rp_name} agregada al pipeline!")
                        st.rerun()
                    if cancelled:
                        st.session_state.recruit_adding = False
                        st.rerun()

            # ---- Pipeline Board (Kanban-style) ----
            if pipeline:
                st.markdown("---")
                for stage in stages:
                    stage_items = [p for p in pipeline if p.get('stage') == stage]
                    if not stage_items:
                        continue

                    st.markdown(
                        f'<div style="background:{stage_colors[stage]}10;padding:10px 14px;border-radius:10px;border-left:4px solid {stage_colors[stage]};margin-bottom:8px;">'
                        f'<span style="font-weight:700;color:{stage_colors[stage]};font-size:14px;">{stage_labels[stage]}</span>'
                        f'<span style="color:#94a3b8;font-size:12px;margin-left:8px;">{len(stage_items)} personas</span>'
                        '</div>',
                        unsafe_allow_html=True
                    )

                    for prospect in stage_items:
                        p_id = prospect['id']
                        score = prospect.get('score', 0)
                        score_color = '#22c55e' if score >= 60 else '#f59e0b' if score >= 30 else '#ef4444'

                        st.markdown(
                            f'<div style="background:white;padding:14px 18px;border-radius:12px;margin-bottom:8px;border:1px solid #e2e8f0;box-shadow:0 1px 4px rgba(0,0,0,0.04);">'
                            f'<div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:6px;">'
                            f'<div style="font-weight:600;color:#1e293b;font-size:14px;">{prospect["name"]}</div>'
                            f'<div style="display:flex;gap:8px;align-items:center;">'
                            f'<span style="background:{score_color}15;color:{score_color};padding:2px 10px;border-radius:12px;font-size:11px;font-weight:700;">{score}pts</span>'
                            f'<span style="color:#94a3b8;font-size:11px;">{prospect.get("created", "")}</span>'
                            f'</div></div>'
                            f'<div style="display:flex;gap:12px;font-size:12px;color:#64748b;margin-bottom:4px;">'
                            f'<span>📱 {prospect.get("phone", "—")}</span>'
                            f'<span>📍 {prospect.get("source", "")}</span>'
                            f'<span>{prospect.get("profile", "")}</span>'
                            f'</div>'
                            f'<div style="font-size:12px;color:#94a3b8;">{prospect.get("notes", "")[:80]}</div>'
                            '</div>',
                            unsafe_allow_html=True
                        )

                        # Action buttons for this prospect
                        act_cols = st.columns([1, 1, 1, 1])
                        next_stage_map = {'prospecto': 'contacto', 'contacto': 'muestra', 'muestra': 'inscripcion', 'inscripcion': 'activa'}
                        prev_stage_map = {'contacto': 'prospecto', 'muestra': 'contacto', 'inscripcion': 'muestra', 'activa': 'inscripcion'}

                        with act_cols[0]:
                            if stage in next_stage_map:
                                next_s = next_stage_map[stage]
                                if st.button(f"→ {stage_labels[next_s].split(' ')[1]}", key=f"advance_{p_id}", use_container_width=True):
                                    for pp in pipeline:
                                        if pp['id'] == p_id:
                                            pp['stage'] = next_s
                                            pp['last_contact'] = datetime.now().strftime("%Y-%m-%d")
                                            break
                                    recruit_data['pipeline'] = pipeline
                                    _save_recruitment_data(recruit_data)
                                    st.rerun()
                        with act_cols[1]:
                            if stage in prev_stage_map:
                                prev_s = prev_stage_map[stage]
                                if st.button(f"← Regresar", key=f"regress_{p_id}", use_container_width=True):
                                    for pp in pipeline:
                                        if pp['id'] == p_id:
                                            pp['stage'] = prev_s
                                            break
                                    recruit_data['pipeline'] = pipeline
                                    _save_recruitment_data(recruit_data)
                                    st.rerun()
                        with act_cols[2]:
                            wa_msg = f"Hola {prospect['name'].split()[0]}! 🌿"
                            wa_link = f"https://wa.me/593{prospect.get('phone', '').lstrip('0').replace(' ', '')}"
                            st.markdown(f'<a href="{wa_link}" target="_blank" style="display:block;text-align:center;padding:6px;background:#25D366;color:white;border-radius:8px;text-decoration:none;font-size:12px;font-weight:600;">💬 WhatsApp</a>', unsafe_allow_html=True)
                        with act_cols[3]:
                            if st.button("🗑️", key=f"del_prospect_{p_id}", use_container_width=True):
                                pipeline[:] = [pp for pp in pipeline if pp['id'] != p_id]
                                recruit_data['pipeline'] = pipeline
                                _save_recruitment_data(recruit_data)
                                st.rerun()
            else:
                st.info("Tu pipeline está vacío. ¡Agrega tu primera prospecto! 🌱")

        # ==============================================
        # RECRUITMENT SUB-TAB 3: SOCIAL MEDIA CONTENT
        # ==============================================
        with r_tab3:
            st.markdown(
                '<div style="font-weight:700;font-size:1.1rem;color:#1e293b;margin-bottom:4px;">📱 Estrategia de Contenido para Reclutamiento</div>'
                '<div style="color:#64748b;font-size:13px;margin-bottom:16px;">Contenido que atrae a las candidatas correctas — mamás y emprendedoras que necesitan ingresos flexibles</div>',
                unsafe_allow_html=True
            )

            # ---- Content Pillars ----
            st.markdown(
                '<div style="background:white;padding:18px 22px;border-radius:14px;border:1px solid #e2e8f0;margin-bottom:16px;">'
                '<div style="font-weight:700;color:#1e293b;font-size:15px;margin-bottom:12px;">4 Pilares de Contenido</div>'
                '<div style="display:grid;grid-template-columns:1fr 1fr;gap:10px;">'
                # Pillar 1 - Lifestyle
                '<div style="background:#fefce8;padding:14px;border-radius:10px;">'
                '<div style="font-weight:600;color:#854d0e;font-size:13px;">🌅 ESTILO DE VIDA (40%)</div>'
                '<div style="font-size:12px;color:#a16207;margin-top:6px;line-height:1.6;">'
                '• Tu día como mamá emprendedora<br>'
                '• Libertad de horarios con tu hija<br>'
                '• "Hoy trabajé desde el parque"<br>'
                '• Rutina matutina con aceites<br>'
                '• Pedidos empacados desde casa'
                '</div></div>'
                # Pillar 2 - Opportunity
                '<div style="background:#f0fdf4;padding:14px;border-radius:10px;">'
                '<div style="font-weight:600;color:#166534;font-size:13px;">💰 OPORTUNIDAD (25%)</div>'
                '<div style="font-size:12px;color:#15803d;margin-top:6px;line-height:1.6;">'
                '• "Cómo gano dinero sin horario fijo"<br>'
                '• Testimonio de ingreso real (sin exagerar)<br>'
                '• "Lo que me costó el kit vs lo que gané"<br>'
                '• Comparación: empleo vs doTERRA<br>'
                '• "Buscamos mamás emprendedoras"'
                '</div></div>'
                # Pillar 3 - Education
                '<div style="background:#eff6ff;padding:14px;border-radius:10px;">'
                '<div style="font-weight:600;color:#1e40af;font-size:13px;">🧠 EDUCACIÓN (25%)</div>'
                '<div style="font-size:12px;color:#2563eb;margin-top:6px;line-height:1.6;">'
                '• Tips de aceites para mamás<br>'
                '• Recetas con aceites esenciales<br>'
                '• "3 aceites que toda mamá necesita"<br>'
                '• Diferencia doTERRA vs marca genérica<br>'
                '• Clase en vivo semanal (Instagram/FB)'
                '</div></div>'
                # Pillar 4 - Testimony
                '<div style="background:#fdf4ff;padding:14px;border-radius:10px;">'
                '<div style="font-weight:600;color:#86198f;font-size:13px;">🌟 TESTIMONIOS (10%)</div>'
                '<div style="font-size:12px;color:#a21caf;margin-top:6px;line-height:1.6;">'
                '• Historias de tu equipo actual<br>'
                '• Antes/después de clientas<br>'
                '• "Llevo 6 meses y esto cambió"<br>'
                '• Video testimonial de miembro<br>'
                '• Capturas de logros (con permiso)'
                '</div></div>'
                '</div></div>',
                unsafe_allow_html=True
            )

            # ---- Weekly Content Calendar ----
            st.markdown(
                '<div style="background:white;padding:18px 22px;border-radius:14px;border:1px solid #e2e8f0;margin-bottom:16px;">'
                '<div style="font-weight:700;color:#1e293b;font-size:15px;margin-bottom:12px;">📅 Calendario Semanal de Publicaciones</div>'
                '<div style="overflow-x:auto;">'
                '<table style="width:100%;border-collapse:collapse;font-size:12px;">'
                '<tr style="background:#f1f5f9;">'
                '<th style="padding:8px 10px;text-align:left;font-weight:600;color:#475569;border-bottom:2px solid #e2e8f0;">Día</th>'
                '<th style="padding:8px 10px;text-align:left;font-weight:600;color:#475569;border-bottom:2px solid #e2e8f0;">Instagram</th>'
                '<th style="padding:8px 10px;text-align:left;font-weight:600;color:#475569;border-bottom:2px solid #e2e8f0;">Facebook</th>'
                '<th style="padding:8px 10px;text-align:left;font-weight:600;color:#475569;border-bottom:2px solid #e2e8f0;">TikTok</th>'
                '<th style="padding:8px 10px;text-align:left;font-weight:600;color:#475569;border-bottom:2px solid #e2e8f0;">WhatsApp Status</th>'
                '</tr>'
                '<tr><td style="padding:8px 10px;border-bottom:1px solid #f1f5f9;font-weight:600;color:#1e293b;">Lunes</td>'
                '<td style="padding:8px 10px;border-bottom:1px solid #f1f5f9;color:#666;">🌅 Reel: Mi rutina matutina</td>'
                '<td style="padding:8px 10px;border-bottom:1px solid #f1f5f9;color:#666;">Post motivacional</td>'
                '<td style="padding:8px 10px;border-bottom:1px solid #f1f5f9;color:#666;">—</td>'
                '<td style="padding:8px 10px;border-bottom:1px solid #f1f5f9;color:#666;">Frase + aceite del día</td></tr>'
                '<tr><td style="padding:8px 10px;border-bottom:1px solid #f1f5f9;font-weight:600;color:#1e293b;">Martes</td>'
                '<td style="padding:8px 10px;border-bottom:1px solid #f1f5f9;color:#666;">Carrusel: Tips aceites</td>'
                '<td style="padding:8px 10px;border-bottom:1px solid #f1f5f9;color:#666;">Grupo: Pregunta interactiva</td>'
                '<td style="padding:8px 10px;border-bottom:1px solid #f1f5f9;color:#666;">Tutorial rápido 30s</td>'
                '<td style="padding:8px 10px;border-bottom:1px solid #f1f5f9;color:#666;">Preparando pedidos</td></tr>'
                '<tr><td style="padding:8px 10px;border-bottom:1px solid #f1f5f9;font-weight:600;color:#1e293b;">Miércoles</td>'
                '<td style="padding:8px 10px;border-bottom:1px solid #f1f5f9;color:#666;">Story: Detrás de cámaras</td>'
                '<td style="padding:8px 10px;border-bottom:1px solid #f1f5f9;color:#666;">Testimonio de clienta</td>'
                '<td style="padding:8px 10px;border-bottom:1px solid #f1f5f9;color:#666;">—</td>'
                '<td style="padding:8px 10px;border-bottom:1px solid #f1f5f9;color:#666;">Resultado de aceite</td></tr>'
                '<tr><td style="padding:8px 10px;border-bottom:1px solid #f1f5f9;font-weight:600;color:#1e293b;">Jueves</td>'
                '<td style="padding:8px 10px;border-bottom:1px solid #f1f5f9;color:#666;">Reel: Oportunidad doTERRA</td>'
                '<td style="padding:8px 10px;border-bottom:1px solid #f1f5f9;color:#666;">Post: Buscamos mamás</td>'
                '<td style="padding:8px 10px;border-bottom:1px solid #f1f5f9;color:#666;">Día en mi vida vendiendo</td>'
                '<td style="padding:8px 10px;border-bottom:1px solid #f1f5f9;color:#666;">Ingreso del mes (vago)</td></tr>'
                '<tr><td style="padding:8px 10px;border-bottom:1px solid #f1f5f9;font-weight:600;color:#1e293b;">Viernes</td>'
                '<td style="padding:8px 10px;border-bottom:1px solid #f1f5f9;color:#666;">Live: Clase abierta aceites</td>'
                '<td style="padding:8px 10px;border-bottom:1px solid #f1f5f9;color:#666;">Live compartido en grupo</td>'
                '<td style="padding:8px 10px;border-bottom:1px solid #f1f5f9;color:#666;">—</td>'
                '<td style="padding:8px 10px;border-bottom:1px solid #f1f5f9;color:#666;">Invitación al Live</td></tr>'
                '<tr><td style="padding:8px 10px;border-bottom:1px solid #f1f5f9;font-weight:600;color:#1e293b;">Sábado</td>'
                '<td style="padding:8px 10px;border-bottom:1px solid #f1f5f9;color:#666;">Carrusel: Estilo de vida</td>'
                '<td style="padding:8px 10px;border-bottom:1px solid #f1f5f9;color:#666;">Evento: Taller gratuito</td>'
                '<td style="padding:8px 10px;border-bottom:1px solid #f1f5f9;color:#666;">Trend + aceites</td>'
                '<td style="padding:8px 10px;border-bottom:1px solid #f1f5f9;color:#666;">Fin de semana con hija</td></tr>'
                '<tr><td style="padding:8px 10px;font-weight:600;color:#1e293b;">Domingo</td>'
                '<td style="padding:8px 10px;color:#666;">Story: Descanso + gratitud</td>'
                '<td style="padding:8px 10px;color:#666;">—</td>'
                '<td style="padding:8px 10px;color:#666;">—</td>'
                '<td style="padding:8px 10px;color:#666;">Reflexión semanal</td></tr>'
                '</table></div></div>',
                unsafe_allow_html=True
            )

            # ---- Copy-paste message templates ----
            st.markdown(
                '<div style="background:white;padding:18px 22px;border-radius:14px;border:1px solid #e2e8f0;">'
                '<div style="font-weight:700;color:#1e293b;font-size:15px;margin-bottom:12px;">💬 Mensajes Listos para Copiar</div>'
                '</div>',
                unsafe_allow_html=True
            )

            msg_templates = [
                ("Primer Contacto (fría)", "Hola [nombre]! 🌿 Vi tu perfil y me encantó tu energía. Soy Suzanna, trabajo con aceites esenciales doTERRA desde casa. Estoy buscando mamás emprendedoras en Quito que quieran generar ingresos con horario flexible. ¿Te interesaría saber cómo funciona? Sin compromiso 😊"),
                ("Primer Contacto (referida)", "Hola [nombre]! 🌿 [Persona] me habló super bien de ti. Trabajo con doTERRA y estoy armando un equipo de mamás que quieren generar ingresos desde casa. ¿Tienes 10 minutos para que te cuente cómo funciona?"),
                ("Follow-up después de interés", "Hola [nombre]! 🙋‍♀️ ¿Pudiste ver la info que te envié sobre doTERRA? Me encantaría responder cualquier pregunta. También te puedo enviar unas muestras para que pruebes los aceites. ¿Cuándo te queda bien una llamada rápida?"),
                ("Invitación a clase virtual", "Hola [nombre]! 🌿 Este viernes hago una clase GRATIS sobre aceites esenciales por Instagram Live. Es súper práctica — aprenderás 3 mezclas para dormir mejor, desestresarte y dar energía. ¿Te anoto? Es a las 7pm 🕖"),
                ("Después de la muestra", "Hola [nombre]! ¿Cómo te fue con las muestras? 🌿 ¿Cuál te gustó más? Me encantaría contarte cómo puedes tener tus propios aceites a precio mayorista Y ganar dinero recomendándolos. ¿Hablamos 15 min?"),
                ("Cierre suave", "Hola [nombre]! 🤗 Después de todo lo que hemos hablado, ¿te gustaría comenzar con tu propio kit? El Kit de Inicio incluye [detalles] y con eso ya empiezas a ganar. Yo te acompaño paso a paso los primeros 30 días. ¿Qué dices?")
            ]

            for title, msg in msg_templates:
                with st.expander(f"📝 {title}"):
                    st.code(msg, language=None)

        # ==============================================
        # RECRUITMENT SUB-TAB 4: METRICS
        # ==============================================
        with r_tab4:
            st.markdown(
                '<div style="font-weight:700;font-size:1.1rem;color:#1e293b;margin-bottom:12px;">📊 Métricas de Reclutamiento</div>',
                unsafe_allow_html=True
            )

            if pipeline:
                # Funnel conversion visualization
                total_prospects = len(pipeline)
                funnel_data = {s: counts[s] for s in stages}

                st.markdown(
                    '<div style="background:white;padding:18px 22px;border-radius:14px;border:1px solid #e2e8f0;margin-bottom:16px;">'
                    '<div style="font-weight:700;color:#1e293b;font-size:15px;margin-bottom:12px;">Embudo de Conversión</div>',
                    unsafe_allow_html=True
                )

                # Visual funnel
                max_count = max(max(funnel_data.values()), 1)
                funnel_html = ''
                for s in stages:
                    pct = (funnel_data[s] / max_count * 100) if max_count > 0 else 0
                    conv = (funnel_data[s] / total_prospects * 100) if total_prospects > 0 else 0
                    funnel_html += (
                        f'<div style="display:flex;align-items:center;gap:12px;margin-bottom:8px;">'
                        f'<div style="width:120px;font-size:12px;font-weight:600;color:#475569;text-align:right;">{stage_labels[s]}</div>'
                        f'<div style="flex:1;background:#f1f5f9;border-radius:6px;height:28px;overflow:hidden;">'
                        f'<div style="width:{max(pct, 5)}%;height:100%;background:{stage_colors[s]};border-radius:6px;display:flex;align-items:center;padding-left:10px;">'
                        f'<span style="color:white;font-size:12px;font-weight:600;">{funnel_data[s]}</span>'
                        f'</div></div>'
                        f'<div style="width:50px;font-size:11px;color:#94a3b8;">{conv:.0f}%</div>'
                        f'</div>'
                    )
                st.markdown(funnel_html + '</div>', unsafe_allow_html=True)

                # Source breakdown
                sources = {}
                for p in pipeline:
                    src = p.get('source', 'Otro')
                    sources[src] = sources.get(src, 0) + 1

                st.markdown(
                    '<div style="background:white;padding:18px 22px;border-radius:14px;border:1px solid #e2e8f0;margin-bottom:16px;">'
                    '<div style="font-weight:700;color:#1e293b;font-size:15px;margin-bottom:12px;">Fuentes de Prospectos</div>',
                    unsafe_allow_html=True
                )
                source_html = '<div style="display:flex;flex-wrap:wrap;gap:8px;">'
                source_icons = {'Facebook': '📘', 'Instagram': '📸', 'TikTok': '🎵', 'WhatsApp': '💬', 'Referida': '🤝', 'Evento presencial': '🏫', 'Taller': '🎓', 'Otro': '📌'}
                for src, count in sorted(sources.items(), key=lambda x: -x[1]):
                    icon = source_icons.get(src, '📌')
                    source_html += (
                        f'<div style="background:#f8fafc;padding:10px 16px;border-radius:10px;border:1px solid #e2e8f0;text-align:center;">'
                        f'<div style="font-size:1.2rem;">{icon}</div>'
                        f'<div style="font-weight:700;color:#1e293b;font-size:16px;">{count}</div>'
                        f'<div style="font-size:11px;color:#64748b;">{src}</div>'
                        f'</div>'
                    )
                source_html += '</div>'
                st.markdown(source_html + '</div>', unsafe_allow_html=True)

                # Score distribution
                avg_score = sum(p.get('score', 0) for p in pipeline) / len(pipeline) if pipeline else 0
                high_score = len([p for p in pipeline if p.get('score', 0) >= 60])
                st.markdown(
                    '<div style="background:white;padding:18px 22px;border-radius:14px;border:1px solid #e2e8f0;">'
                    f'<div style="font-weight:700;color:#1e293b;font-size:15px;margin-bottom:12px;">Calidad del Pipeline</div>'
                    f'<div style="display:flex;gap:16px;">'
                    f'<div style="flex:1;background:#f0fdf4;padding:14px;border-radius:10px;text-align:center;">'
                    f'<div style="font-size:1.5rem;font-weight:700;color:#22c55e;">{avg_score:.0f}</div>'
                    f'<div style="font-size:12px;color:#15803d;">Score Promedio</div></div>'
                    f'<div style="flex:1;background:#eff6ff;padding:14px;border-radius:10px;text-align:center;">'
                    f'<div style="font-size:1.5rem;font-weight:700;color:#3b82f6;">{high_score}</div>'
                    f'<div style="font-size:12px;color:#2563eb;">Alta Calidad (60+)</div></div>'
                    f'<div style="flex:1;background:#fefce8;padding:14px;border-radius:10px;text-align:center;">'
                    f'<div style="font-size:1.5rem;font-weight:700;color:#eab308;">{total_prospects}</div>'
                    f'<div style="font-size:12px;color:#ca8a04;">Total Pipeline</div></div>'
                    f'</div></div>',
                    unsafe_allow_html=True
                )
            else:
                st.info("Agrega prospectos al pipeline para ver métricas 📊")

        # ==============================================
        # RECRUITMENT SUB-TAB 5: STEP-BY-STEP GUIDE
        # ==============================================
        with r_tab5:
            st.markdown(
                '<div style="font-weight:700;font-size:1.1rem;color:#1e293b;margin-bottom:4px;">📖 El Plan Completo: De 0 a Piernas Productivas</div>'
                '<div style="color:#64748b;font-size:13px;margin-bottom:16px;">Plan de 90 días para construir un equipo que realmente produzca</div>',
                unsafe_allow_html=True
            )

            # ---- Phase 1: Weeks 1-2 ----
            st.markdown(
                '<div style="background:white;padding:20px 24px;border-radius:14px;border:1px solid #e2e8f0;box-shadow:0 2px 8px rgba(0,0,0,0.04);margin-bottom:14px;">'
                '<div style="display:flex;align-items:center;gap:10px;margin-bottom:12px;">'
                '<div style="background:#dbeafe;width:36px;height:36px;border-radius:50%;display:flex;align-items:center;justify-content:center;font-weight:700;color:#1e40af;font-size:14px;">1</div>'
                '<div><div style="font-weight:700;color:#1e293b;font-size:15px;">SEMANAS 1-2: Preparar el Terreno</div>'
                '<div style="font-size:12px;color:#64748b;">Antes de buscar gente, prepara tu imagen y herramientas</div></div></div>'
                '<div style="padding-left:46px;font-size:13px;color:#475569;line-height:1.8;">'
                '<div style="margin-bottom:6px;"><b style="color:#1e40af;">✅ Optimizar perfiles de redes sociales:</b> Bio que diga qué haces + que buscas equipo. Foto profesional pero cercana. Link a tu WhatsApp.</div>'
                '<div style="margin-bottom:6px;"><b style="color:#1e40af;">✅ Crear contenido semilla (10 posts):</b> 4 de estilo de vida, 3 educativos, 2 de oportunidad, 1 testimonio. Programarlos para las próximas 2 semanas.</div>'
                '<div style="margin-bottom:6px;"><b style="color:#1e40af;">✅ Preparar kit de bienvenida digital:</b> PDF con info de doTERRA, video tuyo de 2 min explicando la oportunidad, FAQ para candidatas.</div>'
                '<div style="margin-bottom:6px;"><b style="color:#1e40af;">✅ Unirse a grupos de Facebook:</b> "Mamás emprendedoras Quito", "Trabajo desde casa Ecuador", grupos de yoga/bienestar Quito.</div>'
                '<div><b style="color:#1e40af;">✅ Pedir 5 muestras doTERRA:</b> Lavanda, Menta, On Guard, Deep Blue, Balance — las más impactantes para primera experiencia.</div>'
                '</div></div>',
                unsafe_allow_html=True
            )

            # ---- Phase 2: Weeks 3-4 ----
            st.markdown(
                '<div style="background:white;padding:20px 24px;border-radius:14px;border:1px solid #e2e8f0;box-shadow:0 2px 8px rgba(0,0,0,0.04);margin-bottom:14px;">'
                '<div style="display:flex;align-items:center;gap:10px;margin-bottom:12px;">'
                '<div style="background:#fef3c7;width:36px;height:36px;border-radius:50%;display:flex;align-items:center;justify-content:center;font-weight:700;color:#92400e;font-size:14px;">2</div>'
                '<div><div style="font-weight:700;color:#1e293b;font-size:15px;">SEMANAS 3-4: Prospección Activa</div>'
                '<div style="font-size:12px;color:#64748b;">Salir a buscar candidatas con intención</div></div></div>'
                '<div style="padding-left:46px;font-size:13px;color:#475569;line-height:1.8;">'
                '<div style="margin-bottom:6px;"><b style="color:#92400e;">✅ Meta: 10 prospectos por semana.</b> Usar el pipeline de esta herramienta para trackear cada una.</div>'
                '<div style="margin-bottom:6px;"><b style="color:#92400e;">✅ Filtrar con la pregunta clave:</b> "¿Necesitas realmente el ingreso o es un hobby?" Si es hobby → no invertir más tiempo.</div>'
                '<div style="margin-bottom:6px;"><b style="color:#92400e;">✅ Mensaje directo personalizado:</b> Usar las plantillas de la pestaña "Contenido Social". NO copiar-pegar masivamente.</div>'
                '<div style="margin-bottom:6px;"><b style="color:#92400e;">✅ Primera clase virtual:</b> Hacer un IG Live o Zoom el viernes. Tema: "Cómo gano dinero desde casa con aceites". Invitar a todas las prospectos.</div>'
                '<div><b style="color:#92400e;">✅ Enviar muestras:</b> A toda prospecto que muestre interés real, enviar muestra física. El olor vende más que cualquier pitch.</div>'
                '</div></div>',
                unsafe_allow_html=True
            )

            # ---- Phase 3: Weeks 5-8 ----
            st.markdown(
                '<div style="background:white;padding:20px 24px;border-radius:14px;border:1px solid #e2e8f0;box-shadow:0 2px 8px rgba(0,0,0,0.04);margin-bottom:14px;">'
                '<div style="display:flex;align-items:center;gap:10px;margin-bottom:12px;">'
                '<div style="background:#fed7aa;width:36px;height:36px;border-radius:50%;display:flex;align-items:center;justify-content:center;font-weight:700;color:#9a3412;font-size:14px;">3</div>'
                '<div><div style="font-weight:700;color:#1e293b;font-size:15px;">SEMANAS 5-8: Convertir e Inscribir</div>'
                '<div style="font-size:12px;color:#64748b;">Cerrar inscripciones y activar nuevas piernas</div></div></div>'
                '<div style="padding-left:46px;font-size:13px;color:#475569;line-height:1.8;">'
                '<div style="margin-bottom:6px;"><b style="color:#9a3412;">✅ Meta: 2 inscripciones por mes.</b> De 10 prospectos/semana → 5 contactos → 2 muestras → 1 inscripción cada 2 semanas.</div>'
                '<div style="margin-bottom:6px;"><b style="color:#9a3412;">✅ Llamada de cierre 1:1:</b> No en grupo. Llamada personal de 15 min. Escuchar su situación. Presentar el kit que mejor le sirve.</div>'
                '<div style="margin-bottom:6px;"><b style="color:#9a3412;">✅ Onboarding día 1:</b> Ayudarla a hacer su primera publicación, configurar su cuenta doTERRA, unirla al grupo de WhatsApp del equipo.</div>'
                '<div style="margin-bottom:6px;"><b style="color:#9a3412;">✅ Plan de 30 días para nueva inscrita:</b> Semana 1: conocer productos. Semana 2: primera venta a familia/amigos. Semana 3: primera publicación propia. Semana 4: primer prospecto de ella.</div>'
                '<div><b style="color:#9a3412;">✅ Check-in diario por WhatsApp:</b> Los primeros 30 días, mensaje diario. "¿Cómo te fue hoy? ¿Necesitas algo?" Esto retiene.</div>'
                '</div></div>',
                unsafe_allow_html=True
            )

            # ---- Phase 4: Weeks 9-12 ----
            st.markdown(
                '<div style="background:white;padding:20px 24px;border-radius:14px;border:1px solid #e2e8f0;box-shadow:0 2px 8px rgba(0,0,0,0.04);margin-bottom:14px;">'
                '<div style="display:flex;align-items:center;gap:10px;margin-bottom:12px;">'
                '<div style="background:#bbf7d0;width:36px;height:36px;border-radius:50%;display:flex;align-items:center;justify-content:center;font-weight:700;color:#166534;font-size:14px;">4</div>'
                '<div><div style="font-weight:700;color:#1e293b;font-size:15px;">SEMANAS 9-12: Escalar y Duplicar</div>'
                '<div style="font-size:12px;color:#64748b;">Tu equipo empieza a reclutar por su cuenta</div></div></div>'
                '<div style="padding-left:46px;font-size:13px;color:#475569;line-height:1.8;">'
                '<div style="margin-bottom:6px;"><b style="color:#166534;">✅ Entrenar a tus inscritas a reclutar:</b> Compartirles esta misma herramienta. Enseñarles el embudo. Que repliquen el proceso.</div>'
                '<div style="margin-bottom:6px;"><b style="color:#166534;">✅ Reunión semanal de equipo:</b> Zoom de 30 min cada lunes. Compartir logros, resolver dudas, motivar. Crear cultura de equipo.</div>'
                '<div style="margin-bottom:6px;"><b style="color:#166534;">✅ Reconocimiento público:</b> Publicar logros de tu equipo en redes. "María hizo su primera venta esta semana 🎉". Esto motiva y atrae más candidatas.</div>'
                '<div style="margin-bottom:6px;"><b style="color:#166534;">✅ Sistema de metas compartidas:</b> Meta grupal mensual. Si el equipo llega a X PV, celebración. Crear presión social positiva.</div>'
                '<div><b style="color:#166534;">✅ Evaluar y podar:</b> A los 90 días, evaluar quién produce y quién no. Invertir más tiempo en las que producen. Las que no, dejar de presionar — buscar reemplazos.</div>'
                '</div></div>',
                unsafe_allow_html=True
            )

            # ---- Key Numbers ----
            st.markdown(
                '<div style="background:linear-gradient(135deg,#1e293b,#334155);padding:20px 24px;border-radius:14px;margin-bottom:14px;">'
                '<div style="font-weight:700;color:#e2e8f0;font-size:15px;margin-bottom:12px;">🔢 Los Números que Importan</div>'
                '<div style="display:grid;grid-template-columns:1fr 1fr 1fr 1fr;gap:10px;">'
                '<div style="background:rgba(255,255,255,0.1);padding:12px;border-radius:10px;text-align:center;">'
                '<div style="font-size:1.4rem;font-weight:700;color:#fbbf24;">10</div>'
                '<div style="font-size:11px;color:#94a3b8;">Prospectos / semana</div></div>'
                '<div style="background:rgba(255,255,255,0.1);padding:12px;border-radius:10px;text-align:center;">'
                '<div style="font-size:1.4rem;font-weight:700;color:#34d399;">50%</div>'
                '<div style="font-size:11px;color:#94a3b8;">Tasa contacto</div></div>'
                '<div style="background:rgba(255,255,255,0.1);padding:12px;border-radius:10px;text-align:center;">'
                '<div style="font-size:1.4rem;font-weight:700;color:#60a5fa;">20%</div>'
                '<div style="font-size:11px;color:#94a3b8;">Tasa inscripción</div></div>'
                '<div style="background:rgba(255,255,255,0.1);padding:12px;border-radius:10px;text-align:center;">'
                '<div style="font-size:1.4rem;font-weight:700;color:#f472b6;">2</div>'
                '<div style="font-size:11px;color:#94a3b8;">Nuevas piernas / mes</div></div>'
                '</div></div>',
                unsafe_allow_html=True
            )

    # ============================================
    # TAB 3: STRIPE
    # ============================================
    with tab_stripe:
        st.markdown(
            '<div style="background:#f5f0ff;padding:20px;border-radius:12px;border:1px solid #d1c4e9;margin-bottom:16px;">'
            '<div style="font-weight:700;color:#5e35b1;font-size:1.2rem;margin-bottom:10px;">Integración con Stripe</div>'
            '<div style="color:#555;font-size:14px;line-height:1.7;">'
            'Conecta tu cuenta de Stripe para aceptar pagos directamente desde la web. '
            'Los clientes podrán pagar con tarjeta de crédito, débito y otros métodos de pago.'
            '</div></div>',
            unsafe_allow_html=True
        )

        # Stripe connection status
        st.markdown("##### Estado de Conexión")
        stripe_key_set = bool(os.environ.get('STRIPE_SECRET_KEY', ''))
        if stripe_key_set:
            st.success("Stripe conectado correctamente")
        else:
            st.warning("Stripe no está conectado. Agrega tu clave secreta en los secretos de Streamlit Cloud.")
            st.code("# En Streamlit Cloud > Settings > Secrets:\nSTRIPE_SECRET_KEY = \"sk_live_...\"", language="toml")

        # Product sync overview
        st.markdown("##### Productos y Stripe")
        stripe_products = [p for p in products_data if p.get('stripe_price_id')]
        no_stripe = [p for p in products_data if not p.get('stripe_price_id') and p.get('active', True)]

        col_s1, col_s2 = st.columns(2)
        with col_s1:
            st.metric("Conectados a Stripe", len(stripe_products))
        with col_s2:
            st.metric("Activos sin Stripe", len(no_stripe))

        if stripe_products:
            st.markdown("**Productos con Stripe Price ID:**")
            for sp in stripe_products:
                st.markdown(
                    f'<div style="padding:8px 12px;background:#f0fdf4;border-radius:8px;margin-bottom:6px;border-left:3px solid #22c55e;">'
                    f'<span style="font-weight:600;">{sp["nombre"]}</span>'
                    f'<span style="color:#888;margin-left:8px;font-size:13px;">SKU: {sp.get("doterra_sku", "—")} | Price ID: {sp.get("stripe_price_id", "—")}</span>'
                    f'</div>',
                    unsafe_allow_html=True
                )

        if no_stripe:
            st.markdown("**Productos activos sin Stripe (necesitan Price ID):**")
            for np_item in no_stripe[:10]:
                st.markdown(
                    f'<div style="padding:8px 12px;background:#fff7ed;border-radius:8px;margin-bottom:6px;border-left:3px solid #f59e0b;">'
                    f'<span style="font-weight:600;">{np_item["nombre"]}</span>'
                    f'<span style="color:#888;margin-left:8px;font-size:13px;">SKU: {np_item.get("doterra_sku", "—")} | ${np_item.get("precio_usd", 0):.2f}</span>'
                    f'</div>',
                    unsafe_allow_html=True
                )
            if len(no_stripe) > 10:
                st.caption(f"... y {len(no_stripe) - 10} productos más")

        # Checkout settings
        st.markdown("---")
        st.markdown("##### Configuración de Checkout")
        st.markdown(
            '<div style="background:#f8f9fa;padding:16px;border-radius:10px;border:1px solid #dee2e6;margin-top:8px;">'
            '<div style="color:#555;font-size:14px;line-height:1.7;">'
            '<div style="margin-bottom:8px;"><span style="font-weight:600;">Moneda:</span> USD</div>'
            '<div style="margin-bottom:8px;"><span style="font-weight:600;">Método de envío:</span> Entrega local en Ecuador</div>'
            '<div><span style="font-weight:600;">URL de éxito:</span> Se configurará automáticamente al conectar Stripe</div>'
            '</div></div>',
            unsafe_allow_html=True
        )

    # ============================================
    # TAB 3: CONFIGURACIÓN
    # ============================================
    with tab_config:
        st.markdown("##### Información de la Advocada")
        col1, col2 = st.columns(2)
        with col1:
            st.info(f"📱 **WhatsApp:** {WHATSAPP_NUMBER}")
        with col2:
            st.info(f"🎯 **ID Advocada:** {ADVOCATE_ID}")

        st.markdown("---")
        st.markdown("##### Datos del Sitio")
        col_a, col_b = st.columns(2)
        with col_a:
            st.metric("Total Productos", len(products_data))
            st.metric("Categorías", len(symptom_flow['categories']))
        with col_b:
            st.metric("Fecha", datetime.now().strftime("%d/%m/%Y"))
            st.metric("Productos Activos", f"{active_count}/{len(products_data)}")

        st.markdown("---")
        st.markdown("##### Exportar Datos")
        col_exp1, col_exp2 = st.columns(2)
        with col_exp1:
            products_json = json.dumps(products_data, ensure_ascii=False, indent=2)
            st.download_button(
                label="📥 Descargar products.json",
                data=products_json,
                file_name="products.json",
                mime="application/json",
                key="export_products"
            )
        with col_exp2:
            try:
                import pandas as pd
                df = pd.DataFrame(products_data)
                csv_data = df.to_csv(index=False)
                st.download_button(
                    label="📥 Descargar CSV",
                    data=csv_data,
                    file_name="productos.csv",
                    mime="text/csv",
                    key="export_csv"
                )
            except Exception:
                st.caption("Instala pandas para exportar CSV")

        st.markdown("---")
        st.markdown("##### Seguridad")
        st.markdown(
            '<div style="background:#fff8f0;padding:16px;border-radius:10px;border:1px solid #fed7aa;">'
            '<div style="color:#9a3412;font-size:14px;line-height:1.7;">'
            'Para cambiar la contraseña del dashboard, edita <code>DASHBOARD_PASSWORD</code> en el código fuente de app.py.'
            '</div></div>',
            unsafe_allow_html=True
        )

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
