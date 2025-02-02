from flask import Flask, render_template, request, jsonify, send_file
from datetime import datetime
import sqlite3
import uuid
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import os

app = Flask(__name__)

# Email Configuration
SMTP_SERVER = "smtp.gmail.com"
SMTP_PORT = 587
SMTP_USERNAME = "thanusha314@gmail.com"  # Replace with your email
SMTP_PASSWORD = "sxectyzaoygclsnn"  # Use an App Password
BASE_URL = "http://localhost:5000"  # Change to your public domain if needed

# Initialize Database
def init_db():
    conn = sqlite3.connect('emails.db')
    c = conn.cursor()
    c.execute('''
        CREATE TABLE IF NOT EXISTS emails (
            id TEXT PRIMARY KEY,
            subject TEXT,
            recipient TEXT,
            sent_time TEXT,
            delivered_time TEXT,
            opened_time TEXT,
            tracking_pixel TEXT
        )
    ''')
    conn.commit()
    conn.close()

# Create Email Content with Tracking Pixel
def create_html_email(subject, content, tracking_pixel):
    return f"""
    <!DOCTYPE html>
    <html>
    <head>
        <style>
            body {{ font-family: Arial, sans-serif; line-height: 1.6; }}
            .container {{ padding: 20px; }}
        </style>
    </head>
    <body>
        <div class="container">
            <h2>{subject}</h2>
            <div>{content}</div>
            <img src="{BASE_URL}/track/{tracking_pixel}" width="1" height="1" style="display:none;">
        </div>
    </body>
    </html>
    """

# Send Email to Multiple Recipients
def send_email(recipients, subject, content):
    try:
        recipients_list = recipients.split(",")  # Split multiple emails
        success_list = []
        
        for recipient in recipients_list:
            recipient = recipient.strip()
            email_id = str(uuid.uuid4())  # Unique email ID
            tracking_pixel = str(uuid.uuid4())  # Unique tracking ID
            sent_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

            # Save email log **before** sending to ensure sent_time is recorded
            conn = sqlite3.connect('emails.db')
            c = conn.cursor()
            c.execute('''
                INSERT INTO emails (id, subject, recipient, sent_time, delivered_time, tracking_pixel)
                VALUES (?, ?, ?, ?, ?, ?)
            ''', (email_id, subject, recipient, sent_time, None, tracking_pixel))
            conn.commit()
            conn.close()

            # Compose Email
            msg = MIMEMultipart('alternative')
            msg['Subject'] = subject
            msg['From'] = SMTP_USERNAME
            msg['To'] = recipient

            html_content = create_html_email(subject, content, tracking_pixel)
            msg.attach(MIMEText(html_content, 'html'))

            # Send Email via SMTP
            with smtplib.SMTP(SMTP_SERVER, SMTP_PORT) as server:
                server.starttls()
                server.login(SMTP_USERNAME, SMTP_PASSWORD)
                server.send_message(msg)

            # If email is sent successfully, update delivered_time
            delivered_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            conn = sqlite3.connect('emails.db')
            c = conn.cursor()
            c.execute('''
                UPDATE emails SET delivered_time = ? WHERE id = ?
            ''', (delivered_time, email_id))
            conn.commit()
            conn.close()

            success_list.append(recipient)

        return success_list
    except Exception as e:
        print(f"Error sending email: {str(e)}")
        return []

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/send_email', methods=['POST'])
def send_email_route():
    data = request.json
    success_recipients = send_email(data['recipients'], data['subject'], data['message'])

    if success_recipients:
        return jsonify({'status': 'success', 'message': f'Emails sent to: {", ".join(success_recipients)}'})
    else:
        return jsonify({'status': 'error', 'message': 'Failed to send emails'}), 500
@app.route('/track/<tracking_pixel>')
def track_open(tracking_pixel):
    """Update the opened time when the recipient opens the email"""
    opened_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    conn = sqlite3.connect('emails.db')
    c = conn.cursor()

    # Check if the tracking pixel exists
    c.execute("SELECT opened_time FROM emails WHERE tracking_pixel = ?", (tracking_pixel,))
    record = c.fetchone()

    if record and record[0] is None:  # Only update if it hasn't been opened before
        c.execute('''
            UPDATE emails 
            SET opened_time = ? 
            WHERE tracking_pixel = ?
        ''', (opened_time, tracking_pixel))
        conn.commit()

    conn.close()

    # Return a transparent tracking pixel
    return send_file('static/pixel.gif', mimetype='image/gif', as_attachment=False)

@app.route('/get_emails')
def get_emails():
    """Fetch all email records with timestamps"""
    conn = sqlite3.connect('emails.db')
    c = conn.cursor()
    c.execute('SELECT * FROM emails ORDER BY sent_time DESC')
    emails = c.fetchall()
    conn.close()

    email_list = []
    for email in emails:
        email_list.append({
            'id': email[0],
            'subject': email[1],
            'recipient': email[2],
            'sent_time': email[3] if email[3] else "Pending",
            'delivered_time': email[4] if email[4] else "Pending",
            'opened_time': email[5] if email[5] else "Not Opened",
            'tracking_pixel': email[6]
        })

    return jsonify(email_list)

if __name__ == '__main__':
    init_db()
    os.makedirs('static', exist_ok=True)
    
    # Ensure the tracking pixel exists
    if not os.path.exists('static/pixel.gif'):
        with open('static/pixel.gif', 'wb') as f:
            f.write(b'GIF89a\x01\x00\x01\x00\x80\x00\x00\xff\xff\xff\x00\x00\x00!\xf9\x04\x01\x00\x00\x00\x00,\x00\x00\x00\x00\x01\x00\x01\x00\x00\x02\x02D\x01\x00;')
    
    app.run(debug=True)
