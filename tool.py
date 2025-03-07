import os
import json
from relevanceai import RelevanceAI
from relevanceai.resources.tool import AsyncTool
from relevanceai.types.tool import ToolOutput

def mistakes_detect(text):
    client = RelevanceAI(
        api_key= os.getenv("RAI_API_KEY"),
        region= os.getenv("RAI_REGION"),
        project= os.getenv("RAI_PROJECT")
    )

    tool_ids = [
        "abf7d314-66ee-4b1f-983f-6c1af9a56728",
        "e93d7563-4b56-4de3-bdcf-73f98f312533",
        "5ccfde02-c039-4f85-a53f-544e30b9e784"
    ]

    input_data = text 
    for i in range(3):
        my_tool = client.tools.retrieve_tool(tool_id=tool_ids[i])
        try:
            print(f"Running tool {i+1}...")
            if i == 0:
                response = my_tool.trigger(params={
                    "long_text": input_data
                })
            else:
                # response = my_tool.trigger(params={
                #     "json": json.dumps(input_data)
                # })
                if isinstance(input_data, dict):
                    json_data = json.dumps(input_data)
                else:
                    # If for some reason it's not a dict, try to make it one
                    try:
                        # If it looks like a string that's already JSON
                        if isinstance(input_data, str) and (input_data.startswith('{') or input_data.startswith('[')):
                            json_data = input_data
                        else:
                            json_data = json.dumps({"data": input_data})
                    except Exception as e:
                        print(f"Error preparing JSON: {e}")
                        json_data = json.dumps({"text": str(input_data)})
                
                print(f"Sending JSON to tool {i+1}: {json_data[:100]}...")  # Print first 100 chars for debugging
                response = my_tool.trigger(params={
                    "json": json_data
                })

            print(f"Response type: {type(response)}")
            print(f"Response dir: {dir(response)}")  # This will show all attributes and methods

            input_data = response.output
            response = None
            print(f"Tool {i+1} completed successfully.")

            
        except Exception as e:
            print(f"Error: {e}")

    return input_data


text_file = "extracted_texts/sample_5_languagepoint3_no_comments.txt"
with open(text_file, "r") as file_text:
    text = file_text.read()

res = None
res = mistakes_detect(text)
if res is not None: 
    print("Result: ",res)