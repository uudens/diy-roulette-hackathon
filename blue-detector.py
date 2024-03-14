import cv2
import numpy as np


def is_raspberry_pi():
    try:
        with open('/sys/firmware/devicetree/base/model', 'r') as f:
            return 'Raspberry Pi' in f.read()
    except Exception:
        return False


def create_capture():
    if is_raspberry_pi():
        from picamera2 import Picamera2

        picam2 = Picamera2()
        picam2.configure(picam2.create_preview_configuration(main={"format": 'XRGB8888', "size": (640, 480)}))
        picam2.start()

        return picam2
    else:
        return cv2.VideoCapture(0)


def read_frame(capture):
    if is_raspberry_pi():
        return capture.capture_array()
    else:
        # ret will return a true value if the frame exists otherwise False
        ret, frame = capture.read()
        return frame


if __name__ == '__main__':
    capture = create_capture()

    while True:
        frame = read_frame(capture)

        into_hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
        # changing the color format from BGr to HSV
        # This will be used to create the mask
        L_limit = np.array([98, 50, 50])  # setting the blue lower limit
        U_limit = np.array([139, 255, 255])  # setting the blue upper limit

        b_mask = cv2.inRange(into_hsv, L_limit, U_limit)
        # creating the mask using inRange() function
        # this will produce an image where the color of the objects
        # falling in the range will turn white and rest will be black
        blue=cv2.bitwise_and(frame, frame, mask=b_mask)
        # this will give the color to mask.
        cv2.imshow('Original', frame) # to display the original frame
        cv2.imshow('Blue Detector', blue) # to display the blue object output

        if cv2.waitKey(1) == 27:
            break
        # this function will be triggered when the ESC key is pressed
        # and the while loop will terminate and so will the program

    capture.release()

    cv2.destroyAllWindows()