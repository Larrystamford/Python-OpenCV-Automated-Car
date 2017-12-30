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


def main():
    while(True):
        if left_x and right_x is not None:
            two_lanes_control(left_x, right_x)
        elif left_x is not None:
            left_lane_control(left_x)
        elif right_x is not None:
            right_lane_control(right_x)
        else:
            slow_down()
            print('No lanes found! Stopping.')
        
main()

