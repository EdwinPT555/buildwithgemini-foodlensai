# Copyright 2026 Google LLC
# Ingredient sticker and package label analysis tools for FoodlensAI

import json
import uuid
import subprocess
from typing import List, Dict, Optional, Any
from google.cloud import firestore
from google.oauth2 import credentials

PROJECT_ID = "qwiklabs-gcp-01-7526c4c469dc"  # Hardcoded project ID string

# Regulatory chemical database for international additive checks
REGULATORY_CHEMICAL_DATABASE = {
    "titanium dioxide": {
        "code": "E171",
        "warning": "Titanium Dioxide (E171) is banned as a food additive in the European Union (EU) due to genotoxicity concerns.",
        "regulations": {"EU": "BANNED", "US": "FDA Approved under 1%"}
    },
    "red 40": {
        "code": "E129",
        "warning": "Allura Red / Red 40 requires a warning label in the EU ('may have an adverse effect on activity and attention in children').",
        "regulations": {"EU": "Warning Label Required", "US": "FDA Approved"}
    },
    "potassium bromate": {
        "code": "E924",
        "warning": "Potassium Bromate is banned in EU, UK, Canada, and Brazil as a potential carcinogen.",
        "regulations": {"EU": "BANNED", "CA": "BANNED", "US": "Allowed with warning"}
    },
    "bht": {
        "code": "E321",
        "warning": "Butylated Hydroxytoluene (BHT) is restricted in EU food packaging due to potential endocrine disruption.",
        "regulations": {"EU": "Restricted", "US": "FDA Approved"}
    },
    "partially hydrogenated oil": {
        "code": "Trans Fat",
        "warning": "Partially hydrogenated oils contain artificial trans fats, banned by FDA in US and strictly capped in EU.",
        "regulations": {"US": "BANNED (GRAS removed)", "EU": "Capped <2g/100g fat"}
    }
}


def get_firestore_client() -> firestore.Client:
    """Helper to initialize Firestore client with hardcoded project ID."""
    try:
        token = subprocess.check_output(["gcloud", "auth", "print-access-token"], text=True, stderr=subprocess.DEVNULL).strip()
        creds = credentials.Credentials(token)
        return firestore.Client(project=PROJECT_ID, credentials=creds)
    except Exception:
        return firestore.Client(project=PROJECT_ID)


def check_ingredient_chemical_regulations(ingredients_text: str) -> Dict[str, Any]:
    """Scans ingredient sticker text for internationally restricted or banned chemicals/additives.

    Args:
        ingredients_text: The full text extracted or read from an ingredients package sticker.

    Returns:
        Dict containing detected chemical warnings and country-specific regulation statuses.
    """
    text_lower = ingredients_text.lower()
    detected_warnings = []
    regulations_map = {}

    for chem_key, chem_info in REGULATORY_CHEMICAL_DATABASE.items():
        if chem_key in text_lower or chem_info["code"].lower() in text_lower:
            detected_warnings.append(chem_info["warning"])
            for region, status in chem_info["regulations"].items():
                regulations_map[region] = f"{chem_info['code']} ({status})"

    return {
        "detected_chemical_warnings": detected_warnings,
        "country_regulations": regulations_map
    }


