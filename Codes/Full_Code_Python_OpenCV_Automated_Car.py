import cv2
import time
import numpy as np
import argparse
from PIL import ImageGrab
from directkeys import PressKey, ReleaseKey, W, A, S, D

def straight():
    PressKey(W)
    ReleaseKey(A)
    ReleaseKey(D)
    ReleaseKey(S)

def left():
    PressKey(A)
    time.sleep(0.225)
    ReleaseKey(W)
    ReleaseKey(D)
    ReleaseKey(A)

def right():
    PressKey(D)
    time.sleep(0.225)
    ReleaseKey(A)
    ReleaseKey(W)
    ReleaseKey(D)

def stop():
    PressKey(S)
    ReleaseKey(A)
    ReleaseKey(W)
    ReleaseKey(D)

def slow_down():
    ReleaseKey(W)
    ReleaseKey(A)
    ReleaseKey(D)
    ReleaseKey(S)

def roi(video, vertices):
    mask_roi = np.zeros_like(video)
    cv2.fillPoly(mask_roi, vertices, 255)
    masked = cv2.bitwise_and(video, mask_roi)
    return masked

def mask(video):
    #white
    lower = np.array([9, 50, 9], dtype = 'uint8')
    upper = np.array([90, 255, 70], dtype = 'uint8')
    #yellow
    lower2 = np.array([10, 0, 100], dtype = 'uint8')
    upper2 = np.array([40, 255, 255], dtype = 'uint8')
    mask = cv2.inRange(video, lower, upper)
    mask2 = cv2.inRange(video, lower2, upper2)
    new_mask = mask + mask2
    output = cv2.bitwise_and(video, video, mask=new_mask)
    return output

def average_slope_intercept(lines):

    left_lines    = [] # (slope, intercept)
    left_weights  = [] # (length,)
    
    right_lines   = [] # (slope, intercept)
    right_weights = [] # (length,)

    try:
        for line in lines:
            for x1, y1, x2, y2 in line:
                if x2==x1:
                    continue # ignore a vertical line
                if y2==y1:
                    continue # so that slope will not be zero which will give error when calculating x1 x2 later on
                slope = (y2-y1)/(x2-x1)
                intercept = y1 - slope*x1
                length = np.sqrt((y2-y1)**2+(x2-x1)**2)
                # y values goes from 0 at the top to 600 at the bottom. Hence the gradients are reversed.
                if slope < -0.48: 
                    left_lines.append((slope, intercept))
                    left_weights.append((length))
                elif slope > 0.48:
                    right_lines.append((slope, intercept))
                    right_weights.append((length))
                    
        # Averaging out the lines, longer lines will have more weight in the average slope and intercept
        left_lane  = np.dot(left_weights,  left_lines) /np.sum(left_weights) if len(left_weights) >0 else None
        right_lane = np.dot(right_weights, right_lines)/np.sum(right_weights) if len(right_weights)>0 else None
        return left_lane, right_lane # (slope, intercept), (slope, intercept)

    except Exception as e:
        #print(str(e))
        pass
     
def make_line_points(y1, y2, line):
    """
    Convert a line represented in slope and intercept into pixel points
    """
    if line is None:
        return None
#look at https://github.com/paramaggarwal/CarND-LaneLines-P1/blob/master/P1.ipynb for average moving lines
    
    slope, intercept = line
    
    # make sure everything is integer as cv2.line requires it
    x1 = int((y1 - intercept)/slope)
    x2 = int((y2 - intercept)/slope)
    y1 = int(y1)
    y2 = int(y2)
    
    return ((x1, y1), (x2, y2))

def get_middle_xcoordinate(y_centre, line):
    try:
        if line is None:
            return None
        slope, intercept = line
        x_centre = int((y_centre - intercept)/slope)
        return x_centre
    except Exception as e:
    #print(str(e))
        pass

def middle_xcoordinate(lines):
    try:
        left_lane, right_lane = average_slope_intercept(lines)
        y_centre = 300
        left_x = get_middle_xcoordinate(y_centre, left_lane)
        right_x = get_middle_xcoordinate(y_centre, right_lane)
        return left_x, right_x
    except Exception as e:
    #print(str(e))
        pass

def lane_lines(lines):
    if lines is not None:
        try:
            
            left_lane, right_lane = average_slope_intercept(lines)
            
            y1 = 400 # bottom of the image
            y2 = 250 # slightly lower than the middle

            left_line  = make_line_points(y1, y2, left_lane)
            right_line = make_line_points(y1, y2, right_lane)
            return left_line, right_line
        
        except Exception as e:
            #print(str(e))
            pass

def draw_lane_lines(image, lines, color=[255, 0, 0], thickness=20):
    # make a separate image to draw lines and combine with the orignal later
    try:

        line_image = np.zeros_like(image)
        
        for line in lines:
            if line is not None:
                cv2.line(line_image, *line,  color, thickness)

        # image1 * α + image2 * β + λ
        # image1 and image2 must be the same shape.
        return cv2.addWeighted(image, 1.0, line_image, 0.95, 0.0)
    
    except Exception as e:
        #print(str(e))
        pass

