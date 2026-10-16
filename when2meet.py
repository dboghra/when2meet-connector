"""Show who has responded to a When2meet event, and optionally wait until
a list of people have all filled it out.

Usage:
    python when2meet.py
    python when2meet.py "https://www.when2meet.com/?1234567-AbCde"
"""

import ctypes
import os
import re
import smtplib
import sys
import time
import winsound
from email.message import EmailMessage

import requests

# When2meet writes each responder into the page's JavaScript, like:
#   PeopleNames[0] = 'Alice';PeopleIDs[0] = 1234567;
# The page includes this list more than once, so we key by the index number.
NAME_PATTERN = re.compile(r"PeopleNames\[(\d+)\]\s*=\s*'(.*?)';")

CHECK_EVERY_SECONDS = 60
DEFAULT_RECIPIENT = "d.boghra@northeastern.edu"


def get_names(url):
    """Download the When2meet page and return the list of responder names."""
    response = requests.get(url, timeout=15)
    response.raise_for_status()  # stop with an error if the page didn't load
    by_index = {int(i): name for i, name in NAME_PATTERN.findall(response.text)}
    return [by_index[i] for i in sorted(by_index)]


def normalize(name):
    return name.strip().lower()


def send_email(subject, body):
    """Email the alert. Settings come from environment variables:
    EMAIL_USER and EMAIL_PASSWORD (required), EMAIL_SERVER, EMAIL_PORT and
    EMAIL_TO (optional). Returns quietly if email isn't set up."""
    user = os.environ.get("EMAIL_USER")
    password = os.environ.get("EMAIL_PASSWORD")
    if not user or not password:
        print("(Email skipped: EMAIL_USER / EMAIL_PASSWORD not set.)")
        return

    message = EmailMessage()
    message["Subject"] = subject
    message["From"] = user
    message["To"] = os.environ.get("EMAIL_TO", DEFAULT_RECIPIENT)
    message.set_content(body)

    server = os.environ.get("EMAIL_SERVER", "smtp.office365.com")
    port = int(os.environ.get("EMAIL_PORT", "587"))
    try:
        with smtplib.SMTP(server, port, timeout=30) as smtp:
            smtp.starttls()
            smtp.login(user, password)
            smtp.send_message(message)
        print(f"Email sent to {message['To']}.")
    except (smtplib.SMTPException, OSError) as error:
        print(f"Could not send email: {error}")


def notify(message):
    """Email, beep, and pop up a Windows message box."""
    print(message)
    send_email("When2meet: everyone has responded", message)
    winsound.MessageBeep()
    ctypes.windll.user32.MessageBoxW(0, message, "When2meet", 0x40)


def wait_for_everyone(url, wanted):
    """Check the page repeatedly until every wanted name has responded."""
    print(f"Waiting for: {', '.join(wanted)}")
    print(f"Checking every {CHECK_EVERY_SECONDS} seconds. Press Ctrl+C to stop.\n")
    while True:
        try:
            responded = {normalize(n) for n in get_names(url)}
        except requests.RequestException as error:
            print(f"[{time.strftime('%H:%M:%S')}] Could not load page ({error}); retrying.")
        else:
            missing = [n for n in wanted if normalize(n) not in responded]
            if not missing:
                notify("Everyone has filled out the When2meet!")
                return
            print(f"[{time.strftime('%H:%M:%S')}] Still waiting on: {', '.join(missing)}")
        time.sleep(CHECK_EVERY_SECONDS)


def main():
    # Take the URL from the command line, or ask for it if none was given.
    if len(sys.argv) > 1:
        url = sys.argv[1]
    else:
        url = input("Paste the When2meet URL: ").strip()

    if "when2meet.com" not in url:
        print("That doesn't look like a When2meet URL.")
        sys.exit(1)

    try:
        names = get_names(url)
    except requests.RequestException as error:
        print(f"Could not load that page: {error}")
        sys.exit(1)

    print(f"{len(names)} people responded:")
    for name in names:
        print(f"  - {name.strip()}")

    answer = input(
        "\nNames to wait for, separated by commas (or press Enter to skip): "
    )
    wanted = [n.strip() for n in answer.split(",") if n.strip()]
    if wanted:
        print()
        try:
            wait_for_everyone(url, wanted)
        except KeyboardInterrupt:
            print("\nStopped.")
#jyza iyjp jyiv ochm

if __name__ == "__main__":
    main()
