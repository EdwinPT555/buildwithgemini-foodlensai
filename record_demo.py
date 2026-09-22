import asyncio
import os
import shutil
from playwright.async_api import async_playwright

FRONTEND_URL = "https://foodlensai-frontend-188142736025.us-east1.run.app"
ARTIFACT_DIR = "/config/.gemini/antigravity/brain/97cb01e4-7e65-48ed-80fd-146d1a04dc8c"
VIDEO_TEMP_DIR = os.path.join(ARTIFACT_DIR, "scratch", "raw_videos")

async def record_demo():
    os.makedirs(VIDEO_TEMP_DIR, exist_ok=True)
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        context = await browser.new_context(
            record_video_dir=VIDEO_TEMP_DIR,
            record_video_size={"width": 1280, "height": 800},
            viewport={"width": 1280, "height": 800}
        )
        page = await context.new_page()

        print("Navigating to FoodlensAI Cloud Run frontend...")
        await page.goto(FRONTEND_URL, wait_until="networkidle")
        await page.wait_for_timeout(2000)

        # 1. First interaction: Barcode Lookup & Auto DB Ingestion
        print("Executing Prompt 1: Barcode Lookup 5449000000996...")
        await page.fill("#input", "🔍 Check barcode 5449000000996")
        await page.wait_for_timeout(1000)
        await page.click("button[type='submit']")
        
        # Wait for agent response to appear (A2UI card or text bubble)
        await page.wait_for_selector(".msg-row.agent", timeout=45000)
        await page.wait_for_timeout(8000)

        # 2. Second interaction: Botanical RAG Corpus Lookup
        print("Executing Prompt 2: Botanical RAG Corpus Lookup...")
        await page.fill("#input", "🌿 Consult herbal corpus for chamomile and mint remedies")
        await page.wait_for_timeout(1000)
        await page.click("button[type='submit']")

        # Wait for second agent response
        await page.wait_for_selector(".msg-row.agent:nth-of-type(2)", timeout=45000)
        await page.wait_for_timeout(8000)

        video_path = await page.video.path()
        await context.close()
        await browser.close()

        final_video_path = os.path.join(ARTIFACT_DIR, "foodlensai_demo.webm")
        shutil.copy(video_path, final_video_path)
        print(f"Demo video saved to: {final_video_path}")

if __name__ == "__main__":
    asyncio.run(record_demo())
