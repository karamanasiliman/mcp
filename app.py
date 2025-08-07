from flask import Flask, render_template, request, jsonify, session
from facebook_business.adobjects.adaccount import AdAccount
import meta_api
import openai_api
import os

app = Flask(__name__)
# A secret key is required for Flask session management
app.secret_key = os.urandom(24)

@app.route('/')
def index():
    # Clear session history when the user loads the page
    session.clear()
    return render_template('chat.html')

@app.route('/chat', methods=['POST'])
def chat():
    user_message = request.json.get('message')
    if 'history' not in session:
        session['history'] = []

    # Add user message to history
    session['history'].append({"role": "user", "content": user_message})

    # Get AI response
    # Note: The real implementation will call the actual OpenAI API
    ai_response_json = openai_api.get_ai_response(user_message, session['history'])

    # Add AI response to history
    # The real implementation will need to parse the JSON and store it correctly
    session['history'].append({"role": "assistant", "content": ai_response_json})

    # Ensure the session is saved
    session.modified = True

    return jsonify(ai_response_json)


if __name__ == '__main__':
    # Using port 8080 for compatibility with more environments.
    app.run(debug=True, port=8080)
