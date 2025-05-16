from flask import Flask, render_template, request, jsonify
import json
import os

app = Flask(__name__)

# Load legal cases from JSON file
with open('legal_data.json', 'r', encoding='utf-8') as f:
    legal_data = json.load(f)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/ask', methods=['POST'])
def ask():
    data = request.json
    query = data.get('query', '').lower()
    language = data.get('language', 'en')
    
    response = {
        'en': "I couldn't find information about that. Try asking about property, divorce, or driving licenses.",
        'hi': "मुझे इस बारे में जानकारी नहीं मिली। संपत्ति, तलाक या ड्राइविंग लाइसेंस के बारे में पूछें।",
        'te': "దాని గురించి నాకు సమాచారం దొరకలేదు. ఆస్తి, డివోర్స్ లేదా డ్రైవింగ్ లైసెన్స్ల గురించి అడగండి."
    }

    for case in legal_data["legal_cases"]:
        if any(keyword.lower() in query for keyword in case["keywords"]):
            response_text = case.get(language) or case.get('answer')
            response = response_text
            break

    return jsonify({'response': response})

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port, debug=True)
