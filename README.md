# FoodlensAI — AI Health & Nutrition Assistant

![FoodlensAI Demo](demo.gif)

**FoodlensAI** is an AI-powered health, nutrition, and food product assistant built with the **Google Agent Development Kit (ADK)**, **Vertex AI Agent Runtime**, **Firestore**, **Google Cloud Storage**, **Vertex AI RAG Engine**, and **A2UI (Agent-to-User Interface)**.

It allows users to look up packaged foods by barcode, analyze ingredient sticker text, store dietary health preferences and allergies across sessions, and consult a grounded botanical RAG corpus for herbal inquiries.

---

## 🌟 Implemented Features & Google Cloud Integrations

The following tools and services are fully implemented and wired up in this project (`app/`):

### 1. 🗄️ Firestore Database (`app/firestore_tools.py`)
- **`get_product_by_barcode`**: Look up product nutrition, ingredients, and health score by barcode number.
- **`search_products_by_name`**: Search food product database by product title or brand name.
- **`add_product_to_database`**: Add and seed new food items into the Firestore catalog.
- **`save_user_favorite_product` & `get_user_favorite_products`**: Manage user favorite food items.
- **`save_scanned_ingredients_label`**: Persist analyzed ingredient label scan reports into Firestore.

### 2. 🪣 Cloud Storage Media Bucket (`app/gcs_tools.py`)
- **`upload_product_image`**: Upload user-provided barcode or ingredient sticker photos to a public Cloud Storage bucket (`foodlensai-media-7526c4c4`) and return public HTTP URLs.
- **`list_uploaded_product_images`**: Inspect uploaded product images stored in the Cloud Storage bucket.

### 3. 📚 Serverless Vertex AI RAG Corpus (`app/rag_tools.py`)
- **`consult_herbal_corpus`**: Perform grounded semantic retrieval against a Serverless Vertex AI RAG Corpus containing Culpeper's Complete Herbal text for botanical ingredient inquiries.

### 4. 🏷️ Package Ingredients Sticker Analysis (`app/ingredient_tools.py`)
- **`analyze_package_ingredients_sticker`**: Evaluate ingredient list safety, highlight additive/chemical warnings (e.g., Titanium Dioxide, Red 40), and generate a health score.

### 5. 🧠 Memory Bank & Health Profile Personalization (`app/database.py`, `app/agent.py`)
- **`PreloadMemoryTool` & Firestore Session Store**: Remembers user allergies, medical conditions (e.g. diabetes, hypertension), diet plans (e.g. keto, low-sodium), and fitness goals across user chat sessions.

### 6. 🎨 A2UI Rich UI Components (`app/a2ui_utils.py`)
- Integrated `A2uiSchemaManager` (v0.8) and `BasicCatalog` to stream native interactive UI cards directly into the web frontend.

---

## 🚧 Status of Planned Features

- **On-Demand Food Image Generation**: *Planned, not yet implemented.* (Image generation models are not currently wired as a tool in `app/`).

---

## 📁 Repository Structure

```
simple-agent/
├── app/                        # Core ADK Agent & Tool implementations
│   ├── agent.py                # Main FoodlensAI Agent logic & system instructions
│   ├── firestore_tools.py      # Firestore database read/write tools
│   ├── gcs_tools.py            # Google Cloud Storage media upload tools
│   ├── ingredient_tools.py     # Package label & sticker analysis tools
│   ├── rag_tools.py            # Vertex AI RAG corpus retrieval tools
│   └── database.py             # Firestore session & memory bank configuration
├── frontend/                   # FastAPI Proxy & Plain Chat UI
│   ├── main.py                 # FastAPI proxy server interfacing with A2A Protocol
│   ├── Dockerfile              # Container definition for Cloud Run deployment
│   └── static/index.html       # FoodlensAI Chat UI & inline A2UI renderer
├── demo.gif                    # Animated walkthrough demo
├── agents-cli-manifest.yaml    # ADK Agent configuration manifest
└── deployment_metadata.json    # Agent deployment metadata
```

---

## 🚀 Local Development Setup & Execution

### Prerequisites
- Python 3.10+
- `uv` package manager (`pip install uv` or install script)
- Google Cloud SDK (`gcloud`) authenticated with GCP credentials

### 1. Install Dependencies
```bash
uv pip install --python .venv -r requirements.txt
uv pip install --python .venv -r frontend/requirements.txt
```

### 2. Configure Environment Variables
Set your environment variables in `.env` or export them in your terminal session:
```bash
export GOOGLE_CLOUD_PROJECT="<your-gcp-project-id>"
export GOOGLE_CLOUD_LOCATION="us-east1"
export AGENT_ENGINE_RESOURCE_NAME="<your-reasoning-engine-resource-name>"
export AGENT_DIRECTORY="app"
```

### 3. Run Agent CLI Playground (Local Agent Testing)
```bash
agents-cli playground
```

### 4. Run Frontend Web Application Locally
Start the FastAPI proxy server locally on port 8080:
```bash
cd frontend
AGENT_ENGINE_RESOURCE_NAME="<your-reasoning-engine-resource-name>" AGENT_DIRECTORY="app" PORT=8080 uv run python main.py
```
Open a browser and navigate to `http://localhost:8080`.

---

## ☁️ Deployment Instructions

### Deploy Agent to Vertex AI Agent Runtime
```bash
agents-cli deploy
```

### Deploy Frontend Web UI to Google Cloud Run
```bash
gcloud run deploy foodlensai-frontend \
  --source ./frontend \
  --region us-east1 \
  --allow-unauthenticated \
  --set-env-vars AGENT_ENGINE_RESOURCE_NAME="<your-reasoning-engine-resource-name>",AGENT_DIRECTORY="app"
```