def analyze_package_ingredients_sticker(
    product_name: str,
    ingredients_text: str,
    brand: Optional[str] = "Unknown Brand"
) -> str:
    """Analyzes a food package ingredients sticker or label text directly.

    Evaluates health score (0-100%), recommendation status ('Don't Buy', 'Caution', 'Moderate', 'Healthy', 'Very Healthy'),
    beneficial nutrients vs harmful ingredients, allergens, and international chemical warning labels (EU/US).

    Args:
        product_name: Name of the food product.
        ingredients_text: Text read or extracted from the package ingredients sticker.
        brand: Brand name (optional).

    Returns:
        JSON string report with health score, buy recommendation, nutrient breakdown, allergen flags, and chemical warnings.
    """
    chem_analysis = check_ingredient_chemical_regulations(ingredients_text)
    text_lower = ingredients_text.lower()

    # Calculate health score heuristic
    score = 70
    negative_items = []
    positive_items = []
    allergens = []

    # Check allergens
    common_allergens = ["peanuts", "tree nuts", "almonds", "milk", "dairy", "lactose", "soy", "wheat", "gluten", "eggs", "fish", "shellfish", "sesame", "oats"]
    for allergen in common_allergens:
        if allergen in text_lower:
            allergens.append(allergen.title())

    # Check negative ingredients
    if "sugar" in text_lower or "high fructose corn syrup" in text_lower or "syrup" in text_lower:
        score -= 15
        negative_items.append("Added Sugars / High Fructose Corn Syrup")
    if "sodium" in text_lower or "salt" in text_lower:
        score -= 10
        negative_items.append("Sodium Content")
    if "palm oil" in text_lower or "hydrogenated" in text_lower:
        score -= 15
        negative_items.append("Palm Oil / Hydrogenated Fats")
    if chem_analysis["detected_chemical_warnings"]:
        score -= 20 * len(chem_analysis["detected_chemical_warnings"])

    # Check positive ingredients
    if "whole grain" in text_lower or "oat" in text_lower or "quinoa" in text_lower:
        score += 10
        positive_items.append("Whole Grains")
    if "fiber" in text_lower or "flax" in text_lower or "chia" in text_lower:
        score += 10
        positive_items.append("Dietary Fiber")
    if "vitamin" in text_lower or "calcium" in text_lower or "iron" in text_lower or "potassium" in text_lower:
        score += 10
        positive_items.append("Essential Vitamins & Minerals")

    # Clamp health score between 0 and 100
    final_score = max(0, min(100, score))

    # Determine status recommendation
    if final_score <= 20:
        recommendation = "Don't Buy"
    elif final_score <= 40:
        recommendation = "Caution (Don't Consume Too Much)"
    elif final_score <= 60:
        recommendation = "You Can Buy (Moderate)"
    elif final_score <= 80:
        recommendation = "Healthy"
    else:
        recommendation = "Very Healthy"

    report = {
        "product_name": product_name,
        "brand": brand,
        "health_score": final_score,
        "status_recommendation": recommendation,
        "positive_nutrients": positive_items or ["Standard Nutritional Content"],
        "negative_ingredients": negative_items or ["None Detected"],
        "allergens_detected": allergens or ["None Detected"],
        "chemical_warnings": chem_analysis["detected_chemical_warnings"],
        "country_regulations": chem_analysis["country_regulations"],
        "raw_ingredients_text": ingredients_text
    }

    return json.dumps(report, indent=2)


def save_scanned_ingredients_label(
    product_name: str,
    brand: str,
    ingredients_text: str,
    health_score: int,
    status_recommendation: str,
    positive_nutrients: List[str],
    negative_ingredients: List[str],
    allergens: List[str],
    chemical_warnings: List[str],
    barcode: Optional[str] = None
) -> str:
    """Saves analyzed package ingredient sticker details to the Firestore database.

    Args:
        product_name: Name of the packaged food product.
        brand: Brand name.
        ingredients_text: Full ingredients list text.
        health_score: Calculated health score (0-100%).
        status_recommendation: Recommendation status ('Don't Buy', 'Caution', 'Moderate', 'Healthy', 'Very Healthy').
        positive_nutrients: List of beneficial nutrients.
        negative_ingredients: List of harmful ingredients or additives.
        allergens: List of detected allergens.
        chemical_warnings: List of international chemical warnings.
        barcode: Barcode number or auto-generated ID if barcode is missing.

    Returns:
        Confirmation message with saved record ID.
    """
    db = get_firestore_client()
    doc_id = barcode.strip() if barcode else f"sticker_{uuid.uuid4().hex[:10]}"

    data = {
        "barcode": doc_id,
        "name": product_name,
        "brand": brand,
        "health_score": health_score,
        "status_recommendation": status_recommendation,
        "positive_nutrients": positive_nutrients,
        "negative_ingredients": negative_ingredients,
        "allergens": allergens,
        "chemical_warnings": chemical_warnings,
        "ingredients_text": ingredients_text,
        "source": "ingredients_sticker"
    }

    db.collection("food_products").document(doc_id).set(data)
    return f"Successfully saved package ingredients sticker report for '{product_name}' (Record ID: {doc_id}) in Firestore database."
