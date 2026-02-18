import json
from datetime import UTC, datetime, timedelta
import requests

from constant import (
    AUTH_BASE_URL,
    CLEINT_ID,
    CLIENT_SECRET,
)


def get_logger(name):
    import logging

    logger = logging.getLogger(name)
    logger.setLevel(logging.INFO)
    handler = logging.StreamHandler()
    formatter = logging.Formatter(
        "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    )
    handler.setFormatter(formatter)
    logger.addHandler(handler)
    return logger


def get_access_token():
    with open("response.json", "r") as response:
        data = response.read()
        parsed_data = json.loads(data)
        access_token = parsed_data.get("access_token")
        expires_at = parsed_data.get("expires_at")
        expires_date = datetime.fromisoformat(expires_at)
        if expires_date > datetime.now(UTC):
            return access_token
        else:
            print("Access token expired, renewing...")
            new_data = renew_access_token()
            if new_data:
                return new_data.get("access_token")
            else:
                return None


def get_refresh_token():
    with open("response.json", "r") as response:
        data = response.read()
        parsed_data = json.loads(data)
        print(parsed_data.get("refresh_token"), "refresh_token")
        return parsed_data.get("refresh_token")


def renew_access_token():
    """
    Renew access token from Zoho and save to response.json
    """

    url = f"{AUTH_BASE_URL}/oauth/v2/token"
    headers = {"Content-Type": "application/x-www-form-urlencoded"}
    print("Checking for the Refresh Token...")
    refresh_token = get_refresh_token()
    if not refresh_token:
        print("No refresh token found, please login again")
        return None
    print("Getting New access token...")
    data = {
        "refresh_token": refresh_token,
        "client_id": CLEINT_ID,
        "client_secret": CLIENT_SECRET,
        "grant_type": "refresh_token",
    }
    response = requests.post(url, headers=headers, data=data)
    if response.status_code != 200:
        print("Failed to renew access token: ", response.text, "response")
        return None
    else:
        new_data = response.json()
        expires_at = datetime.now(UTC) + timedelta(seconds=new_data.get("expires_in"))
        with open("response.json", "r+") as f:
            data = f.read()
            parsed_data = json.loads(data)
            parsed_data["access_token"] = new_data.get("access_token")
            parsed_data["expires_at"] = expires_at.isoformat()
            f.seek(0)
            f.write(json.dumps(parsed_data))
            f.truncate()
        return new_data


from bs4 import BeautifulSoup
import re


def extract_main_email(html_content: str) -> str:
    soup = BeautifulSoup(html_content, "html.parser")

    # remove quoted blocks entirely
    for block in soup.find_all("blockquote"):
        block.decompose()

    text = soup.get_text(separator="\n")

    # remove reply markers (On Thu, NAME wrote...)
    text = re.split(r"On .* wrote:", text, flags=re.IGNORECASE)[0]

    # remove the Zoho "---- On ..." style signature
    text = re.split(r"---- On .* wrote ---", text, flags=re.IGNORECASE)[0]

    # clean up weird multiple line breaks
    text = "\n".join(line.strip() for line in text.splitlines() if line.strip())

    return text


def get_message_with_content_count():
    with open("messages_with_content.json", "r") as f:
        messages = json.load(f)
    return len(messages)


if __name__ == "__main__":
    print(get_message_with_content_count())
