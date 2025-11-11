

from fastapi import APIRouter

from service import ZohoService
from utils import get_access_token


router = APIRouter(tags=["Zoho"])



@router.get("/list-messages")
async def list_messages():
    access_token = get_access_token()
    return ZohoService(access_token).get_messages_list()


@router.get("/message/{message_id}")
async def get_message_by_id(message_id: str):
    access_token = get_access_token()
    folder_id  = "7291442000000017037"
    return ZohoService(access_token).get_message_by_id(message_id, folder_id)
    

@router.get('/append-content')
async def append_content():
    access_token = get_access_token()
    return ZohoService(access_token).append_content_and_attachments()


@router.get('/stats')
def get_stats():
    access_token = get_access_token()
    return ZohoService(access_token).get_stats()