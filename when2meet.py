"""Print who has responded to a When2meet event, and how many people that is.

Usage:
    python when2meet.py
    python when2meet.py "https://www.when2meet.com/?1234567-AbCde"
"""

import re
import sys

import requests

# When2meet writes each responder into the page's JavaScript, like:
#   PeopleNames[0] = 'Alice';PeopleIDs[0] = 1234567;
NAME_PATTERN = re.compile(r"PeopleNames\[\d+\]\s*=\s*'(.*?)';")


def get_names(url):
    """Download the When2meet page and return the list of responder names."""
    response = requests.get(url, timeout=15)
    response.raise_for_status()  # stop with an error if the page didn't load
    return NAME_PATTERN.findall(response.text)


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
        print(f"  - {name}")


if __name__ == "__main__":
    main()
