import brevo_python as brevo
import os
from flask import Flask, jsonify

BREVO_API_KEY = os.getenv('BREVO_API_KEY')
if not BREVO_API_KEY:
    raise ValueError("Please set the BREVO_API_KEY environment variable.")

configuration = brevo.Configuration()
configuration.api_key['api-key'] = BREVO_API_KEY

api_instance = brevo.TransactionalEmailsApi(brevo.ApiClient(configuration))

# --- Flask Server Setup ---
app = Flask(__name__)

# Define the email sending function
def send_email():
    """Sends a transactional email using the Brevo API."""
    try:
        # The sender's email must be registered and authenticated in your Brevo account.
        sender_email = "shubhamaher758@gmail.com"
        sender_name = "Shubham"
        recipient_email = "shubhamaher909090@gmail.com"
        recipient_name = "Receiver"
        
        # Create the email message object
        send_smtp_email = brevo.SendSmtpEmail(
            sender={"name": sender_name, "email": sender_email},
            to=[{"email": recipient_email, "name": recipient_name}],
            subject="Brevo API Test Message",
            html_content="<p>Hi,</p><p>This is a test message from your Flask server using the Brevo API.</p>"
        )
        
        # Call the API to send the email
        api_instance.send_transac_email(send_smtp_email)
        
        return jsonify({"message": "Email sent successfully!"}), 200
    except brevo.ApiException as e:
        print("Exception when calling TransactionalEmailsApi->send_transac_email: %s\n" % e)
        return jsonify({"error": "Failed to send email. Check server logs."}), 500
    except Exception as e:
        print(f"An unexpected error occurred: {e}")
        return jsonify({"error": "An unexpected error occurred."}), 500

# --- Flask Routes ---
@app.route("/send-email", methods=['GET'])
def trigger_email():
    """Endpoint to trigger the email sending process."""
    return send_email()

@app.route("/", methods=['GET'])
def index():
    """A simple index page."""
    return "<h1>Brevo Email Sender</h1><p>Navigate to /send-email to send a test message.</p>"

if __name__ == '__main__':
    # Run the Flask app
    app.run(debug=True)
