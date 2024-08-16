import asyncio
import base64
from playwright.async_api import async_playwright

js_script = """
    function captureInteractiveElements() {
        return new Promise((resolve, reject) => {
            // Load html2canvas library if not already loaded
            if (!window.html2canvas) {
                var script = document.createElement('script');
                script.src = 'https://html2canvas.hertzen.com/dist/html2canvas.min.js';
                document.head.appendChild(script);
                script.onload = function() {
                    executeCapture();
                };
            } else {
                executeCapture();
            }

            function executeCapture() {
                // Function to generate XPath for an element
                function generateXPath(element) {
                    if (element.id !== '') {
                        return 'id("' + element.id + '")';
                    }
                    if (element === document.body) {
                        return element.tagName.toLowerCase();
                    }

                    var ix = 0;
                    var siblings = element.parentNode.childNodes;
                    for (var i = 0; i < siblings.length; i++) {
                        var sibling = siblings[i];
                        if (sibling === element) {
                            return generateXPath(element.parentNode) + '/' + element.tagName.toLowerCase() + '[' + (ix + 1) + ']';
                        }
                        if (sibling.nodeType === 1 && sibling.tagName === element.tagName) {
                            ix++;
                        }
                    }
                }

                // Function to get text from a label or nearby text node
                function getLabelText(element) {
                    var labelText = '';
                    var labels = document.querySelectorAll('label');
                    labels.forEach(function(label) {
                        if (label.htmlFor === element.id) {
                            labelText = label.innerText;
                        }
                    });
                    if (!labelText) {
                        var previousSibling = element.previousElementSibling;
                        if (previousSibling && previousSibling.tagName.toLowerCase() === 'label') {
                            labelText = previousSibling.innerText;
                        }
                    }
                    if (!labelText && element.closest('label')) {
                        labelText = element.closest('label').innerText;
                    }
                    return labelText;
                }

                // Function to get dimensions of pseudo-elements
                function getPseudoElementDimensions(element, pseudo) {
                    var style = window.getComputedStyle(element, pseudo);
                    return {
                        top: parseFloat(style.top) || 0,
                        left: parseFloat(style.left) || 0,
                        width: parseFloat(style.width) || 0,
                        height: parseFloat(style.height) || 0,
                        content: style.content
                    };
                }

                // Function to process elements and their shadow DOMs
                function processElements(elements, locators, startIndex) {
                    elements.forEach(function(el, index) {
                        var rect = el.getBoundingClientRect();

                        // Create a div for the bounding box
                        var boundingBox = document.createElement('div');
                        boundingBox.style.position = 'absolute';
                        boundingBox.style.border = '2px solid red';
                        boundingBox.style.left = rect.left + window.scrollX + 'px';
                        boundingBox.style.top = rect.top + window.scrollY + 'px';
                        boundingBox.style.width = rect.width + 'px';
                        boundingBox.style.height = rect.height + 'px';
                        boundingBox.style.pointerEvents = 'none';
                        boundingBox.style.zIndex = '9999';

                        // Create a span for the number
                        var numberLabel = document.createElement('span');
                        numberLabel.style.position = 'absolute';
                        numberLabel.style.color = 'red';
                        numberLabel.style.backgroundColor = 'white';
                        numberLabel.style.fontSize = '16px';
                        numberLabel.style.fontWeight = 'bold';
                        numberLabel.style.padding = '2px';
                        numberLabel.style.left = (rect.left + window.scrollX) + 'px';
                        numberLabel.style.top = (rect.top + window.scrollY - 20) + 'px';
                        numberLabel.style.zIndex = '10000';
                        numberLabel.textContent = startIndex + index + 1;

                        // Append bounding box and number to the body
                        document.body.appendChild(boundingBox);
                        document.body.appendChild(numberLabel);

                        // Handle pseudo-elements ::before and ::after
                        ['::before', '::after'].forEach(function(pseudo) {
                            var pseudoRect = getPseudoElementDimensions(el, pseudo);
                            if (pseudoRect.width && pseudoRect.height) {
                                var pseudoBox = document.createElement('div');
                                pseudoBox.style.position = 'absolute';
                                pseudoBox.style.border = '2px dashed blue';
                                pseudoBox.style.left = rect.left + window.scrollX + pseudoRect.left + 'px';
                                pseudoBox.style.top = rect.top + window.scrollY + pseudoRect.top + 'px';
                                pseudoBox.style.width = pseudoRect.width + 'px';
                                pseudoBox.style.height = pseudoRect.height + 'px';
                                pseudoBox.style.pointerEvents = 'none';
                                pseudoBox.style.zIndex = '9998';
                                document.body.appendChild(pseudoBox);
                            }
                        });

                        // Generate locators
                        var elementLocators = {
                            coordinates: {
                                x: rect.left + window.scrollX,
                                y: rect.top + window.scrollY
                            }
                        };
                        if (el.id) {
                            elementLocators.id = el.id;
                        }
                        if (el.name) {
                            elementLocators.name = el.name;
                        }
                        if (el.className) {
                            elementLocators.class = el.className;
                        }
                        elementLocators.xpath = generateXPath(el);

                        // Get label or nearby text
                        var labelText = getLabelText(el);
                        if (labelText) {
                            elementLocators.label = labelText;
                        }

                        // Ensure uniqueness of locators
                        locators[startIndex + index + 1] = elementLocators;

                        // Process shadow DOM
                        if (el.shadowRoot) {
                            processElements(el.shadowRoot.querySelectorAll('*'), locators, startIndex + index + 1);
                        }

                        // Process iframes
                        if (el.tagName.toLowerCase() === 'iframe') {
                            var iframeDocument;
                            try {
                                iframeDocument = el.contentDocument || el.contentWindow.document;
                            } catch (e) {
                                console.log("Cannot access iframe content due to cross-origin restrictions");
                                return;
                            }
                            if (iframeDocument) {
                                var iframeElements = iframeDocument.querySelectorAll('a, button, input, textarea, select, [tabindex]:not([tabindex="-1"]), [role="button"], [role="link"], [contenteditable="true"], summary');
                                processElements(iframeElements, locators, startIndex + index + 1);

                                // Create a yellow bounding box around the iframe
                                var iframeRect = el.getBoundingClientRect();
                                var iframeBoundingBox = document.createElement('div');
                                iframeBoundingBox.style.position = 'absolute';
                                iframeBoundingBox.style.border = '2px solid yellow';
                                iframeBoundingBox.style.left = iframeRect.left + window.scrollX + 'px';
                                iframeBoundingBox.style.top = iframeRect.top + window.scrollY + 'px';
                                iframeBoundingBox.style.width = iframeRect.width + 'px';
                                iframeBoundingBox.style.height = iframeRect.height + 'px';
                                iframeBoundingBox.style.pointerEvents = 'none';
                                iframeBoundingBox.style.zIndex = '9999';
                                document.body.appendChild(iframeBoundingBox);
                            }
                        }
                    });
                }

                var locators = {};
                var tempElements = [];

                // Identify interactive elements including shadow DOM and other elements like nav bar
                var interactiveElements = document.querySelectorAll('a, button, input, textarea, select, [tabindex]:not([tabindex="-1"]), [role="button"], [role="link"], [contenteditable="true"], summary, nav, header, div[role="navigation"], div[role="menu"], img, svg');
                processElements(interactiveElements, locators, 0);

                // Take screenshot using html2canvas
                html2canvas(document.body).then(function(canvas) {
                    var base64Image = canvas.toDataURL();

                    // Clean up temporary elements
                    tempElements.forEach(function(el) {
                        document.body.removeChild(el);
                    });

                    resolve({ locators: locators, screenshot: base64Image });
                }).catch(reject);
            }
        });
    }
"""

