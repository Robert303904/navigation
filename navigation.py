from multi_ball_tracker import FrameProcessor
import math

class Frame:
    """
    Starts the calculations done to locate the balls in the frame.
    :param frame: numpy array that is provided from cv2:VideoCapture:read()
    :param color_range: a dictionary in the form of
        {color_identifier : (hsv_min, hsv_max) } as calculated from
        range-detector.py
    :param frame_count: optional interger used to describe the frame number
    """
    def __init__(self, frame, color_range, servo_angle=0,
		target_spacing=1, camera_ratio=0.0189634, frame_count=0):
        self.frame = frame
        self.color_range = color_range
		self.target_spacing = target_spacing
		self.camera_ratio = camera_ratio
        self.frame_count = frame_count
        self.frameProcessor = FrameProcessor(frame, frame_count, color_range)
        self.frameProcessor.start()

    """
    Checks to see if the frame processor has finished calculating
    the location of balls in the frame
    """
    def result_available(self):
        return self.frameProcessor.isAlive()

    def get_balls(self):
	return self.frameProcessor.get_balls()

    """
    Calculate the position of the robot using the center point coordinates of the balls/targets.
    Ball1 is the origin
	    ----------------------------
	    |			      		   |
	    |    A    Starting     B   |
	    |                          |
   	BLUE|Ball1a              Ball1b|RED
   GREEN|Ball2a              Ball2b|GREEN
 	 RED|Ball3a              Ball3b|BLUE
   	    |                          |
 	    |                          |
 	   ^|                          |
  	   ||          Mining          |
	   y----------------------------
      (0,0) x->
    """
    def calculate_xyr(self, balls):
        ## TODO: Calculate rotation
		ordered_balls  = sorted(balls.values())
        angle1 = ratio * math.sqrt(math.pow(balls[1].x - balls[2].x, 2) + math.pow(balls[1].y - balls[2].y, 2))
        angle2 = ratio * math.sqrt(math.pow(balls[2].x - balls[3].x, 2) + math.pow(balls[2].y - balls[3].y, 2))
        num = targetSpacing * sin(angle1+angle2)
        den = (targetSpacing * sin(angle2) / sin(angle1)) - (targetSpacing * cos(angle1+angle2))
        alpha = atan(num/den)
        r = targetSpacing * sin(angle1 + alpha) / sin(angle1)
        x = r * sin(alpha)
        y = r * cos(alpha)
        return(x,y,r)

class CameraCapture:
    def __init__(self):
        pass

    def get_current_position(self):
        pass

class Navigation(threading.Thread):

    def __init__(self, autonomy):
        self.autonomy = autonomy
        self.run_flag = True
        self.camera = CameraCapture()

    def run(self):
        while self.run_flag:
            position = camera.get_current_position()
            autonomy.update_current_position(position)


if __name__ == "__main__":
    pass
