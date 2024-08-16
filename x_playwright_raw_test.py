
# Raw Template 

# from playwright.sync_api import sync_playwright
# def run(play):
    
#     # 1.Launch Browser
#     browser = play.chromium.launch(headless=True)
#     context = browser.new_context()
    
#     # Open a new Page
#     page = context.new_page()
    
#     # Go to URL
#     page.goto("https://google.com")
    
#     # Print title of page
#     print(f"Page Title : {page.title()}")
    
#     browser.close()
    
# with sync_playwright() as play:
#     run(play)
    
    
# Simple Execution (Test search in google.com)
import asyncio
from playwright.async_api import async_playwright

async def run_playwright_task(objective):
    async with async_playwright() as p:
        # Initialize the browser (headless mode)
        browser = await p.chromium.launch(headless=True)
        context = await browser.new_context()
        page = await context.new_page()

        # Navigate to the application URL
        await page.goto(objective['application_url'])

        # Simulate the "search test on google.com" objective
        search_selector = 'input[name="q"]'  # Google's search bar
        await page.fill(search_selector, 'test')
        await page.press(search_selector, 'Enter')

        # Optionally, you can wait for the results to load
        await page.wait_for_selector('text=All')  # Check for a common result element

        # You can take a screenshot or extract information if needed
        await page.screenshot(path="search_result.png")

        # Close the browser
        await browser.close()

# Objective data as a Python dictionary
objective_data = {
    "application_url": "https://google.com",
    "objective": "search test on google.com",
    "jira_ids": [],
    "conflunce_urls": []
}

# Run the Playwright task
asyncio.run(run_playwright_task(objective_data))

    