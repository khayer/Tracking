#!/usr/bin/env python

import cv, time
from numpy import *
from sys import stdout

class Target:

    def __init__(self):
        #self.capture = cv.CaptureFromCAM(0)
        self.capture = cv.CaptureFromFile("/Users/hayer/github/Tracking/mouse1-Zeromaze.m4v")
        self._numframes = cv.GetCaptureProperty(self.capture,cv.CV_CAP_PROP_FRAME_COUNT)
        cv.NamedWindow("Target", 1)
        print self._numframes

    def run(self):


        #future = time.time() + 300
        # Capture first frame to get size
        frame = cv.QueryFrame(self.capture)
        frame_size = cv.GetSize(frame)
        # Preparing files
        color_image = cv.CreateImage(frame_size, 8, 3)
        grey_image = cv.CreateImage(frame_size, cv.IPL_DEPTH_8U, 1)
        moving_average = cv.CreateImage(frame_size, cv.IPL_DEPTH_32F, 3)
        tmp_image_open_arms = cv.CreateImage(frame_size, 8, 1)
        tmp_image_closed_arms = cv.CreateImage(frame_size, 8, 1)

        time_on_open_arm = 0
        start = 0
        end = 0
        # 2. No. of transitions from closed-> open
        number_of_transitions = 0
        distance_open_arm = 0

        first = True
        is_open_arm = False

        k = 0
        upper = 500
        distance = 0
        center_point_old = (0,0)

        # Define open arms area
        image = cv.LoadImageM("/Users/hayer/github/Tracking/01_color_image.png")
        size = frame_size
        cv.Smooth(image, image, cv.CV_GAUSSIAN, 1, 0)

        open_arms = cv.CreateImage(size, 8, 1)
        red = cv.CreateImage(size, 8, 1)
        hsv = cv.CreateImage(size, 8, 3)
        sat = cv.CreateImage(size, 8, 1)
        imgblue = cv.CreateImage(size, 8, 1)
        imggray = cv.CreateImage(size, 8, 1)


        #split image into hsv, grab the sat
        cv.CvtColor(image, hsv, cv.CV_BGR2HSV)
        #cv.ShowImage("HAHA", hsv)
        cv.Split(hsv, None, sat, None, None)
        #cv.ShowImage("HIHI", sat)

        #split image into rgb
        cv.Split(image, None, None, red, None)
        #cv.ShowImage("HEHE", red)

        #find the car by looking for red, with high saturation
        cv.Threshold(red, red, 128, 255, cv.CV_THRESH_BINARY)
        #cv.ShowImage("HOHO", red)
        cv.Threshold(sat, sat, 128, 255, cv.CV_THRESH_BINARY)
        #cv.ShowImage("BLUBB", sat)

        #AND the two thresholds, finding the car
        cv.Mul(red, sat, open_arms)


        #remove noise, highlighting the car
        #cv.Erode(open_arms, open_arms,  None, 1)
        #cv.ShowImage("Erode", car)
        #cv.Dilate(open_arms, open_arms,  None, 1)
        #cv.ShowImage("Dilate", car)
        #cv.InRangeS(image,cv.Scalar(0),cv.Scalar(255),open_arms)

        #storage = cv.CreateMemStorage(0)
        #obj = cv.FindContours(open_arms, storage, cv.CV_RETR_CCOMP, cv.CV_CHAIN_APPROX_SIMPLE)

        #print obj
        obj = 5


        if not obj:
            car_rect = (0, 0, 0, 0)
        else:
            car_rect = (0, 0, 0, 0)
          #car_rect = cv.BoundingRect(obj)
          #car_poly = cv.ApproxPoly(obj,storage,cv.CV_POLY_APPROX_DP)

        #print car_rect
        #for (x,y) in car_poly:
        #    print (x,y)

        closed_arms = cv.CreateImage(size, 8, 1)
        blue = cv.CreateImage(size, 8, 1)
        hsv = cv.CreateImage(size, 8, 3)
        sat = cv.CreateImage(size, 8, 1)


        #split image into hsv, grab the sat
        cv.CvtColor(image, hsv, cv.CV_BGR2HSV)
        cv.Split(hsv, None, sat, None, None)

        #split image into rgb
        cv.Split(image, blue, None, None, None)

        #find the car by looking for red, with high saturation
        cv.Threshold(blue, blue, 128, 255, cv.CV_THRESH_BINARY)
        cv.Threshold(sat, sat, 128, 255, cv.CV_THRESH_BINARY)

        #AND the two thresholds, finding the car
        cv.Mul(blue, sat, closed_arms)

        #remove noise, highlighting the car
        #cv.Erode(car, car,  None, 10)
        #cv.Dilate(car, car,  None, 10)
