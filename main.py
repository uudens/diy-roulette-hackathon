import numpy as np
import cv2 as cv

# https://theailearner.com/tag/cv2-getperspectivetransform/
# 0 to 100
pt_A = [18, 21]
pt_B = [14, 105]
pt_C = [92, 105]
pt_D = [80, 20]

source = "wheel2.mp4"
# cap = cv.VideoCapture(0)
cap = cv.VideoCapture(source)

if not cap.isOpened():
    print("Cannot open source")
    exit()

# RGB: 3D7880
# HSV: 187 52.3 50.2
# targetCol = [187, 134, 129]
# threshold = 0.1
targetCol = [87, 134, 129]
threshold = 0.5

cv.namedWindow('frame')

def onChangeH(val):
    targetCol[0] = val

def onChangeThreshold(val):
    global threshold
    threshold = val / 100

def setPt(pt, index, val):
    pt[index] = val

cv.createTrackbar('H', 'frame', targetCol[0], 255, onChangeH)
cv.createTrackbar('Threshold', 'frame', int(threshold * 100), 100, onChangeThreshold)
cv.createTrackbar('Ax', 'frame', pt_A[0], 120, lambda val: setPt(pt_A, 0, val))
cv.createTrackbar('Ay', 'frame', pt_A[1], 120, lambda val: setPt(pt_A, 1, val))
cv.createTrackbar('Bx', 'frame', pt_B[0], 120, lambda val: setPt(pt_B, 0, val))
cv.createTrackbar('By', 'frame', pt_B[1], 120, lambda val: setPt(pt_B, 1, val))
cv.createTrackbar('Cx', 'frame', pt_C[0], 120, lambda val: setPt(pt_C, 0, val))
cv.createTrackbar('Cy', 'frame', pt_C[1], 120, lambda val: setPt(pt_C, 1, val))
cv.createTrackbar('Dx', 'frame', pt_D[0], 120, lambda val: setPt(pt_D, 0, val))
cv.createTrackbar('Dy', 'frame', pt_D[1], 120, lambda val: setPt(pt_D, 1, val))

def on_mouse_click (event, x, y, flags, frame):
    if event == cv.EVENT_LBUTTONUP:
        col = frame[y,x].tolist()
        print("yo", col)
        targetCol[0] = col[0]
        targetCol[1] = col[1]
        targetCol[2] = col[2]

while True:
    # Capture frame-by-frame
    ret, frame = cap.read()
    # if frame is read correctly ret is True
    if not ret:
        print("No frame, trying to repeat capture")
        cap = cv.VideoCapture(source)
        ret, frame = cap.read()

    hsv = cv.cvtColor(frame, cv.COLOR_BGR2HSV)
    L_limit = np.array([targetCol[0] * (1 - threshold), targetCol[1] * (1 - threshold), targetCol[2] * (1 - threshold)])
    U_limit = np.array([targetCol[0] * (1 + threshold), targetCol[1] * (1 + threshold), targetCol[2] * (1 + threshold)])
    mask = cv.inRange(hsv, L_limit, U_limit)
    contours, hierarchy = cv.findContours(mask, cv.RETR_TREE, cv.CHAIN_APPROX_SIMPLE)
    kernel = np.ones((5, 5), np.uint8)
    mask = cv.morphologyEx(mask, cv.MORPH_OPEN, kernel)
    frame = cv.drawContours(frame, contours, -1, (0,255,0), 3)
    # cv.imshow('mask', mask)
    # cv.imshow('frame', frame)

    # key = cv.waitKey(1)
    # if key == ord('q'):
    #     break
    # if key == ord('p'):
    #     cv.waitKey(-1)

    # continue


    mask = cv.inRange(hsv, L_limit, U_limit)
    color = cv.bitwise_and(frame, frame, mask=mask)
    cv.imshow('mask', mask)
    gray = cv.cvtColor(color, cv.COLOR_BGR2GRAY)

    contours, hierarchy = cv.findContours(gray, cv.RETR_TREE, cv.CHAIN_APPROX_SIMPLE)
    # out = cv.drawContours(frame, contours, -1, (0,255,0), 3)

    w = cap.get(cv.CAP_PROP_FRAME_WIDTH) / 100
    h = cap.get(cv.CAP_PROP_FRAME_HEIGHT) / 100

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
    col = [0,255,255]
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

    largestRadius = 0
    largestCenter = None
    for cnt in contours:
        (x,y),radius = cv.minEnclosingCircle(cnt)
        center = (int(x),int(y))
        radius = int(radius)
        if (radius > largestRadius):
            largestCenter = center
            largestRadius = radius
    
    if (largestCenter != None):
        cv.circle(frame, largestCenter, largestRadius,(0,255,0),2)

    cv.imshow('frame', frame)
    cv.setMouseCallback('frame', on_mouse_click, hsv)
    cv.imshow('out', out)
    key = cv.waitKey(1)
    if key == ord('q'):
        break
    if key == ord('p'):
        cv.waitKey(-1)
    
    print(targetCol, threshold)
# When everything done, release the capture
cap.release()
cv.destroyAllWindows()