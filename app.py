from flask import Flask, render_template, request, redirect, url_for
import meta_api

app = Flask(__name__)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/create', methods=['POST'])
def create():
    """
    Handles the form submission to create a new campaign.
    """
    # Get form data
    name = request.form.get('name')
    objective = request.form.get('objective')
    status = request.form.get('status')
    message = ""

    try:
        meta_api.initialize_api()
        ad_account = meta_api.get_ad_account()

        # Call the existing function to create the campaign
        campaign = meta_api.create_campaign(
            ad_account=ad_account,
            name=name,
            objective=objective,
            status=status
        )

        if campaign:
            message = f"Successfully created campaign! ID: {campaign['id']}"
        else:
            # The error is already printed to the console by meta_api.py
            message = "Failed to create campaign. Check the application console for error details."

    except FileNotFoundError:
        message = "ERROR: config.ini not found. Please copy config.ini.template to config.ini and fill in your credentials."
    except KeyError as e:
        message = f"ERROR: Missing configuration key: {e}. Please make sure your config.ini file is complete."
    except Exception as e:
        message = f"An unexpected error occurred: {e}"

    return render_template('result.html', message=message)

if __name__ == '__main__':
    # Using port 8080 for compatibility with more environments.
    app.run(debug=True, port=8080)
