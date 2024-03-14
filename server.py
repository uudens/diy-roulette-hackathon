from flask import Flask, Response
from lib import create_capture, read_frame
import cv2 as cv
import numpy as np


app = Flask(__name__)


def convert_to_blue(frame, capture):
    into_hsv = cv.cvtColor(frame, cv.COLOR_BGR2HSV)
    # changing the color format from BGr to HSV
    # This will be used to create the mask
    L_limit = np.array([98, 50, 50])  # setting the blue lower limit
    U_limit = np.array([139, 255, 255])  # setting the blue upper limit

    b_mask = cv.inRange(into_hsv, L_limit, U_limit)
    # creating the mask using inRange() function
    # this will produce an image where the color of the objects
    # falling in the range will turn white and rest will be black
    blue = cv.bitwise_and(frame, frame, mask=b_mask)
    # this will give the color to mask.

    return blue

def draw_green(frame):
    # RGB: 3D7880
    # HSV: 187 52.3 50.2
    # targetCol = [187, 134, 129]
    # threshold = 0.1
    targetCol = [87, 134, 129]
    threshold = 0.5

    hsv = cv.cvtColor(frame, cv.COLOR_BGR2HSV)
    L_limit = np.array([targetCol[0] * (1 - threshold), targetCol[1] * (1 - threshold), targetCol[2] * (1 - threshold)])
    U_limit = np.array([targetCol[0] * (1 + threshold), targetCol[1] * (1 + threshold), targetCol[2] * (1 + threshold)])
    mask = cv.inRange(hsv, L_limit, U_limit)
    contours, hierarchy = cv.findContours(mask, cv.RETR_TREE, cv.CHAIN_APPROX_SIMPLE)
    kernel = np.ones((5, 5), np.uint8)
    mask = cv.morphologyEx(mask, cv.MORPH_OPEN, kernel)
    frame = cv.drawContours(frame, contours, -1, (0,255,0), 3)
    return frame

def warp_perspective(frame, capture):
    # https://theailearner.com/tag/cv2-getperspectivetransform/
    # 0 to 100
    pt_A = [18, 21]
    pt_B = [14, 105]
    pt_C = [92, 105]
    pt_D = [80, 20]

    # mask = cv.inRange(hsv, L_limit, U_limit)
    #
    # color = cv.bitwise_and(frame, frame, mask=mask)
    # gray = cv.cvtColor(color, cv.COLOR_BGR2GRAY)
    #
    # contours, hierarchy = cv.findContours(gray, cv.RETR_TREE, cv.CHAIN_APPROX_SIMPLE)
    # out = cv.drawContours(frame, contours, -1, (0,255,0), 3)

    w = capture.get(cv.CAP_PROP_FRAME_WIDTH) / 100
    h = capture.get(cv.CAP_PROP_FRAME_HEIGHT) / 100

    pt_A_abs = [int(pt_A[0] * w), int(pt_A[1] * h)]
    pt_B_abs = [int(pt_B[0] * w), int(pt_B[1] * h)]
    pt_C_abs = [int(pt_C[0] * w), int(pt_C[1] * h)]
    pt_D_abs = [int(pt_D[0] * w), int(pt_D[1] * h)]
    width_AD = np.sqrt(((pt_A_abs[0] - pt_D_abs[0]) ** 2) + ((pt_A_abs[1] - pt_D_abs[1]) ** 2))
    width_BC = np.sqrt(((pt_B_abs[0] - pt_C_abs[0]) ** 2) + ((pt_B_abs[1] - pt_C_abs[1]) ** 2))
    maxWidth = max(int(width_AD), int(width_BC))
    height_AB = np.sqrt(((pt_A_abs[0] - pt_B_abs[0]) ** 2) + ((pt_A_abs[1] - pt_B_abs[1]) ** 2))
    height_CD = np.sqrt(((pt_C_abs[0] - pt_D_abs[0]) ** 2) + ((pt_C_abs[1] - pt_D_abs[1]) ** 2))
    # maxHeight = max(int(height_AB), int(height_CD))
    maxHeight = maxWidth

    # Mark corners on frame
    col = [0, 255, 255]
    cv.line(frame, pt_A_abs, pt_B_abs, col, 2)
    cv.line(frame, pt_B_abs, pt_C_abs, col, 2)
    cv.line(frame, pt_C_abs, pt_D_abs, col, 2)
    cv.line(frame, pt_D_abs, pt_A_abs, col, 2)

    input_pts = np.float32([pt_A_abs, pt_B_abs, pt_C_abs, pt_D_abs])
    output_pts = np.float32([
        [0, 0],
        [0, maxHeight - 1],
        [maxWidth - 1, maxHeight - 1],
        [maxWidth - 1, 0]
    ])
    M = cv.getPerspectiveTransform(input_pts, output_pts)
    out = cv.warpPerspective(frame, M, (maxWidth, maxHeight), flags=cv.INTER_LINEAR)
    return out

def mark_winning(frame, capture):
    with_green = draw_green(frame)
    warped = warp_perspective(with_green, capture)
    return warped
def generate_frames(capture, f):
    while True:
        frame = read_frame(capture)
        if frame is None:
            break
        else:
            converted = f(frame, capture)
            ret, buffer = cv.imencode('.jpg', converted)
            encoded = buffer.tobytes()
            yield (b'--frame\r\n'
                   b'Content-Type: image/jpeg\r\n\r\n' + encoded + b'\r\n')


@app.route('/')
def hello_world():
    return 'Hello, World!'


mimeType = 'multipart/x-mixed-replace; boundary=frame'


@app.route('/recorded-video')
def recorded_video_feed():
    source = "wheel2.mp4"
    capture = cv.VideoCapture(source)
    return Response(generate_frames(capture, mark_winning), mimetype=mimeType)


@app.route('/live-video')
def live_video_feed():
    capture = create_capture()
    return Response(generate_frames(capture, convert_to_blue), mimetype=mimeType)


# http://127.0.0.1:5000/video
if __name__ == '__main__':
    app.run(debug=True)