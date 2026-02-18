from fastapi import APIRouter, BackgroundTasks

from group_service import GroupService
from service import ZohoService
from utils import get_access_token


router = APIRouter(tags=["Zoho"])


@router.get("/list-messages")
async def list_messages(background_tasks: BackgroundTasks):
    access_token = get_access_token()
    zoho_service = ZohoService(access_token)

    def fetch_messages():
        zoho_service.get_messages_list()

    background_tasks.add_task(fetch_messages)
    return {
        "status": "success",
        "message": "Message fetching started in background",
    }


@router.get("/message/{message_id}")
async def get_message_by_id(message_id: str):
    access_token = get_access_token()
    folder_id = "7291442000000017037"
    return ZohoService(access_token).get_message_by_id(message_id, folder_id)


@router.get("/accounts")
async def get_accounts():
    access_token = get_access_token()
    return ZohoService(access_token).get_accounts()


@router.get("/append-content")
async def append_content(background_tasks: BackgroundTasks):
    access_token = get_access_token()
    zoho_service = ZohoService(access_token)

    def append_messages_content():
        zoho_service.append_content_and_attachments()

    background_tasks.add_task(append_messages_content)
    return {
        "status": "success",
        "message": "Content appending started in background",
    }


@router.get("/stats")
def get_stats():
    access_token = get_access_token()
    return ZohoService(access_token).get_stats()


@router.get("/group-messages")
async def group_messages(background_tasks: BackgroundTasks):
    group_service = GroupService()

    def process_group_messages():
        group_service.process_messages()

    background_tasks.add_task(process_group_messages)
    return {
        "status": "success",
        "message": "Message grouping started in background",
    }
