document.getElementById('emailForm').addEventListener('submit', function(event) {
    event.preventDefault();

    const recipients = document.getElementById('recipients').value;
    const subject = document.getElementById('subject').value;
    const message = document.getElementById('message').value;

    fetch('/send_email', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ recipients, subject, message })
    })
    .then(response => response.json())
    .then(data => {
        document.getElementById('statusMessage').innerText = data.message;
        loadEmails();
    })
    .catch(error => {
        console.error('Error:', error);
        document.getElementById('statusMessage').innerText = 'Error sending email.';
    });
});

// Function to load email tracking data
function loadEmails() {
    fetch('/get_emails')
    .then(response => response.json())
    .then(data => {
        const tableBody = document.getElementById('emailTableBody');
        tableBody.innerHTML = '';

        data.forEach(email => {
            const row = `<tr>
                <td>${email.recipient}</td>
                <td>${email.subject}</td>
                <td>${email.sent_time}</td>
                <td>${email.delivered_time}</td>
                <td>${email.opened_time}</td>
            </tr>`;
            tableBody.innerHTML += row;
        });
    })
    .catch(error => console.error('Error:', error));
}

// Load emails on page load
window.onload = loadEmails;
