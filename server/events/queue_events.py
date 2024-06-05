from main import server


@server.socketio.on("queue-register")
def handle_queue_registration(data):
    print(f"Received {data}")
