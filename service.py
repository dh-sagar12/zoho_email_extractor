import json
import time
from typing import List
from fastapi import HTTPException
import requests
from constant import BASE_URL, ACCOUNT_ID
from utils import extract_main_email, renew_access_token


class ZohoService:
    def __init__(self, access_token: str):
        self.access_token = access_token
        self.base_url = BASE_URL
        self.headers = {
            "Authorization": f"Zoho-oauthtoken {self.access_token}",
            "Content-Type": "application/json",
            "Accept": "application/json",
        }
        self.account_id = ACCOUNT_ID

    def get_messages_list(self):
        list_url = f"{self.base_url}/accounts/{self.account_id}/messages/view"
        # six_months_ago = int((time.time() - 15552000) * 1000)
        start = 1
        messages = []
        loop_count = 0

        while True:
            params = {
                "limit": 200,
                "status": "all",
                # "fromDate": six_months_ago,
                "includeto": True,
                "includesent": True,
                # "includearchive": True,
                # "sortBy": "date",
            }
            if start:
                params["start"] = start

            print(
                f"Fetching messages from {start} to {start + 199} WITH URL: {list_url} and PARAMS: {params}"
            )
            res = requests.get(
                list_url,
                headers=self.headers,
                params=params,
            )
            response = res.json()
            print(f"Total messages fetched: {len(response['data'])}")
            messages.extend(response["data"])
            if len(response["data"]) < 200:
                self._save_to_json(messages=messages)
                messages = []
                print(f"No more messages to fetch...")
                print(f"Last response Length: {len(response['data'])}")
                break
            start += 200
            loop_count += 1
            if loop_count == 10:
                self._save_to_json(messages=messages)
                messages = []
                loop_count = 0

        return messages

    def _save_to_json(self, messages: List, file_name: str = "messages.json"):
        with open(file_name, "a+") as f:
            print("Saving messages to file...")
            import os

            # Move file pointer to start and check if file is empty
            f.seek(0)
            content = f.read().strip()
            f.seek(0, os.SEEK_END)  # Move back to end for appending if needed

            if not content:
                # File is empty, write messages as the initial list
                f.seek(0)
                f.write(json.dumps(messages, ensure_ascii=False, indent=4))
            else:
                # File has content, update the existing JSON list
                # Move to start to read current JSON array
                f.seek(0)
                try:
                    existing = json.load(f)
                except Exception:
                    f.seek(0)
                    content_nonempty = f.read().strip()
                    if content_nonempty:
                        # Try to load from existing content (e.g. multiple lists appended)
                        first_bracket = content_nonempty.find("[")
                        last_bracket = content_nonempty.rfind("]")
                        if first_bracket != -1 and last_bracket != -1:
                            content_clean = content_nonempty[
                                first_bracket : last_bracket + 1
                            ]
                            existing = json.loads(content_clean)
                        else:
                            existing = []
                    else:
                        existing = []
                # Add the new messages to the existing list
                existing.extend(messages)
                # Truncate and rewrite combined list
                f.seek(0)
                f.truncate()
                f.write(json.dumps(existing, ensure_ascii=False, indent=4))

    def get_message_by_id(self, message_id: str, folder_id: str) -> dict:
        message_url = f"{self.base_url}/accounts/{self.account_id}/folders/{folder_id}/messages/{message_id}/content"
        params = {
            "includeBlockContent": False,
        }
        print(
            f"Fetching Message Content by ID: {message_id} with URL: {message_url} and PARAMS: {params}"
        )
        res = requests.get(
            message_url,
            headers=self.headers,
            params=params,
        )
        response = res.json()
        if response.get("status", {}).get("code") == 401:
            print(f"Unauthorized, renewing access token...")
            new_data = renew_access_token()
            access_token = new_data.get("access_token")
            if not access_token:
                print(f"Failed to renew access token, please login again")
                return {
                    "success": False,
                    "message": "Failed to renew access token, please login again",
                }
            self.headers["Authorization"] = f"Zoho-oauthtoken {access_token}"
            return self.get_message_by_id(message_id, folder_id)
        else:
            message = response.get("data").get("content")
            print(f"Extracting Main Email from Message... ")
            main_email = extract_main_email(message)
            return main_email

    def append_content_and_attachments(self) -> dict:
        with open("messages.json", "r") as f:
            messages = json.load(f)

        print("Loading Messages from file... Total Messages: ", len(messages))
        messages_with_content = []
        total_messages = len(messages)
        loop_count = 0
        for message in messages:
            message_id = message.get("messageId")
            folder_id = message.get("folderId")
            main_email = self.get_message_by_id(
                message_id,
                folder_id,
            )
            has_attachments = message.get("hasAttachment", "0")
            message["content"] = main_email
            if has_attachments == "1":
                print(f"Message {message_id} has attachments")
                attachments = self.get_attachments(message_id, folder_id)
                message["attachments"] = attachments
            messages_with_content.append(message)
            loop_count += 1
            if loop_count == 100 or loop_count == total_messages:
                self._save_to_json(
                    messages=messages_with_content,
                    file_name="messages_with_content.json",
                )
                messages_with_content = []
                loop_count = 0
            print("-----------------------------------------------------\n")
        return {
            "success": True,
        }

    def _construct_attachment_urls(
        self,
        folder_id: str,
        message_id: str,
        attachments: list,
    ) -> list:
        print(f"Constructing attachment URLs for Message {message_id}...")
        attachment_urls = []
        for attachment in attachments:
            attachment_id = attachment.get("attachmentId")
            url = f"{self.base_url}/accounts/{self.account_id}/folders/{folder_id}/messages/{message_id}/attachments/{attachment_id}"
            attachment_urls.append(url)
        return attachment_urls

    def get_attachments(self, message_id: str, folder_id: str) -> list:
        attachment_url = f"{self.base_url}/accounts/{self.account_id}/folders/{folder_id}/messages/{message_id}/attachmentinfo"
        print(
            f"Fetching Attachments Details For ID: {message_id} with URL: {attachment_url}"
        )
        res = requests.get(
            attachment_url,
            headers=self.headers,
        )
        response = res.json()
        # check for attachments
        attachments = response.get("data", {}).get("attachments", [])
        attachment_urls = self._construct_attachment_urls(
            folder_id=folder_id,
            message_id=message_id,
            attachments=attachments,
        )
        return attachment_urls

    def get_stats(self) -> dict:
        with open("messages.json", "r") as f:
            messages = json.load(f)
        return {
            "total_messages": len(messages),
        }


    def get_accounts(self) -> dict:
        accounts_url = f"{self.base_url}/accounts"
        print(f"Fetching Accounts with URL: {accounts_url}")
        res = requests.get(
            accounts_url,
            headers=self.headers,
        )
        response = res.json()
        return response.get("data", [])