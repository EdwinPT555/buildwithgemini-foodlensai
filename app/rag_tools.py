# Copyright 2026 Google LLC
# RAG Retrieval Tool for FoodlensAI

import subprocess
import vertexai
from vertexai.preview import rag
from google.oauth2 import credentials

CORPUS_NAME = "projects/188142736025/locations/us-central1/ragCorpora/8181307692606816256"
PROJECT_ID = "qwiklabs-gcp-01-7526c4c469dc"
LOCATION = "us-central1"


def consult_herbal_corpus(query: str) -> str:
    """Searches Nicholas Culpeper's Complete Herbal book corpus for traditional botanical, herbal, and plant remedy information.

    Args:
        query: Botanical name, herb, plant ingredient, or ailment to look up in Culpeper's Herbal text.

    Returns:
        Matched historical passages from Culpeper's Complete Herbal text.
    """
    try:
        token = subprocess.check_output(["gcloud", "auth", "print-access-token"], text=True, stderr=subprocess.DEVNULL).strip()
        creds = credentials.Credentials(token)
        vertexai.init(project=PROJECT_ID, location=LOCATION, credentials=creds)
    except Exception:
        vertexai.init(project=PROJECT_ID, location=LOCATION)

    try:
        resp = rag.retrieval_query(
            text=query,
            rag_resources=[rag.RagResource(rag_corpus=CORPUS_NAME)],
            rag_retrieval_config=rag.RagRetrievalConfig(top_k=5),
        )
    except Exception as e:
        return f"Retrieval from Herbal corpus failed: {str(e)}"

    contexts = getattr(resp.contexts, "contexts", [])
    passages = [c.text.strip() for c in contexts if getattr(c, "text", "").strip()]

    if passages:
        return "\n\n---\n\n".join(passages)
    return "No relevant passages found in Culpeper's Herbal corpus."
