from fastapi import FastAPI, Request, HTTPException, Depends
from linebot import LineBotApi, WebhookHandler
from linebot.exceptions import InvalidSignatureError
from linebot.models import TextSendMessage
from linebot.models.events import MessageEvent, FollowEvent, JoinEvent
from schemas import SendMessageRequest
from dotenv import load_dotenv
import os

load_dotenv()

app = FastAPI()

# Store credentials for multiple LINE Official Accounts
LINE_ACCOUNTS = {
    "sonnep": {
        "channel_secret": os.getenv("LINE_CHANNEL_SECRET_1", ""),
        "access_token": os.getenv("LINE_CHANNEL_ACCESS_TOKEN_1", ""),
    },
    "ninja": {
        "channel_secret": os.getenv("LINE_CHANNEL_SECRET_2", ""),
        "access_token": os.getenv("LINE_CHANNEL_ACCESS_TOKEN_2", ""),
    },
}

# Store separate handlers for each account
HANDLERS = {}

# Setup LINE API and Handlers
def setup_line_bot(account: str):
    account_config = LINE_ACCOUNTS[account]
    line_bot_api = LineBotApi(account_config["access_token"])
    handler = WebhookHandler(account_config["channel_secret"])
    HANDLERS[account] = (line_bot_api, handler)
    return line_bot_api, handler

# Webhook Endpoint
@app.post("/{account}/webhook")
async def webhook(account: str, request: Request):
    if account not in HANDLERS:
        raise HTTPException(status_code=404, detail="Account not found")

    line_bot_api, handler = HANDLERS[account]
    body = await request.body()
    signature = request.headers.get("X-Line-Signature")

    if not signature:
        raise HTTPException(status_code=400, detail="Missing signature")

    try:
        handler.handle(body.decode("utf-8"), signature)
    except InvalidSignatureError:
        raise HTTPException(status_code=400, detail="Invalid signature")

    return {"status": "ok"}

@app.post("/{account}/line/sendmsg")
async def send_message(account: str, req: SendMessageRequest):
    if account not in HANDLERS:
        raise HTTPException(status_code=404, detail="Account not found")

    line_bot_api, _ = HANDLERS[account]
    try:
        line_bot_api.push_message(req.user_id, TextSendMessage(text=req.message))
        return {"status": "success", "message": f"Message sent to {req.user_id}"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    

@app.get("/{account}/line/quota_usage")
async def get_quota_usage(account: str):
    if account not in HANDLERS:
        raise HTTPException(status_code=404, detail="Account not found")

    line_bot_api, _ = HANDLERS[account]
    try:
        quota = line_bot_api.get_message_quota()
        return {"status": "success", "quota": quota}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/{account}/line/quota_consumption")
async def get_quota_consumption(account: str):
    if account not in HANDLERS:
        raise HTTPException(status_code=404, detail="Account not found")
    
    line_bot_api, _ = HANDLERS[account]
    try:
        consumption = line_bot_api.get_message_quota_consumption()
        return {"status": "success", "consumption": consumption}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/{account}/line/delivery_push")
async def get_delivery_push(account: str, date: str):
    if account not in HANDLERS:
        raise HTTPException(status_code=404, detail="Account not found")

    line_bot_api, _ = HANDLERS[account]
    try:
        response = line_bot_api.get_insight_message_delivery(date)
        return {"status": "success", "delivery_push": response}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))



# Define Handlers for Each Account
def register_handlers(account: str):
    _, handler = HANDLERS[account]

    @handler.add(MessageEvent)
    def handle_message(event):
        if event.message.type == "text":
            user_message = event.message.text
            if user_message.lower() == "who am i?":
                reply_message = TextSendMessage(text=f"Your user ID is: {event.source.user_id}")
            elif user_message.lower() == "what group?":
                if event.source.type == "group":
                    reply_message = TextSendMessage(text=f"This group ID is: {event.source.group_id}")
                else:
                    reply_message = TextSendMessage(text="This is not a group chat.")
            else:
                reply_message = TextSendMessage(text=f"You said: {user_message}")

            reply_token = event.reply_token
            line_bot_api, _ = HANDLERS[account]
            line_bot_api.reply_message(reply_token, reply_message)

    @handler.add(FollowEvent)
    def handle_follow(event):
        user_id = event.source.user_id  # Get the user ID
        print(f"New follower for account '{account}': {user_id}")
        welcome_message = TextSendMessage(text="Thank you for following our LINE Official Account!")
        reply_token = event.reply_token
        line_bot_api, _ = HANDLERS[account]
        line_bot_api.reply_message(reply_token, welcome_message)

    @handler.add(JoinEvent)
    def handle_join(event):
        if event.source.type == "group":
            group_id = event.source.group_id  # Get the group ID
            print(f"Joined group for account '{account}': {group_id}")
        elif event.source.type == "room":
            room_id = event.source.room_id  # Get the room ID
            print(f"Joined room for account '{account}': {room_id}")
        welcome_message = TextSendMessage(text="Thank you for inviting me to this group or room!")
        reply_token = event.reply_token
        line_bot_api, _ = HANDLERS[account]
        line_bot_api.reply_message(reply_token, welcome_message)

# Initialize Handlers for All Accounts
@app.on_event("startup")
async def startup():
    for account in LINE_ACCOUNTS:
        setup_line_bot(account)
        register_handlers(account)
        print(f"Handlers registered for account: {account}")
