# Gemini Share Screen sample

This is a sample of using Gemini 2.0 to share screen

Original source code: https://github.com/google-gemini/cookbook/blob/main/quickstarts/Get_started_LiveAPI.py

With this sample you cannot choose the screen to share. The screen are shared automatically.

## 🔧 Setup

Tested on Windows:

1. Create environment:
First of all you need to create a .venv environment: in visual code editor CTRL+Shift+P
You need to select the version of python you have and then selecting the requirement.txt file to install dependencies


2. Add APIKey:
Create a file name .env and put the api Key named like this: GOOGLE_API_KEY=""
Because of .gitignore file your API key will not be saved to git repository

## 🏁 Run

To run the script:
- Start your venv environment: `.venv\Scripts\Activate.ps1`
- Run the code: `python geminiLiveAPI.py`

## 🚧 Troubleshoot

When running the original source code i got a deprecated warning:

> DeprecationWarning: The `session.send` method is deprecated and will be removed in a future version (not before Q3 2025).
Please use one of the more specific methods: `send_client_content`, `send_realtime_input`, or `send_tool_response` instead.

So i tried to use one of the suggested methods.
I replaced this lines:

`103: await self.session.send(input=text or ".", end_of_turn=True)` by this line: `await self.session.send_realtime_input(media=text or ".")`

`181: await self.session.send(input=msg)` by this line: `await self.session.send_realtime_input(media=msg)`



