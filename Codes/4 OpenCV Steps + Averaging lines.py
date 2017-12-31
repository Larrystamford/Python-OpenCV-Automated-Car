
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
    # diagonal roi will create line and cause inaccuracy
    vertices = np.array([[0,410], [800,410], [800,300], [700,300], [700,240], [100,240], [100,325], [0,325]], np.int32)
    processed_img = cv2.cvtColor(image, cv2.COLOR_BGR2HLS)
    processed_img = mask(processed_img)
    # for some reason roi has to go after masking
    processed_img = roi(processed_img, [vertices])
    processed_img = cv2.GaussianBlur(processed_img, (3,3), 0)
    processed_img = cv2.Canny(processed_img, threshold1 = 50, threshold2 = 200)
    processed_img = cv2.circle(processed_img, (400,300), 10, (255,255,255), -1)

    return processed_img




