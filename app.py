# app.py (with cProfile profiling)
import os
os.environ['TF_CPP_MIN_LOG_LEVEL'] = '3'
os.environ['TOKENIZERS_PARALLELISM'] = 'false'

from flask import Flask, request, jsonify, render_template
from chatbot.intent_handler import IntentHandler
from chatbot.caching import EmbeddingCache
from chatbot.knowledge import KnowledgeBase
import uuid
from chatbot.nl_generation import ResponseGenerator
import cProfile
import pstats
import io
import time  # Import time for simple timing

app = Flask(__name__)
app.config['TIMEOUT'] = 300
cache = EmbeddingCache()
kb = KnowledgeBase()
response_generator = ResponseGenerator()
handler = IntentHandler(cache, kb, response_generator)

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/api/chat', methods=['POST'])
def handle_chat():
    data = request.json
    session_id = data.get('session_id', str(uuid.uuid4()))

    response, resp_type = handler.handle_query(
        query=data['message'],
        session_id=session_id,
        mode=data.get('mode', 'script')
    )

    return jsonify({
        'response': response,
        'type': resp_type,
        'session_id': session_id
    })

if __name__ == '__main__':
    pr = cProfile.Profile()
    pr.enable()
    start_time = time.time() # Simple timer start

    app.run(port=5000, debug=False, use_reloader=False)

    pr.disable()
    end_time = time.time() # Simple timer end
    startup_time = end_time - start_time
    print(f"\nFlask App Startup Time: {startup_time:.2f} seconds\n") # Print startup time

    s = io.StringIO()
    ps = pstats.Stats(pr, stream=s).sort_stats('cumulative')
    ps.print_stats(20) # Print top 20 slow functions

    print("\ncProfile Stats (Top 20 by cumulative time):\n", s.getvalue())