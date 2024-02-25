from . import base
import cv2
import numpy as np
# from pynput import keyboard
import time
import curses

class Config(base.Config):
    pass


class Brain(base.Brain):

    """The autonomous Brain object, drives the vehicle autonomously based on information gathered by the sensors"""

    def __init__(self, config: Config, *arg):
        super().__init__(config, *arg)
        
        self.state = "forward"
        self.next_state = "forward"
        
    # def on_press(self, key):
    #     try:
    #         if key.char == 'q':  # If 'q' is pressed
    #             self.next_state = "kill"
    #             # Stop listener
    #             return False
    #     except AttributeError:
    #         pass  # Handle special key presses that don't involve characters here if needed
        
    def line_following(self):
        image = cv2.rotate(self.camera.image_array, cv2.ROTATE_180)
        image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
        hsl_image = cv2.cvtColor(image, cv2.COLOR_BGR2HLS)
        rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
        cv2.imwrite('rgb2_image.jpg', image)

        lower_blue = np.array([90, 70, 170])
        upper_blue = np.array([150, 235, 255])

        # Threshold the HSV image to get only blue colors
        mask = cv2.inRange(hsl_image, lower_blue, upper_blue)
        cv2.imwrite('after_mask.jpg', mask)

        # Find contours in the mask
        contours, _ = cv2.findContours(mask, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)

        next_state = None
        if contours:
            # Assume the largest contour is the blue line
            largest_contour = max(contours, key=cv2.contourArea)
            M = cv2.moments(largest_contour)
            
            if M["m00"] != 0:
                # Calculate the center of the contour
                cx = int(M["m10"] / M["m00"])
                cy = int(M["m01"] / M["m00"])
                print("LINE DETECTED!")  
                
                img_center = image.shape[1] // 2  # Get the center x-coordinate of the image
                
                if cx < img_center - 40:  # Threshold to avoid minor deviations
                    self.vehicle.pivot_right(0.35)
                elif cx > img_center + 40:
                    self.vehicle.pivot_left(0.35)
                else:
                    self.vehicle.drive_forward(0.5)
                    
                next_state = "forward"
            else:
                print("Contour too small or not detected")  # Default action if contour is too small or not detected
                # self.vehicle.stop()
                next_state = "forward"
                # TODO: do something different maybe
        else:
            print("No blue line detected")  # Default action if no blue line is detected
            next_state = "forward"
            # TODO: do something different maybe
            
        return next_state
            
    # Returns True if the distance to the front is less than 0.25m
    def check_front_distance(self):
        print(self.distance_sensors[0].distance, self.distance_sensors[1].distance)
        if self.distance_sensors[0].distance < 0.1:
            return True
        
        return False

    def logic(self):
        """
        Find the blue line in the camera feed, and drive the vehicle to follow it
        """
        try:
            # print(self.sample_hz)
            self.state = self.next_state
        
            print(self.state)
            match self.state:
                case "forward":
                    if self.check_front_distance():
                        self.next_state = "avoid"
                        return
                    
                    print("line following")
                    self.next_state = self.line_following() # should call drive_forward and sets next_state
                    
                case "avoid":
                    print("avoid")
                    self.vehicle.stop()
                    self.next_state = "stop"
                    
                case "stop":
                    self.vehicle.stop()
                    self.next_state = "stop"
                    
                case "kill":
                    print("kill state")
                    self.vehicle.stop()
                    self.next_state = None
                    return

                case _:
                    self.vehicle.stop()
                    self.next_state = None
                    return
                 
        except KeyboardInterrupt as e:
            print(e)
            self.vehicle.stop()
            self.next_state = None
            return