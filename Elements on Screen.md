```js
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
                    var elementLocators = {};
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
```

### Generate Scenarios

```js
function captureInteractiveElementsAndFetch() {
    captureInteractiveElements().then(result => {
        const base64Screenshot = result.screenshot;
        const locators = result.locators;
        const messages = [
            { "role": "user", "content": "Generate functional test scenarios" }
        ];

        // Create payload
        const payload = {
            current_screenshot: base64Screenshot,
            user_messages: messages
        };

        // Fetch call with streaming output
        fetch('https://stg-gateway.quinnox.info:8243/encapsulate/v1/api/encapsulate/scenarios', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'Custom': "eyJhbGciOiJSUzI1NiIsInR5cCIgOiAiSldUIiwia2lkIiA6ICJzeUpEcndvbWZLT3FuaXJtbGl0NWNTeER6LXdaRUF2M3FMV0hmbWpzNW5NIn0.eyJleHAiOjE3MTk5MDYxNjcsImlhdCI6MTcxOTgxOTc2NywianRpIjoiNDAzMTcxMzctYTYwZi00M2JiLTk3NTEtZWU1YTZlOTk2MTYyIiwiaXNzIjoiaHR0cHM6Ly9zc28tc3RnLnF5cnVzLmNvbS9yZWFsbXMvc3RhZ2luZyIsImF1ZCI6ImFjY291bnQiLCJzdWIiOiI2N2ViODQxMy0yM2M3LTQwNGQtYmMzYy1lMDA1NzI1MmM4NDUiLCJ0eXAiOiJCZWFyZXIiLCJhenAiOiJ1aSIsInNlc3Npb25fc3RhdGUiOiJlZjAwN2ZjYS1jOGQ0LTQxZDUtYWYxNC1iYzZkNzNiZjc1OWMiLCJhbGxvd2VkLW9yaWdpbnMiOlsiaHR0cDovL2xvY2FsaG9zdDo0MzAwIiwiaHR0cHM6Ly9zdGctYXBpLnF5cnVzLmNvbSIsImh0dHBzOi8vc2FnZS10ZXN0Y2xvdWQucXVpbm5veC5pbmZvIiwiaHR0cHM6Ly9zdGctbGFicy5xeXJ1cy5jb20iLCJodHRwczovL3N0Zy10ZXN0Y2xvdWQucXVpbm5veC5pbmZvIiwiaHR0cDovL2xvY2FsaG9zdDo1MTczIiwiaHR0cDovL2xvY2FsaG9zdDo1MTczL2NhbGxiYWNrIiwiaHR0cHM6Ly90ZXN0dWktcXlydXNib3QucXVpbm5veC5pbmZvIiwiaHR0cHM6Ly9zdGctZGF0YXRlc3RpbmcucXlydXMuY29tIl0sInJlYWxtX2FjY2VzcyI6eyJyb2xlcyI6WyJvZmZsaW5lX2FjY2VzcyIsInVtYV9hdXRob3JpemF0aW9uIl19LCJyZXNvdXJjZV9hY2Nlc3MiOnsiYWNjb3VudCI6eyJyb2xlcyI6WyJtYW5hZ2UtYWNjb3VudCIsIm1hbmFnZS1hY2NvdW50LWxpbmtzIiwidmlldy1wcm9maWxlIl19fSwic2NvcGUiOiJvcGVuaWQgcHJvZmlsZSBlbWFpbCIsInNpZCI6ImVmMDA3ZmNhLWM4ZDQtNDFkNS1hZjE0LWJjNmQ3M2JmNzU5YyIsInJvbGUiOiJST0xFX1VTRVIiLCJlbWFpbF92ZXJpZmllZCI6dHJ1ZSwib3JnYW5pemF0aW9uIjoiMTg2NyIsIm9yZ2FuaXphdGlvbl9pZCI6ImU5M2YyYzVlYTI3MDQzMzc5NTQ0NjhiN2NlZDlmOTYxIiwibmFtZSI6IlZhdHNhbCBTYWdsYW5pIiwicHJlZmVycmVkX3VzZXJuYW1lIjoidmF0c2Fsc0BxdWlubm94LmNvbSIsIm9yZ2FuaXphdGlvbl9uYW1lIjoiY3RjcXVpbm5veCIsImdpdmVuX25hbWUiOiJWYXRzYWwiLCJmYW1pbHlfbmFtZSI6IlNhZ2xhbmkiLCJwbGFuIjoiUFJPIiwiZW1haWwiOiJ2YXRzYWxzQHF1aW5ub3guY29tIn0.AGNCSRuRhhp8rIR8sKkfjA_N42M8rsIOOJi91nXETH8XnYfNNu3Yd9BZN1IUPmqMM-Vb8CnTJLGxDtvXqahe7N1oHUmRrj0RCFmokvbVZOCTIti4_hrppQdHzAVDbhfpuvUg6h1xkSjgtqOj4qS1IsIiTaEbDSHqSawZHcT7Vg84Jdk3m2p4vQffK8_QPYTs_qGv5b1nHa5T0_VzK_mhFve-IunlztnbRHLfIJChwOLHSdW0gtZPSNddDQ8bs94WVyJnPEsh0AHNTFrLCwqvufNJy5KNEOvFNaAhJKMSEadYCP2dG7jjHvZJmZ7pQAZBXqyje-XPA3reyDoBu1jAjA",
                'Authorization': 'Bearer 90540897-748a-3ef2-b3a3-c6f8f42022da'
            },
            body: JSON.stringify(payload)
        })
        .then(response => {
            if (!response.body) {
                throw new Error('ReadableStream not yet supported in this browser.');
            }
            const reader = response.body.getReader();
            const decoder = new TextDecoder();
            let buffer = '';

            reader.read().then(function processText({ done, value }) {
                if (done) {
                    console.log('Stream complete');
                    return;
                }
                buffer += decoder.decode(value, { stream: true });
                const lines = buffer.split('\n');
                lines.slice(0, -1).forEach(line => console.log(line));
                buffer = lines.slice(-1)[0];
                return reader.read().then(processText);
            });
        })
        .catch(error => {
            console.error('Fetch error:', error);
        });
    }).catch(console.error);
}
```

