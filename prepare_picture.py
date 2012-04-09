#!/usr/bin/env python

import cv, time
from numpy import *
from sys import stdout

class Prepare:

    def __init__(self):
        #self.capture = cv.CaptureFromCAM(0)
        self.capture = cv.CaptureFromFile("/Users/hayer/github/Tracking/225.m4v")
        self._numframes = cv.GetCaptureProperty(self.capture,cv.CV_CAP_PROP_FRAME_COUNT)
        cv.NamedWindow("Prepare", 1)
        print self._numframes

    def run(self):

        frame = cv.QueryFrame(self.capture)
        k = cv.SetCaptureProperty(self.capture, cv.CV_CAP_PROP_POS_MSEC, 0)
        frame_size = cv.GetSize(frame)

        # Preparing files
        color_image = cv.CreateImage(frame_size, 8, 3)



        frame_number = range(1,int(math.ceil(self._numframes)))
        for i in frame_number:

            color_image = cv.QueryFrame(self.capture)
            #k = cv.GetCaptureProperty(self.capture, cv.CV_CAP_PROP_POS_MSEC)
            #print k

            #cv.InRangeS(color_image,cv.Scalar(0,0,0),cv.Scalar(4,4,4),black_mouse) # Select a range of blue color
            #.Erode(black_mouse, black_mouse, None, 4)
            #cv.Dilate(black_mouse, black_mouse, None, 10)

            # Smooth to get rid of false positives
            cv.Smooth(color_image, color_image, cv.CV_GAUSSIAN, 3, 0)
            cv.SaveImage("foo.png",color_image)

            exit()
            c = cv.WaitKey(7) % 0x100
            if c == 27:
                exit()


    ######### METHODS #########

    ###########################

if __name__=="__main__":
    t = Prepare()
    t.run()