class KeywordFramework:

    def __init__(self):
        self.browser = None
        self.page = None
        self.playwright = None

    async def start_browser(self):
        self.playwright = await async_playwright().start()
        try:
            self.browser = await self.playwright.chromium.launch(
                headless=True,
                args=[
                    "--no-sandbox", "--disable-dev-shm-usage",
                    "--window-size=1920,1080"
                ],
            )
            self.page = await self.browser.new_page()
        except Exception as e:
            print(f"Error starting browser: {e}")
            raise e
        
    async def close_browser(self):
        if self.page:
            await self.page.close()
            self.page = None
        if self.browser:
            await self.browser.close() 
            self.browser = None
        if self.playwright:
            await self.playwright.stop()
            

    async def capture_elements_with_screenshot(self, js_script):
        try:
            result = await self.page.evaluate(js_script)
            locators = result.get('locators', {})
            # screenshot_base64 = result.get('screenshot', '') # if using this line, 1st fix base64 padding, 2nd write the file to local with 'wb'
            screen_shot = await self.page.screenshot(path='screenshot_with_bounding_boxes.png') # saves/writes here in this one line itself
            return locators, screen_shot

        except Exception as e:
            print(f"Error capturing elements with screenshot: {e}")
            return {}, ''

    async def search_google(self, query):
        try:
            await self.page.goto("https://google.com")
            await self.page.fill('input[name="q"]', query)
            await self.page.press('input[name="q"]', 'Enter')
            # Wait for the results to load, you can adjust this condition based on the results' page content
            await self.page.wait_for_selector('h3')
            return True
        except Exception as e:
            print(f"Error searching on Google: {e}")
            return False

    async def run(self, search_query):
        try:
            await self.start_browser()
            search_successful = await self.search_google(search_query)
            
            if search_successful:
                locators, screenshot_base64 = await self.capture_elements_with_screenshot(js_script)
                for index, locator in locators.items():
                    print(f"{index}: {locator}")
        except Exception as e:
            print(f"Error in run method: {e}")
        finally:
            await self.close_browser()

# Entry point
async def main(query):
    framework = KeywordFramework()
    await framework.run(query)

# Execute the main function
if __name__ == "__main__":
    search_query = "Playwright Python"  # Replace with your desired search query
    asyncio.run(main(search_query))