### Execute


### Output Execute

```json
{
    "screen_updated": false,
    "steps": [
        {
            "identifier": "Class",
            "userAction": "Set",
            "stepUUID": "184f3d4d-4eaf-43bc-b393-75559f373ffb",
            "controlType": "WebElement",
            "data": "ABC",
            "dataColumn": null,
            "identifierValue": "sBbkle",
            "property": "text",
            "description": "Enter search query 'ABC' in search bar.",
            "isConditional": "N",
            "screenshots": "Y"
        },
        {
            "identifier": "Xpath",
            "userAction": "Click",
            "stepUUID": "42de63ca-e013-4a63-8f81-a097aa21191a",
            "controlType": "WebElement",
            "data": "",
            "dataColumn": null,
            "identifierValue": "id(\"cnt\")/div[4]/div[1]/div[1]/div[1]/div[1]",
            "property": "text",
            "description": "Click on the search button to submit query.",
            "isConditional": "N",
            "screenshots": "Y"
        },
        {
            "identifier": "Class",
            "userAction": "Verify Text",
            "stepUUID": "9f819d2b-7a85-4258-a49c-c3a44d423aac",
            "controlType": "WebElement",
            "data": "Results for ABC",
            "dataColumn": null,
            "identifierValue": {},
            "property": "text",
            "description": "Verify that search results are displayed.",
            "isConditional": "N",
            "screenshots": "Y"
        },
        {
            "identifier": "Class",
            "userAction": "Verify Text",
            "stepUUID": "df46cafa-6b4f-4c77-a4fa-d1bcfdd8d925",
            "controlType": "WebElement",
            "data": "Academic Bank of Credits: ABC",
            "dataColumn": null,
            "identifierValue": {},
            "property": "text",
            "description": "Check that the search results are relevant to the query.",
            "isConditional": "N",
            "screenshots": "Y"
        },
        {
            "identifier": "Class",
            "userAction": "Set",
            "stepUUID": "ef3f7285-f074-4382-a837-59c8f05cc3e7",
            "controlType": "WebElement",
            "data": "American Broadcasting Company",
            "dataColumn": null,
            "identifierValue": "sBbkle",
            "property": "text",
            "description": "Test with exact match query 'American Broadcasting Company'.",
            "isConditional": "N",
            "screenshots": "Y"
        },
        {
            "identifier": "Xpath",
            "userAction": "Click",
            "stepUUID": "e4918dfe-735c-4554-bead-d96a90d3f78c",
            "controlType": "WebElement",
            "data": "",
            "dataColumn": null,
            "identifierValue": "id(\"cnt\")/div[4]/div[1]/div[1]/div[1]/div[1]",
            "property": "text",
            "description": "Click on the search button to submit query.",
            "isConditional": "N",
            "screenshots": "Y"
        },
        {
            "identifier": "Class",
            "userAction": "Verify Text",
            "stepUUID": "c66b2eed-4b8a-408f-b1f9-b6341d916e9c",
            "controlType": "WebElement",
            "data": "Results for American Broadcasting Company",
            "dataColumn": null,
            "identifierValue": {},
            "property": "text",
            "description": "Verify that search results are displayed.",
            "isConditional": "N",
            "screenshots": "Y"
        },
        {
            "identifier": "Id",
            "userAction": "Verify Text",
            "stepUUID": "081523c1-bac6-4369-86ee-caea0da81032",
            "controlType": "WebElement",
            "data": "American Broadcasting Company",
            "dataColumn": null,
            "identifierValue": "dimg_3PJ0ZvOmJJWl2roPudafuA0_29",
            "property": "text",
            "description": "Check that the search results are relevant to the query.",
            "isConditional": "N",
            "screenshots": "Y"
        },
        {
            "identifier": "Class",
            "userAction": "Set",
            "stepUUID": "79a63811-d73a-4d11-8d3d-ec79ee65d06c",
            "controlType": "WebElement",
            "data": "ABC Network",
            "dataColumn": null,
            "identifierValue": "sBbkle",
            "property": "text",
            "description": "Test with partial match query 'ABC Network'.",
            "isConditional": "N",
            "screenshots": "Y"
        },
        {
            "identifier": "Xpath",
            "userAction": "Click",
            "stepUUID": "fc159e57-d913-43a9-a8cb-fbc3d98104fe",
            "controlType": "WebElement",
            "data": "",
            "dataColumn": null,
            "identifierValue": "id(\"cnt\")/div[4]/div[1]/div[1]/div[1]/div[1]",
            "property": "text",
            "description": "Click on the search button to submit query.",
            "isConditional": "N",
            "screenshots": "Y"
        },
        {
            "identifier": "Class",
            "userAction": "Verify Text",
            "stepUUID": "44fd58ef-07f4-4e06-8b7f-7c8e1981799f",
            "controlType": "WebElement",
            "data": "Results for ABC Network",
            "dataColumn": null,
            "identifierValue": {},
            "property": "text",
            "description": "Verify that search results are displayed.",
            "isConditional": "N",
            "screenshots": "Y"
        },
        {
            "identifier": "Class",
            "userAction": "Verify Text",
            "stepUUID": "520738b2-cb4a-475a-83f8-d881e6c97ecc",
            "controlType": "WebElement",
            "data": "ABC Network",
            "dataColumn": null,
            "identifierValue": "MJ8UF iTPLzd rNSxBe eY4mx lUn2nc",
            "property": "text",
            "description": "Check that the search results are relevant to the query.",
            "isConditional": "N",
            "screenshots": "Y"
        },
        {
            "identifier": "Class",
            "userAction": "Set",
            "stepUUID": "f782fec7-4a8a-47d5-b74c-1804a1eba648",
            "controlType": "WebElement",
            "data": "Amrican Broadcsting Company",
            "dataColumn": null,
            "identifierValue": "sBbkle",
            "property": "text",
            "description": "Test with misspelled query 'Amrican Broadcsting Company'.",
            "isConditional": "N",
            "screenshots": "Y"
        },
        {
            "identifier": "Xpath",
            "userAction": "Click",
            "stepUUID": "04322912-5814-4a15-ae95-c000cbdb8340",
            "controlType": "WebElement",
            "data": "",
            "dataColumn": null,
            "identifierValue": "id(\"cnt\")/div[4]/div[1]/div[1]/div[1]/div[1]",
            "property": "text",
            "description": "Click on the search button to submit query.",
            "isConditional": "N",
            "screenshots": "Y"
        },
        {
            "identifier": "Class",
            "userAction": "Verify Text",
            "stepUUID": "251ee4f1-a781-4605-af3c-4cd10fd4945a",
            "controlType": "WebElement",
            "data": "Results for Amrican Broadcsting Company",
            "dataColumn": null,
            "identifierValue": {},
            "property": "text",
            "description": "Verify that search results are displayed.",
            "isConditional": "N",
            "screenshots": "Y"
        },
        {
            "identifier": "Id",
            "userAction": "Verify Text",
            "stepUUID": "abad7151-863e-4562-9430-0a58f02a1ceb",
            "controlType": "WebElement",
            "data": "American Broadcasting Company",
            "dataColumn": null,
            "identifierValue": "dimg_3PJ0ZvOmJJWl2roPudafuA0_29",
            "property": "text",
            "description": "Check that the search results are relevant to the query.",
            "isConditional": "N",
            "screenshots": "Y"
        },
        {
            "identifier": "Id",
            "userAction": "Click",
            "stepUUID": "2ca4ace0-3d38-4dfb-bcca-64cc091c31d4",
            "controlType": "WebElement",
            "data": "",
            "dataColumn": null,
            "identifierValue": "pnnext",
            "property": "text",
            "description": "Ensure that pagination works by clicking on the next page.",
            "isConditional": "N",
            "screenshots": "Y"
        },
        {
            "identifier": "Xpath",
            "userAction": "Verify Text",
            "stepUUID": "51f078ef-f637-4e7b-a711-6226be751c8a",
            "controlType": "WebElement",
            "data": "Page 2",
            "dataColumn": null,
            "identifierValue": "id(\"center_col\")/div[7]",
            "property": "text",
            "description": "Verify that the next page of results is displayed.",
            "isConditional": "N",
            "screenshots": "Y"
        },
        {
            "identifier": "Class",
            "userAction": "Verify Text",
            "stepUUID": "c9b2c73d-6002-4551-a7f4-698d6b818878",
            "controlType": "WebElement",
            "data": "No results found",
            "dataColumn": null,
            "identifierValue": {},
            "property": "text",
            "description": "Check for any error messages or unexpected behavior.",
            "isConditional": "N",
            "screenshots": "Y"
        }
    ],
    "end_execution": false,
    "objective": {
        "objective_name": "Test Search Functionality",
        "objective_description": "Ensure that the search functionality works correctly and returns accurate results.",
        "steps_checklist_to_fulfil_objective": [
            "Navigate to the search page or locate the search bar.",
            "Enter a search query relevant to the content.",
            "Submit the search query.",
            "Verify that the search results are displayed.",
            "Check that the search results are relevant to the query.",
            "Test with different types of queries (e.g., exact match, partial match, misspelled words).",
            "Ensure that the search results are sorted correctly.",
            "Verify that pagination works if there are multiple pages of results.",
            "Check for any error messages or unexpected behavior."
        ]
    }
}
```


