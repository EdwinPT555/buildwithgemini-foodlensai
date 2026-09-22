# Copyright 2026 Google LLC
# Script to create a serverless Vertex AI RAG corpus and import Culpeper's Herbal text

import subprocess
import vertexai
from vertexai.preview import rag
from vertexai.preview.rag.utils import resources as rr
from google.oauth2 import credentials

PROJECT_ID = "qwiklabs-gcp-01-7526c4c469dc"
LOCATION = "us-central1"  # Serverless RAG mode is us-central1
GCS_PATH = "gs://foodlensai-media-7526c4c4/rag/pg49513.txt"

PARSING_PROMPT = (
    "Extract the individual useful facts, medicinal properties, and botanical remedies described in this text. "
    "Ignore and omit all metadata, boilerplate, and Project Gutenberg license text. "
    "Output clean, self-contained prose."
)

def get_creds():
    try:
        token = subprocess.check_output(["gcloud", "auth", "print-access-token"], text=True, stderr=subprocess.DEVNULL).strip()
        return credentials.Credentials(token)
    except Exception:
        return None

def main():
    creds = get_creds()
    vertexai.init(project=PROJECT_ID, location=LOCATION, credentials=creds)

    print("1. Updating RAG Engine Config to Serverless Mode...")
    cfg = f"projects/{PROJECT_ID}/locations/{LOCATION}/ragEngineConfig"
    rag.update_rag_engine_config(
        rag_engine_config=rag.RagEngineConfig(
            name=cfg,
            rag_managed_db_config=rag.RagManagedDbConfig(mode=rr.Serverless()),
        )
    )

    print("2. Creating RAG Corpus 'herbal-remedies-culpeper'...")
    corpus = rag.create_corpus(
        display_name="herbal-remedies-culpeper",
        embedding_model_config=rag.EmbeddingModelConfig(
            publisher_model="publishers/google/models/text-embedding-005"
        ),
    )
    print(f"✅ Created Corpus ID: {corpus.name}")

    print(f"3. Importing and indexing file from {GCS_PATH}...")
    resp = rag.import_files(
        corpus_name=corpus.name,
        paths=[GCS_PATH],
        transformation_config=rag.TransformationConfig(
            chunking_config=rag.ChunkingConfig(chunk_size=512, chunk_overlap=100)
        ),
        llm_parser=rag.LlmParserConfig(
            model_name="gemini-2.5-flash",
            custom_parsing_prompt=PARSING_PROMPT
        ),
    )
    print(f"✅ Imported {resp.imported_rag_files_count} file(s) into RAG corpus!")
    print(f"\nSave this Corpus Name for your agent: {corpus.name}")

if __name__ == "__main__":
    main()
