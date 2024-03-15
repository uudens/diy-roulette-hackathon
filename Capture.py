from abc import ABC, abstractmethod
import cv2 as cv


class Capture(ABC):

    @abstractmethod
    def read_frame(self):
        pass

    @abstractmethod
    def get_width_height(self) -> tuple[float, float]:
        pass


    @abstractmethod
    def get_frame_rate(self) -> float:
        pass

class CvCapture(Capture):

    def __init__(self, source):
        # Source can be a path (file capture) or an integer (live capture)
        self.capture = cv.VideoCapture(source)

    def read_frame(self):
        success, frame = self.capture.read()
        if not success:
            print("Failed to read frame from capture source.")
            return None
        else:
            return frame

    def get_width_height(self) -> tuple[float, float]:
        w = self.capture.get(cv.CAP_PROP_FRAME_WIDTH)
        h = self.capture.get(cv.CAP_PROP_FRAME_HEIGHT)
        return w, h

    def get_frame_rate(self) -> float:
        return self.capture.get(cv.CAP_PROP_FPS)

class RaspberryCapture(Capture):
    picamera = None
    resolution = (640, 480)

    def __init__(self, width=640, height=480):
        RaspberryCapture.resolution = (width, height)
        if RaspberryCapture.picamera is None:
            from picamera2 import Picamera2
            RaspberryCapture.picamera = Picamera2()
            try:
                RaspberryCapture.picamera.configure(RaspberryCapture.picamera.create_preview_configuration(main={"format": 'XRGB8888', "size": RaspberryCapture.resolution}))
                RaspberryCapture.picamera.start()
                RaspberryCapture.picamera.set_controls({"AfMode": 2, "AfTrigger": 0})
            except Exception as e:
                print(f"Failed to initialize Picamera2: {e}")

    def read_frame(self):
        if RaspberryCapture.picamera is not None:
            return RaspberryCapture.picamera.capture_array()
        else:
            print("Picamera2 is not initialized, cannot read frame.")
            return None

    def get_width_height(self) -> tuple[float, float]:
        return RaspberryCapture.resolution

    def get_frame_rate(self) -> float:
        return 60


def is_raspberry_pi() -> bool:
    try:
        with open('/sys/firmware/devicetree/base/model', 'r') as f:
            return 'Raspberry Pi' in f.read()
    except Exception:
        return False


def create_live_capture() -> Capture:
    if is_raspberry_pi():
        return RaspberryCapture()
    else:
        return CvCapture(0)


def create_file_capture(source) -> Capture:
    return CvCapture(source)
