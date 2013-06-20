#!/usr/bin/env python

import cv, cv2, time, itertools
from numpy import *
from sys import *

class Target:

    def __init__(self,video,image):
        self.capture = cv.CaptureFromFile(video)
        self.image = cv.LoadImageM(image)
        self._numframes = cv.GetCaptureProperty(self.capture,
            cv.CV_CAP_PROP_FRAME_COUNT)
        print >> stderr, self._numframes
        self.fps = cv.GetCaptureProperty(self.capture,
            cv.CV_CAP_PROP_FPS)
        print >> stderr, self.fps
        self.length_cali = 500
        self.size = cv.GetSize(cv.QueryFrame(self.capture))
        self.background = self.get_background(video)
        self.open_arm = self.get_open_arm()
        self.closed_arm = self.get_closed_arm()
        self.zero_maze = self.get_zeromaze()
        self.mouse_area = self.get_mouse_area()
        self.conversion = 11.75
        print >> stderr, self.mouse_area

    ######### METHODS #########

    def get_background(self,video):
        capture = cv2.VideoCapture(video)
        _,frame = capture.read()
        average = float32(frame)
        print >> stderr, "background start"
        for i in range(1,self.length_cali):
            _,frame = capture.read()
            cv2.accumulateWeighted(frame,average,0.01)
            background = cv2.convertScaleAbs(average)
            cv2.imshow('background',background)
            k = cv2.waitKey(1)
            percent = i/(self.length_cali/100)
            l = int(percent/2)
            if l%2==0:
               stderr.write("\r[%-50s] %d%%" % ('='*int(l), percent))
               stderr.flush()
        stderr.write("\r[%-50s] %d%%\n" % ('='*50, 100))
        print >> stderr, "background done"
        return cv.fromarray(background)

    def get_open_arm(self):
        ######## Define open arms area
        cv.Smooth(self.image, self.image, cv.CV_GAUSSIAN, 1, 0)
        open_arms = cv.CreateImage(self.size, 8, 1)
        red = cv.CreateImage(self.size, 8, 1)
        hsv = cv.CreateImage(self.size, 8, 3)
        sat = cv.CreateImage(self.size, 8, 1)
        black_mouse = cv.CreateImage(self.size, 8, 1)
        cv.CvtColor(self.image, hsv, cv.CV_BGR2HSV)
        cv.Split(hsv, None, sat, None, None)
        cv.Split(self.image, None, None, red, None)
        cv.Threshold(red, red, 128, 255, cv.CV_THRESH_BINARY)
        cv.Threshold(sat, sat, 128, 255, cv.CV_THRESH_BINARY)
        cv.Mul(red, sat, open_arms)
        return open_arms

    def get_closed_arm(self):
        ######## Define closed area
        closed_arm = cv.CreateImage(self.size, 8, 1)
        blue = cv.CreateImage(self.size, 8, 1)
        hsv = cv.CreateImage(self.size, 8, 3)
        sat = cv.CreateImage(self.size, 8, 1)
        #split image into hsv, grab the sat
        cv.CvtColor(self.image, hsv, cv.CV_BGR2HSV)
        cv.Split(hsv, None, sat, None, None)
        #split image into rgb
        cv.Split(self.image, blue, None, None, None)
        cv.Threshold(blue, blue, 128, 255, cv.CV_THRESH_BINARY)
        cv.Threshold(sat, sat, 128, 255, cv.CV_THRESH_BINARY)
        cv.Mul(blue, sat, closed_arm)
        return closed_arm

    def get_zeromaze(self):
        mix_open_closed = cv.CreateImage(self.size, 8, 1)
        cv.Or(self.open_arm, self.closed_arm, mix_open_closed)
        cv.Dilate(mix_open_closed, mix_open_closed, None, 10)
        cv.Erode(mix_open_closed, mix_open_closed, None, 10)
        return mix_open_closed

    def distance_func(self, points):
        p0, p1 = points
        return (p0[0] - p1[0])**2 + (p0[1] - p1[1])**2

    def where_is_the_nose(self,max_pair, image ):
        white_space = 0
        nose_coord = (0,0)
        for (x,y) in max_pair:
            cv.SetImageROI(image, (x-20, y-20, 40 , 40))
            storage = cv.CreateMemStorage(0)
            contour = cv.FindContours(image, storage, cv.CV_RETR_CCOMP, cv.CV_CHAIN_APPROX_SIMPLE)
            if contour:
                area = cv.ContourArea(contour)
                if area > white_space:
                    nose_coord = (x,y)
            cv.ResetImageROI(image)
        return nose_coord

    def get_mouse_area(self):
        print >> stderr, "Calibration ..."
        frame = cv.QueryFrame(self.capture)
        frame_size = cv.GetSize(frame)
        # Jump 30 second into video file
        cv.SetCaptureProperty(self.capture, cv.CV_CAP_PROP_POS_MSEC, 30000)
        color_image = cv.CreateImage(frame_size, 8, 3)
        grey_image = cv.CreateImage(frame_size, cv.IPL_DEPTH_8U, 1)
        moving_average = cv.CreateImage(frame_size, cv.IPL_DEPTH_32F, 3)
        black_mouse = cv.CreateImage(frame_size, 8, 1)
        first = True
        areas = zeros(self.length_cali)
        for i in range(1,self.length_cali):
            grey_image = cv.CreateImage(frame_size, cv.IPL_DEPTH_8U, 1)
            color_image = cv.QueryFrame(self.capture)
            cv.InRangeS(color_image,cv.Scalar(0,0,0),cv.Scalar(4,4,4),black_mouse) # Select a range of blue color
            cv.ShowImage("Mouse Color 1",black_mouse)
            cv.And(black_mouse,self.zero_maze,black_mouse)
            cv.ShowImage("Mouse Color 2",black_mouse)
            cv.Erode(black_mouse, black_mouse, None, 3)
            cv.Dilate(black_mouse, black_mouse, None, 8)
            cv.Erode(black_mouse, black_mouse, None, 3)
            if first:
                difference = cv.CloneImage(color_image)
                first = False
            cv.Smooth(color_image, color_image, cv.CV_GAUSSIAN, 7, 7)
            cv.AbsDiff(color_image, self.background, difference)
            cv.ShowImage("difference", difference)
            # Convert the image to grayscale.
            cv.CvtColor(difference, grey_image, cv.CV_RGB2GRAY)
            cv.ShowImage("Only Movement 1", grey_image)
            ### Where do both pictures overlap
            # Convert the image to black and white.
            cv.Threshold(grey_image, grey_image, 75, 255, cv.CV_THRESH_BINARY)
            cv.Erode(grey_image, grey_image, None, 1)
            cv.ShowImage("Only Movement", grey_image)
            # Dilate and erode to get mouse shapes
            cv.And(grey_image, black_mouse, grey_image)
            cv.ShowImage("Mix",grey_image)
            storage = cv.CreateMemStorage(0)
            contour = cv.FindContours(grey_image, storage, cv.CV_RETR_CCOMP, cv.CV_CHAIN_APPROX_SIMPLE)
            if contour:
                areas[i] = cv.ContourArea(contour)
            c = cv.WaitKey(7) % 0x100
            cv.SetCaptureProperty(self.capture, cv.CV_CAP_PROP_POS_MSEC, i * 100)
            percent = i/(self.length_cali/100)
            l = int(percent/2)
            if l%2==0:
               stderr.write("\r[%-50s] %d%%" % ('='*int(l), percent))
               stderr.flush()
        areas = sort(areas)
        last_position_zeros = max(where(areas == 0)[0])
        areas = areas[self.length_cali/2:self.length_cali]
        stderr.write("\r[%-50s] %d%%\n" % ('='*50, 100))
        print >> stderr, "Preparing done"
        c = cv.WaitKey(7) % 0x100
        cv.DestroyWindow("Mix")
        print >> stderr, mean(areas)
        return [mean(areas)/5,mean(areas)+std(areas)]

    def run(self):
        threshold_bout = 9

        frame = cv.QueryFrame(self.capture)
        cv.ShowImage("Original",frame)
        k = cv.SetCaptureProperty(self.capture, cv.CV_CAP_PROP_POS_MSEC, 0)
        frame_size = cv.GetSize(frame)
        start_total = cv.GetCaptureProperty(self.capture, cv.CV_CAP_PROP_POS_MSEC)
        # Preparing files
        color_image = cv.CreateImage(frame_size, 8, 3)
        grey_image = cv.CreateImage(frame_size, cv.IPL_DEPTH_8U, 1)
        moving_average = cv.CreateImage(frame_size, cv.IPL_DEPTH_32F, 3)
        tmp_image_open_arms = cv.CreateImage(frame_size, 8, 1)
        tmp_image_closed_arms = cv.CreateImage(frame_size, 8, 1)
        time_on_open_arm = 0
        start = 0
        end = 0
        number_of_transitions_open_closed = 0
        number_of_transitions_closed_open = 0
        distance_open_arm = 0
        start_bouts = 500
        end_bouts = 0
        time_bout = 0
        distance_bout = 0
        distance_bout_open_arm = 0
        start_bouts_open_arm = 400
        end_bouts_open_arm = 0
        time_bout_open_arm = 0
        first = True
        is_open_arm = False
        distance = 0
        point1 = (0,0)
        point2 = (0,0)
        point3 = (0,0)
        point4 = (0,0)
        point5 = (0,0)
        center_point_old = (0,0)
        center_point = (0,0)
        cv.Smooth(self.image, self.image, cv.CV_GAUSSIAN, 1, 0)
        open_arms = cv.CreateImage(self.size, 8, 1)
        red = cv.CreateImage(self.size, 8, 1)
        hsv = cv.CreateImage(self.size, 8, 3)
        sat = cv.CreateImage(self.size, 8, 1)
        black_mouse = cv.CreateImage(self.size, 8, 1)
        frame_number = 0
        percent_in_video = 0
        counter_for_bouts = 0
        number_of_bouts = 0
        bout_starts = True

        while frame_number < self._numframes:
            cv.SetCaptureProperty(self.capture, cv.CV_CAP_PROP_POS_FRAMES,frame_number)
            color_image = cv.QueryFrame(self.capture)
            percent_in_video = cv.GetCaptureProperty(self.capture, cv.CV_CAP_PROP_POS_AVI_RATIO)
            frame_number += 2

            cv.InRangeS(color_image,cv.Scalar(0,0,0),cv.Scalar(4,4,4),black_mouse) # Select a range of blue color
            cv.And(black_mouse,self.zero_maze,black_mouse)
            cv.Erode(black_mouse, black_mouse, None, 1)
            cv.Dilate(black_mouse, black_mouse, None, 7)
            cv.Erode(black_mouse, black_mouse, None, 4)

            # Smooth to get rid of false positives
            cv.Smooth(color_image, color_image, cv.CV_GAUSSIAN, 7, 7)

            if first:
                difference = cv.CloneImage(color_image)
                first = False

            cv.AbsDiff(color_image, self.background, difference)
            cv.ShowImage("difference", difference)
            # Convert the image to grayscale.
            cv.CvtColor(difference, grey_image, cv.CV_RGB2GRAY)
            # Dilate and erode to get people blobs
            cv.Dilate(grey_image, grey_image, None, 1)
            # Convert the image to black and white.
            cv.Threshold(grey_image, grey_image, 75, 255, cv.CV_THRESH_BINARY)

            ### Where do both pictures overlap
            cv.And(grey_image, black_mouse, grey_image)
            cv.ShowImage("Mix", grey_image)
            #cv.Erode(grey_image, grey_image, None, 10)
            cv.And(grey_image, self.open_arm, tmp_image_open_arms)
            cv.And(grey_image, self.closed_arm, tmp_image_closed_arms)

            storage = cv.CreateMemStorage(0)
            contour = cv.FindContours(grey_image, storage, cv.CV_RETR_CCOMP, cv.CV_CHAIN_APPROX_SIMPLE)

            # Draw Contour
            cv.DrawContours(color_image,contour,cv.CV_RGB(255,255,0),cv.CV_RGB(50,203,60),1)
            contour3 = contour

            if contour and len(contour) > 1:
                # Points furthest away from each other
                max_pair = max(itertools.combinations(contour, 2), key=self.distance_func)
                cv.Line(color_image,max_pair[0],max_pair[1],cv.CV_RGB(255,255,0))
                nose_coord = self.where_is_the_nose(max_pair,grey_image)
                cv.Circle(color_image, nose_coord, 3, cv.CV_RGB(255,0,0), 1)

            points = []
            while contour:
                bound_rect = cv.BoundingRect(list(contour))
                contour = contour.h_next()

                pt1 = (bound_rect[0], bound_rect[1])
                pt2 = (bound_rect[0] + bound_rect[2], bound_rect[1] + bound_rect[3])

                points.append(pt1)
                points.append(pt2)

                if is_open_arm:
                    storage2 = cv.CreateMemStorage(0)
                    contour2 = cv.FindContours(tmp_image_closed_arms, storage2, cv.CV_RETR_CCOMP, cv.CV_CHAIN_APPROX_SIMPLE)
                    if contour2:
                        area = cv.ContourArea(contour2)
                        if area > self.mouse_area[0]:
                            is_open_arm = False
                            end = cv.GetCaptureProperty(self.capture, cv.CV_CAP_PROP_POS_MSEC)
                            time_on_open_arm += (end-start) / 1000
                            number_of_transitions_open_closed += 1
                else:
                    storage2 = cv.CreateMemStorage(0)
                    contour2 = cv.FindContours(tmp_image_open_arms, storage2, cv.CV_RETR_CCOMP, cv.CV_CHAIN_APPROX_SIMPLE)
                    if contour2:
                        area = cv.ContourArea(contour2)
                        if area > self.mouse_area[1] and not cv.FindContours(tmp_image_closed_arms, storage2, cv.CV_RETR_CCOMP, cv.CV_CHAIN_APPROX_SIMPLE):
                            is_open_arm = True
                            start = cv.GetCaptureProperty(self.capture, cv.CV_CAP_PROP_POS_MSEC)
                            number_of_transitions_closed_open += 1

            if len(points):
                point5 = reduce(lambda a, b: ((a[0] + b[0]) / 2, (a[1] + b[1]) / 2), points)
                if point1 != (0,0):
                    x = (point1[0] + point2[0] + point3[0] + point4[0] + point5[0]) / 5
                    y = (point1[1] + point2[1] + point3[1] + point4[1] + point5[1]) / 5
                    center_point = (x,y)
                    if is_open_arm:
                        color = cv.CV_RGB(255,0,0)
                    else:
                        color = cv.CV_RGB(255, 255, 255)

                    cv.Circle(color_image, center_point, 10, color, 1)

                    dist = abs(array(center_point)-array(center_point_old))
                    if math.sqrt(dist[0]*dist[1]) > 3.0:
                        distance += math.sqrt(dist[0]*dist[1])
                        counter_for_bouts += 1
                        if counter_for_bouts > threshold_bout:
                            cv.Circle(color_image, center_point, 10, color, -1)
                            distance_bout += math.sqrt(dist[0]*dist[1])
                            if is_open_arm:
                                distance_bout_open_arm += math.sqrt(dist[0]*dist[1])
                            if bout_starts:
                                number_of_bouts += 1
                                bout_starts = False
                                start_bouts = cv.GetCaptureProperty(self.capture, cv.CV_CAP_PROP_POS_MSEC)
                                if is_open_arm:
                                    start_bouts_open_arm = cv.GetCaptureProperty(self.capture, cv.CV_CAP_PROP_POS_MSEC)
                    else:
                        counter_for_bouts = 0
                        if not bout_starts:
                            end_bouts = cv.GetCaptureProperty(self.capture, cv.CV_CAP_PROP_POS_MSEC)
                            time_bout += (end_bouts-start_bouts) / 1000
                            end_bouts_open_arm = cv.GetCaptureProperty(self.capture, cv.CV_CAP_PROP_POS_MSEC)
                            time_dummy = (end_bouts_open_arm - start_bouts_open_arm)
                            if start_bouts_open_arm == start_bouts :
                                time_bout_open_arm += time_dummy / 1000
                            else:
                                start_bouts_open_arm = 400
                        bout_starts = True

                    cv.ShowImage("Target", color_image)

                if is_open_arm and point1 != (0,0):
                    if math.sqrt(dist[0]*dist[1]) > 2.0:
                        distance_open_arm += math.sqrt(dist[0]*dist[1])
                if center_point == (0,0):
                    center_point_old = point5
                else:
                    center_point_old = center_point
                point1 = point2
                point2 = point3
                point3 = point4
                point4 = point5

            percent = int(percent_in_video * 100)
            l = int(percent_in_video * 100 / 2)
            if l%2==0:
               stderr.write("\r[%-50s] %d%%" % ('='*int(l), percent))
               stderr.flush()

            # Listen for ESC key
            c = cv.WaitKey(5)
            if c == 27:
                end_total = cv.GetCaptureProperty(self.capture, cv.CV_CAP_PROP_POS_MSEC)
                total_time = (end_total-start_total) / 1000
                print "------ Until now:"
                print "total distance traveled in pixel\t", distance/self.conversion
                print "total length of experiment\t", total_time
                print "average-speed of travel in s in pixel per second\t", (distance/self.conversion)/total_time
                print "--- Closed arm ----------------------------------------"
                print "distance on closed arm\t", (distance - distance_open_arm)/self.conversion
                print "s spent on closed arm\t", total_time - time_on_open_arm
                print "speed in pixel per second\t", ((distance - distance_open_arm)/self.conversion) / (total_time - time_on_open_arm)
                print "--- Open arm ----------------------------------------"
                print "distance on open arm\t", distance_open_arm/self.conversion
                print "s spent on open arm\t", time_on_open_arm
                if time_on_open_arm == 0:
                    print "Speed in open arm not available"
                else:
                    print "speed in pixel per second\t", (distance_open_arm/self.conversion) / time_on_open_arm
                print "--- Transitions ----------------------------------------"
                print "transitions from closed->open\t", number_of_transitions_closed_open
                print "transitions from open->closed\t", number_of_transitions_open_closed
                print "--- Bouts ----------------------------------------"
                print "Bouts in s in open arm\t", time_bout
                if time_bout == 0:
                    print "Speed in open arm not available"
                else:
                    print "Speed in open arm\t", (distance_bout / self.conversion)/time_bout
                print "# of bouts\t", number_of_bouts
                break

        if is_open_arm:
            end = cv.GetCaptureProperty(self.capture, cv.CV_CAP_PROP_POS_MSEC)
            time_on_open_arm += (end-start) / 1000

        end_total = cv.GetCaptureProperty(self.capture, cv.CV_CAP_PROP_POS_MSEC)
        total_time = (end_total-start_total) / 1000
        stderr.write("\r[%-50s] %d%%\n" % ('='*50, 100))
        print "total distance traveled in pixel\t", distance/self.conversion
        print "total length of experiment\t", total_time
        print "average-speed of travel in s in pixel per second\t", (distance/self.conversion)/total_time
        print "--- Closed arm ----------------------------------------"
        print "distance on closed arm\t", (distance - distance_open_arm)/self.conversion
        print "s spent on closed arm\t", total_time - time_on_open_arm
        print "speed in pixel per second\t", ((distance - distance_open_arm)/self.conversion) / (total_time - time_on_open_arm)
        print "--- Open arm ----------------------------------------"
        print "distance on open arm\t", distance_open_arm/self.conversion
        print "s spent on open arm\t", time_on_open_arm
        if time_on_open_arm == 0:
            print "Speed in open arm not available"
        else:
            print "speed in pixel per second\t", (distance_open_arm/self.conversion) / time_on_open_arm
        print "--- Transitions ----------------------------------------"
        print "transitions from closed->open\t", number_of_transitions_closed_open
        print "transitions from open->closed\t", number_of_transitions_open_closed
        print "--- Bouts ----------------------------------------"
        print "Bouts in s in open arm\t", time_bout
        print "Speed in open arm\t", (distance_bout / self.conversion)/time_bout
        print "# of bouts\t", number_of_bouts
