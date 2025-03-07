import os
import json
import asyncio
from relevanceai import RelevanceAI


client = RelevanceAI(
    api_key= os.getenv("RAI_API_KEY"),
    region= os.getenv("RAI_REGION"),
    project= os.getenv("RAI_PROJECT")
)

tools = client.tools.list_tools()
print(tools)
# my_tool = client.tools.retrieve_tool(tool_id="a76c3375-88ef-41bf-b344-ac42cb7c6566")
# print(my_tool.get_params_schema())