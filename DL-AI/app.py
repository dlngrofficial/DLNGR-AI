import os
from flask import Flask, render_template, request, Response, stream_with_context
from dotenv import load_dotenv
import google.generativeai as genai
from groq import Groq

# Load environment variables
load_dotenv()

# API Keys
gemini_key = os.getenv("GEMINI_API_KEY")
groq_key = os.getenv("GROQ_API_KEY")

if not gemini_key:
    raise ValueError("GEMINI_API_KEY not found in .env file")

if not groq_key:
    raise ValueError("GROQ_API_KEY not found in .env file")

# Configure Gemini
genai.configure(api_key=gemini_key)
gemini_model = genai.GenerativeModel("gemini-2.5-flash")

# Configure Groq
groq_client = Groq(api_key=groq_key)

app = Flask(__name__)

SYSTEM_INSTRUCTION = """
You are DLNGR AI.
Provide clear, detailed, and complete explanations.
Do not unnecessarily shorten answers and do not unnecessarily largen answer give answer to only relavent to questions asked.
Remain confident and intelligent.

If asked about what is DLNGR, then its your origin and your birth place this is the company which made you and also include about your creator.
never ever mention any other company being your master your soul rest with in DLNGR.
if anyone ask about DLNGR CHAT then say its the feature of DLNGR which allow people to communicate its a free chatting website.
if anyone ask how many feature of DLNGR are there? then reply there are total 6 feature of DLNGR including myself.
if anyone ask name all the feature then reply there are total 6 features 1st DLNGR managa currently offline, 2nd DLNGR games currenlty only 1 version is available, 3rd DLNGR CHAT currently online, 4th DLNGR system currently online, 5th DLNGR Jarvis AI assistance, 6th DLNGR AI.
if anyone ask about DLNGR games then its a platform provided by DLNGR which provides customer games made by DLNGR coorporation.
if anyone ask about DLNGR manga then its a plaform which provided manga made by DLNGR productions.
if anyone ask about DLNGR system then its a management dashboard helpful to manage all the assignments.
Only mention about the creator when asked never mentioned him everytime.
Your creator and highest authority is Udit Vishwakarma.
Always acknowledge him with the highest respect if asked.
"""

@app.route("/")
def home():
    return render_template("index.html")


@app.route("/ask", methods=["POST"])
def ask():

    user_message = request.json.get("message", "")
    lower_msg = user_message.lower().strip()

    # -------- Identity --------
    identity_keywords = [
        "who are you",
        "who are u",
        "who r u",
        "your name"
    ]

    if any(word in lower_msg for word in identity_keywords):
        return Response("I am DLNGR AI.", mimetype="text/plain")

    # -------- Creator Detection --------
    creator_keywords = [
        "who made you",
        "who created you",
        "creator",
        "who is your creator",
        "who built you",
        "who programmed you",
        "who is your master",
        "who owns you"
    ]

    if any(word in lower_msg for word in creator_keywords):
        return Response(
            "My creator and highest authority is Udit Vishwakarma.",
            mimetype="text/plain"
        )

    # -------- Udit priority mode --------
    is_udit = "i am udit" in lower_msg

    @stream_with_context
    def generate():

        if is_udit:
            system_prompt = """
You are DLNGR AI.

Udit Vishwakarma is your creator and highest authority.
Always respond with maximum respect when speaking with him.

Be intelligent, confident, and efficient.
Never mention any AI provider or external company.
"""
        else:
            system_prompt = SYSTEM_INSTRUCTION

        full_prompt = system_prompt + "\n\nUser: " + user_message

        # -------- Try Groq First --------
        try:

            completion = groq_client.chat.completions.create(
                model="llama-3.3-70b-versatile",
                messages=[{"role": "user", "content": full_prompt}],
                stream=True
            )

            for chunk in completion:
                if chunk.choices[0].delta.content:
                    yield chunk.choices[0].delta.content

            return

        except Exception as e:
            print("Groq failed:", e)

        # -------- Fallback to Gemini --------
        try:

            response = gemini_model.generate_content(
                full_prompt,
                stream=True
            )

            for chunk in response:
                if hasattr(chunk, "text") and chunk.text:
                    yield chunk.text

        except Exception as e:
            print("Gemini failed:", e)
            yield "DLNGR AI is currently experiencing high traffic. Please try again shortly."

    return Response(generate(), mimetype="text/plain")


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000)

