from email.message import EmailMessage
from email.header import decode_header
from email import message_from_bytes
from dotenv import load_dotenv
import imapclient
import smtplib
import random
import openai
import time
import os

load_dotenv()

VENDORS = {
    "DHL": "dhl@example.com",
    "FedEx": "fedex@example.com",
    "XPO": "xpo@example.com"
}

openai.api_key = os.getenv("OPENAI_KEY")

def simulate_send_email_to_all_vendor(data):
    vendors = ["DHL", "XPO", "FreightQuote"]
    return [
        {"vendor": v, "rate": round(random.uniform(300, 800), 2)}
        for v in vendors
    ]

def send_email_to_all_vendors(data, timeout_minutes=10):
    # Step 1: Send quote requests
    for name, email in VENDORS.items():
        send_email_vendor(data, email, name)
        print(f"📨 Sent email to {name} ({email})")

    # Step 2: Wait for replies
    print("⏳ Waiting for vendor replies...")
    start = time.time()
    received = {}
    while time.time() - start < timeout_minutes * 60:
        emails = fetch_unread_vendor_emails()
        for email in emails:
            parsed = parse_vendor_email(email["body"])
            if parsed and 'vendor_name' in parsed:
                name = parsed["vendor_name"]
                if name not in received:
                    received[name] = parsed
                    print(f"✅ Parsed reply from {name}")
        if len(received) >= len(VENDORS):
            break
        time.sleep(30)

    print(f"📦 Got replies from {len(received)} vendor(s)")
    return list(received.values())

def send_email_vendor(data, vendor_email, vendor_name):
    msg = EmailMessage()
    msg["Subject"] = f"Freight Quote Request – {data['origin']} to {data['destination']}"
    msg["From"] = os.getenv("EMAIL_USER")  # Your company email
    msg["To"] = vendor_email

    body = f"""Dear {vendor_name},

        We are requesting a freight quote for the following shipment:

        • Origin: {data['origin']}
        • Destination: {data['destination']}
        • Weight: {data['weight']} kg
        • Freight Class: {data['freight_class']}
        • Mode: {data['mode']}
        • Cargo Description:
        {data.get('description', 'N/A')}

        Please respond with your best rate, service type, and estimated transit days.

        Best regards,  
        AMZ Prep Philippines
        """
    msg.set_content(body)

    with smtplib.SMTP_SSL("smtp.gmail.com", 465) as smtp:
        smtp.login(os.getenv("EMAIL_USER"), os.getenv("EMAIL_PASS"))
        smtp.send_message(msg)
    pass

def decode_mime_words(s):
    """Decode MIME-encoded words (e.g., =?utf-8?q?...?=)."""
    decoded = decode_header(s)
    return ''.join(
        str(part, encoding or 'utf-8') if isinstance(part, bytes) else part
        for part, encoding in decoded
    )

def fetch_unread_vendor_emails():
    USER = os.getenv("EMAIL_USER")
    PASS = os.getenv("EMAIL_PASS")

    with imapclient.IMAPClient("imap.gmail.com", ssl=True) as client:
        client.login(USER, PASS)
        client.select_folder("INBOX", readonly=True)

        messages = client.search(['UNSEEN', 'SUBJECT "Freight Quote Request"'])
        emails = []

        for uid in messages:
            raw_data = client.fetch([uid], ['BODY[]'])
            raw_msg = raw_data[uid][b'BODY[]']
            msg = message_from_bytes(raw_msg)

            # Get From address
            from_addr = msg.get("From")
            if from_addr:
                from_addr = decode_mime_words(from_addr)

            # Get Subject
            subject = msg.get("Subject")
            if subject:
                subject = decode_mime_words(subject)

            # Extract message body
            body = ""
            if msg.is_multipart():
                for part in msg.walk():
                    content_type = part.get_content_type()
                    if content_type == "text/plain" and not part.get("Content-Disposition"):
                        charset = part.get_content_charset() or 'utf-8'
                        try:
                            body = part.get_payload(decode=True).decode(charset, errors='replace')
                            break
                        except:
                            pass
            else:
                charset = msg.get_content_charset() or 'utf-8'
                body = msg.get_payload(decode=True).decode(charset, errors='replace')

            emails.append({
                "from": from_addr,
                "subject": subject,
                "body": body.strip()
            })

        return emails
    
def parse_vendor_email(text):
    prompt = f"""
Extract the freight quote details from the email below. Return JSON with:
- vendor_name
- quoted_rate (in PHP)
- service_type (e.g., Express, Economy)
- estimated_days (transit time in days)

Email:
{text}
"""
    response = openai.ChatCompletion.create(
        model="gpt-4",
        messages=[
            {"role": "system", "content": "You extract structured data from logistics emails."},
            {"role": "user", "content": prompt}
        ],
        temperature=0.3
    )

    try:
        return eval(response['choices'][0]['message']['content'])  # OR use json.loads if JSON
    except Exception as e:
        return {"error": "Failed to parse vendor reply", "details": str(e)}
    
def wait_for_vendor_reply_and_parse(timeout_minutes=10):
    print("⏳ Waiting for vendor reply...")

    start = time.time()
    while time.time() - start < timeout_minutes * 60:
        emails = fetch_unread_vendor_emails()
        if emails:
            print(f"📩 Received {len(emails)} reply(ies). Parsing first one...")
            return parse_vendor_email(emails[0]["body"])
        time.sleep(30)  # wait 30 seconds before checking again

    print("❌ Timeout: No reply received.")
    return None