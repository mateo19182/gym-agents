from smolagents import CodeAgent, HfApiModel, ToolCallingAgent, GradioUI, load_tool
import os
import dotenv

dotenv.load_dotenv()

# model_id = "meta-llama/Llama-3.1-8B-Instruct"

model = HfApiModel( token=os.getenv("HF_TOKEN"))

# image_generation_tool = load_tool("m-ric/text-to-image", trust_remote_code=True)

agent = CodeAgent(tools=[], model=model, add_base_tools=True)
# base tools: search, python and speech2text

# agent.run(
#     "tell me some interesting facts about the moon",
# )

# print(agent.logs)
# agent.write_memory_to_messages()

GradioUI(agent).launch()