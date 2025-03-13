import os
import json
from relevanceai import RelevanceAI

def mistakes_detect(text: str) -> (dict | None):
    client = RelevanceAI(
        api_key= os.getenv("RAI_API_KEY"),
        region= os.getenv("RAI_REGION"),
        project= os.getenv("RAI_PROJECT")
    )

    tool_ids = [
        "8949c2fb-d5e7-4893-a55e-6c65a10921bc",
        "b96bf2d9-13ab-4359-aa23-5e6c6ff56dbc",
        "bf893971-7786-4476-906d-3fbbc0813f43",
        "442760c3-092e-4b58-bc81-289c069021f5"
    ]

    input_data = text 
    try:
        my_tool_1 = client.tools.retrieve_tool(tool_id=tool_ids[0])
        my_tool_2 = client.tools.retrieve_tool(tool_id=tool_ids[1])
        my_tool_3 = client.tools.retrieve_tool(tool_id=tool_ids[2])
        my_tool_4 = client.tools.retrieve_tool(tool_id=tool_ids[3])

        # First get the output from tool 1
        print("Correcting the text...")
        tool1_result = my_tool_1.trigger(params={"long_text": input_data})

        print("Text corrected")
        # Extract the JSON data properly 
        if 'to_json_output' in tool1_result.output:
            json_data = tool1_result.output["to_json_output"]
        if 'corrections' in tool1_result.output:
            json_data = tool1_result.output["corrections"]
        else:
            json_data = tool1_result.output

        print("Identifying mistakes...")
        if isinstance(json_data, str):
            tool2_result = my_tool_2.trigger(params={"long_text": json_data})
        else:
            tool2_result = my_tool_2.trigger(params={"long_text": json.dumps(json_data)})

        print("Mistakes identified")

        if 'to_json_output' in tool2_result.output:
            json_data = tool2_result.output["to_json_output"]
        if 'corrections' in tool2_result.output:
            json_data = tool2_result.output["corrections"]
        else:
            json_data = tool2_result.output

        if isinstance(json_data, str):
            try:
                parsed_json = json.loads(json_data)
            except json.JSONDecodeError:
                parsed_json = None
                print("Warning: Could not parse JSON string")
        else:
            parsed_json = json_data

        print("Analyzing the mistakes...")
        # Process based on size
        if parsed_json and isinstance(parsed_json, dict) and len(parsed_json) > 7000:
            print(f"Large JSON detected with {len(parsed_json)} items. Splitting for processing.")
            
            # Split the list into two halves
            mid_point = len(parsed_json) // 2
            first_half = parsed_json[:mid_point]
            second_half = parsed_json[mid_point:]
            
            # Process first half
            print(f"Processing first half ({len(first_half)} items)")
            first_half_json = json.dumps(first_half)
            first_result = my_tool_3.trigger(params={"long_text": first_half_json}).output
            if not isinstance(first_result, str):
                first_result = json.dumps(first_result)
            
            # Process second half
            print(f"Processing second half ({len(second_half)} items)")
            second_half_json = json.dumps(second_half)
            second_result = my_tool_3.trigger(params={"long_text": second_half_json}).output
            if not isinstance(second_result, str):
                second_result = json.dumps(second_result)

            response = my_tool_4.trigger(params={
                "long_text": first_result,
                "long_text_1": second_result
            })
        else:
            # Original processing for smaller JSON data
            if parsed_json is None:
                print("Error: parsed_json is None")
            if isinstance(parsed_json, str):
                response = my_tool_3.trigger(params={"long_text": parsed_json})
            else:
                print('go dump')
                json_string = json.dumps(parsed_json)
                response = my_tool_3.trigger(params={"long_text": json.dumps(json_string)})
        print("Mistakes analyzed")
        result = response.output

        print("Processing response")
        if 'to_json_output' in result:
            result = result["to_json_output"]
        if 'text' in result:
            result = result["text"]
        if 'results' in result:
            result = result["results"]
        else:
            result = response.output

        print(result)

        if isinstance(result, str):
            try:
                result = json.loads(result)
            except json.JSONDecodeError:
                result = None
                print("Warning: Could not parse JSON string")

        print(type(result))

        return result
        
    except Exception as e:
        print(f"Error: {e}")
    # for i in range(3):
    #     my_tool = client.tools.retrieve_tool(tool_id=tool_ids[i])
    #     try:
    #         print(f"Running tool {i+1}...")
    #         if i == 0:
    #             response = my_tool.trigger(params={
    #                 "long_text": input_data
    #             })
    #         else:
    #             # response = my_tool.trigger(params={
    #             #     "json": json.dumps(input_data)
    #             # })
    #             if isinstance(input_data, dict):
    #                 json_data = json.dumps(input_data)
    #             else:
    #                 # If for some reason it's not a dict, try to make it one
    #                 try:
    #                     # If it looks like a string that's already JSON
    #                     if isinstance(input_data, str) and (input_data.startswith('{') or input_data.startswith('[')):
    #                         json_data = input_data
    #                     else:
    #                         json_data = json.dumps({"data": input_data})
    #                 except Exception as e:
    #                     print(f"Error preparing JSON: {e}")
    #                     json_data = json.dumps({"text": str(input_data)})
                
    #             print(f"Sending JSON to tool {i+1}: {json_data[:100]}...")  # Print first 100 chars for debugging
    #             response = my_tool.trigger(params={
    #                 "json": json_data
    #             })

    #         print(f"Response type: {type(response)}")
    #         print(f"Response dir: {dir(response)}")  # This will show all attributes and methods

    #         input_data = response.output
    #         response = None
    #         print(f"Tool {i+1} completed successfully.")

            
    #     except Exception as e:
    #         print(f"Error: {e}")


# text_file = "extracted_texts/sample_5_languagepoint3_no_comments.txt"
# with open(text_file, "r") as file_text:
#     text = file_text.read()

# res = None
# res = mistakes_detect(text)
# print(f"Result: {res}")