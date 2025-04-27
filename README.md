📜 Overview

The Email Read Status Tracker is a system designed to track when an email has been opened by a recipient. It provides real-time notifications and helps users and businesses improve communication transparency and follow-ups.

🚀 Features

Tracks when emails are opened by the recipient
Sends real-time read status updates
Provides analytics on email engagement
Easy integration with existing email systems

🛠️ Tech Stack

Backend: Python / Node.js
Frontend: HTML, CSS, JavaScript
Database: MySQL / MongoDB

Libraries:
Flask or Express (for server setup)
SMTP for sending emails
Pixel tracking mechanism (embedded invisible image)

🏗️ How It Works

Send Email: Email is sent with an invisible tracking pixel embedded.
Pixel Request: When the email is opened, the pixel (an image URL) is requested from the server.
Server Logs: The server records the email open event with a timestamp.
Notification: Sender is notified in real-time that the email was opened.

⚡ Getting Started

Clone the repository:
git clone https://github.com/Poojagowda8660/email-read-status-tracker.git

Install required libraries:
pip install flask sqlalchemy
Configure SMTP settings and database connection.

Run the server:
python app.py

🤝 Contributing

Open to contributions! Feel free to fork the repository, suggest features, or report bugs through issues or pull requests.

