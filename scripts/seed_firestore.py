# Copyright 2026 Google LLC
# Seed script for FoodlensAI Firestore collection

import subprocess
import google.auth
from google.oauth2 import credentials
from google.cloud import firestore

PROJECT_ID = "qwiklabs-gcp-01-7526c4c469dc"  # Hardcoded project ID string

def get_firestore_client():
    try:
        token = subprocess.check_output(["gcloud", "auth", "print-access-token"], text=True).strip()
        creds = credentials.Credentials(token)
        return firestore.Client(project=PROJECT_ID, credentials=creds)
    except Exception:
        return firestore.Client(project=PROJECT_ID)

def seed_firestore():
    db = get_firestore_client()
    collection_ref = db.collection("food_products")

    sample_products = [
        {
            "barcode": "073700530001",
            "name": "NutriCrunch Organic Oat Granola",
            "brand": "NutriCrunch",
            "health_score": 88,
            "status_recommendation": "Very Healthy",
            "positive_nutrients": ["High Fiber (8g)", "Plant Protein (6g)", "Whole Grains"],
            "negative_ingredients": ["Low Added Sugar (2g)"],
            "allergens": ["Tree Nuts", "Oats"],
            "chemical_warnings": [],
            "country_regulations": {"EU": "Compliant", "US": "FDA Approved", "CA": "Prop 65 Clear"}
        },
        {
            "barcode": "8901030856123",
            "name": "Fiesta Crispy Potato Chips - Extreme Salt",
            "brand": "Fiesta Snack Co",
            "health_score": 18,
            "status_recommendation": "Don't Buy",
            "positive_nutrients": ["Potassium"],
            "negative_ingredients": ["Excess Sodium (650mg)", "Palm Oil", "Artificial Dyes (E129 Allura Red)"],
            "allergens": ["Gluten"],
            "chemical_warnings": ["Contains Red 40 / E129 (Requires warning label in EU for child activity)", "High Trans Fat Warning"],
            "country_regulations": {"EU": "Warning Label Required", "US": "FDA Approved"}
        },
        {
            "barcode": "041220576921",
            "name": "Silk Pure Almond Milk - Vanilla Zero Sugar",
            "brand": "Silk",
            "health_score": 78,
            "status_recommendation": "Healthy",
            "positive_nutrients": ["Calcium (45% DV)", "Vitamin D", "Zero Added Sugar"],
            "negative_ingredients": ["Gellan Gum", "Natural Flavors"],
            "allergens": ["Almonds", "Tree Nuts"],
            "chemical_warnings": [],
            "country_regulations": {"EU": "Compliant", "US": "FDA Approved"}
        },
        {
            "barcode": "012345678905",
            "name": "UltraEnergy Sugar-Free Sparkling Drink",
            "brand": "UltraEnergy",
            "health_score": 35,
            "status_recommendation": "Don't Consume Too Much",
            "positive_nutrients": ["Vitamin B12", "Niacin"],
            "negative_ingredients": ["Sucralose", "Acesulfame Potassium", "Sodium Benzoate", "Titanium Dioxide E171"],
            "allergens": [],
            "chemical_warnings": ["Titanium Dioxide E171 (Banned as food additive in European Union since 2022)"],
            "country_regulations": {"EU": "BANNED (E171 Titanium Dioxide)", "US": "FDA Approved"}
        }
    ]

    for product in sample_products:
        doc_ref = collection_ref.document(product["barcode"])
        doc_ref.set(product)
        print(f"Seeded product: {product['name']} (Barcode: {product['barcode']})")

    print(f"Successfully seeded {len(sample_products)} food products into Firestore 'food_products' collection.")

if __name__ == "__main__":
    seed_firestore()
