import logging
from flask import Flask, jsonify, request
from flask_socketio import SocketIO
from elasticsearch import Elasticsearch
from datetime import datetime

# App
app = Flask(__name__)
sio = SocketIO(app, cors_allowed_origins="*")
es = Elasticsearch("http://elasticsearch:9200")


# Logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Data
clients = {}

# WS
@sio.event
def connect():
    client_id : str = request.sid
    logger.info(f'Client connected: {client_id}')
    clients[client_id] = len(clients) + 1
    # index in ES
    client_doc = {
        'id': client_id,
        'date': datetime.now().timestamp()
    }
    es.index(index='clients', id=client_id, document=client_doc)

@sio.on('disconnect')
def handle_disconnect():
    logger.info('Client disconnected')
    clients.pop(request.sid)

@sio.event
def message(data):
    logger.info(f'Received message: {data}')

def send_ping():
    while True:
        logger.info("Sending ping")
        sio.send({'data': 'Hello from the server!'})
        sio.sleep(5)

# REST
@app.route('/clients', methods=['GET'])
def get_clients():
    logger.info(f"HTTP /connect endpoint called. {request}")
    return jsonify({"clients": clients})

@app.route('/createindex', methods=['GET'])
def create_index():
    # Init ES
    mappings = {
        "properties": {
            "id": {"type": "text", "analyzer": "english"},
            # "ethnicity": {"type": "text", "analyzer": "standard"},
            "date": {"type": "integer"}
        }
    }
    resp = es.indices.create(index="clients", mappings=mappings)
    # es.indices.delete(index="clients", ignore_unavailable=True)

    return jsonify(resp.body)

@app.route('/getindex', methods=['GET'])
def get_index():
    resp = es.search(
        index="clients",
        # Query to match all documents
        query = {
            "match_all": {}
        }
    )
    
    return jsonify(resp.body)


if __name__ == '__main__':
    logger.info("Starting Flask-SocketIO server")

    sio.start_background_task(send_ping)
    sio.run(app, host='0.0.0.0', port=5000)
    