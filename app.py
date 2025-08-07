from flask import Flask, render_template, request, jsonify, session
from facebook_business.adobjects.adaccount import AdAccount
import meta_api
import openai_api
import os
import json
from datetime import datetime
from werkzeug.utils import secure_filename

app = Flask(__name__)
# A secret key is required for Flask session management
app.secret_key = os.urandom(24)
app.config['UPLOAD_FOLDER'] = 'uploads'

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
    ai_response_str = openai_api.get_ai_response(user_message, session['history'])

    # Add AI response to history for context in future calls
    session['history'].append({"role": "assistant", "content": ai_response_str})
    session.modified = True

    # Parse the AI's response to decide what to do next
    try:
        ai_response = json.loads(ai_response_str)
        response_type = ai_response.get("type")
        payload = ai_response.get("payload")

        if response_type == "message":
            # Just send the AI's message back to the user
            return jsonify({"type": "message", "payload": payload})

        elif response_type == "function_call":
            # The AI wants to call a function. Store it and ask for confirmation.
            session['pending_action'] = payload
            session.modified = True

            func_name = payload.get("name")
            func_params = payload.get("parameters")

            # Format the parameters for display
            params_str = json.dumps(func_params, indent=2)

            message = (
                f"The AI wants to execute the function `{func_name}` with the following parameters:\n"
                f"```\n{params_str}\n```\n"
                f"Do you approve?"
            )
            return jsonify({"type": "confirmation", "payload": message})

        else:
            return jsonify({"type": "message", "payload": "Error: AI response was not in the expected format."})

    except json.JSONDecodeError:
        return jsonify({"type": "message", "payload": "Error: Failed to decode the AI's response."})
    except Exception as e:
        return jsonify({"type": "message", "payload": f"An unexpected error occurred while processing the AI response: {e}"})


if __name__ == '__main__':
    # Using port 8080 for compatibility with more environments.
    app.run(debug=True, port=8080)

@app.route('/execute', methods=['POST'])
def execute():
    """
    Executes the pending action that the user has confirmed.
    """
    pending_action = session.get('pending_action')
    if not pending_action:
        return jsonify({"type": "message", "payload": "Error: No pending action to execute."})

    func_name = pending_action.get("name")
    params = pending_action.get("parameters", {})

    try:
        meta_api.initialize_api()
        config = meta_api.get_config()
        ad_account_id = config['META_API']['ad_account_id']
        ad_account = AdAccount(ad_account_id)

        result_message = ""

        # This is where we map the function name from the AI to our actual Python functions
        if func_name == "create_campaign":
            campaign = meta_api.create_campaign(ad_account=ad_account, **params)
            if campaign:
                result_message = f"Successfully executed `create_campaign`. New Campaign ID: {campaign['id']}"
            else:
                result_message = "Execution of `create_campaign` failed. Check console for details."

        elif func_name == "create_ad_set":
            # Handle string-to-datetime conversion for start_time
            if 'start_time' in params:
                params['start_time'] = datetime.fromisoformat(params['start_time'])

            ad_set = meta_api.create_ad_set(ad_account=ad_account, **params)
            if ad_set:
                result_message = f"Successfully executed `create_ad_set`. New Ad Set ID: {ad_set['id']}"
            else:
                result_message = "Execution of `create_ad_set` failed. Check console for details."

        elif func_name == "create_ad_creative":
            params['page_id'] = config['META_API']['page_id']
            creative = meta_api.create_ad_creative(ad_account=ad_account, **params)
            if creative:
                result_message = f"Successfully executed `create_ad_creative`. New Creative ID: {creative['id']}"
            else:
                result_message = "Execution of `create_ad_creative` failed. Check console for details."

        elif func_name == "get_campaigns":
            campaigns = meta_api.get_campaigns(ad_account)
            if campaigns is not None:
                # We will return the list directly in the payload for the UI to format
                return jsonify({"type": "list", "payload": campaigns})
            else:
                result_message = "Failed to retrieve campaigns."

        elif func_name == "update_campaign":
            success = meta_api.update_campaign(**params)
            if success:
                result_message = f"Successfully updated campaign {params.get('campaign_id')}."
            else:
                result_message = f"Failed to update campaign {params.get('campaign_id')}."

        elif func_name == "delete_campaign":
            success = meta_api.delete_campaign(**params)
            if success:
                result_message = f"Successfully deleted campaign {params.get('campaign_id')}."
            else:
                result_message = f"Failed to delete campaign {params.get('campaign_id')}."

        elif func_name == "get_insights":
            insights = meta_api.get_insights(**params)
            if insights:
                # Return a special type for the UI to handle
                return jsonify({"type": "insights", "payload": insights})
            else:
                result_message = f"Could not retrieve insights for object {params.get('object_id')}."

        elif func_name == "create_custom_audience_from_emails":
            audience_id = meta_api.create_custom_audience_from_emails(ad_account=ad_account, **params)
            if audience_id:
                result_message = f"Successfully created new custom audience. ID: {audience_id}"
            else:
                result_message = "Failed to create custom audience."

        else:
            result_message = f"Error: Unknown function '{func_name}'."

        # Clear the pending action after execution
        session.pop('pending_action', None)
        session.modified = True

        return jsonify({"type": "message", "payload": result_message})

    except Exception as e:
        return jsonify({"type": "message", "payload": f"An unexpected error occurred during execution: {e}"})

@app.route('/upload', methods=['POST'])
def upload_file():
    if 'file' not in request.files:
        return jsonify({"error": "No file part"}), 400
    file = request.files['file']
    if file.filename == '':
        return jsonify({"error": "No selected file"}), 400
    if file:
        filename = secure_filename(file.filename)
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(filepath)

        try:
            # Initialize API and get ad account
            meta_api.initialize_api()
            config = meta_api.get_config()
            ad_account_id = config['META_API']['ad_account_id']
            ad_account = AdAccount(ad_account_id)

            # Upload image and get hash
            image_hash = meta_api.upload_image(ad_account, filepath)

            # Clean up the uploaded file
            os.remove(filepath)

            if image_hash:
                return jsonify({"type": "image_hash", "payload": image_hash})
            else:
                return jsonify({"error": "Failed to upload image to Meta."}), 500

        except Exception as e:
            # Clean up the file in case of an error
            if os.path.exists(filepath):
                os.remove(filepath)
            return jsonify({"error": str(e)}), 500
