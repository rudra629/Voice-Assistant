# # gemini_agent.py
# import google.generativeai as genai

# genai.configure(api_key="AIzaSyCxtnv1EJBTrYH-7IHm_WY-YTWbXoKevP0")

# model = genai.GenerativeModel("gemini-2.5-pro")

# def get_code_from_gemini(command):
#     prompt = f"""
# You are a helpful PC assistant. Convert the following natural language command into executable Python code that automates tasks on a Windows PC.

# Command: "{command}"

# Reply ONLY with Python code. No explanation or markdown.
# """

#     response = model.generate_content(prompt)
#     return response.text.strip()
