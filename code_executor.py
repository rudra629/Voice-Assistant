# code_executor.py
import system_actions

def execute_code(code_string):
    safe_globals = {'system_actions': system_actions} 
    try:
        exec(code_string, safe_globals)
    except Exception as e:
        print(f"Error while executing code: {e}")