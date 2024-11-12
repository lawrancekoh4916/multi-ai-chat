import os
from flask import Flask, render_template, request, Response
import asyncio
from dotenv import load_dotenv
import aiohttp

load_dotenv()

app = Flask(__name__, template_folder='templates')

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")  # Placeholder - replace with actual Gemini API key

async def get_openai_response(message, q):
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {OPENAI_API_KEY}"
    }
    data = {
        "model": "gpt-3.5-turbo",  # Or another suitable model
        "messages": [{"role": "user", "content": message}]
    }
    async with aiohttp.ClientSession() as session:
        async with session.post("https://api.openai.com/v1/chat/completions", headers=headers, json=data, stream=True) as response:
            async for line in response.content:
                q.put(f"OpenAI: {line.decode()}\n")

async def get_gemini_response(message, q):
    # Placeholder - Replace with actual Gemini API call using aiohttp
    # This will depend on the Gemini API's specifics.
    q.put(f"Gemini: {message} (Gemini API call not implemented)\n")


@app.route("/openai", methods=["POST"])
def openai_stream():
    message = request.form["message"]
    q = Queue()
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    loop.run_until_complete(get_openai_response(message, q))
    def stream():
        while not q.empty():
            yield f"data: {q.get()}\n\n"
    return Response(stream(), mimetype="text/event-stream")

@app.route("/gemini", methods=["POST"])
def gemini_stream():
    message = request.form["message"]
    q = Queue()
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    loop.run_until_complete(get_gemini_response(message, q))
    def stream():
        while not q.empty():
            yield f"data: {q.get()}\n\n"
    return Response(stream(), mimetype="text/event-stream")

@app.route("/", methods=["GET"])
def index():
    return render_template("index.html")

if __name__ == "__main__":
    app.run(debug=True)