#
        #storage = cv.CreateMemStorage(0)
        #obj = cv.FindContours(car, storage, cv.CV_RETR_CCOMP, cv.CV_CHAIN_APPROX_SIMPLE)
        #cv.ShowImage('A', car)

        #if not obj:
        car_rect2 = (0, 0, 0, 0)
        #else:
        #  car_rect2 = (0, 0, 0, 0)
          #car_rect2 = cv.BoundingRect(obj)
          #car_poly = cv.ApproxPoly(obj,storage,cv.CV_POLY_APPROX_DP,5,1)

        #print car_rect
        #for (x,y) in car_poly:
        #    print (x,y)
        #    cv.Circle(car, (x,y), 3,cv.CV_RGB(150,0,150), 1)


        #print car_rect2



        #jetzt = time.time()
        frame_number = range(1,int(math.ceil(self._numframes)))
        for i in frame_number:
        #while True:
            #print time.time() - jetzt
            #jetzt = time.time()
            #if time.time() > future:
            #    print distance, " pixel"
            #    print distance / 108.78 , " inches"
            #    print (distance / 108.78) * 2.54 , " cm"
            #    print time_on_open_arm , " s spent on open arm"
            #    print number_of_transitions , " transitions from closed->open"
            #    print distance_open_arm , " distance on open arm"
            #    if time_on_open_arm == 0:
            #        print "Speed in open arm not available"
            #    else:
            #        print distance_open_arm / time_on_open_arm, " speed in pixel per second"
            #    break
            color_image = cv.QueryFrame(self.capture)

            cv.InRangeS(color_image,cv.Scalar(0,0,0),cv.Scalar(4,4,4),imgblue) # Select a range of blue color
            cv.InRangeS(color_image,cv.Scalar(90,90,90),cv.Scalar(150,150,150),imggray)
            cv.Erode(imgblue, imgblue, None, 4)
            cv.Dilate(imgblue, imgblue, None, 10)
            #cv.Erode(imggray, imggray, None, 4)
            #cv.Dilate(imggray, imggray, None, 10)

            #cv.ShowImage("HUHU", imgblue)
            #cv.ShowImage("HIHI", imggray)


            # Smooth to get rid of false positives
            cv.Smooth(color_image, color_image, cv.CV_GAUSSIAN, 3, 0)
            #cv.Smooth(moving_average, moving_average, cv.CV_GAUSSIAN, 3, 0)
            #cv.SaveImage("/Users/hayer/github/Tracking/01_color_image.png", color_image)

            if first:
                difference = cv.CloneImage(color_image)
                temp = cv.CloneImage(color_image)
                cv.ConvertScale(color_image, moving_average, 1.0, 0.0)
                first = False
            else:
                cv.RunningAvg(color_image, moving_average, 0.0005, None)

            #cv.SaveImage("/Users/hayer/github/Tracking/02_moving_average.png", moving_average)

            # Convert the scale of the moving average.
            cv.ConvertScale(moving_average, temp, 1.0, 0.0)
            #temp = moving_average
            #cv.SaveImage("/Users/hayer/github/Tracking/03_temp.png", temp)

            # Minus the current frame from the moving average.
            cv.AbsDiff(color_image, temp, difference)
            #cv.SaveImage("/Users/hayer/github/Tracking/04_difference.png", difference)


            # Convert the image to grayscale.
            cv.CvtColor(difference, grey_image, cv.CV_RGB2GRAY)
            #cv.SaveImage("/Users/hayer/github/Tracking/05_grey_image.png", grey_image)

            cv.And(grey_image, imgblue, grey_image)

            # Convert the image to black and white.
            cv.Threshold(grey_image, grey_image, 90, 255, cv.CV_THRESH_BINARY)
            #cv.SaveImage("/Users/hayer/github/Tracking/06_grey_image.png", grey_image)

            # Dilate and erode to get people blobs
            cv.Dilate(grey_image, grey_image, None, 10)
            #cv.SaveImage("/Users/hayer/github/Tracking/07_grey_image_dilate.png", grey_image)
            cv.Erode(grey_image, grey_image, None, 10)
            #cv.SaveImage("/Users/hayer/github/Tracking/08_grey_image_erode.png", grey_image)
            cv.And(grey_image, open_arms, tmp_image_open_arms)
            ##cv.ShowImage("HaHa", tmp_image_open_arms)
            cv.And(grey_image, closed_arms, tmp_image_closed_arms)
            #cv.ShowImage("HeHe", tmp_image_closed_arms)
            storage = cv.CreateMemStorage(0)
            contour = cv.FindContours(grey_image, storage, cv.CV_RETR_CCOMP, cv.CV_CHAIN_APPROX_SIMPLE)
            points = []


            while contour:
                bound_rect = cv.BoundingRect(list(contour))
                contour = contour.h_next()

                pt1 = (bound_rect[0], bound_rect[1])
                pt2 = (bound_rect[0] + bound_rect[2], bound_rect[1] + bound_rect[3])

                # is rectangle big enough?
                # size = abs(bound_rect[2]) * abs(bound_rect[3])
                # print size

                # is rectangle close to center_point?
                #diff = max(abs(array(pt1) - array(center_point)))
                #diff2 = max(abs(array(pt2) - array(center_point)))
                #maximum = max(diff,diff2)
                #print maximum
                #if first:
                #    maximum = 5


                points.append(pt1)
                points.append(pt2)
                cv.Rectangle(color_image, pt1, pt2, cv.CV_RGB(255,0,0), 1)


