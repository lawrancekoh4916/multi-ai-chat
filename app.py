from flask import Flask, render_template, request, Response
import os
from dotenv import load_dotenv
import google.generativeai as genai
import openai
from threading import Thread
from queue import Queue
import json

load_dotenv()

app = Flask(__name__)

# Configure API clients
genai.configure(api_key=os.getenv('GOOGLE_API_KEY'))
gemini_model = genai.GenerativeModel('gemini-pro')
openai.api_key = os.getenv('OPENAI_API_KEY')

def stream_gemini(prompt, queue):
    response = gemini_model.generate_content(prompt, stream=True)
    for chunk in response:
        if chunk.text:
            queue.put(('gemini', chunk.text))
    queue.put(('gemini', '[DONE]'))

def stream_openai(prompt, queue):
    response = openai.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[{"role": "user", "content": prompt}],
        stream=True
    )
    
    for chunk in response:
        if chunk.choices[0].delta.content:
            queue.put(('openai', chunk.choices[0].delta.content))
    queue.put(('openai', '[DONE]'))

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/stream', methods=['POST'])
def stream():
    try:
        prompt = request.json['prompt']
        queue = Queue()
        
        Thread(target=stream_gemini, args=(prompt, queue)).start()
        Thread(target=stream_openai, args=(prompt, queue)).start()
        
        def generate():
            try:
                done_count = 0
                while done_count < 2:
                    model, text = queue.get()
                    if text == '[DONE]':
                        done_count += 1
                        continue
                    yield f"data: {json.dumps({'model': model, 'text': text})}\n\n"
            except Exception as e:
                print(f"Error in generate(): {str(e)}")
                yield f"data: {json.dumps({'model': 'error', 'text': str(e)})}\n\n"
        
        return Response(generate(), mimetype='text/event-stream')
    except Exception as e:
        print(f"Error in stream(): {str(e)}")
        return Response(
            f"data: {json.dumps({'model': 'error', 'text': str(e)})}\n\n",
            mimetype='text/event-stream'
        )

if __name__ == '__main__':
    app.run(debug=True) 