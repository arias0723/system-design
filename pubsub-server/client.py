import redis
import json
import socketio
import collections

sio = socketio.Client()
redis_client = redis.Redis(host='localhost', port=6380, db=0)

# Redis
def redis_common_handler(msg):
    data: collections.defaultdict = {}
    try:
        data = collections.defaultdict(None, json.loads(msg['data']))
    except Exception as e:
        print(e)
        pass

    if data.get('sender') != sio.sid:
        print(f'Got a redis-channel from {data.get('sender') or "XD"}: ', data.get('data') or msg['data'])

pubsub = redis_client.pubsub()
pubsub.subscribe(**{'common_channel': redis_common_handler})
pubsub.run_in_thread(1);

# WS
@sio.event
def connect():
    print('Connected: ', sio.sid)

@sio.event
def message(data):
    # print(f'{sio.sid} received a websocket: ', data)
    redis_client.publish('common_channel', json.dumps({'sender': sio.sid, 'data': 123}))

@sio.event
def disconnect():
    print('Disconnected from server')

sio.connect('http://localhost:5000', )
sio.wait()
