# from existing playwright
from playwright.async_api import async_playwright
import asyncio
import base64
# from webcopilotagent.utils.clean_html import clean_html


class KeywordFramework:

    def __init__(self):
        self.browser = None
        self.page = None

    async def start_browser(self):
        playwright = await async_playwright().start()
        self.browser = await playwright.chromium.launch(
            headless=True,
            args=[
                "--no-sandbox", "--disable-dev-shm-usage",
                "--window-size=1920,1080"
            ],
        )
        self.page = await self.browser.new_page()

    async def close_browser(self):
        await self.browser.close()

    async def get_visible_html(self):
        html = await self.page.content()
        # return clean_html(html)

    def get_selector(self, locator_type, locator_value):
        selector_strategy = {
            "id": f"id={locator_value}",
            "name": f"name={locator_value}",
            "xpath": f"xpath={locator_value}",
            "href": f'css=[href="{locator_value}"]',
            "css": f"css={locator_value}",
            "link_text": f"link={locator_value}",
            "class": f".{locator_value}",
        }
        return selector_strategy[locator_type]

    async def get_screenshot(self):
        buffer = self.page.screenshot(type="png")
        return base64.b64encode(buffer).decode()

    async def execute_keyword(self,
                              action,
                              locator_type=None,
                              locator_value=None,
                              data=None,
                              **kwargs):
        action_lower = action.lower()

        selector = self.get_selector(
            locator_type,
            locator_value) if locator_type and locator_value else None

        if action_lower in ["set"]:
            await self.page.fill(selector, data)
        elif action_lower in ["click"]:
            await self.page.click(selector)
        elif action_lower in ["right click"]:
            await self.page.click(selector, button="right")
        elif action_lower in ["wait"]:
            await asyncio.sleep(int(data))
        elif action_lower in ["clear"]:
            await self.page.fill(selector, "")
        elif action_lower in ["select"]:
            await self.page.select_option(selector, label=data)
        elif action_lower in ["verify text"]:
            element = await self.page.wait_for_selector(selector)
            text = await element.text_content()
            assert (
                text == data
            ), f"Text verification failed: Expected '{data}', but got '{text}'"
        elif action_lower in ["verify text contains"]:
            element = await self.page.wait_for_selector(selector)
            text = await element.text_content()
            assert (
                data in text
            ), f"Text verification failed: Expected '{data}' inside '{text}'"
        elif action_lower in ["verify html title"]:
            page_title = await self.page.title()
            assert (
                page_title == data
            ), f"HTML title verification failed: Expected '{data}', but got '{page_title}'"
        elif action_lower in ["verify element present"]:
            elements = await self.page.query_selector_all(selector)
            assert (
                len(elements) > 0
            ), f"Element with selector '{selector}' (Locator Type: {locator_type} & Locator Value: {locator_value}) is not present on the page."
        elif action_lower in ["verify element present"]:
            elements = await self.page.query_selector_all(selector)
            assert (
                len(elements) == 0
            ), f"Element with selector '{selector}' (Locator Type: {locator_type} & Locator Value: {locator_value}) is present on the page."
        elif action_lower in ["verify element visible"]:
            element = await self.page.wait_for_selector(selector)
            assert (
                element
            ), f"Element with selector '{selector}' (Locator Type: {locator_type} & Locator Value: {locator_value}) is not visible on the page"
        elif action_lower in ["verify element not visible"]:
            element = await self.page.query_selector(selector)
            visible = await element.is_visible() if element else False
            assert (
                not visible
            ), f"Element with selector '{selector}' (Locator Type: {locator_type} & Locator Value: {locator_value}) is visible on the page"
        elif action_lower in ["verify element enabled"]:
            element = await self.page.wait_for_selector(selector)
            is_enabled = await element.is_enabled()
            assert (
                is_enabled
            ), f"Element with selector '{selector}' (Locator Type: {locator_type} & Locator Value: {locator_value}) is not enabled on the page"
        elif action_lower in ["verify element disabled"]:
            element = await self.page.wait_for_selector(selector)
            is_enabled = await element.is_enabled()
            assert (
                not is_enabled
            ), f"Element with selector '{selector}' (Locator Type: {locator_type} & Locator Value: {locator_value}) is enabled on the page"
