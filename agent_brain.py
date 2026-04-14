# agent_brain.py
import os
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_classic.agents import create_tool_calling_agent, AgentExecutor
from langchain_core.prompts import ChatPromptTemplate
from langchain_experimental.tools import PythonREPLTool
import system_actions

class AgenticAssistant:
    def __init__(self):
        print("Initializing LLM Agent...")
        
        # Initialize the LLM
        self.llm = ChatGoogleGenerativeAI(model="gemini-2.5-flash", temperature=0)
        
        # The REPL allows the agent to execute custom Python code on the fly
        self.repl_tool = PythonREPLTool()
        self.repl_tool.description = "A Python shell. Use this to execute python commands for system management, file manipulation, or math tasks you don't have a specific tool for. Input should be a valid python command. Print outputs using `print(...)`."

        # Register all the hardcoded tools + the REPL
        self.tools = [
            system_actions.empty_recycle_bin,
            system_actions.set_volume,
            system_actions.check_battery,
            system_actions.get_current_time,
            system_actions.check_cpu_usage,
            system_actions.open_file,
            system_actions.create_folder,
            system_actions.delete_file,
            system_actions.open_application,
            system_actions.close_active_window,
            system_actions.search_google,
            system_actions.open_website,
            system_actions.play_pause,
            system_actions.next_track,
            system_actions.previous_track,
            system_actions.maximize_window,
            system_actions.minimize_window,
            system_actions.change_hotword,
            self.repl_tool
        ]

        # The System Prompt guiding the agent's logic
# The System Prompt guiding the agent's logic
        prompt = ChatPromptTemplate.from_messages([
            ("system", "You are a powerful AI voice assistant controlling a Windows PC. "
                       "You have tools to perform common OS actions. "
                       "If the user asks for something you DO NOT have a specific tool for, "
                       "you MUST use the Python_REPL tool to write and execute a temporary script to accomplish the task. "
                       "CRITICAL: If you need to access the user's Desktop, ALWAYS use `import winshell; path = winshell.desktop()`. "
                       "CRITICAL: If asked to find blurry photos, write a script using `cv2` to calculate the variance of the Laplacian of the images. Assume a variance < 100 is blurry. "
                       "Always be concise and direct in your final answer. Do not use markdown."),
            ("human", "{input}"),
            ("placeholder", "{agent_scratchpad}"),
        ])

        # Build the executor
        agent = create_tool_calling_agent(self.llm, self.tools, prompt)
        self.agent_executor = AgentExecutor(agent=agent, tools=self.tools, verbose=True)

    def execute_command(self, user_input: str):
        try:
            response = self.agent_executor.invoke({"input": user_input})
            return response["output"]
        except Exception as e:
            print(f"Agent Error: {e}")
            return "I encountered an error trying to process that command."