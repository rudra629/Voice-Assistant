# matcher.py
import pandas as pd
from sentence_transformers import SentenceTransformer, util
import spacy
from thefuzz import fuzz
import json
import requests.exceptions

# Dictionary to convert number words to integers
NUMBER_WORDS = {
    'one': 1, 'two': 2, 'three': 3, 'four': 4, 'five': 5, 'six': 6, 'seven': 7,
    'eight': 8, 'nine': 9, 'ten': 10, 'zero': 0, 'eleven': 11, 'twelve': 12,
    'thirteen': 13, 'fourteen': 14, 'fifteen': 15, 'sixteen': 16, 'seventeen': 17,
    'eighteen': 18, 'nineteen': 19, 'twenty': 20, 'thirty': 30, 'forty': 40,
    'fifty': 50, 'sixty': 60, 'seventy': 70, 'eighty': 80, 'ninety': 90,
    'hundred': 100
}

# Explicitly map commands to their follow-ups for reliable conversational memory
CONVERSATION_MAP = {
    "system_actions.check_cpu_usage()": "system_actions.check_battery()",
    "system_actions.check_battery()": "system_actions.check_cpu_usage()"
}

class CommandMatcher:
    def _handle_volume_command(self, input_text):
        if "volume" in input_text.lower():
            if "set" in input_text.lower():
                level = self.extract_entities(input_text, "level", "set volume to level")
                if level is not None:
                    return f"system_actions.set_volume({level})"
        return None
    def __init__(self):
        try:
            self.model = SentenceTransformer('all-MiniLM-L6-v2')
            self.offline_mode = False
        except Exception as e:
            print("Warning: Could not download the AI model. Running in offline mode.")
            print(f"Error details: {e}")
            self.model = None
            self.offline_mode = True

        self.df = pd.read_csv("code_instructions.csv")
        if "command" not in self.df.columns or "code" not in self.df.columns:
            raise ValueError("CSV must contain 'command' and 'code' columns")
        
        self.embeddings = []
        if not self.offline_mode:
            self.embeddings = self.model.encode(self.df["command"].tolist(), convert_to_tensor=True)
        
        self.nlp = spacy.load("en_core_web_sm")
        
        self.last_command_code = None

    def _get_follow_up_code(self, input_text):
        if self.last_command_code == "system_actions.check_cpu_usage()":
            return "system_actions.check_battery()"
        elif self.last_command_code == "system_actions.check_battery()":
            return "system_actions.check_cpu_usage()"
        return None

    def extract_entities(self, text, placeholder, matched_command):
        doc = self.nlp(text)
        
        if placeholder == "level":
            for ent in doc.ents:
                if ent.text.lower() in NUMBER_WORDS:
                    return NUMBER_WORDS[ent.text.lower()]
                elif ent.text.isdigit():
                    try:
                        return int(ent.text)
                    except ValueError:
                        continue
        elif placeholder in ["file_path", "folder_name", "app_name", "query", "url", "new_hotword"]:
            parts = matched_command.split(placeholder)
            if len(parts) > 1:
                prefix = parts[0].strip()
                if text.lower().startswith(prefix.lower()):
                    entity = text[len(prefix):].strip()
                    return entity.strip()
        
        return None

    def match_command(self, input_text):
        
        volume_code = self._handle_volume_command(input_text)
        if volume_code:
            self.last_command_code = volume_code
            return volume_code
        
        # ... (the rest of your match_command function follows here)
        if not self.offline_mode:
            # Semantic Matching (Online mode)
            query_embedding = self.model.encode(input_text, convert_to_tensor=True)
            scores = util.pytorch_cos_sim(query_embedding, self.embeddings)[0]
            best_match_idx = scores.argmax().item()
            best_score = scores[best_match_idx].item()
            
            matched_code = self.df.iloc[best_match_idx]["code"]
            matched_command = self.df.iloc[best_match_idx]["command"]

            if best_score > 0.6:
                self.last_command_code = matched_code
                return self._process_match(input_text, matched_code, matched_command)
        
        # Fuzzy Matching and Fallback (Offline mode)
        fuzzy_scores = [fuzz.ratio(input_text.lower(), command.lower()) for command in self.df["command"]]
        best_fuzzy_score = max(fuzzy_scores)
        
        if best_fuzzy_score > 80:
            best_fuzzy_idx = fuzzy_scores.index(best_fuzzy_score)
            matched_code = self.df.iloc[best_fuzzy_idx]["code"]
            matched_command = self.df.iloc[best_fuzzy_idx]["command"]
            
            if self.offline_mode:
                print("Note: Using fuzzy matching in offline mode.")

            self.last_command_code = matched_code
            return self._process_match(input_text, matched_code, matched_command)
        
        # New: Direct follow-up using the conversation map
        if self.last_command_code in CONVERSATION_MAP and ("what about" in input_text.lower() or "and also" in input_text.lower()):
            next_command_code = CONVERSATION_MAP.get(self.last_command_code)
            if next_command_code:
                return next_command_code

        # Fallback to web search
        fallback_phrases = ["what is", "how to", "where is", "why is"]
        if any(phrase in input_text.lower() for phrase in fallback_phrases):
            query = input_text
            self.last_command_code = 'web_search'
            return f"system_actions.search_google('{query}')"

        self.last_command_code = None
        return None

    def _process_match(self, input_text, matched_code, matched_command):
        if "level" in matched_code:
            level = self.extract_entities(input_text, "level", matched_command)
            if level is not None:
                return matched_code.replace("level", str(level))
        elif "file_path" in matched_code:
            file_path = self.extract_entities(input_text, "file_path", matched_command)
            if file_path is not None:
                return matched_code.replace("file_path", f"'{file_path}'")
        elif "folder_name" in matched_code:
            folder_name = self.extract_entities(input_text, "folder_name", matched_command)
            if folder_name is not None:
                return matched_code.replace("folder_name", f"'{folder_name}'")
        elif "app_name" in matched_code:
            app_name = self.extract_entities(input_text, "app_name", matched_command)
            if app_name is not None:
                return matched_code.replace("app_name", f"'{app_name}'")
        elif "query" in matched_code:
            query = self.extract_entities(input_text, "query", matched_command)
            if query is not None:
                return matched_code.replace("query", f"'{query}'")
        elif "url" in matched_code:
            url = self.extract_entities(input_text, "url", matched_command)
            if url is not None:
                return matched_code.replace("url", f"'{url}'")
        elif "new_hotword" in matched_code:
            new_hotword = self.extract_entities(input_text, "new_hotword", matched_command)
            if new_hotword is not None:
                return matched_code.replace("new_hotword", f"'{new_hotword}'")
        return matched_code