#### Might Help

```js
function captureInteractiveElementsAndFetch() {

captureInteractiveElements().then(result => {

const base64Screenshot = result.screenshot;

const locators = result.locators;

const messages = [

{ "role": "user", "content": "Generate functional test scenarios" }

];

  

// Create payload

const payload = {

current_screenshot: base64Screenshot,

user_messages: messages

};

  

// Fetch call with streaming output

fetch('http://localhost:8888/api/encapsulate/general', {

method: 'POST',

headers: {

'Content-Type': 'application/json'

},

body: JSON.stringify(payload)

})

.then(response => {

if (!response.body) {

throw new Error('ReadableStream not yet supported in this browser.');

}

const reader = response.body.getReader();

const decoder = new TextDecoder();

let buffer = '';

  

reader.read().then(function processText({ done, value }) {

if (done) {

console.log('Stream complete');

return;

}

buffer += decoder.decode(value, { stream: true });

const lines = buffer.split('\n');

lines.slice(0, -1).forEach(line => console.log(line));

buffer = lines.slice(-1)[0];

return reader.read().then(processText);

});

})

.catch(error => {

console.error('Fetch error:', error);

});

}).catch(console.error);

}
```

#### Might Help 2

```js
function captureInteractiveElements() {

return new Promise((resolve, reject) => {

// Load html2canvas library if not already loaded

if (!window.html2canvas) {

var script = document.createElement("script");

script.src = "https://html2canvas.hertzen.com/dist/html2canvas.min.js";

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

if (element.id !== "") {

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

return (

generateXPath(element.parentNode) +

"/" +

element.tagName.toLowerCase() +

"[" +

(ix + 1) +

"]"

);

}

if (sibling.nodeType === 1 && sibling.tagName === element.tagName) {

ix++;

}

}

}

  

// Function to get text from a label or nearby text node

function getLabelText(element) {

var labelText = "";

var labels = document.querySelectorAll("label");

labels.forEach(function (label) {

if (label.htmlFor === element.id) {

labelText = label.innerText;

}

});

if (!labelText) {

var previousSibling = element.previousElementSibling;

if (

previousSibling &&

previousSibling.tagName.toLowerCase() === "label"

) {

labelText = previousSibling.innerText;

}

}

if (!labelText && element.closest("label")) {

labelText = element.closest("label").innerText;

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

content: style.content,

};

}

  

// Function to process elements and their shadow DOMs

function processElements(elements, locators, startIndex) {

elements.forEach(function (el, index) {

var rect = el.getBoundingClientRect();

  

// Create a div for the bounding box

var boundingBox = document.createElement("div");

boundingBox.style.position = "absolute";

boundingBox.style.border = "2px solid red";

boundingBox.style.left = rect.left + window.scrollX + "px";

boundingBox.style.top = rect.top + window.scrollY + "px";

boundingBox.style.width = rect.width + "px";

boundingBox.style.height = rect.height + "px";

boundingBox.style.pointerEvents = "none";

boundingBox.style.zIndex = "9999";

  

// Create a span for the number

var numberLabel = document.createElement("span");

numberLabel.style.position = "absolute";

numberLabel.style.color = "red";

numberLabel.style.backgroundColor = "white";

numberLabel.style.fontSize = "16px";

numberLabel.style.fontWeight = "bold";

numberLabel.style.padding = "2px";

numberLabel.style.left = rect.left + window.scrollX + "px";

numberLabel.style.top = rect.top + window.scrollY - 20 + "px";

numberLabel.style.zIndex = "10000";

numberLabel.textContent = startIndex + index + 1;

  

// Append bounding box and number to the body

document.body.appendChild(boundingBox);

document.body.appendChild(numberLabel);

  

// Handle pseudo-elements ::before and ::after

["::before", "::after"].forEach(function (pseudo) {

var pseudoRect = getPseudoElementDimensions(el, pseudo);

if (pseudoRect.width && pseudoRect.height) {

var pseudoBox = document.createElement("div");

pseudoBox.style.position = "absolute";

pseudoBox.style.border = "2px dashed blue";

pseudoBox.style.left =

rect.left + window.scrollX + pseudoRect.left + "px";

pseudoBox.style.top =

rect.top + window.scrollY + pseudoRect.top + "px";

pseudoBox.style.width = pseudoRect.width + "px";

pseudoBox.style.height = pseudoRect.height + "px";

pseudoBox.style.pointerEvents = "none";

pseudoBox.style.zIndex = "9998";

document.body.appendChild(pseudoBox);

}

});

  

// Generate locators

var elementLocators = {};

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

processElements(

el.shadowRoot.querySelectorAll("*"),

locators,

startIndex + index + 1

);

}

  

// Process iframes

if (el.tagName.toLowerCase() === "iframe") {

var iframeDocument;

try {

iframeDocument = el.contentDocument || el.contentWindow.document;

} catch (e) {

console.log(

"Cannot access iframe content due to cross-origin restrictions"

);

return;

}

if (iframeDocument) {

var iframeElements = iframeDocument.querySelectorAll(

'a, button, input, textarea, select, [tabindex]:not([tabindex="-1"]), [role="button"], [role="link"], [contenteditable="true"], summary'

);

processElements(iframeElements, locators, startIndex + index + 1);

  

// Create a yellow bounding box around the iframe

var iframeRect = el.getBoundingClientRect();

var iframeBoundingBox = document.createElement("div");

iframeBoundingBox.style.position = "absolute";

iframeBoundingBox.style.border = "2px solid yellow";

iframeBoundingBox.style.left =

iframeRect.left + window.scrollX + "px";

iframeBoundingBox.style.top =

iframeRect.top + window.scrollY + "px";

iframeBoundingBox.style.width = iframeRect.width + "px";

iframeBoundingBox.style.height = iframeRect.height + "px";

iframeBoundingBox.style.pointerEvents = "none";

iframeBoundingBox.style.zIndex = "9999";

document.body.appendChild(iframeBoundingBox);

}

}

});

}

  

var locators = {};

var tempElements = [];

  

// Identify interactive elements including shadow DOM and other elements like nav bar

var interactiveElements = document.querySelectorAll(

'a, button, input, textarea, select, [tabindex]:not([tabindex="-1"]), [role="button"], [role="link"], [contenteditable="true"], summary, nav, header, div[role="navigation"], div[role="menu"], img, svg'

);

processElements(interactiveElements, locators, 0);

  

// Take screenshot using html2canvas

html2canvas(document.body)

.then(function (canvas) {

var base64Image = canvas.toDataURL();

  

// Clean up temporary elements

tempElements.forEach(function (el) {

document.body.removeChild(el);

});

  

resolve({ locators: locators, screenshot: base64Image });

})

.catch(reject);

}

});

}

  

function captureScreenshot() {

return new Promise((resolve, reject) => {

// Load html2canvas library if not already loaded

if (!window.html2canvas) {

var script = document.createElement("script");

script.src = "https://html2canvas.hertzen.com/dist/html2canvas.min.js";

document.head.appendChild(script);

script.onload = function () {

executeScreenshot();

};

} else {

executeScreenshot();

}

  

function executeScreenshot() {

html2canvas(document.body)

.then(function (canvas) {

var base64Image = canvas.toDataURL();

resolve(base64Image);

})

.catch(reject);

}

});

}

  

function fetchWithScreenshotsAndLocators() {

Promise.all([

captureScreenshot(),

captureScreenshot(),

captureInteractiveElements(),

]).then(([screenshot1, screenshot2, interactiveResult]) => {

const payload = {

screenshots: [screenshot1, screenshot2],

locator_map: interactiveResult.locators,

element_screenshot: interactiveResult.screenshot,

user_messages: [

{ role: "user", content: "test the search functionality" },

],

html: "html",

};

  

fetch("http://localhost:8888/api/encapsulate/execute", {

method: "POST",

headers: {

"Content-Type": "application/json",

Accept: "application/json",

},

body: JSON.stringify(payload),

})

.then((response) => {

return response.json();

})

.then((data) => {

console.log(data);

});

});

}
```