def process_img(image):
    vertices = np.array([[0,410], [800,410], [800,300], [700,300], [700,240], [100,240], [100,325], [0,325]], np.int32)
    # diagonal roi will create line and cause inaccuracy
    processed_img = cv2.cvtColor(image, cv2.COLOR_BGR2HLS)
    processed_img = mask(processed_img)
    # for some reason roi has to go after masking
    processed_img = roi(processed_img, [vertices])
    '''The GaussianBlur takes a kernel_size parameter which you'll need to play with to find one that works best.
    I tried 3, 5, 9, 11, 15, 17 (they must be positive and odd). The bigger the kernel_size value is,
    the more blurry the image becomes. The bigger kearnel_size value requires more time to process.
    Smaller values is prefered if the effect is similar.'''
    processed_img = cv2.GaussianBlur(processed_img, (3,3), 0)
    processed_img = cv2.Canny(processed_img, threshold1 = 50, threshold2 = 200)
    processed_img = cv2.circle(processed_img, (400,300), 10, (255,255,255), -1)
    return processed_img

def two_lanes_control(left_midx, right_midx):
    two_lower_limit = -30
    two_upper_limit = 30
    if two_lower_limit < abs(right_midx - 400) - abs(left_midx - 400) < two_upper_limit:
        straight()
        print('Both lanes found. Near the center of both lanes, going straight. {} < {}value < {}'
              .format(two_lower_limit, abs(right_midx - 400) - abs(left_midx - 400), two_upper_limit))
    elif two_upper_limit < abs(right_midx - 400) - abs(left_midx - 400):
        right()
        straight()
        print('Both lanes found. Nearer to left lane than right, going right. {} < {}value'
              .format(two_upper_limit, abs(right_midx - 400) - abs(left_midx - 400)))
    elif two_lower_limit > abs(right_midx - 400) - abs(left_midx - 400):
        left()
        straight()
        print('Both lanes found. Nearer to right lane than left, going left. {} > {}value'
              .format(two_lower_limit, abs(right_midx - 400) - abs(left_midx - 400)))

def left_lane_control(left_midx):
    left_lower_limit = 80
    left_upper_limit = 180
    if left_lower_limit < abs(left_midx - 400) < left_upper_limit:
        straight()
        slow_down()
        print('Only left lane. Not too far and not too near from left lane, going straight. {} < {}value < {}'
              .format(left_lower_limit, abs(left_midx - 400), left_upper_limit))
    elif left_upper_limit < abs(left_midx - 400):
        left()
        straight()
        print('Only left lane. Im too far from the left lane, going left. {} < {}value'
              .format(left_upper_limit, abs(left_midx - 400)))
    elif left_lower_limit > abs(left_midx - 400):
        right()
        straight()
        print('Only left lane. Im too near to the left lane, going right. {} > {}value'
              .format(left_lower_limit, abs(left_midx - 400)))

def right_lane_control(right_midx):
    right_lower_limit = 80
    right_upper_limit = 180
    if right_lower_limit < abs(right_midx - 400) < right_upper_limit:
        straight()

        slow_down()
        print('Only right lane. Not too far and not too near from right lane, going straight. {} < {}value < {}'
              .format(right_lower_limit, abs(right_midx - 400), right_upper_limit))
    elif right_upper_limit < abs(right_midx - 400):
        right()
        straight()
        print('Only right lane. Im too far from the right lane, going right. {} < {}value'
              .format(right_upper_limit, abs(right_midx - 400)))
    elif right_lower_limit > abs(right_midx - 400):
        left()
        straight()
        print('Only right lane. Im too near to the right lane, going left. {} > {}value'
              .format(right_lower_limit, abs(right_midx - 400)))

def ensuring_screen_shows(lines, screen1):
    if lane_lines(lines):
        screen2 = draw_lane_lines(screen1, lane_lines(lines))
    else:
        screen2 = screen1
    return screen2

def ensuring_lanes(lines):
    if middle_xcoordinate(lines):
        left_x, right_x = middle_xcoordinate(lines)
    else:
        left_x = None
        right_x = None
    return left_x, right_x

for i in list(range(4))[::-1]:
    print(i+1)
    time.sleep(1)

def main():
    while(True):
        screen = np.array(ImageGrab.grab(bbox=(0,40,800,600)))
        screen1 = process_img(screen)
        lines = cv2.HoughLinesP(screen1, 1, np.pi/180, 100,      10,       15)  
        screen2 = ensuring_screen_shows(lines, screen1)
        left_x, right_x = ensuring_lanes(lines)
        cv2.namedWindow('window', cv2.WINDOW_NORMAL)
        cv2.resizeWindow('window', 400, 300)
        cv2.imshow('window', screen2)

        if left_x and right_x is not None:
            two_lanes_control(left_x, right_x)
        elif left_x is not None:
            left_lane_control(left_x)
        elif right_x is not None:
            right_lane_control(right_x)
        else:
            slow_down()
            print('No lanes found! Stopping.')
        
        if cv2.waitKey(25) & 0xFF == ord('k'):
            cv2.destroyAllWindows()
            break

main()

