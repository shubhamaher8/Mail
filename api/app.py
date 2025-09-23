import brevo_python as brevo
import os
from flask import Flask, jsonify, request, render_template
from flask_cors import CORS # Import CORS
from dotenv import load_dotenv
from twilio.rest import Client

# Load environment variables
load_dotenv()

# --- Brevo Setup ---
BREVO_API_KEY = os.getenv('BREVO_API_KEY')
if not BREVO_API_KEY:
    raise ValueError("Please set the BREVO_API_KEY environment variable.")
configuration = brevo.Configuration()
configuration.api_key['api-key'] = BREVO_API_KEY
api_instance = brevo.TransactionalEmailsApi(brevo.ApiClient(configuration))

# --- Twilio Setup ---
TWILIO_ACCOUNT_SID = os.getenv("TWILIO_ACCOUNT_SID")
TWILIO_AUTH_TOKEN = os.getenv("TWILIO_AUTH_TOKEN")
TWILIO_PHONE_NUMBER = os.getenv("TWILIO_PHONE_NUMBER")
twilio_client = None
if all([TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN, TWILIO_PHONE_NUMBER]):
    twilio_client = Client(TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN)
else:
    print("⚠️ Warning: Twilio environment variables not set. SMS functionality will not work.")

# --- Flask Setup ---
app = Flask(__name__)
CORS(app) # Enable CORS for all routes

# --- Helper Functions (send_email and send_sms are unchanged) ---
def send_email(recipients, subject, html_content):
    # This function remains the same
    results = []
    sender_email = "dchitale07@gmail.com"
    sender_name = "Test Sender"
    for r in recipients:
        try:
            send_smtp_email = brevo.SendSmtpEmail(
                sender={"name": sender_name, "email": sender_email},
                to=[{"email": r["email"], "name": r.get("name", "")}],
                subject=subject,
                html_content=html_content
            )
            api_instance.send_transac_email(send_smtp_email)
            results.append({"email": r["email"], "status": "sent"})
        except Exception as e:
            results.append({"email": r["email"], "status": "failed", "error": str(e)})
    return results

def send_sms(recipient_numbers, message):
    # This function remains the same
    if not twilio_client:
        raise ConnectionError("Twilio client is not configured. Check environment variables.")
    results = []
    for number in recipient_numbers:
        try:
            msg = twilio_client.messages.create(body=message, from_=TWILIO_PHONE_NUMBER, to=number)
            results.append({"number": number, "status": "sent", "sid": msg.sid})
        except Exception as e:
            results.append({"number": number, "status": "failed", "error": str(e)})
    return results

# --- Page Rendering Routes ---

@app.route("/", methods=['GET'])
def email_sender_page():
    return render_template('email.html')

@app.route("/sms", methods=['GET'])
def sms_sender_page():
    return render_template('sms.html')

@app.route("/emailtxt", methods=['GET'])
def email_text_template_page():
    return render_template('emailtxt.html')

@app.route("/smstxt", methods=['GET'])
def smstxt_page():
    return render_template('smstxt.html')

# --- UPDATED API Routes ---
@app.route("/send-email", methods=['POST'])
def trigger_email():
    try:
        # Get data from the JSON body of the request
        data = request.get_json()
        recipients = data.get("recipients")
        subject = data.get("subject")
        message = data.get("message")

        if not all([recipients, subject, message]) or not isinstance(recipients, list):
            return jsonify({"error": "Invalid payload. 'recipients' (list), 'subject', and 'message' are required."}), 400

        html_content = message
        results = send_email(recipients, subject, html_content)
        
        failed = [res for res in results if res['status'] == 'failed']
        if failed:
            return jsonify({"error": f"Failed to send to: {', '.join([f['email'] for f in failed])}"}), 500
        return jsonify({"message": f"Successfully sent email to {len(recipients)} recipient(s)."}), 200
    except Exception as e:
        return jsonify({"error": "An internal server error occurred."}), 500

@app.route("/send-sms", methods=['POST'])
def trigger_sms():
    try:
        # Get data from the JSON body of the request
        data = request.get_json()
        recipient_numbers = data.get("recipient_numbers")
        message = data.get("message")

        if not all([recipient_numbers, message]) or not isinstance(recipient_numbers, list):
            return jsonify({"error": "Invalid payload. 'recipient_numbers' (list) and 'message' are required."}), 400

        results = send_sms(recipient_numbers, message)

        failed = [res for res in results if res['status'] == 'failed']
        if failed:
            return jsonify({"error": f"Failed to send to: {', '.join([f['number'] for f in failed])}"}), 500
        return jsonify({"message": f"Successfully sent SMS to {len(recipient_numbers)} number(s)."}), 200
    except ConnectionError as e:
        return jsonify({"error": str(e)}), 500
    except Exception as e:
        return jsonify({"error": "An internal server error occurred."}), 500

# --- Run ---
if __name__ == '__main__':
    app.template_folder = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'templates')
    app.run(debug=True)