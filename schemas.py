from pydantic import BaseModel

# Define a Pydantic model for the request body
class SendMessageRequest(BaseModel):
    user_id: str
    message: str