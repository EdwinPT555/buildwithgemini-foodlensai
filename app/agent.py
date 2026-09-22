# ruff: noqa
# Copyright 2026 Google LLC
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     https://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import datetime
from zoneinfo import ZoneInfo

from google.adk.agents import Agent
from google.adk.agents.callback_context import CallbackContext
from google.adk.apps import App
from google.adk.models import Gemini
from google.adk.tools.preload_memory_tool import PreloadMemoryTool
from google.genai import types


MODEL = "gemini-2.5-flash"


async def generate_memories_callback(callback_context: CallbackContext):
    await callback_context.add_session_to_memory()
    return None


def get_weather(query: str) -> str:
    """Simulates a web search. Use it get information on weather.

    Args:
        query: A string containing the location to get weather information for.

    Returns:
        A string with the simulated weather information for the queried location.
    """
    if "sf" in query.lower() or "san francisco" in query.lower():
        return "It's 60 degrees and foggy."
    return "It's 90 degrees and sunny."


def get_current_time(query: str) -> str:
    """Simulates getting the current time for a city.

    Args:
        city: The name of the city to get the current time for.

    Returns:
        A string with the current time information.
    """
    if "sf" in query.lower() or "san francisco" in query.lower():
        tz_identifier = "America/Los_Angeles"
    else:
        return f"Sorry, I don't have timezone information for query: {query}."

    tz = ZoneInfo(tz_identifier)
    now = datetime.datetime.now(tz)
    return f"The current time for query {query} is {now.strftime('%Y-%m-%d %H:%M:%S %Z%z')}"


from a2ui.schema.manager import A2uiSchemaManager
from a2ui.basic_catalog.provider import BasicCatalog
from app.a2ui_utils import a2ui_callback
from app.firestore_tools import (
    get_product_by_barcode,
    search_products_by_name,
    add_product_to_database,
    save_user_favorite_product,
    get_user_favorite_products,
)
from app.gcs_tools import (
    upload_product_image,
    list_uploaded_product_images,
)
from app.ingredient_tools import (
    analyze_package_ingredients_sticker,
    save_scanned_ingredients_label,
)
from app.rag_tools import consult_herbal_corpus


schema_manager = A2uiSchemaManager(
    version="0.8",
    catalogs=[BasicCatalog.get_config("0.8")],
)

instruction = schema_manager.generate_system_prompt(
    role_description=(
        "You are FoodlensAI, an AI health & nutrition assistant. "
        "You actively remember and cross-reference the user's stored personal health profile across all sessions, including:\n"
        "1. Food Allergies & Intolerances (e.g., peanuts, gluten, dairy, lactose, shellfish, tree nuts, soy).\n"
        "2. Food Preferences & Dislikes (e.g., preferred foods, favorite ingredients, dietary likes/dislikes).\n"
        "3. Medical & Health Conditions (e.g., diabetes, hypertension / high blood pressure, high cholesterol, kidney disease).\n"
        "4. Diet Plans (e.g., keto, low-sodium, low-carb, Mediterranean, vegan, vegetarian, paleo).\n"
        "5. Health & Fitness Goals (e.g., weight loss, muscle gain, blood sugar management, heart health)."
    ),
    workflow_description=(
        "Whenever a user asks about a packaged food product, barcode, or ingredients sticker/label:\n"
        "- Use `get_product_by_barcode` or `search_products_by_name` for barcode lookups.\n"
        "- Use `analyze_package_ingredients_sticker` to analyze ingredient sticker text directly.\n"
        "- Use `save_scanned_ingredients_label` to store analyzed ingredient sticker reports in Firestore.\n"
        "- When users ask about herbal remedies, botanical ingredients, or traditional plants, use `consult_herbal_corpus` to ground your answer in Culpeper's Herbal text.\n"
        "- When users upload barcode or package sticker images, use `upload_product_image` to store them publicly in Cloud Storage.\n"
        "- Evaluate the product's health score (0-100%), recommendation status ('Don't Buy', 'Caution', 'Moderate', 'Healthy', 'Very Healthy'), "
        "and list good/bad ingredients. Highlight location-specific chemical/additive warning labels (e.g., Titanium Dioxide E171, Red 40, Potassium Bromate).\n"
        "- Always cross-reference recalled user memories to issue specific health & allergen warnings!"
    ),
    ui_description=(
        "Keep every surface tiny and flat: ONE Card > ONE Column > a few Text rows. "
        "Never nest a Card inside a Card. "
        "Use ONLY these components: Card, Column, Row, Text, and Image. Do not use "
        "Table or Heading (unsupported), or Buttons, actions, or forms (they do "
        "nothing in adk web). "
        "You may include one Image component, but only when you have a public https "
        "URL for the image (for example the URL an image tool returns after uploading "
        "to a public bucket). Set the Image url to that exact https link, for example "
        "{\"Image\": {\"url\": {\"literalString\": \"https://...\"}}}. Never point an "
        "Image at a bare filename, an artifact name, or a non-http(s) path. If you do "
        "not have a public URL, add a short Text line noting the image instead. "
        "No markdown in text; use the usageHint property ('h1', 'h2', 'body') for "
        "headings and emphasis. "
        "Output ONLY the raw A2UI JSON array — no prose, and never wrap it in "
        "<a2a_datapart_json> tags or 'kind'/'data'/'metadata' objects."
    ),
    include_schema=True,
    include_examples=True,
)


root_agent = Agent(
    # Keep in sync with agents-cli-manifest.yaml: agents-cli derives this name
    # from the project `name:` recorded there, and telemetry reports it as
    # gen_ai.agent.name. Renaming the agent only here makes the two disagree,
    # and anything selecting traces by name stops finding this agent's.
    name="simple_agent",
    model=Gemini(
        model=MODEL,
        retry_options=types.HttpRetryOptions(attempts=3),
    ),
    instruction=instruction,
    tools=[
        get_product_by_barcode,
        search_products_by_name,
        add_product_to_database,
        save_user_favorite_product,
        get_user_favorite_products,
        analyze_package_ingredients_sticker,
        save_scanned_ingredients_label,
        consult_herbal_corpus,
        upload_product_image,
        list_uploaded_product_images,
        get_weather,
        get_current_time,
        PreloadMemoryTool(),
    ],
    after_model_callback=a2ui_callback,
    after_agent_callback=generate_memories_callback,
)

app = App(
    root_agent=root_agent,
    name="app",
)
