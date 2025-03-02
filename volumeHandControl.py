import cv2
import time
import numpy as np
import HandTrackingModule as htm
import math
from comtypes import CLSCTX_ALL
from pycaw.pycaw import AudioUtilities, IAudioEndpointVolume

######################
wCam, hCam = 640, 480
######################

cap = cv2.VideoCapture(0)
cap.set(3, wCam)
cap.set(4, hCam)
pTime = 0
detector = htm.handDetector(detectionCon=0.7)

devices = AudioUtilities.GetSpeakers()
interface = devices.Activate( IAudioEndpointVolume._iid_, CLSCTX_ALL, None)
volume = interface.QueryInterface(IAudioEndpointVolume)
volume.GetMute()
volume.GetMasterVolumeLevel()
volume_range = volume.GetVolumeRange()

min_vol = volume_range[0]
max_vol = volume_range[1]
vol = 0
vol_percentage = 0
vol_bar = 400

while True:
    success, img = cap.read()
    img = detector.findHands(img)
    lmlist = detector.findpos(img, draw=False)
    if len(lmlist) != 0:
        # print(lmlist[4], lmlist[8])

        x1, y1 = lmlist[4][1], lmlist[4][2]
        x2, y2 = lmlist[8][1], lmlist[8][2]
        cx, cy = (x1 + x2) // 2, (y1 + y2) // 2

        cv2.circle(img, (x1, y1), 10, (255, 0, 255), cv2.FILLED)
        cv2.circle(img, (x2, y2), 10, (255, 0, 255), cv2.FILLED)
        cv2.circle(img, (cx, cy), 10, (255, 0, 255), cv2.FILLED)
        cv2.line(img, (x1, y1), (x2, y2), (255, 0, 255), 3)


        length = math.hypot(x2 - x1, y2 - y1)
        # print(length)

        # hand range = 50 - 300
        # vol range = 0, 63

        vol = np.interp(length, [20, 250], [min_vol, max_vol])  ## numpy
        vol_bar = np.interp(length, [20, 250], [400, 150])  ## numpy
        vol_percentage = np.interp(length, [20, 250], [0, 100])  ## numpy

        print(int(length), vol)
        volume.SetMasterVolumeLevel(vol, None)

        if length < 25:
            cv2.circle(img, (cx, cy), 10, (0, 255, 0), cv2.FILLED)

    cv2.rectangle(img, (50, 150), (85, 400), (0, 255, 0), 3)
    cv2.rectangle(img, (50, int(vol_bar)), (85, 400), (0, 255, 0), cv2.FILLED)
    cv2.putText(img, f'{int(vol_percentage)}%', (40, 450), cv2.FONT_HERSHEY_COMPLEX, 1, (0, 255, 0), 3)

    cTime = time.time()
    fps = 1 / (cTime - pTime)
    pTime = cTime

    cv2.putText(img, f'FPS: {int(fps)}', (40, 50), cv2.FONT_HERSHEY_COMPLEX, 1, (255, 0, 0), 3)
    cv2.imshow("Image", img)
    cv2.waitKey(1)
