# Copyright 2026 Google LLC
# Firestore tools for FoodlensAI

import json
import subprocess
from typing import Optional, List, Dict, Any
from google.cloud import firestore
from google.oauth2 import credentials

PROJECT_ID = "qwiklabs-gcp-01-7526c4c469dc"  # Hardcoded project ID string

def get_firestore_client() -> firestore.Client:
    """Helper to initialize Firestore client with hardcoded project ID."""
    try:
        token = subprocess.check_output(["gcloud", "auth", "print-access-token"], text=True, stderr=subprocess.DEVNULL).strip()
        creds = credentials.Credentials(token)
        return firestore.Client(project=PROJECT_ID, credentials=creds)
    except Exception:
        return firestore.Client(project=PROJECT_ID)


def get_product_by_barcode(barcode: str) -> str:
    """Fetches product nutrition facts, health score, ingredients, allergens, and chemical warning labels from Firestore by barcode number.

    Args:
        barcode: The barcode string of the packaged food product (e.g., '073700530001', '8901030856123', '041220576921').

    Returns:
        JSON string with product details including health score out of 100%, buy recommendation, ingredients, allergens, and regional chemical warning labels.
    """
    db = get_firestore_client()
    doc_ref = db.collection("food_products").document(barcode.strip())
    doc = doc_ref.get()

    if doc.exists:
        return json.dumps(doc.to_dict(), indent=2)
    
    return json.dumps({
        "error": f"Product with barcode {barcode} not found in database.",
        "suggestion": "You can add new product details or search Open Food Facts."
    })


def search_products_by_name(query: str) -> str:
    """Searches food products in Firestore by product name or brand keyword.

    Args:
        query: Keyword to search in food product names (e.g. 'granola', 'milk', 'chips').

    Returns:
        JSON list of matching food products.
    """
    db = get_firestore_client()
    docs = db.collection("food_products").stream()
    
    results = []
    q_lower = query.lower()
    for doc in docs:
        data = doc.to_dict()
        if q_lower in data.get("name", "").lower() or q_lower in data.get("brand", "").lower():
            results.append(data)
            
    if results:
        return json.dumps(results, indent=2)
    return json.dumps({"message": f"No food products found matching query '{query}'."})


def add_product_to_database(
    barcode: str,
    name: str,
    brand: str,
    health_score: int,
    status_recommendation: str,
    positive_nutrients: List[str],
    negative_ingredients: List[str],
    allergens: List[str],
    chemical_warnings: Optional[List[str]] = None,
    country_regulations: Optional[Dict[str, str]] = None
) -> str:
    """Adds or updates a food product entry in the Firestore database.

    Args:
        barcode: The product barcode identifier.
        name: Name of the food product.
        brand: Brand name.
        health_score: Health score from 0 to 100.
        status_recommendation: Recommendation status ('Don't Buy', 'Caution', 'Moderate', 'Healthy', 'Very Healthy').
        positive_nutrients: List of beneficial nutrients (e.g. ['High Fiber', 'Calcium']).
        negative_ingredients: List of harmful ingredients or excess sodium/sugar.
        allergens: List of allergen warnings (e.g. ['Peanuts', 'Lactose', 'Gluten']).
        chemical_warnings: Optional location-specific chemical/additive warnings (e.g. Titanium Dioxide E171).
        country_regulations: Optional map of country-specific regulation statuses (e.g. {'EU': 'Banned'}).

    Returns:
        Confirmation message.
    """
    db = get_firestore_client()
    product_data = {
        "barcode": barcode.strip(),
        "name": name,
        "brand": brand,
        "health_score": health_score,
        "status_recommendation": status_recommendation,
        "positive_nutrients": positive_nutrients,
        "negative_ingredients": negative_ingredients,
        "allergens": allergens,
        "chemical_warnings": chemical_warnings or [],
        "country_regulations": country_regulations or {}
    }
    
    db.collection("food_products").document(barcode.strip()).set(product_data)
    return f"Successfully saved food product '{name}' (Barcode: {barcode}) to Firestore database."


def save_user_favorite_product(barcode: str, user_id: str = "default_user") -> str:
    """Saves a food product to the user's favorites collection in Firestore.

    Args:
        barcode: The product barcode to add to favorites.
        user_id: The ID of the user (defaults to 'default_user').

    Returns:
        Confirmation string.
    """
    db = get_firestore_client()
    product_doc = db.collection("food_products").document(barcode.strip()).get()
    
    if not product_doc.exists:
        return f"Error: Cannot favorite barcode {barcode} as it does not exist in the database."

    product_data = product_doc.to_dict()
    favorite_ref = db.collection("user_favorites").document(f"{user_id}_{barcode.strip()}")
    favorite_ref.set({
        "user_id": user_id,
        "barcode": barcode.strip(),
        "product_name": product_data.get("name"),
        "health_score": product_data.get("health_score"),
        "status_recommendation": product_data.get("status_recommendation")
    })
    return f"Added '{product_data.get('name')}' (Barcode: {barcode}) to user favorites!"


def get_user_favorite_products(user_id: str = "default_user") -> str:
    """Retrieves all favorite food products saved by the user from Firestore.

    Args:
        user_id: The user ID to query favorites for (defaults to 'default_user').

    Returns:
        JSON list of favorite products.
    """
    db = get_firestore_client()
    query = db.collection("user_favorites").where("user_id", "==", user_id).stream()
    
    favorites = [doc.to_dict() for doc in query]
    if favorites:
        return json.dumps(favorites, indent=2)
    return json.dumps({"message": f"No favorite products saved for user {user_id}."})
