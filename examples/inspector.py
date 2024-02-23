import aiohttp.web
import socketio

# Create a Socket.IO server
sio = socketio.AsyncServer(async_mode="aiohttp", cors_allowed_origins="*")
app = aiohttp.web.Application()
sio.attach(app)


# Event handler for new connections
@sio.event
async def connect(sid, environ):
    print("connect ", sid)


# Event handler for messages
@sio.event
async def message(sid, data):
    print("message ", data)
    await sio.emit("reply", room=sid, data="Received your message!")


# Event handler for disconnections
@sio.event
async def disconnect(sid):
    print("disconnect ", sid)


# Add a simple HTTP route for demonstration
async def index(request):
    return aiohttp.web.Response(
        text="Hello, this is an aiohttp server!", content_type="text/html"
    )


app.router.add_get("/", index)

if __name__ == "__main__":
    aiohttp.web.run_app(app, host="127.0.0.1", port=5000)
