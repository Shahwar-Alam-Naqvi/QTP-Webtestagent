# IMPORTS (buit-in)
import asyncio
import json
import base64
from datetime import datetime
from PIL import Image, ImageChops
import os
import sys
import re

# RECOGNITION for seamless custom imports from Project Hierarchy 
sys.path.append('D:\AI-2024-Services\qtp-new')

# IMPORTS (custom)
from webtestagent.moving_parts.objective import objective
from webtestagent.moving_parts.planner import plan
from qai import QAILLMs
from framework.framework import KeywordFramework

# QAI instance
llm = QAILLMs()

# KEYWORDFRAMEWORK instance
framework = KeywordFramework()

# OBJECTIVE Storing (to be removed later)
my_objective = dict()

# IMAGE to BASE64 string
def image_to_base64(image_path):
    print(f"⏺️ Coverting Image to base64 String...")
    with open(image_path, "rb") as image_file:
        base64_string = base64.b64encode(image_file.read()).decode('utf-8')
    print(f"🟩Conversion Complete...")
    return base64_string

# FORM OBJECTIVE
async def formObjective():
    global my_objective
    print(f"⏺️ Forming Objective....")
    response = await objective(model="gpt-4o", llm=llm, user_message="I want to search Qyrus AI on yahoo.com")
    # print(f"Objective Response: {response}")
    obj = response[0]
    
    if "parameters" in obj:
        my_objective = obj.get('parameters')
        if my_objective is not None:
            print(f"🟩My Objective : {my_objective}")
        else:
            print("Parameters/My Objective is None.")
    else:
        print("Parameters key does not exist in the response. So Cannot assign to to My Objective")
        

async def instantScreenshot(i,action):
    screenshot_dir = r'D:/AI-2024-Services/qtp-new/screenshots_dir'
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    screenshot_path = os.path.join(screenshot_dir, f"step_{i}_{action}_{timestamp}.png")
    await framework.page.screenshot(path=screenshot_path)

# def correctXpath(selector):
#     # Replace id("...") and class("...") statements with appropriate XPath attribute queries
#     selector = re.sub(r'id\("?([^"]*)"?\)', r'@id="\1"', selector)
#     selector = re.sub(r'class\("?([^"]*)"?\)', r'@class="\1"', selector)
    
#     # Ensure the selector starts with '//*'
#     if not selector.startswith('//*'):
#         selector = '//*[' + selector + ']'
    
#     # Remove any unmatched parenthesis or incorrect escape characters that may cause issues
#     selector = selector.replace('\\', '')

#     # Ensure matching closing brackets
#     b_open = selector.count('[')
#     b_close = selector.count(']')
#     if b_open > b_close:
#         selector += ']' * (b_open - b_close)
    
#     return selector


# EXECUTE STEPS
async def executeSteps(steps, locators):
    global my_objective
    print(f"⏺️ Executing Steps....")

    # Execute each step
    for i, step in enumerate(steps):
        try:
            print(f"⏺️ Step {i}...")
            action = step.get('action').lower()
            print(f"🔹action : {action}")
            locator_index = step.get('locator_index')
            print(f"🔹locator_index : {locator_index}")
            data = step.get('data')
            print(f"🔹data : {data}")

            if locator_index in locators:

                # EXTRACT COORDINATES
                midpointX = locators[locator_index]['coordinates']['midpointX']
                midpointY = locators[locator_index]['coordinates']['midpointY']
                selector = locators[locator_index]['xpath']
                # corrected_selector = correctXpath(selector)
                corrected_selector = selector
                print(f"⏺️ Selector : {selector}")
                print(f"🟩Corrected Selector : {corrected_selector}")

                # MOVE MOUSE TO COORDINATES
                await framework.page.mouse.move(midpointX, midpointY)
                await instantScreenshot(i, action)

                if action == 'tap':
                    await framework.page.mouse.click(midpointX, midpointY, click_count=2) #count likh chuke hain bas count try karna hai
                    await instantScreenshot(i, action)
                elif action == 'set':
                    # Click to focus on the element
                    await framework.page.mouse.click(midpointX, midpointY, click_count=2)
                    await framework.page.fill(corrected_selector,data) #yahan timeout try karo
                    await instantScreenshot(i, action)

                # Dynamic wait after actions (wait for any network activity to finish)
                await framework.page.wait_for_load_state('networkidle')
                # Add a small delay to ensure the page has time to update
                await framework.page.wait_for_timeout(1000)  # 1 second delay

        except Exception as e:
            print(f"⚠️ An error occurred on step {i}: {str(e)}")
        # finally:
            # await framework.close_browser()
            # print(f"🟩Browser Page Closed...")


async def planSteps():
    global my_objective
    # START BROWSER, also opens a page
    await framework.start_browser()

    # SNATCH URL
    url = my_objective.get('application_url')
    if not url:
        raise ValueError("🔴The 'application_url' is missing in 'my_objective'.")
    print(f"⏺️ URL check...")
    if not url.startswith("http"):
        if url.startswith("www."):
            url = 'https://' + url
        else:
            url = 'https://www.' + url

    print(f"⏺️ Navigating to URL: {url}")
    print(f"🟩Navigated...")

    # NAVIGATE TO URL
    await framework.page.goto(url)

    # GAIN LOCATORS
    locators = await framework.getLocators()
    # print(f"⏺️ Locators = {locators}")

    # GAIN SCREENSHOT
    await framework.takeScreenShot()

    # IMAGE to BASE64
    base64ss_boxes = image_to_base64(r"D:/AI-2024-Services/qtp-new/screenshot_with_bounding_boxes.png")

    # PLANNING STEPS
    print(f"🟩Planning Steps....")
    response = await plan(model='gpt-4o', llm=llm, objective=my_objective, base64ss_boxes=base64ss_boxes)
    # print(f"Response : {response}")

    # EXTRACT Steps and SEND for Execution
    print(f"⏺️ Extracting Steps...")
    steps = response[0]['parameters']['steps']
    print(f"🟩Extracted Steps : {steps}")
    await executeSteps(steps, locators)
    await asyncio.sleep(1)
    await framework.close_browser()

async def main():
    await formObjective()
    await asyncio.sleep(1)
    await planSteps()

asyncio.run(main())

