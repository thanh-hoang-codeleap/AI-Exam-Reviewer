import os
import json
import ast
from relevanceai import RelevanceAI

def mistakes_detect(text: str) -> (dict | None):
    client = RelevanceAI(
        api_key= os.getenv("RAI_API_KEY"),
        region= os.getenv("RAI_REGION"),
        project= os.getenv("RAI_PROJECT")
    )

    tool_ids = [
        "37acd9e8-8a39-4167-b667-1e4696bfbc9e",
        "7c97d71a-3967-4577-b190-7234aa185c09",
        "d5c87002-eda5-4d2d-8b78-3f0966c62312"
    ]
    # Correcting the text
    json_data = mistakes_correction(client, text, tool_ids[0])
    # Identify the mistakes
    json_data_1 = mistakes_identification(client, json_data, tool_ids[1])
    # Analyze the mistakes
    first_json, second_json = mistakes_analysis(client, json_data_1, tool_ids[2])

    return first_json, second_json


def mistakes_correction(client: RelevanceAI, text: str, tool_id: str) -> (dict | None):
    try:
        # Retrive tool
        correction_tool = client.tools.retrieve_tool(tool_id=tool_id)
 
        print("Correcting the text...")
        tool_result = correction_tool.trigger(params={"long_text": text})

        print("Text corrected")

        # Extract output
        if 'to_json_output' in tool_result.output:
            json_data = tool_result.output["to_json_output"]
        if 'corrections' in tool_result.output:
            json_data = tool_result.output["corrections"]
        else:
            json_data = tool_result.output
            
        return json_data
    
    except Exception as e:
        print(f"Error: {e}")


def mistakes_identification(client: RelevanceAI, json_data: str|dict, tool_id: str) -> (dict|None):
    try:
        # Retrive tool
        identification_tool = client.tools.retrieve_tool(tool_id=tool_id)
        print("Identifying mistakes...")

        # Handle based on input type
        if isinstance(json_data, str):
            tool_result = identification_tool.trigger(params={"long_text": json_data})
        else:
            tool_result = identification_tool.trigger(params={"long_text": json.dumps(json_data)})

        print("Mistakes identified")

        # Extract output
        json_data = tool_result.output
        if 'to_json_output' in json_data:
            output_data = json_data["to_json_output"] 
        if 'corrections' in json_data:
            output_data = json_data["corrections"]

        return output_data
    
    except Exception as e:
        print(f"Error: {e}")


def split_json(json_data: str | dict) -> (tuple[dict, dict] | None):
    try:
        # Parse JSON
        if isinstance(json_data, str):
            try:
                parsed_json = json.loads(json_data)
            except json.JSONDecodeError:
                parsed_json = None
                print("Warning: Could not parse JSON string")
        else:
            parsed_json = json_data

        if isinstance(parsed_json, dict) and 'text' in parsed_json:
            data = parsed_json['text']
        else:
            data = parsed_json

        # Split into two halves
        midpoint =  len(data) // 2

        first_half = data[:midpoint]
        second_half = data[midpoint:]

        first_json = {"text": first_half}
        second_json = {"text": second_half}

        return first_json, second_json
    
    except Exception as e:
        print(f"Error: {e}")
    

def mistakes_analysis(client: RelevanceAI, json_data: str|dict, tool_id: str) -> (tuple[list, list] | None):
    try:
        # Retrieve tool
        analysis_tool = client.tools.retrieve_tool(tool_id=tool_id)
        
        # Split the input data into two halves
        first_json, second_json = split_json(json_data)

        if first_json is None or second_json is None:
            print("Error: Failed to split JSON properly.")
            return None, None

        # Process the first half
        print("Processing first half...")
        first_result = analysis_tool.trigger(params={
            "long_text": json.dumps(first_json)
        }).output['to_json_output']['results']

        # Process the second half
        print(f"Processing second half...")
        second_result = analysis_tool.trigger(params={
            "long_text": json.dumps(second_json)
        }).output['to_json_output']['results']

        return first_result, second_result
    
    except Exception as e:
        print(f"Error: {e}")


def process_output(first_result: list, second_result: list) -> list:
    a = ast.literal_eval(first_result)
    b = ast.literal_eval(second_result)
    a.update(b)
    return a