# LINE Bot with FastAPI for Multiple Official Accounts 🤖⚡

This repository provides a LINE Bot integration using [FastAPI](https://fastapi.tiangolo.com/) and the [line-bot-sdk-python](https://github.com/line/line-bot-sdk-python). It supports multiple LINE Official Accounts (OAs), enabling distinct handlers and configurations for each account.

## Features

- **Webhook Endpoint (`/{account}/webhook`)**:  
  Handles events from the LINE platform, including text messages, follow events (when a user adds your bot as a friend), and join events (when the bot is invited to a group or room). Supports multiple LINE OAs by specifying the account in the URL.

- **Reply Messages**:  
  Automatically replies to incoming messages from LINE users based on text content. Each account has independent handlers for tailored responses.

- **Follow Event Handling**:  
  Sends a welcome message to users who start following your LINE Official Account.

- **Join Event Handling**:  
  Sends a welcome message when the bot is added to a group or room.

- **Push Messages (`/{account}/line/sendmsg`)**:  
  Allows sending a text message to a user by making a POST request to the endpoint, scoped to the specified LINE OA.

## Prerequisites

1. **LINE Messaging API Credentials for Multiple Accounts**:  
   You need credentials for each LINE OA:
   - `LINE_CHANNEL_ACCESS_TOKEN`
   - `LINE_CHANNEL_SECRET`

   Example for two accounts:
   - `LINE_CHANNEL_ACCESS_TOKEN_1`, `LINE_CHANNEL_SECRET_1`
   - `LINE_CHANNEL_ACCESS_TOKEN_2`, `LINE_CHANNEL_SECRET_2`

2. **Environment Variables**:  
   Create a `.env` file in the root directory and set the following:
   ```env
   LINE_CHANNEL_ACCESS_TOKEN_1=YOUR_CHANNEL_ACCESS_TOKEN_FOR_ACCOUNT_1
   LINE_CHANNEL_SECRET_1=YOUR_CHANNEL_SECRET_FOR_ACCOUNT_1
   LINE_CHANNEL_ACCESS_TOKEN_2=YOUR_CHANNEL_ACCESS_TOKEN_FOR_ACCOUNT_2
   LINE_CHANNEL_SECRET_2=YOUR_CHANNEL_SECRET_FOR_ACCOUNT_2
   ```

3. **Python and Dependencies**:  
   - Python 3.8+ is recommended.
   - Use a virtual environment to manage dependencies.

## Setup Instructions

### Step 1: Clone the Repository
```bash
git clone https://github.com/ASonneP/line-bot-fastapi.git
cd line-bot-fastapi
```

### Step 2: Create a Virtual Environment
#### On macOS/Linux
```bash
python3 -m venv venv
source venv/bin/activate
```

#### On Windows
```bash
python -m venv venv
venv\Scripts\activate
```

### Step 3: Install Dependencies
```bash
pip install -r requirements.txt
```

### Step 4: Set Up Environment Variables
Create a `.env` file in the root directory with the following content:
```env
LINE_CHANNEL_ACCESS_TOKEN_1=YOUR_CHANNEL_ACCESS_TOKEN_FOR_ACCOUNT_1
LINE_CHANNEL_SECRET_1=YOUR_CHANNEL_SECRET_FOR_ACCOUNT_1
LINE_CHANNEL_ACCESS_TOKEN_2=YOUR_CHANNEL_ACCESS_TOKEN_FOR_ACCOUNT_2
LINE_CHANNEL_SECRET_2=YOUR_CHANNEL_SECRET_FOR_ACCOUNT_2
```
Replace the placeholders with your LINE Messaging API credentials.

### Step 5: Run the Application
Start the FastAPI server:
```bash
uvicorn main:app --reload
```

The application will run locally on `http://127.0.0.1:8000`.

## API Endpoints

### 1. Webhook Endpoint (`/{account}/webhook`)
This endpoint receives events from the LINE platform for a specified account.

- **Method**: `POST`
- **URL**: `/{account}/webhook` (e.g., `/sonnep/webhook`, `/ninja/webhook`)
- **Content-Type**: `application/json`
- **Headers**: Includes `X-Line-Signature` for validating the request from LINE.

### 2. Send Message Endpoint (`/{account}/line/sendmsg`)
Allows you to push a message to a specific user for the specified LINE OA.

- **Method**: `POST`
- **URL**: `/{account}/line/sendmsg` (e.g., `/sonnep/line/sendmsg`, `/ninja/line/sendmsg`)
- **Content-Type**: `application/json`
- **Request Body**:
  ```json
  {
    "user_id": "USER_ID",
    "message": "Your custom message"
  }
  ```
- **Response**:
  ```json
  {
    "status": "success",
    "message": "Message sent to USER_ID"
  }
  ```

## Project Structure
```plaintext
.
├── main.py            # Main application file with FastAPI routes
├── schemas.py         # Pydantic models for request validation
├── requirements.txt   # Project dependencies
├── .env               # Environment variables file
├── venv/              # Virtual environment (created locally)
└── README.md          # Documentation (this file)
```

## Handling Events

### Message Event (`/{account}/webhook`)
- Responds to text messages with custom replies for each LINE OA.
- Supported commands:
  - "Who am I?": Returns the user ID.
  - "What group?": Returns the group ID (if in a group chat).

### Follow Event
- Sends a welcome message to new followers of the specified LINE OA.

### Join Event
- Sends a welcome message when the bot is added to a group or room for the specified LINE OA.

## Multiple LINE OA Support

This application allows independent management of multiple LINE OAs:
- Each account has its own `WebhookHandler` and `LineBotApi` instance.
- Event handlers (`MessageEvent`, `FollowEvent`, `JoinEvent`) are defined independently for each account.

## Development and Testing

1. Use the [LINE Developer Console](https://developers.line.biz/) to set up your webhook URLs for each account:
   - `http://<your-server-domain>/sonnep/webhook`
   - `http://<your-server-domain>/ninja/webhook`

2. For local testing, use tools like [ngrok](https://ngrok.com/) to expose your local server to the internet:
   ```bash
   ngrok http 8000
   ```

3. Test the API endpoints using tools like [Postman](https://www.postman.com/) or `curl`.

