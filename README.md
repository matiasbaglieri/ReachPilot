# ReachPilot

ReachPilot is an AI-powered automation tool designed to streamline lead generation and engagement across LinkedIn and Mailgun. It enables users to connect, message, and follow up with prospects on LinkedIn, while simultaneously managing email campaigns through Mailgun — all from a single, unified interface.

## Features

- **LinkedIn Automation:** Connect, message, and follow up with prospects automatically.
- **Email Campaigns:** Manage and send personalized email campaigns using Mailgun.
- **Unified Dashboard:** Control all your outreach from one place.
- **Contact Import:** Easily import contacts from CSV files.
- **HTML Email Templates:** Use custom HTML templates for your email campaigns.

## Getting Started

1. **Clone the repository:**
    ```sh
    git clone https://github.com/yourusername/ReachPilot.git
    cd ReachPilot
    ```

2. **Install dependencies:**
    ```sh
    pip3 install -r requirements.txt
    ```

3. **Configure your database:**
    - Edit `config.ini` with your database connection details.

4. **Initialize the database:**
    ```sh
    python3 init_db.py
    ```

5. **Prepare your data:**
    - Place your CSV files and HTML email templates in the [`dumps/`](./dumps/) directory.

6. **download chromedriver:**
    - download the chromedriver 
    brew install chromedriver
    xattr -d com.apple.quarantine /usr/local/bin/chromedriver
    
7. **Run ReachPilot:**
    ```sh
    python3 main.py
    ```

## Importing Contacts & Email Templates

For detailed instructions on importing contacts and using HTML email templates, see the [`dumps/README.md`](./dumps/README.md).

## License

MIT License

---

*ReachPilot helps you automate your outreach and scale your business connections efficiently.*