import base64
import json
import httpx
import pandas as pd
from playwright.async_api import async_playwright
from app.llm_utils import llm_solve_task

async def extract_quiz_data(page):
    await page.wait_for_selector("#result")
    content = await page.inner_html("#result")
    decoded = base64.b64decode(content).decode()
    try:
        data_json = json.loads(decoded.strip())
        return data_json
    except json.JSONDecodeError:
        return None

async def solve_and_submit(url, email, secret):
    async with async_playwright() as p:
        browser = await p.chromium.launch()
        page = await browser.new_page()
        await page.goto(url)
        
        quiz_data = await extract_quiz_data(page)
        if not quiz_data:
            await browser.close()
            raise Exception("Failed to extract quiz data")
        
        answer = await llm_solve_task(pd.DataFrame(quiz_data.get("answer", {})))
        submit_url = quiz_data.get("url")
        if not submit_url:
            await browser.close()
            raise Exception("Submit URL not found")
        
        payload = {"email": email, "secret": secret, "url": url, "answer": answer}
        async with httpx.AsyncClient(timeout=30) as client:
            resp = await client.post(submit_url, json=payload)
            if resp.status_code != 200:
                await browser.close()
                raise Exception(f"Submission failed: {resp.status_code}")
            resp_json = resp.json()
        
        await browser.close()
        next_url = resp_json.get("url")
        if next_url:
            return await solve_and_submit(next_url, email, secret)
        return resp_json

# public API function
async def solve_quiz(url, email, secret):
    return await solve_and_submit(url, email, secret)
