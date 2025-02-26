import os
import sqlite3
from datetime import datetime

import tweepy
from google import genai

DB_FILE = "radio_names.db"

# Radio name bot Error
class RadioNameBotError(Exception):
    pass

# Get Environment Variable
def get_env_variable(var_name: str) -> str:
    value = os.environ.get(var_name, "").strip()
    if not value:
        raise ValueError(f"Environment variable '{var_name}' is not set or empty.")
    return value

# Generate radio name
def gen_radio_name(api_key: str, db_file: str = "radio_names.db", prompt_txt_file: str = "prompt.txt") -> str:    
    past_radio_names = get_all_radio_names(db_file)
    try:
        prompt = get_prompt(past_radio_names, prompt_txt_file)

        return send_request_to_gemini_api(
            api_key=api_key,
            prompt=prompt
        )
    except Exception as e:
        raise RadioNameBotError(f"Failed to generate radio name: {e}")

# get prompt from textfile
def get_prompt(past_radio_names: list, prompt_txt_file: str = "prompt.txt") -> str:
    try:
        with open(prompt_txt_file, "r") as f:
            return f"{f.read()}{",".join(past_radio_names)}"
    except FileNotFoundError:
        raise RadioNameBotError(f"File '{prompt_txt_file}' not found.")

# Send request to Google Gemini API
def send_request_to_gemini_api(api_key: str, prompt: str) -> str:
    try:
        client = genai.Client(api_key=api_key)
        response = client.models.generate_content(
            model="gemini-2.0-flash",
            contents=[prompt]
        )
        return response.text
    except Exception as e:
        raise RadioNameBotError(f"Failed to send request to Gemini API: {e}")

# Get past thought radio names from Sqlite3
def get_all_radio_names(db_file: str) -> list:
    conn = None
    try:
        with sqlite3.connect(db_file) as conn:
            c = conn.cursor()
            c.execute("SELECT name FROM radio_names")
            return [name[0] for name in c.fetchall()]
    except sqlite3.Error as e:
        raise RadioNameBotError(f"Failed to fetch radio names from SQLite: {e}")

# Insert radio name to Sqlite3
def insert_radio_name(db_file: str, name: str):
    conn = None
    try:
        with sqlite3.connect(db_file) as conn:
            c = conn.cursor()
            c.execute("INSERT INTO radio_names (name) VALUES (?)", (name,))
            conn.commit()
    except sqlite3.Error as e:
        raise RadioNameBotError(f"Failed to insert radio name to Sqlite3: {e}")

def post_tweet(radio_name: str):
    try:
        client = tweepy.Client(
            consumer_key=X_API_KEY,
            consumer_secret=X_API_KEY_SECRET,
            access_token=X_ACCESS_TOKEN,
            access_token_secret=X_ACCESS_TOKEN_SECRET
        )
        client.create_tweet(text=radio_name)
    except Exception as e:
        raise RadioNameBotError(f"Failed to post tweet: {e}")
    
def print_log(log_level: str, log: str):
    valid_levels = {"INFO", "ERROR", "DEBUG", "WARNING"}
    if log_level not in valid_levels:
        raise ValueError(f"Invalid log level: {log_level}")
    
    print(f"{datetime.now()} [{log_level}] {log}")

# get API Key from Enviroment Variable
try:
    # get Gemini API Key from Enviroment Variable
    GEMINI_API_KEY = get_env_variable("GEMINI_API_KEY")

    # get X API Key from Enviroment Variable
    X_API_KEY = get_env_variable("X_API_KEY")
    X_API_KEY_SECRET = get_env_variable("X_API_KEY_SECRET")
    X_ACCESS_TOKEN = get_env_variable("X_ACCESS_TOKEN")
    X_ACCESS_TOKEN_SECRET = get_env_variable("X_ACCESS_TOKEN_SECRET")
except ValueError as e:
    print(f"{datetime.now()} [ERROR] {e}")
    print_log("ERROR", e)
    exit(1)
    
if __name__ == "__main__":
    try:
        generated_radio_name = gen_radio_name(GEMINI_API_KEY)
        print_log("INFO", f"Generated radio name: {generated_radio_name}")

        insert_radio_name(DB_FILE, generated_radio_name)
        post_tweet(generated_radio_name)
        print_log("INFO", f"Posted radio name: {generated_radio_name}")
    except RadioNameBotError as e:
        print_log("ERROR", e)
        exit(1)
