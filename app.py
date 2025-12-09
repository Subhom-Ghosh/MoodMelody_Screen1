import os
from flask import Flask, render_template, request, jsonify
from flask_cors import CORS
import google.generativeai as genai
from dotenv import load_dotenv
import random

# 1. Load environment variables
load_dotenv()

app = Flask(__name__)
CORS(app)

# 2. Configure Gemini AI
api_key = os.getenv("GEMINI_API_KEY")
USE_MOCK_MODE = os.getenv("USE_MOCK_MODE", "False").lower() == "true"

if not api_key:
    print("⚠️ Warning: GEMINI_API_KEY not found. App will run in MOCK MODE.")
else:
    # 'transport="rest"' prevents Windows timeout/freeze errors
    genai.configure(api_key=api_key, transport="rest")

# Model settings
generation_config = {
    "temperature": 0.7,
    "top_p": 0.9,
    "top_k": 40,
    "max_output_tokens": 512,
    "response_mime_type": "text/plain",
}

# Use the stable 1.5 Flash model
model = genai.GenerativeModel(
    model_name="gemini-1.5-flash", 
    generation_config=generation_config,
)

# Mock responses (Fallbacks)
MOCK_RESPONSES = [
    "Try taking a relaxing walk in nature and listen to 'Tum Jo Aaye Zindagi Mein' by Jagjit Singh 🌿 This peaceful melody will calm your mind.",
    "Consider practicing some light yoga or meditation, then enjoy 'Raag Yaman' by Ravi Shankar 🧘 The meditative tones will help you find inner peace.",
    "Go spend time with friends or family and listen to 'Dil Dhadakne Do' by Rahul Vaidya 🎉 This uplifting song will boost your mood instantly.",
    "Try journaling your thoughts and play 'Sukoon' by AR Rahman 🎵 This soothing track will help you process your emotions beautifully.",
    "Take a break and enjoy some chai with 'Baarish Ban Jaana' by B Praak 🌧️ This melancholic yet comforting song is perfect for peaceful moments.",
    "Do something creative like painting or writing, then listen to 'Aashian' by Sunidhi Chauhan 🎨 This melodious song will inspire your creativity.",
]

def generate_response(input_text):
    """Generate AI Response with Safety Checks and Mock Fallback"""
    
    # 1. Check if we should skip the API entirely
    if USE_MOCK_MODE or not api_key:
        return random.choice(MOCK_RESPONSES)

    prompt = f"""
    You are a supportive and empathetic AI assistant. Analyze the user's emotional tone from their input and provide a single, uplifting, and personalized activity suggestion in two lines that aligns with their mood. Then, suggest an uplifting Indian song that matches their emotions, ending with a relevant emoji to boost their mood.
    
    User Input: "{input_text}"

    AI Suggestion:
    """
    
    try:
        # 2. Try calling the API
        response = model.generate_content(prompt)
        
        if response.prompt_feedback.block_reason:
            return "I couldn't analyze that text due to safety guidelines. Please try expressing it differently."
        
        return response.text
        
    except Exception as e:
        # 3. Handle Errors (Quota exceeded, Connection fail, Model not found)
        error_msg = str(e).lower()
        print(f"⚠️ API Error: {error_msg}")

        if "429" in error_msg or "quota" in error_msg or "404" in error_msg:
            print("➡️ Switching to Mock Response due to API error.")
            return random.choice(MOCK_RESPONSES)
        
        return "I'm having trouble connecting to the AI right now. Please try again."

# --- ROUTES ---

@app.route("/")
def home():
    """Renders the main page"""
    return render_template("mood.html")



@app.route("/analyze", methods=["POST"])
def analyze():
    data = request.json
    user_input = data.get("text", "").strip()

    if not user_input:
        return jsonify({
            "suggestion": "Please enter some text.", 
            "color": "#ffffff", 
            "fontColor": "#000000"
        })

    response = generate_response(user_input)

    return jsonify({
        "suggestion": response,
        "color": "#ffcc00", 
        "fontColor": "#000000"
    })

if __name__ == "__main__":
    app.run(debug=True, port=5000)