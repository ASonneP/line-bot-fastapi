from fastapi import FastAPI, Request, HTTPException
from linebot import LineBotApi, WebhookHandler
from linebot.exceptions import InvalidSignatureError
from linebot.models import TextSendMessage
from linebot.models.events import MessageEvent, FollowEvent, JoinEvent
from schemas import SendMessageRequest



from dotenv import load_dotenv
import os


load_dotenv()

app = FastAPI()

# LINE SDK Setup
line_bot_api = LineBotApi(os.getenv("LINE_CHANNEL_ACCESS_TOKEN"))
handler = WebhookHandler(os.getenv("LINE_CHANNEL_SECRET"))

# Webhook Endpoint
@app.post("/webhook")
async def webhook(request: Request):
    body = await request.body()
    signature = request.headers.get("X-Line-Signature")

    if not signature:
        raise HTTPException(status_code=400, detail="Missing signature")

    try:
        handler.handle(body.decode("utf-8"), signature)
    except InvalidSignatureError:
        raise HTTPException(status_code=400, detail="Invalid signature")

    return {"status": "ok"}

@app.post("/line/sendmsg")
async def send_message(req: SendMessageRequest):
    try:
        line_bot_api.push_message(req.user_id, TextSendMessage(text=req.message))
        return {"status": "success", "message": f"Message sent to {req.user_id}"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))



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
        line_bot_api.reply_message(reply_token, reply_message)
# Follow Event Handler
@handler.add(FollowEvent)
def handle_follow(event):
    user_id = event.source.user_id  # Get the user ID
    print(f"New follower: {user_id}")

    # Send a welcome message
    welcome_message = TextSendMessage(text="Thank you for following our LINE Official Account!")
    line_bot_api.reply_message(event.reply_token, welcome_message)
    
@handler.add(JoinEvent)
def handle_join(event):
    if event.source.type == "group":
        group_id = event.source.group_id  # Get the group ID
        print(f"Joined group: {group_id}")
    elif event.source.type == "room":
        room_id = event.source.room_id  # Get the room ID
        print(f"Joined room: {room_id}")

    # Send a welcome message
    welcome_message = TextSendMessage(text="Thank you for inviting me to this group or room!")
    line_bot_api.reply_message(event.reply_token, welcome_message)