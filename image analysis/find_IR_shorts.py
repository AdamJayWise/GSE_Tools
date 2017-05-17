import numpy as np
import cv2
import matplotlib.pyplot as plt
from matplotlib.patches import Ellipse
import os



def find_IR_blobs(fname):
    try:
        ir_img = cv2.imread(fname)
    except:
        print('Problem Loading File!')
        return
    ir_imgBW = np.mean(ir_img,2)


    for i in range(3):
        ir_img[:,:,i]=ir_imgBW

    ir_img[0:60][:][:]=0
    ir_img[220:][:][:]=0
    ir_img[100:140,100:140,:]=0

    # Setup SimpleBlobDetector parameters.
    params = cv2.SimpleBlobDetector_Params()
    params.blobColor = 255
    # Filter by Area.
    params.filterByArea = True
    params.minArea = 1

    params.filterByConvexity=True
    params.filterByCircularity = True
    params.minCircularity = 0.15
    params.minInertiaRatio = 0.15
    # Change thresholds
    params.minThreshold = 150;
    params.maxThreshold = 255;
    params.minConvexity = 0.25

    detector = cv2.SimpleBlobDetector_create(params)

    keypoints = detector.detect(ir_img)

    im_with_keypoints = cv2.drawKeypoints(ir_img, keypoints, np.array([]), (0,0,255), cv2.DRAW_MATCHES_FLAGS_DRAW_RICH_KEYPOINTS)

    f=plt.figure()
    ax=f.add_subplot(111)
    # Show blobs
    ax.imshow( np.maximum(im_with_keypoints[:,:,1],ir_imgBW) ,cmap='Greys_r')
    #ax.imshow(ir_img, cmap='Greys_r')

    ells = [Ellipse(xy=[keypoints[i].pt[0],keypoints[i].pt[1]], width=3*keypoints[i].size, height=3*keypoints[i].size, angle=0) for i in range(len(keypoints))]
    for e in ells:
        ax.add_artist(e)
        e.set_facecolor('none')


    for k in keypoints:
        #ax.plot(k.pt[0],k.pt[1],'rx')
        ax.text(k.pt[0],k.pt[1]*1.07,np.round(k.size,1),color='white')

    ax.set_xlim([0,240])
    ax.set_ylim([240,0])
    ax.set_xlabel(fname.split('.')[0])

    f.show()
    f.savefig('processed_'+file_name)

    return [file_name,keypoints]

for file_name in os.listdir('test_ir_images//'):
    find_IR_blobs('test_ir_images//'+file_name)