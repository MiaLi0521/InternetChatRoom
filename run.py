from catchat import create_app
from catchat import socketio

if __name__ == "__main__":
    app = create_app('production')
    socketio.run(app)