#
                storage2 = cv.CreateMemStorage(0)
                contour2 = cv.FindContours(tmp_image_open_arms, storage2, cv.CV_RETR_CCOMP, cv.CV_CHAIN_APPROX_SIMPLE)

#
                if contour2 and not is_open_arm:
                    area = cv.ContourArea(contour2)
                    #print area
                    if area > 1800:
                        is_open_arm = True
                        start = time.time()
                        number_of_transitions += 1

                if is_open_arm:
                    storage2 = cv.CreateMemStorage(0)
                    contour2 = cv.FindContours(tmp_image_closed_arms, storage2, cv.CV_RETR_CCOMP, cv.CV_CHAIN_APPROX_SIMPLE)
                    if contour2:
                        area = cv.ContourArea(contour2)
                        #print area
                        if area > 800:
                            is_open_arm = False
                            end = time.time()
                            #print end - start
                            time_on_open_arm += end-start
                            #print "+1"


            if len(points):
                upper = 50
                center_point = reduce(lambda a, b: ((a[0] + b[0]) / 2, (a[1] + b[1]) / 2), points)
                # ==> 1
                #is_open_arm = in_rectangle(center_point, car_rect, car_rect2)
                if is_open_arm:
                    color = cv.CV_RGB(255,0,0)
                else:
                    color = cv.CV_RGB(255, 255, 255)
                #cv.Circle(color_image, center_point, 40, cv.CV_RGB(255, 255, 255), 1)
                #cv.Circle(color_image, center_point, 30, cv.CV_RGB(255, 100, 0), 1)
                cv.Circle(color_image, center_point, 20, color, 1)
                cv.Circle(color_image, center_point, 10, color, 1)
                #cv.Circle(color_image, (0,100), 10, cv.CV_RGB(255, 100, 0), 1)
                # ==> 4)
                dist = abs(array(center_point)-array(center_point_old))
                distance += math.sqrt(dist[0]*dist[1])
                if is_open_arm:
                    distance_open_arm += math.sqrt(dist[0]*dist[1])
                center_point_old = center_point


            #cv.Rectangle(color_image,
            #    (car_rect[0], car_rect[1]),
            #    (car_rect[0] + car_rect[2], car_rect[1] + car_rect[3]),
            #    (255,0,0),
            #    1,
            #    8,
            #    0)
