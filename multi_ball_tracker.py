# USAGE
# python ball_tracking.py --video ball_tracking_example.mp4
# python ball_tracking.py

# import the necessary packages
from collections import deque
from copy import deepcopy
import numpy as np
import argparse
import imutils
import cv2
import threading
from timeit import default_timer as timer

class ColorProcessor (threading.Thread):
    def __init__(self, hsv, frame, color, color_bounds):
        threading.Thread.__init__(self)
        self.hsv = hsv
        self.frame = frame
        self.color = color
        self.color_bounds = color_bounds
        self.circle_center = (-1, -1)
        self.moment_center = None
        self.radius_circle = 0
        
    def run(self):
        mask = cv2.inRange(self.hsv, self.color_bounds['lower'], self.color_bounds['upper'])
	mask = cv2.erode(mask, None, iterations=2)
	mask = cv2.dilate(mask, None, iterations=2)
	cnts = cv2.findContours(mask.copy(), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)[-2]
	if len(cnts) > 0:
	    c = max(cnts, key=cv2.contourArea)
	    (self.circle_center, self.radius_circle) = cv2.minEnclosingCircle(c)
	    M = cv2.moments(c)
	    center = (int(M["m10"] / M["m00"]), int(M["m01"] / M["m00"]))
	    if self.radius_circle > 10:
                self.moment_center = center


    def join(self):
        threading.Thread.join(self)
        return (self.color, self.circle_center, self.moment_center, self.radius_circle)

class FrameProcessor(threading.Thread):

    def __init__(self, frame, frame_count, color_range):
        threading.Thread.__init__(self)
        self.frame = frame
        self.frame_count = frame_count
        self.color_range = color_range
        self.threads = []

    def run(self):
        # resize the frame
        #frame = imutils.resize(frame, width=600)
        
        # convert the frame to HSV
        hsv = cv2.cvtColor(self.frame, cv2.COLOR_BGR2HSV)
    
        # process the frame for every different ball
        for color in color_range:
            processor = ColorProcessor(hsv, self.frame, color, self.color_range[color])
            self.threads.append(processor)
            processor.start()

    def join(self):
        threading.Thread.join(self)
        display = args.get("display")
        balls={}
        for thread in self.threads:
            (color, circle_center, moment_center, radius) = thread.join()
            if radius > 10:
                balls[color] = (circle_center, moment_center, radius)
                if display:
                    (x, y) = circle_center
                    cv2.putText(self.frame, color, (int(x), int(y)), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)
                    cv2.circle(self.frame, (int(x), int(y)), int(radius),(0, 255, 255), 2)
                    cv2.circle(self.frame, moment_center, 5, (0, 0, 255), -1)
        if display:
            cv2.putText(self.frame, str("frame: " + str(self.frame_count)), (10, 20), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)
            cv2.imshow("Frame", self.frame)
        return balls

def process_video(color_range, camera):
    i = 0
    total_time = 0
    try:
        while True:
            i += 1
            # grab the current frame
            (grabbed, frame) = camera.read()
            # then we have reached the end of the video
            if args.get("video") and not grabbed:
                break
            key = cv2.waitKey(1) & 0xFF
            # if the 'q' key is pressed, stop the loop
            if key == ord("q"):
                break
            beginning_time = timer() 
            frame_processor = FrameProcessor(frame, i, color_range)
            frame_processor.start()
            print(frame_processor.join())
            ending_time = timer()
            total_time += (ending_time - beginning_time)
    except(KeyboardInterrupt):
        pass 
    print("average frame time:", (total_time/i))
def main (color_range, camera):
    process_video(color_range, camera)

if __name__ == "__main__":
    # construct the argument parse and parse the arguments
    ap = argparse.ArgumentParser()

    ap.add_argument("-d", "--display", type=bool, default=False,
            help="display to hdmi?")
    ap.add_argument("-v", "--video",
            help="path to the (optional) video file")
    ap.add_argument("-b", "--buffer", type=int, default=10,
            help="max buffer size")
    args = vars(ap.parse_args())

    # define the lower and upper boundaries of the "green"
    # ball in the HSV color space, then initialize the
    # list of tracked points
    color_range = {
        'green': {'lower': (14, 45, 69), 'upper': (54, 129, 242)},
        'red': {'lower': (000, 136, 145), 'upper': (196, 255, 255)},
        'blue': {'lower': (94, 170, 125), 'upper': (117, 255, 255)},
        #'white' :{ 'lower': (34, 20, 179), 'upper': (142, 255, 255)},
        #'orange' : { 'lower': (8, 133,138), 'upper': (25, 255, 255)}
    }

    # if a video path was not supplied, grab the reference
    # to the webcam
    if not args.get("video", False):
        camera = cv2.VideoCapture(0)

    # otherwise, grab a reference to the video file
    else:
        camera = cv2.VideoCapture(args["video"])
    # cleanup the camera and close any open windows
    main(color_range, camera)
    camera.release()
    cv2.destroyAllWindows()
