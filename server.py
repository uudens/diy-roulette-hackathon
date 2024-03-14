from flask import Flask, Response
from lib import create_capture, read_frame
import cv2

app = Flask(__name__)

def convert_to_blue(frame):
    into_hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
    # changing the color format from BGr to HSV
    # This will be used to create the mask
    L_limit = np.array([98, 50, 50])  # setting the blue lower limit
    U_limit = np.array([139, 255, 255])  # setting the blue upper limit

    b_mask = cv2.inRange(into_hsv, L_limit, U_limit)
    # creating the mask using inRange() function
    # this will produce an image where the color of the objects
    # falling in the range will turn white and rest will be black
    blue = cv2.bitwise_and(frame, frame, mask=b_mask)
    # this will give the color to mask.

    return blue

def generate_frames():
    capture = create_capture()

    while True:
        frame = read_frame(capture)
        if frame is None:
            break
        else:
            # blue = convert_to_blue(frame)
            ret, buffer = cv2.imencode('.jpg', frame)
            encoded = buffer.tobytes()
            yield (b'--frame\r\n'
                   b'Content-Type: image/jpeg\r\n\r\n' + encoded + b'\r\n')

@app.route('/video')
def video_feed():
    # Route to stream video
    return Response(generate_frames(), mimetype='multipart/x-mixed-replace; boundary=frame')

# http://127.0.0.1:5000/video
if __name__ == '__main__':
    app.run(debug=True)