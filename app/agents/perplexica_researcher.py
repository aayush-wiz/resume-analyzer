import requests
import os
import re
from urllib.parse import urlparse
import json
import cv2  # <--- Import OpenCV
import numpy as np  # <--- Import NumPy
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)
from typing import Optional, Dict

# --- CONFIGURATION ---
PERPLEXICA_URL = "http://localhost:3000"
SEARXNG_URL = "http://localhost:4000"


def clean_text_for_search_query(text: str) -> str:
    """Removes search-polluting artifacts like [1][2] citations and extra whitespace."""
    text_no_citations = re.sub(r"\[[\d, ]+\]", "", text)  # Handles [1], [2, 3], etc.
    cleaned_text = re.sub(r"\s+", " ", text_no_citations).strip()
    return cleaned_text


def direct_search(user_query: str, focus_mode: str = "webSearch") -> Optional[Dict]:
    """
    Executes a user's query directly on Perplexity AI without any modifications.

    Args:
        user_query: The exact query string from the user.
        focus_mode: The search focus, e.g., "webSearch", "academicSearch".

    Returns:
        A dictionary containing the AI response and sources, or None if the search fails.
    """
    logger.info(
        f"🚀 Executing direct user query: '{user_query}' with focus '{focus_mode}'"
    )

    # Use the existing _search_perplexica method but without the medical-specific system instructions.
    search_url = f"{PERPLEXICA_URL}/api/search"

    payload = {
        "chatModel": {"provider": "gemini", "name": "gemini-2.0-flash"},
        "embeddingModel": {"provider": "gemini", "name": "models/text-embedding-004"},
        "optimizationMode": "balanced",
        "focusMode": focus_mode,
        "query": user_query,  # Direct user query
        "stream": False,
        # No medical-specific system instructions are added here.
        "systemInstructions": "You are a helpful AI assistant.",
    }

    headers = {
        "Content-Type": "application/json",
        "User-Agent": "Direct-Query-Tool/1.0",
    }

    try:
        response = requests.post(search_url, json=payload, headers=headers, timeout=60)
        response.raise_for_status()  # Raise an exception for bad status codes
        result = response.json()
        logger.info(
            f"✅ Direct query successful. AI response length: {len(result.get('message', ''))} chars."
        )
        return result

    except requests.exceptions.RequestException as e:
        logger.error(f"❌ Direct Perplexica API request failed: {e}")
        return None
    except json.JSONDecodeError as e:
        logger.error(f"❌ Failed to parse Perplexica response for direct query: {e}")
        return None


# def get_context_from_perplexica(query: str) -> str | None:
#     """Queries the Perplexica API using Gemini models to get a detailed text answer on a topic."""
#     print(f"--- Step 1: Querying Perplexica (Gemini) for context on: '{query}' ---")
#     payload = {
#         "content": query,
#         "chatId": self.session_chat_id,
#         "chatModel": {"name": "gemini-2.5-flash", "provider": "gemini"},
#         "embeddingModel": {"name": "models/text-embedding-004", "provider": "gemini"},
#         "focusMode": "webSearch",
#         "history": [],
#         "message": {
#             "content": query,
#         },
#         "optimizationMode": "speed",
#         "systemInstructions": None,
#         "files": [],
#     }

#     try:
#         response = requests.post(
#             f"{PERPLEXICA_URL}/api/search",
#             json=payload,
#             headers={"Content-Type": "application/json"},
#             timeout=90,
#         )
#         response.raise_for_status()
#         data = response.json()
#         message = data.get("message")
#         if message:
#             print("[SUCCESS] Got rich context from Perplexica.")
#             return message
#     except requests.exceptions.RequestException as e:
#         print(f"\n[ERROR] Could not connect to Perplexica: {e}")
#         return None
#     return None


# def search_for_images_searxng(
#     query: str, engines: list = ["google images", "bing images"]
# ) -> list | None:
#     """Searches for images using the local SearXNG API."""
#     params = {"q": query, "format": "json", "engines": ",".join(engines)}
#     print(f"--- Step 2: Performing targeted image search with a CLEANED query ---")
#     print(f"-> Querying SearXNG with: '{query[:150]}...'")
#     try:
#         response = requests.get(f"{SEARXNG_URL}/search", params=params)
#         response.raise_for_status()
#         data = response.json()
#         return [
#             result["img_src"]
#             for result in data.get("results", [])
#             if "img_src" in result
#         ]
#     except requests.exceptions.RequestException as e:
#         print(f"\n[ERROR] Could not connect to SearXNG: {e}")
#         return None


