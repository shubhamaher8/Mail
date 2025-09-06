import brevo_python as brevo
import os
from flask import Flask, jsonify, request, render_template
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

BREVO_API_KEY = os.getenv('BREVO_API_KEY')
if not BREVO_API_KEY:
    raise ValueError("Please set the BREVO_API_KEY environment variable.")

configuration = brevo.Configuration()
configuration.api_key['api-key'] = BREVO_API_KEY

api_instance = brevo.TransactionalEmailsApi(brevo.ApiClient(configuration))

# --- Flask Server Setup ---
app = Flask(__name__)

# Define the email sending function
def send_email(recipient_email, recipient_name, subject, html_content):
    """Sends a transactional email using the Brevo API."""
    try:
        # The sender's email must be registered and authenticated in your Brevo account.
        sender_email = "shubhamaher758@gmail.com"
        sender_name = "Amazon"
        
        # Create the email message object
        send_smtp_email = brevo.SendSmtpEmail(
            sender={"name": sender_name, "email": sender_email},
            to=[{"email": recipient_email, "name": recipient_name}],
            subject=subject,
            html_content=html_content
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
@app.route("/send-email", methods=['POST'])
def trigger_email():
    """Endpoint to trigger the email sending process with form data."""
    data = request.form
    recipient_email = data.get('recipient_email')
    recipient_name = data.get('recipient_name')
    subject = data.get('subject')
    html_content = f"<p>{data.get('message')}</p>"
    
    if not all([recipient_email, recipient_name, subject, html_content]):
        return jsonify({"error": "Missing required fields"}), 400
    
    return send_email(recipient_email, recipient_name, subject, html_content)

@app.route("/", methods=['GET'])
def index():
    """A simple index page with an email form."""
    return render_template('index.html')

if __name__ == '__main__':
    # Make sure templates directory is properly set
    app.template_folder = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'templates')
    # Run the Flask app
    app.run(debug=True)
