import cv2 as cv


def is_raspberry_pi():
    try:
        with open('/sys/firmware/devicetree/base/model', 'r') as f:
            return 'Raspberry Pi' in f.read()
    except Exception:
        return False


def create_capture():
    if is_raspberry_pi():
        from picamera2 import Picamera2

        global picam2

        if not picam2:
            picam2 = Picamera2()
            picam2.configure(picam2.create_preview_configuration(main={"format": 'XRGB8888', "size": (640, 480)}))
            picam2.start()

        return picam2
    else:
        return cv.VideoCapture(0)


def read_frame(capture):
    if isinstance(capture, cv.VideoCapture):
        # ret will return a true value if the frame exists otherwise False
        success, frame = capture.read()
        if not success:
            return None
        else:
            return frame
    else:
        return capture.capture_array()

def get_width_height(capture):
    if isinstance(capture, cv.VideoCapture):
        w = capture.get(cv.CAP_PROP_FRAME_WIDTH)
        h = capture.get(cv.CAP_PROP_FRAME_HEIGHT)
        return w, h
    else:
        w = 640
        h = 480
        return w, h
