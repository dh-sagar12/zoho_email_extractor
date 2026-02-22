
# for sales@moutainlodgesofnepal.com
# ACCOUNT_ID ="7291442000000008002"
# CLEINT_ID = "1000.FXQKEDT5MQ082UW1RDUBVSZ4L96K6D"
# CLIENT_SECRET = "fe2153c3ddf8a51b72b89900b08c3db06f3443e548"

import os 
from dotenv import load_dotenv
load_dotenv()
# for reservation.everest@mountainlodgesofnepal.com
ACCOUNT_ID = os.getenv("ACCOUNT_ID")
CLEINT_ID = os.getenv("CLIENT_ID")
CLIENT_SECRET = os.getenv("CLIENT_SECRET")


REDIRECT_URI = "http://localhost:8000/oauth"
SCOPE = "ZohoMail.messages.CREATE,ZohoMail.messages.READ,ZohoMail.accounts.READ"
ACCESS_TYPE = "offline"
BASE_URL = "https://mail.zoho.com/api"
AUTH_BASE_URL="https://accounts.zoho.com"