# def download_and_correct_image(
#     image_url: str, save_folder: str = "image_downloads", min_size_kb: int = 15
# ) -> str | None:
#     """
#     Downloads, VALIDATES, CORRECTS THE COLOR, and saves a single image.
#     """
#     if not os.path.exists(save_folder):
#         os.makedirs(save_folder)
#     try:
#         img_response = requests.get(image_url, stream=True, timeout=10)
#         img_response.raise_for_status()

#         # --- VALIDATION ---
#         content_type = (
#             img_response.headers.get("Content-Type", "").split(";")[0].strip()
#         )
#         if not content_type.startswith("image/"):
#             print(f"[SKIP] Not an image. Content-Type: '{content_type}'")
#             return None

#         content = img_response.content
#         if len(content) < (min_size_kb * 1024):
#             print(f"[SKIP] Image too small (< {min_size_kb} KB).")
#             return None

#         # --- THE FIX: DECODE, CORRECT COLOR, AND RE-ENCODE ---
#         # 1. Load the downloaded data into a NumPy array
#         image_array = np.frombuffer(content, np.uint8)

#         # 2. Decode the array into an OpenCV image (this will be BGR)
#         bgr_image = cv2.imdecode(image_array, cv2.IMREAD_COLOR)
#         if bgr_image is None:
#             print(f"[SKIP] OpenCV could not decode the image data from {image_url}.")
#             return None

#         # 3. Convert the image from BGR to RGB - THIS IS THE CRITICAL STEP
#         rgb_image = cv2.cvtColor(bgr_image, cv2.COLOR_BGR2RGB)

#         # --- SAVE THE CORRECTED IMAGE ---
#         # Create a safe filename with a standard .png extension
#         base_name = os.path.splitext(os.path.basename(urlparse(image_url).path))[0]
#         safe_base_name = (
#             "".join(c for c in base_name if c.isalnum() or c in ("_", "-")).strip()
#             or "downloaded_image"
#         )
#         final_filename = f"{safe_base_name}.png"  # Save as PNG for broad compatibility
#         filepath = os.path.join(save_folder, final_filename)

#         # 4. Save the corrected RGB image using OpenCV
#         cv2.imwrite(
#             filepath, cv2.cvtColor(rgb_image, cv2.COLOR_RGB2BGR)
#         )  # Must convert back to BGR for imwrite

#         return filepath

#     except requests.exceptions.RequestException as e:
#         print(
#             f"[SKIP] Failed to download from {image_url}. Reason: {e.__class__.__name__}"
#         )
#         return None
#     except Exception as e:
#         print(f"[ERROR] An unexpected error occurred during image processing: {e}")
#         return None


# def run_image_search(search_query: str) -> str | None:
#     """Orchestrates the entire intelligent image search and download process."""
#     context_text = get_context_from_perplexica(search_query)
#     if not context_text:
#         print("\n[FAILURE] Could not get context from Perplexica.")
#         return None

#     cleaned_context = clean_text_for_search_query(context_text)
#     refined_query = f"{search_query} {cleaned_context}"

#     image_urls = search_for_images_searxng(refined_query)
#     if not image_urls:
#         print("\n[FAILURE] No image URLs were found with the refined query.")
#         return None

#     print(
#         f"\n--- Step 3: Found {len(image_urls)} potential images. Validating, correcting, and downloading... ---"
#     )

#     for url in image_urls:
#         saved_file_path = download_and_correct_image(url)  # Using the new function
#         if saved_file_path:
#             print(
#                 f"\n[OVERALL SUCCESS] Corrected image downloaded and saved to: {saved_file_path}"
#             )
#             return saved_file_path

#     print("\n[FAILURE] Scanned the top results, but could not download a valid image.")
#     return None


if __name__ == "__main__":
    query = "What is Covid"
    result = direct_search(user_query=query)
    print(result)
