from pydantic import BaseModel, Field
from typing import List, Dict
from enum import Enum

class ActionEnum(str, Enum):
    set = "set"
    tap="tap"
    double_tap="double_tap"
    wait="wait"
    clear="clear"

class StepSchema(BaseModel):
    action: ActionEnum = Field(...,description="The action to be performed")
    data: str = Field(...,description="Data related to the action")
    locator_index: str = Field(..., description="The index of the locator")

class PlanStepsSchema(BaseModel):
    what_would_a_human_do: str = Field(...,description="Think what would a human tester do? You will have information about the objective. You might have access to extra information as well related to the objective.")
    steps: List[StepSchema] = Field(...,description="Steps to fulfill the objective")