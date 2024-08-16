# Import (default)
import asyncio
import os

# Recognise the project (to make custom imports)
import sys
sys.path.append('D:\AI-2024-Services\qtp-new')

# Import (custom)
from webtestagent.system_prompts import SYSTEM_PROMPTS
from webtestagent.schemas.objective_schema import ObjectiveSchema

# QAI Import for putting type for llm
from qai import QAILLMs

# Objective Creation Tool
async def objective(
    model: str,
    llm: QAILLMs,
    user_message: str,    
):
    # yield "__OBJECTIVE START__\n"
    await asyncio.sleep(1)
    
    # User message to be shown to GPT
    final_user_message = [] # different media formats like text/image can be appended (simulating an upload if it's an image)
    
    # Part 1 (Text Custom Instruction)
    if user_message:
        final_user_message.append(
            {
                "type":"text",
                "text":f"Custom Instructions : {user_message}"
            }
        )
        
    # Part 2 (Previous Objective Objects)
    # TODO: Append Previous Objectives to final_user_message
    #  ===========================
    #  ===========================
    #  ===========================
    
    # Part 3 (Image)
    # TODO: Append Image to final_user_message
    # final_user_message.append(
    #     {
    #         "type":"image_url",
    #         "image_url": {
    #             "url": f"data:image/png;base64, {base64_ss}"
    #         }
    #     }
    # )
    
    model = model
    
    messages = [{"role":"system",
          "content": SYSTEM_PROMPTS.OBJECTIVE},
         {"role":"user","content":final_user_message}]
    
    fcs = [{
        "name":"GetObjective",
        "description":"Get the Objective Dictionary",
        "parameters": ObjectiveSchema.model_json_schema()
    }]
    
    response = await llm.openai.llm.__function_call__(
        model,
        messages,
        fcs,
        tool_choice = None,
        max_tokens = 2046
    )
        
    # print(f"Response: {response}\n")
    await asyncio.sleep(1)
    # yield "__OBJECTIVE_END__\n"
    return response

# async def main():
#     async for result_part in objective(model="gpt-4o", llm=llm, user_message="I want to test www.google.com"):
#         # print(f"Result Part : {result_part}") # to mark start and end of call eg. __START__, __END__ etc.
#         pass

# asyncio.run(main())
