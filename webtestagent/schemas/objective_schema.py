from pydantic import BaseModel, Field
from typing import List, Union, Literal

class ObjectiveSchema(BaseModel):
    application_url: str = Field(...,description="Provide the URL from the user message if you see it")
    objective: str = Field(...,description="Provide the brief summary of the ask from user in less than 7 to 8 words.")
    jira_ids: List = Field(...,description="Store the Jira Ids in the list if you find them.")
    confluence_urls: List = Field(...,description="Provide the list of confluence urls if any.")