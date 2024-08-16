from typing import Dict, List, Optional

# Import (default)
import asyncio
import os
import base64

# Recognise the project (to make custom imports)
import sys
sys.path.append('D:\AI-2024-Services\qtp-new')

# Import (custom)
from webtestagent.system_prompts import SYSTEM_PROMPTS
from webtestagent.schemas.plan_steps_schema import PlanStepsSchema

# # QAI Import for putting type for llm
from qai import QAILLMs

async def plan(model: str,
               llm: QAILLMs,
               objective: Dict,
               base64ss_boxes: str,
# url: str,
# objective_fulfilled: bool,
# steps_taken: Optional[List[Dict]]=None,
# extra_info=None
):
    # Function Call to get Steps
    final_steps_ask = []

    final_steps_ask.append(
        {
            "type": "text",
            "text":f"Objective: {objective}"
        }
    )

    final_steps_ask.append(
        {
            "type": "image_url",
            "image_url": {
                "url": f"data:image/png;base64,{base64ss_boxes}"
            }
        }
    )

    # custom instructions can be added
    # steps taken append
    # ... append

    model = model

    messages = [
        {"role":"system", "content": SYSTEM_PROMPTS.PLAN_STEPS},
        {"role":"user", "content": final_steps_ask}
    ]

    fcs = [{
        "name":"GetPlanSteps",
        "description":"Get Plan Steps for the Objective",
        "parameters": PlanStepsSchema.model_json_schema()
    }]

    response = await llm.openai.llm.__function_call__(
        model,
        messages,
        fcs,
        tool_choice = None,
        max_tokens = 2046
    )

    await asyncio.sleep(1)
    return response