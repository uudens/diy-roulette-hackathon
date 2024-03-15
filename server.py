from flask import Flask, Response, request
from Capture import *
from WinningNumberDetector import detect_winning_number
from webui import webui_root
import cv2 as cv
import json
import cv2
import numpy as np
import math
from SensorValueTracker import SensorValueTracker
import time


app = Flask(__name__)


def detect_angle(frame, hsv_values_key: str, contour_colour: tuple[int, int, int], midpoint_colour: tuple[int, int, int]):
    global config
    hsv_values = config["colors_hsv"][hsv_values_key]

    L_limit = np.array(hsv_values[0])
    U_limit = np.array(hsv_values[1])
    hsv = cv.cvtColor(frame, cv.COLOR_BGR2HSV)
    mask = cv.inRange(hsv, L_limit, U_limit)
    contours, hierarchy = cv.findContours(mask, cv.RETR_TREE, cv.CHAIN_APPROX_SIMPLE)
    kernel = np.ones((5, 5), np.uint8)
    mask = cv.morphologyEx(mask, cv.MORPH_OPEN, kernel)
    frame = cv.drawContours(frame, contours, -1, contour_colour, 3)

    if contours:
        largest_contour = max(contours, key=cv.contourArea)
        M = cv.moments(largest_contour)
        if M["m00"] != 0:
            cX = int(M["m10"] / M["m00"])
            cY = int(M["m01"] / M["m00"])
        else:
            # Default to center if contour is too small
            cX, cY = frame.shape[1]//2, frame.shape[0]//2
        cv.drawContours(frame, [largest_contour], -1, contour_colour, 3)
        # Draw centroid
        cv.circle(frame, (cX, cY), 5, midpoint_colour, -1)

        frame_center_x, frame_center_y = frame.shape[1] // 2, frame.shape[0] // 2
        cv.circle(frame, (frame_center_x, frame_center_y), 5, (128, 128, 44), -1) # Show center

        # Calculate the angle in radians, then convert to degrees
        angle_rad = math.atan2(cY - frame_center_y, cX - frame_center_x)
        angle_deg = math.degrees(angle_rad)

        return frame, angle_deg
    else:
        return frame, None


def warp_perspective(frame, capture: Capture):
    # https://theailearner.com/tag/cv2-getperspectivetransform/
    # 0 to 100
    global config
    corners = config["corners"]
    pt_A = corners[0]
    pt_B = corners[1]
    pt_C = corners[2]
    pt_D = corners[3]

    # mask = cv.inRange(hsv, L_limit, U_limit)
    #
    # color = cv.bitwise_and(frame, frame, mask=mask)
    # gray = cv.cvtColor(color, cv.COLOR_BGR2GRAY)
    #
    # contours, hierarchy = cv.findContours(gray, cv.RETR_TREE, cv.CHAIN_APPROX_SIMPLE)
    # out = cv.drawContours(frame, contours, -1, (0,255,0), 3)

    w, h = capture.get_width_height()
    w = w / 100
    h = h / 100

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


sensor_value_tracker: SensorValueTracker = SensorValueTracker(threshold_seconds=2)


def mark_winning(frame, capture: Capture):
    global sensor_value_tracker
    if config["transform"]:
        frame2 = warp_perspective(frame, capture)
    else:
        frame2 = frame

    frame3, zero_angle_deg = detect_angle(frame2, "zero", (0, 255, 0), (255, 0, 0))
    frame4, ball_angle_deg = detect_angle(frame3, "ball", (255, 255, 0), (255, 0, 255))

    if zero_angle_deg is not None and ball_angle_deg is not None:
        winning = detect_winning_number(zero_angle_deg, ball_angle_deg)
        sensor_value_tracker.report_value(winning)
        permanent_winning = sensor_value_tracker.get_value()

        cv.putText(frame4, f"Winning = {permanent_winning} (tmp: {winning}, ZA: {zero_angle_deg:.0f}, BA: {ball_angle_deg:.0f})", (0, 30), cv.FONT_HERSHEY_SIMPLEX, 0.7, (255, 0, 255), 2)

    return frame4


def generate_frames(capture: Capture, f):
    while True:
        frame = capture.read_frame()
        if frame is None:
            break
        else:
            converted = f(frame, capture)
            ret, buffer = cv2.imencode('.jpg', converted)
            encoded = buffer.tobytes()
            yield (b'--frame\r\n'
                   b'Content-Type: image/jpeg\r\n\r\n' + encoded + b'\r\n')


def generate_frames_respecting_frame_rate(capture: Capture, f):
    frame_rate = capture.get_frame_rate()  # Assuming Capture class has this method
    time_between_frames = 1 / frame_rate

    while True:
        frame_start_time = time.time()
        frame = capture.read_frame()
        if frame is None:
            break
        else:
            converted = f(frame, capture)
            ret, buffer = cv2.imencode('.jpg', converted)
            encoded = buffer.tobytes()
            yield (b'--frame\r\n'
                   b'Content-Type: image/jpeg\r\n\r\n' + encoded + b'\r\n')
        time_elapsed = time.time() - frame_start_time
        sleep_time = time_between_frames - time_elapsed
        if sleep_time > 0:
            time.sleep(sleep_time)


config = json.loads("""{
    "colors_hsv": {
        "zero": [[45,119,60], [65,171,112]],
        "ball": [[92, 200, 116], [112, 255, 255]]
    },
    "corners": 
       [[27, 22], [23, 103], [82, 101], [72, 21]]
    ,
    "transform": true
}""")


@app.route('/')
def root():
    return webui_root(json.dumps(config))


@app.route('/configure', methods=['POST'])
def configure():
    global config
    config = request.json
    print("config updated", config)
    return "OK"


def __streaming_response(capture: Capture) -> Response:
    mime_type = 'multipart/x-mixed-replace; boundary=frame'
    return Response(generate_frames_respecting_frame_rate(capture, mark_winning), mimetype=mime_type)


@app.route('/recorded-video')
def recorded_video_feed() -> Response:
    capture = create_file_capture("test.mp4")
    return __streaming_response(capture)


@app.route('/live-video')
def live_video_feed() -> Response:
    capture = create_live_capture()
    return __streaming_response(capture)


# http://127.0.0.1:5555/
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5555, debug=True)