#
            #cv.Circle(color_image,
            #  (car_rect[0], car_rect[1]),
            #  20,
            #  (0, 0, 255),
            #  -1,
            #  8,
            #  0)
#
            #cv.Circle(color_image,
            #  (car_rect[0] + car_rect[2], car_rect[1] + car_rect[3]),
            #  20,
            #  (0, 0, 255),
            #  -1,
            #  8,
            #  0)
#
            #cv.Rectangle(color_image,
            #    (car_rect2[0], car_rect2[1]),
            #    (car_rect2[0] + car_rect2[2], car_rect2[1] + car_rect2[3]),
            #    (255,0,0),
            #    1,
            #    8,
            #    0)
#
            #cv.Circle(color_image,
            #  (car_rect2[0], car_rect2[1]),
            #  20,
            #  (0, 0, 255),
            #  -1,
            #  8,
            #  0)
#
            #cv.Circle(color_image,
            #  (car_rect2[0] + car_rect2[2], car_rect2[1] + car_rect2[3]),
            #  20,
            #  (0, 0, 255),
            #  -1,
            #  8,
            #  0)
#


            cv.ShowImage("Target", color_image)
            #if k == 100:
            #    exit()

            # Problems to solve:
            # 1) Time spent on the open arm
            # 2) No. of transitions from closed arm
            # 3) Speed of the mouse in the open arm
            # 4) Total distance traveled


            #k += 1
            # Listen for ESC key
            percent = int(100/self._numframes * i)
            l = percent / 2
            if l%2==0:
                stdout.write("\r[%-50s] %d%%" % ('='*int(l), percent))
                stdout.flush()
            c = cv.WaitKey(7) % 0x100
            if c == 27:
                break
            #    print distance, " pixel"
            #    print distance / 108.78 , " inches"
            #    print (distance / 108.78) * 2.54 , " cm"
            #    print time_on_open_arm , " s spent on open arm"
            #    print number_of_transitions , " transitions from closed->open"
            #    print distance_open_arm , " distance on open arm"
            #    print distance_open_arm / time_on_open_arm, " speed in pixel per second"
            #    break

        stdout.write("\r[%-50s] %d%%\n" % ('='*50, 100))
        #stdout.flush()
        print distance, " total distance traveled in pixel"
        #print distance / 108.78 , " inches"
        #print (distance / 108.78) * 2.54 , " cm"
        print time_on_open_arm , " s spent on open arm"
        print number_of_transitions , " transitions from closed->open"
        print distance_open_arm , " distance on open arm"
        if time_on_open_arm == 0:
            print "Speed in open arm not available"
        else:
            print distance_open_arm / time_on_open_arm, " speed in pixel per second"

    ######### METHODS #########
    def in_rectangle(point, rec1, rec2):
        #print point, "  " , rec1 , "  " , rec2
        in_rec1 = (point[0] > rec1[0]) and (point[0] < rec1[0]+rec1[2]) and (point[1] > rec1[1]) and (point[1] < rec1[1]+rec1[3])
        in_rec2 = (point[0] > rec2[0] and point[0] < rec2[0]+rec2[2]) and (point[1] > rec2[1] and point[1] < rec2[1]+rec2[3])
        return in_rec1 or in_rec2
    ###########################

if __name__=="__main__":
    t = Target()
    t.run()

