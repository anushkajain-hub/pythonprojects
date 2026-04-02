import cv2

# create ONCE before the loop
cap = cv2.VideoCapture(0)
bg_subtractor = cv2.createBackgroundSubtractorMOG2(
    history=500, varThreshold=50, detectShadows=False
)

while True:
    ret, frame = cap.read()

    # draw zone
    cv2.rectangle(frame, (0, 0), (250, 400), (255, 165, 0), 2)
    cv2.putText(frame, "BLIND SPOT", (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 165, 0), 2)

    # motion detection
    fg_mask = bg_subtractor.apply(frame)

    # crop to zone and count moving pixels
    blind_region = fg_mask[0:400, 0:250]
    motion_pixels = cv2.countNonZero(blind_region)

    # alert if enough motion
    if motion_pixels > 2000:
        cv2.putText(frame, "MOTION DETECTED!", (10, 60),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 0, 255), 2)

    # show both windows
    cv2.imshow("SafeX", frame)
    cv2.imshow("Motion Mask", fg_mask)

    if cv2.waitKey(1) == ord('s'):
        break

cap.release()
cv2.destroyAllWindows()  # note the 's' at the end


#The golden rule to remember:**

#before loop  → setup things once (cap, bg_subtractor)inside loop  → everything that runs on every frameafter loop   → cleanup (release, destroyAllWindows)