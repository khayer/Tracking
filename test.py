import cv2
import numpy as np
 
c = cv2.VideoCapture("/Users/kat/Desktop/225.m4v")
_,f = c.read()
 
avg1 = np.float32(f)
avg2 = np.float32(f)
#avg1 = np.asarray(f[:,:])
#avg2 = np.asarray(f[:,:])
while(1):
    _,f = c.read()
     
    cv2.accumulateWeighted(f,avg1,0.1)
    cv2.accumulateWeighted(f,avg2,0.01)
     
    res1 = cv2.convertScaleAbs(avg1)
    res2 = cv2.convertScaleAbs(avg2)
 
    cv2.imshow('img',f)
    cv2.imshow('avg1',res1)
    cv2.imshow('avg2',res2)
    k = cv2.waitKey(20)
 
    if k == 27:
        break
 
cv2.destroyAllWindows()
c.release()

#import cv
#import cv2
#import numpy as np
#
#if __name__ == '__main__':
#  cv.NamedWindow("test1", cv.CV_WINDOW_AUTOSIZE)
#  cv.NamedWindow("test2", cv.CV_WINDOW_AUTOSIZE)
#  capture = cv.CreateFileCapture('/Users/kat/Desktop/225.m4v')
#  frame = cv.QueryFrame(capture)
#
#  img = cv.CreateImage(cv.GetSize(frame),8,1)
#  thresh = cv.CreateImage(cv.GetSize(frame),8,1)
#  foreground = cv.CreateImage(cv.GetSize(frame),8,1)
#  foremat = cv.GetMat(foreground)
#  Nforemat = np.array(foremat, dtype=np.float32)
#
#  thresh = cv.CreateImage(cv.GetSize(img),8,1)
#  mog = cv2.BackgroundSubtractorMOG()
#
#  loop = True
#  nframes=0
#  while(loop):
#    frame = cv.QueryFrame(capture)
#    mat = cv.GetMat(frame)
#    Nmat = np.array(mat, dtype=np.float32)
#
#    cv.CvtColor(frame,img,cv.CV_BGR2GRAY)
#
#    if (frame == None):
#        break
#
#    mog.apply(Nmat,Nforemat,-1)
#    cv.Threshold(img,thresh,100,255,cv.CV_THRESH_BINARY)
#
#    cv.ShowImage("test1", thresh)
#    cv.ShowImage("test2",frame)
#    char = cv.WaitKey(50)
#    if (char != -1):
#        if (char == 27):
#                break
#  cv.DestroyWindow("test1")
#  cv.DestroyWindow("test2")