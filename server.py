from flask import Flask, Response
from lib import create_capture, read_frame
import cv2

app = Flask(__name__)

def generate_frames():
    capture = create_capture()

    while True:
        frame = read_frame(capture)
        if frame is None:
            break
        else:
            ret, buffer = cv2.imencode('.jpg', frame)
            frame = buffer.tobytes()
            yield (b'--frame\r\n'
                   b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')

@app.route('/video_feed')
def video_feed():
    # Route to stream video
    return Response(generate_frames(), mimetype='multipart/x-mixed-replace; boundary=frame')

# http://127.0.0.1:5000/video_feed
if __name__ == '__main__':
    app.run(debug=True)