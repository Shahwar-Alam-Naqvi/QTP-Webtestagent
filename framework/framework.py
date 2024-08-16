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
            script.onload = function () {
                executeCapture();
            };
        } else {
            executeCapture();
        }

        function executeCapture() {
            // Function to generate XPath for an element
            function generateXPath(element) {
                if (element.id) {
                    return `//*[@id="${element.id}"]`;
                }

                if (element === document.body) {
                    return '/html/body';
                }

                let idx = 1;
                let siblings = element.parentNode.childNodes;
                for (let i = 0; i < siblings.length; i++) {
                    const sibling = siblings[i];
                    if (sibling === element) {
                        // Generate XPath for the parent and append the current element with index
                        return `${generateXPath(element.parentNode)}/${element.tagName.toLowerCase()}[${idx}]`;
                    }
                    // Increment index only when sibling is of the same tag type
                    if (sibling.nodeType === 1 && sibling.tagName === element.tagName) {
                        idx++;
                    }
                }
            }

            // Function to get text from a label or nearby text node
            function getLabelText(element) {
                var labelText = '';
                var labels = document.querySelectorAll('label');
                labels.forEach(function (label) {
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
                elements.forEach((el, index) => {
                    var rect = el.getBoundingClientRect();

                    // Calculate midpoints
                    var midpointX = rect.left + window.scrollX + rect.width / 2;
                    var midpointY = rect.top + window.scrollY + rect.height / 2;

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

                    // Create a span for the number with midpoints
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
                    numberLabel.textContent = `${startIndex + index + 1} (X: ${midpointX.toFixed(2)}, Y: ${midpointY.toFixed(2)})`;

                    // Append bounding box and number to the body
                    document.body.appendChild(boundingBox);
                    document.body.appendChild(numberLabel);

                    // Handle pseudo-elements ::before and ::after
                    ['::before', '::after'].forEach(function (pseudo) {
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
                            y: rect.top + window.scrollY,
                            midpointX: midpointX,
                            midpointY: midpointY
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
            html2canvas(document.body).then(function (canvas) {
                var base64Image = canvas.toDataURL();

                // Clean up temporary elements
                tempElements.forEach(function (el) {
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
        print(f"⏺️ Starting Browser...")
        self.playwright = await async_playwright().start()
        try:
            self.browser = await self.playwright.chromium.launch(
                headless=False,
                args=[
                    "--no-sandbox", "--disable-dev-shm-usage",
                    "--window-size=1920,1080"
                ],
            )
            # context = await self.browser.new_context(user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/104.0.0.0 Safari/537.36")
            # context = await self.browser.new_context()
            context = await self.browser.new_context(
                user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/104.0.0.0 Safari/537.36",
                viewport={"width": 1920, "height": 1080},
                locale="en-US",
                geolocation={"latitude": 37.7749, "longitude": -122.4194},
                permissions=["geolocation"],
                timezone_id="America/Los_Angeles"
            )
            self.page = await context.new_page()  # Open a new page in incognito mode
        except Exception as e:
            print(f"🔴Error starting browser: {e}")
            raise e
        
    async def close_browser(self):
        print(f"⏺️ Closing Browser...")
        if self.page:
            await self.page.close()
            self.page = None
        if self.browser:
            await self.browser.close() 
            self.browser = None
        if self.playwright:
            await self.playwright.stop()
            
    async def getLocators(self):
        try:
            print(f"⏺️ JS Evaluation...")
            result = await self.page.evaluate(js_script)
            print(f"⏺️ Getting Locators...")
            locators = result.get('locators', {})
            print(f"🟩 Got Locators...")
            # print(f"Locators : {locators}")
            # print(f"Locators (TYPE) : {type(locators)}")
            return locators
        except Exception as e:
            print(f"🔴Error getting Locators: {e}")
            return {}

    async def takeScreenShot(self):
        try:
            print(f"⏺️ Taking ScreenShot...")
            await self.page.screenshot(path='screenshot_with_bounding_boxes.png')
            print(f"🟩 Taken ScreenShot...")
        except Exception as e:
            print(f"🔴Error taking Screen Shot : {e}")

#     async def run(self):
#         try:
#             await self.start_browser()
#             # await self.page.goto("https://www.canva.com/en_in/")  # Replace with your target URL
#             await self.page.goto("https://www.google.com/")  # Replace with your target URL

#             locators = await self.getLocators()
#             for index, locator in locators.items():
#                 print(f"{index}: {locator}")

#         except Exception as e:
#             print(f"Error in run method: {e}")
#         finally:
#             await self.close_browser()

# # Entry point
# async def main():
#     framework = KeywordFramework()
#     await framework.run()

# # Execute the main function
# if __name__ == "__main__":
#     asyncio.run(main())