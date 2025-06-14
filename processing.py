import os
import joblib
from sklearn import preprocessing
import pickle
import pandas as pd
import numpy as np
import cv2
import math
import csv

#PUNYA JOVAN 
def video2frames(jumlahFrame, video):
    rawImages = {}
    output_dir = '1.frames'
    os.makedirs(output_dir, exist_ok=True)
    cap = cv2.VideoCapture(video)
    target_frames = jumlahFrame
    total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))

    frame_skip = max(total_frames // target_frames, 1)
    print('frameskip : ' + str(frame_skip))
    frame_count = 0
    frame_index = 0
    while frame_index < target_frames:
        ret, frame = cap.read()
        if not ret:
            break
        if frame_count % frame_skip == 0:
            rawImages[frame_index] = frame
            output_image_path = os.path.join(output_dir, f'frame_{frame_index:04d}.png')
            cv2.imwrite(output_image_path, frame)
            frame_index += 1
        frame_count += 1
    cap.release()
    return rawImages


def median_filter(image, kernelsize):
    output_dir = '2.medianfiltered'
    os.makedirs(output_dir, exist_ok=True)
    res = np.copy(image)
    res = cv2.medianBlur(image, kernelsize)
    output_path = os.path.join(output_dir, 'median.png')
    cv2.imwrite(output_path, res)
    return res

def gaussian_blur(image, kernelsize):
    output_dir = '2.gausianblur'
    os.makedirs(output_dir, exist_ok=True)
    res = np.copy(image)
    res  = cv2.GaussianBlur(image, kernelsize, 0)
    output_path = os.path.join(output_dir, 'gaussian.png')
    cv2.imwrite(output_path, res)
    return res

def high_boost_filter(image, lpf, kons):
    output_dir = '3.highboost'
    os.makedirs(output_dir, exist_ok=True)
    res = np.copy(image)
    for i in range(image.shape[0]):
        for j in range(image.shape[1]):
            lpf_rgb = lpf[i, j]
            src_rgb = image[i, j]
            for k in range(3):  # 3 channels (B, G, R)
                # val = kons * src_rgb[k] - lpf_rgb[k]
                val = kons * lpf_rgb[k]
                val = min(max(val, 0), 255)
                res[i, j, k] = val
    res = cv2.cvtColor(res, cv2.COLOR_BGR2GRAY)
    output_path = os.path.join(output_dir, 'highboost.png')
    cv2.imwrite(output_path, res)
    return res


def morph(image):
    output_dir = '4.morphology'
    os.makedirs(output_dir, exist_ok=True)
    res = np.copy(image)
    # ellipse = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (12, 12), (3, 3))
    ellipse = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (3, 3), (1, 1))
    res = cv2.morphologyEx(image, cv2.MORPH_OPEN, ellipse)
    res = cv2.morphologyEx(res, cv2.MORPH_CLOSE, ellipse)
    output_path = os.path.join(output_dir, 'morphology.png')
    cv2.imwrite(output_path, res)
    return res

def thresholding(image, thr_b, thr_a):
    output_dir = '5.thresholding'
    os.makedirs(output_dir, exist_ok=True)
    res = np.copy(image)
    _, res = cv2.threshold(image, thr_b, thr_a, cv2.THRESH_BINARY) #original at 90
    output_path = os.path.join(output_dir, 'threshold.png')
    cv2.imwrite(output_path, res)
    return res

def adaptiveThresholding(image, blockSize, C, k, i):
    output_dir = '5.adaptiveThresholding'
    os.makedirs(output_dir, exist_ok=True)
    res = np.copy(image)
    res = cv2.adaptiveThreshold(image, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY, blockSize=blockSize, C=C)
    output_path = os.path.join(output_dir, 'adaptivethreshold.png')
    kernel = np.ones((k,k), np.uint8)
    erosion = cv2.erode(res, kernel, iterations=i)
    dilation = cv2.dilate(erosion, kernel, iterations=i)
    res = np.copy(image)
    res = dilation
    cv2.imwrite(output_path, res)
    return res

def canny(image):
    output_dir = '6.canny'
    os.makedirs(output_dir, exist_ok=True)
    res = image.copy()
    res = cv2.Canny(image, 0, 255, 3)
    output_path = os.path.join(output_dir, 'canny.png')
    cv2.imwrite(output_path, res)
    return res

def region_filter(R, image):
    output_dir = '7.region'
    os.makedirs(output_dir, exist_ok=True)
    contours, hierarchy = cv2.findContours(image, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
    res = np.zeros_like(image)
    output_path = os.path.join(output_dir, 'region.png')
    for i in range(len(contours)):
        if len(contours[i]) > R:
            # cv2.drawContours(res, contours, i, (255, 0, 0), 1)
            cv2.drawContours(res, contours, i, (255, 0, 0), 1, lineType=8, hierarchy=hierarchy, maxLevel=0, offset=(0, 0))
            cv2.imwrite(output_path, res)
    return res


def coLinear(R, CCX, CCY, X1, Y1, image):
    output_dir = '8.colinear'
    os.makedirs(output_dir, exist_ok=True)
    contours, hierarchy = cv2.findContours(image, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
    res = np.zeros_like(image)
    data = [0] * 100

    idk = 0
    for i in range(len(contours)):
        if len(contours[i]) > R:
            pt = contours[i][len(contours[i]) // 4][0]
            CCX[idk] = pt[0]
            CCY[idk] = pt[1]
            data[idk] = 0
        else:
            CCX[idk] = 0
            CCY[idk] = 0
            data[idk] = 1
        idk += 1
    # Intersection line evaluation
    for i in range(len(contours)):
        for j in range(len(contours)):
            if i == j: continue
            out = 0
            for k in range(len(contours[i]) // 2):
                pt1 = contours[i][k][0]
                pt2 = contours[i][k + 2][0]
                out = intersectionLine(X1, Y1, CCX[j], CCY[j], pt1[0], pt1[1], pt2[0], pt2[1])
                if out == 1:
                    if (abs(CCX[j] - pt1[0]) < 6) and (abs(CCY[j] - pt1[1]) < 6):
                        data[j] = 0
                    else:
                        data[j] = 1
    for i in range(len(contours)):
        if data[i] == 0:
            cv2.drawContours(res, contours, i, (255, 255, 255), 1, lineType=8, hierarchy=hierarchy, maxLevel=0, offset=(0, 0))
            # output_path = os.path.join(output_dir, 'colinear.png')
            # cv2.imwrite(output_path, res)

    contours, hierarchy = cv2.findContours(res, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)

    roi_contours = max(contours, key=cv2.contourArea)
    res = np.zeros_like(image)
    cv2.drawContours(res, [roi_contours], -1, (255, 255, 255), 1, lineType=8, hierarchy=hierarchy, maxLevel=0, offset=(0, 0))
    output_path = os.path.join(output_dir, 'colinear.png')
    cv2.imwrite(output_path, res)
    return res


def triangleEquation(R, CCX, CCY, X1, Y1, source):
    output_dir = '12.Triangle Equation'
    os.makedirs(output_dir, exist_ok=True)
    contours, _ = cv2.findContours(source, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    data1 = [[] for _ in range(200)]
    x1 = [[0] * 100 for _ in range(100)]
    y1 = [[0] * 100 for _ in range(100)]
    x2 = [[0] * 100 for _ in range(100)]
    y2 = [[0] * 100 for _ in range(100)]
    center = [0, 0]
    jum = 0
    jum1 = 0
    jum2 = 0
    noCon = []
    idk = 0
    for i in range(len(contours)):

        if len(contours[i]) > R:
            x, y, w, h = cv2.boundingRect(contours[i])
            center_x = x + w // 2
            center_y = y + h // 2
            pt = (center_x, center_y)
            # pt = (X1, Y1)
            #check titik tengah berada di dalam kontur ROI atau tidak
            out = cv2.pointPolygonTest(contours[i], pt, False)
            print(out)
            if out > 0:
                jum1 += 1
            else:
                noCon.append(i)
                jum2 += 1
        idk += 1

    if jum1 > 0:
        print("bentuk=1")
        res = np.zeros_like(source)
        for m in range(len(contours)):
            if len(contours[m]) > R:
                cv2.drawContours(res, contours, m, (255, 0, 0), 1, lineType=8,)
        output_path = os.path.join(output_dir, 'TriangleEquation.png')
        cv2.imwrite(output_path, res)
        return res

    if jum2 == 1:
        print("bentuk=2")
        j = 0
        res = np.zeros_like(source)
        # startpoint = contours[0][0][0]
        # endpoint = contours[0][int(len(contours[0])/2)][0]
        # cv2.circle(res, startpoint, 5, (255, 0, 0), -1)
        # cv2.circle(res, endpoint, 5, (255, 0, 0), -1)
        for m in range(len(contours)):
            if len(contours[m]) > R:
                k = 0
                for i in range (len(contours[m]) - 7):
                    p1 = contours[m][i][0]
                    p2 = contours[m][i + 1][0]
                    p3 = contours[m][i + 2][0]
                    p4 = contours[m][i + 3][0]
                    p5 = contours[m][i + 4][0]
                    p6 = contours[m][i + 5][0]
                    p7 = contours[m][i + 6][0]
                    d = int(np.sqrt(pow((p1[0] - p7[0]), 2.0) + pow((p1[1] - p7[1]), 2.0))) + \
                        int(np.sqrt(pow((p2[0] - p6[0]), 2.0) + pow((p2[1] - p6[1]), 2.0))) + \
                        int(np.sqrt(pow((p3[0] - p5[0]), 2.0) + pow((p3[1] - p5[1]), 2.0)))

                    if d <= 15:
                        data1[k] = i + 3
                        k += 1
                        CCX[j] = p4[0]
                        CCY[j] = p4[1]
                        cv2.line(source, (int(CCX[j] - 1), int(CCY[j])), (int(CCX[j] + 1), int(CCY[j])), (255, 0, 0), thickness=1)
                        cv2.line(source, (int(CCX[j]), int(CCY[j] - 1)), (int(CCX[j]), int(CCY[j] + 1)), (255, 0, 0), thickness=1)

                print(k)
                k = 0
                for i in range (len(contours[m]) - 7):
                    p1 = contours[m][i][0]
                    p2 = contours[m][i + 1][0]
                    p3 = contours[m][i + 2][0]
                    p4 = contours[m][i + 3][0]
                    p5 = contours[m][i + 4][0]
                    p6 = contours[m][i + 5][0]
                    p7 = contours[m][i + 6][0]
                    d = int(np.sqrt(pow((p1[0] - p7[0]), 2.0) + pow((p1[1] - p7[1]), 2.0))) + \
                        int(np.sqrt(pow((p2[0] - p6[0]), 2.0) + pow((p2[1] - p6[1]), 2.0))) + \
                        int(np.sqrt(pow((p3[0] - p5[0]), 2.0) + pow((p3[1] - p5[1]), 2.0)))
                    if d <= 3 :
                        data1[k] = i + 3
                        k += 1
                        CCX[j] = p4[0]
                        CCY[j] = p4[1]
                        cv2.line(source, (int(CCX[j] - 1), int(CCY[j])), (int(CCX[j] + 1), int(CCY[j])), (255, 255, 255), thickness=1)
                        cv2.line(source, (int(CCX[j]), int(CCY[j] - 1)), (int(CCX[j]), int(CCY[j] + 1)), (255, 255, 255), thickness=1)

                center[0] = X1
                center[1] = Y1
                print(center)
                jum = 0
                min = 2000.0
                p1 = contours[m][data1[0]][0]
                for i in range(data1[1], data1[1] + R):
                    p = contours[m][i][0]
                    a1 = np.sqrt(pow((p1[0] - p[0]), 2.0) + pow((p1[1] - p[1]), 2.0))
                    b1 = np.sqrt(pow((center[0] - p[0]), 2.0) + pow((center[1] - p[1]), 2.0))
                    c1 = np.sqrt(pow((center[0] - p1[0]), 2.0) + pow((center[1] - p1[1]), 2.0))
                    alpha = math.acos(((b1 * b1) + (c1 * c1) - (a1 * a1))/ (2 * b1 * c1)) * (180/math.pi)

                    if (alpha < min):
                        min = alpha
                        jum = i

                jum1 = 0
                min = 2000.0
                p1 = contours[m][jum][0]
                for i in range(data1[0], data1[0] + R):
                    p = contours[m][i][0]
                    a1 = np.sqrt(pow((p1[0] - p[0]), 2.0) + pow((p1[1] - p[1]), 2.0))
                    b1 = np.sqrt(pow((center[0] - p[0]), 2.0) + pow((center[1] - p[1]), 2.0))
                    c1 = np.sqrt(pow((center[0] - p1[0]), 2.0) + pow((center[1] - p1[1]), 2.0))
                    alpha = math.acos(((b1 * b1) + (c1 * c1) - (a1 * a1))/ (2 * b1 * c1)) * (180/math.pi)
                    if (alpha < min):
                        min = alpha
                        jum1 = i

                p1 = contours[m][jum][0]
                p2 = contours[m][jum1][0]
                x1[0][0] = p1[0]
                y1[0][0] = p1[1]
                x2[0][0] = p2[0]
                y2[0][0] = p2[1]

                cv2.circle(source, (int(p1[0]), int(p1[1])), 1, (255, 255, 255), 2, 8, 0)
                cv2.circle(source, (int(p2[0]), int(p2[1])), 1, (255, 255, 255), 2, 8, 0)
                # cv2.line(source, (int(x1[0][0]), int(y1[0][0])), (int(x2[0][0]), int(y2[0][0])), (255, 0, 0), thickness=4)

            j += 1

        # contours, hierarchy = cv2.findContours(source, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        # res = np.zeros_like(source)


        for m in range(len(contours)):

            # cv2.drawContours(res, contours, m, (255, 0, 0), 1, lineType=8,)
            if len(contours[m]) > R:
                end_idx = 0

                # find endpoint index
                # print(len(contours[m]))
                for i in range(len(contours[m])):
                    checkpoint = [contours[m][i][0][0], contours[m][i][0][1]]
                    endpoint = [p2[0], p2[1]]
                    result_variable = np.allclose(np.array(checkpoint), np.array(endpoint), atol =1) #atol nilai toleransi mendekati
                    if (result_variable == True):
                        end_idx = i
                        break

                #redraw contour from startpoint to endpoint
                for i in range(len(contours[m])):
                    checkpoint = [contours[m][i][0][0], contours[m][i][0][1]]
                    startpoint = [p1[0], p1[1]]
                    result_variable = np.allclose(np.array(checkpoint), np.array(startpoint), atol =1)
                    if (result_variable == True):
                        contour_part = [contours[m][i:end_idx+1]]
                        cv2.drawContours(res, contour_part, -1,(255, 0, 0), 1, lineType=8,)
                        break

        output_path = os.path.join(output_dir, 'TriangleEquation.png')
        cv2.imwrite(output_path, res)
        return res
    if jum2 == 2:
        print("bentuk=3")
    if jum2 == 3:
        print("bentuk=4")
    if jum2 == 4 or jum2 == 5:
        print("bentuk=5")

def intersectionLine(x1, y1, x2, y2, x3, y3, x4, y4):
    m1, c1 = straightLine(x1, y1, x2, y2)
    m2, c2 = straightLine(x3, y3, x4, y4)

    if m1 == m2:
        return 0

    xp = (c2 - c1) / (m1 - m2)
    yp = m1 * xp + c1

    if (x1 == x2) and ((xp - x3) * (xp - x4) < 0) and ((yp - y1) * (yp - y2) < 0):
        return 1
    if (x3 == x4) and ((xp - x1) * (xp - x2) < 0) and ((yp - y3) * (yp - y4) < 0):
        return 1

    if ((xp - x1) * (xp - x2) < 0) and ((xp - x3) * (xp - x4) < 0):
        return 1
    else:
        return 0

def straightLine(x1, y1, x2, y2):
    x = x1 - x2
    if x == 0:
        m = 1e6
    else:
        m = (y1 - y2) / x
    b = y1 - m * x1
    return m, b

def GetGoodFeaturesPSAX(jumlah, valnorm, res):
    temp1, temp2, = 0, 0
    count = 0
    banyak = jumlah * 2
    garis = np.zeros(res.shape, dtype=res.dtype)
    hasil = np.zeros(res.shape, dtype=res.dtype)
    color = (np.random.randint(256), np.random.randint(256), np.random.randint(256))

    contours, hierarchy = cv2.findContours(res, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
    minRect = [cv2.minAreaRect(contour) for contour in contours]

    for i in range(len(contours)):
        cv2.drawContours(garis, contours, i, color)
        rect_points = cv2.boxPoints(minRect[i])

    # kondisi1 = rect_points[3][0] - rect_points[0][0]
    # kondisi2 = rect_points[0][1] - rect_points[3][1]

    kondisi1 = rect_points[2][0] - rect_points[1][0]
    kondisi2 = rect_points[1][1] - rect_points[2][1]


    if kondisi1 < kondisi2:
        valnorm = math.sqrt(pow((rect_points[3][0] - rect_points[2][0], 2)) + pow(rect_points[3][1] - rect_points[2][1], 2))
    else:

        # valnorm = math.sqrt(pow(rect_points[2][0] - rect_points[3][0], 2) + pow(rect_points[2][1] - rect_points[3][1], 2))
        valnorm = math.sqrt(pow(rect_points[3][0] - rect_points[2][0], 2) + pow(rect_points[3][1] - rect_points[2][1], 2))

    coordinate1 = []  # Create an empty list for storing coordinates

    for i in range(len(contours)):
        for j in range(len(contours[i]) // 2): #kontur yang terhubung memiliki len 2 sehingga perlu dibagi 2  terlebih dahlu
            count += 1
            coordinate1.append(contours[i][j][0])

    temp1 = 0
    batasan = count
    data1 = count / (banyak + 1)

    coordinate2 = [None] * (banyak + 1)

    for i in np.arange(data1, batasan, data1):
        temp1 += 1
        temp2 = int(round(i))
        coordinate2[temp1] = coordinate1[temp2]

        if temp1 == banyak:
            break

    goodFeatures = []
    for i in range(1, banyak + 1):
        goodFeatures.append(coordinate2[i])

    return goodFeatures, valnorm


def findAngle(x1, y1, x2, y2):
    angle = math.atan2(y2 - y1, x2 - x1) * 180 / math.pi

    if -90 <= angle < 0:
        angle = abs(angle) + 90
    elif 0 <= angle < 90:
        angle = angle - 180 + 90
        angle = abs(angle) + 360
    elif 90 <= angle <= 180:
        angle = -(angle - 180) + 90
        angle += 180
    else:
        angle = abs(angle) + 90

    return angle

def opticalFlowCalcwithNormalization(jumlah, valnorm, lengthDif, sources, goodFeatures):
    thresh_diff = 20.0
    termCrit = (cv2.TERM_CRITERIA_COUNT | cv2.TERM_CRITERIA_EPS, 10, 0.03)
    winSize = (21, 21)
    length = [[] for _ in range(4)]
    for i in range(len(sources)):
        sources[i] = cv2.cvtColor(sources[i], cv2.COLOR_BGR2GRAY)
    for i in range(9):
        maxLevel = 3
        sources[i] = cv2.medianBlur(sources[i], 9)
        #cv2.calcOpticalFlowPyrLK(sources[i], sources[i + 1], goodFeatures[i], goodFeatures[i + 1], status, errs[i], winSize, maxLevel, termCrit)
        goodFeatures[i + 1], status, errs = cv2.calcOpticalFlowPyrLK(sources[i], sources[i + 1], goodFeatures[i], winSize, maxLevel, termCrit)
        print(status[i])
        print(errs[i])

        for k in range(4):
            for j in range(len(goodFeatures[i])):
                length[0] = np.sqrt((goodFeatures[i][j][0][0] - goodFeatures[i + 1][j][0][0]) ** 2 + (goodFeatures[i][j][0][1] - goodFeatures[i + 1][j][0][1]) ** 2) / valnorm * 100
                if length[0] > thresh_diff:
                    if (j > 0 and j < jumlah - 1) or (j > jumlah and j < (jumlah * 2) - 1):
                        length[1] = np.sqrt((goodFeatures[i][j - 1][0][0] - goodFeatures[i + 1][j - 1][0][0]) ** 2 + (goodFeatures[i][j - 1][0][1] - goodFeatures[i + 1][j - 1][0][1]) ** 2) / valnorm * 100
                        length[2] = np.sqrt((goodFeatures[i][j + 1][0][0] - goodFeatures[i + 1][j + 1][0][0]) ** 2 + (goodFeatures[i][j + 1][0][1] - goodFeatures[i + 1][j + 1][0][1]) ** 2) / valnorm * 100

                        if length[1] < thresh_diff:
                            length[3] = np.sqrt((goodFeatures[i][j - 1][0][0] - goodFeatures[i + 1][j - 1][0][0]) ** 2 + (goodFeatures[i][j - 1][0][1] - goodFeatures[i + 1][j - 1][0][1]) ** 2)
                            angleNorm = findAngle(goodFeatures[i][j - 1][0][0], goodFeatures[i][j - 1][0][1], goodFeatures[i + 1][j - 1][0][0], goodFeatures[i + 1][j - 1][0][1])
                            s = np.sin(angleNorm * np.pi / 180)
                            c = np.cos(angleNorm * np.pi / 180)
                            P = (goodFeatures[i][j][0][0] + s * length[3], goodFeatures[i][j][0][1] + c * length[3])
                            goodFeatures[i + 1][j][0] = P

                        elif length[2] < thresh_diff:
                            length[3] = np.sqrt((goodFeatures[i][j + 1][0][0] - goodFeatures[i + 1][j + 1][0][0]) ** 2 + (goodFeatures[i][j + 1][0][1] - goodFeatures[i + 1][j + 1][0][1]) ** 2)
                            angleNorm = findAngle(goodFeatures[i][j + 1][0][0], goodFeatures[i][j + 1][0][1], goodFeatures[i + 1][j + 1][0][0], goodFeatures[i + 1][j + 1][0][1])
                            s = np.sin(angleNorm * np.pi / 180)
                            c = np.cos(angleNorm * np.pi / 180)
                            P = (goodFeatures[i][j][0][0] + s * length[3], goodFeatures[i][j][0][1] + c * length[3])
                            goodFeatures[i + 1][j][0] = P

            for j in range(len(goodFeatures[i])):
                length[0] = np.sqrt((goodFeatures[i][j][0][0] - goodFeatures[i + 1][j][0][0]) ** 2 + (goodFeatures[i][j][0][1] - goodFeatures[i + 1][j][0][1]) ** 2) / valnorm * 100
                if length[0] > thresh_diff:
                    if j == 0 or j == jumlah:
                        length[3] = np.sqrt((goodFeatures[i][j + 1][0][0] - goodFeatures[i + 1][j + 1][0][0]) ** 2 + (goodFeatures[i][j + 1][0][1] - goodFeatures[i + 1][j + 1][0][1]) ** 2)
                        angleNorm = findAngle(goodFeatures[i][j + 1][0][0], goodFeatures[i][j + 1][0][1], goodFeatures[i + 1][j + 1][0][0], goodFeatures[i + 1][j + 1][0][1])
                        s = np.sin(angleNorm * np.pi / 180)
                        c = np.cos(angleNorm * np.pi / 180)
                        P = (goodFeatures[i][j][0][0] + s * length[3], goodFeatures[i][j][0][1] + c * length[3])
                        goodFeatures[i][j][0] = P

                    elif j == (jumlah + 1) or j == (jumlah * 2):
                        length[3] = np.sqrt((goodFeatures[i][j - 1][0][0] - goodFeatures[i + 1][j - 1][0][0]) ** 2 + (goodFeatures[i][j - 1][0][1] - goodFeatures[i + 1][j - 1][0][1]) ** 2)
                        angleNorm = findAngle(goodFeatures[i][j - 1][0][0], goodFeatures[i][j - 1][0][1], goodFeatures[i][j - 1][0][0], goodFeatures[i][j - 1][0][1])
                        s = np.sin(angleNorm * np.pi / 180)
                        c = np.cos(angleNorm * np.pi / 180)
                        P = (goodFeatures[i][j][0][0] + s * length[3], goodFeatures[i][j][0][1] + c * length[3])
                        goodFeatures[i][j][0] = P

    for i in range(9):
        for j in range(len(goodFeatures[i])):
            length = (math.sqrt(((goodFeatures[i][j][0][0] - goodFeatures[i + 1][j][0][0]) ** 2) + ((goodFeatures[i][j][0][1] - goodFeatures[i + 1][j][0][1]) ** 2)) / valnorm) * 100
            lengthDif[i].append(length)

def findCenterPoint(R, source):
    contours, _ = cv2.findContours(source, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    for i in range(len(contours)):
        if len(contours[i]) > R:
            x, y, w, h = cv2.boundingRect(contours[i])
            center_x = x + w // 2
            center_y = y + h // 2
            break

    return center_x, center_y

def featureExtractionPSAX(jumlah, X1, Y1, direction, goodFeatures):
    for j in range(jumlah):
        for i in range(9):
            vec_AC = (X1 - goodFeatures[i][j][0][0], Y1 - goodFeatures[i][j][0][1])
            vec_AB = (goodFeatures[i + 1][j][0][0] - goodFeatures[i][j][0][0], goodFeatures[i + 1][j][0][1] - goodFeatures[i][j][0][1])
            dot_product = vec_AC[0] * vec_AB[0] + vec_AC[1] * vec_AB[1]
            mag_AC = math.sqrt(vec_AC[0]**2 + vec_AC[1]**2)
            mag_AB = math.sqrt(vec_AB[0]**2 + vec_AB[1]**2)
            cos_angle = dot_product / (mag_AC * mag_AB)
            angle_rad = math.acos(cos_angle)
            angle_deg = math.degrees(angle_rad)
            if angle_deg > 90:
                # print("Keluar")
                direction[j][i] = int(0)
            else:
                # print("Masuk")
                direction[j][i] = int(1)


def ExtractionMethod(jumlah, direction):
    pf, nf= [[] for _ in range(jumlah * 2)], [[] for _ in range(jumlah * 2)]
    for j in range(jumlah * 2):
        num1, num2 = 0, 0
        for i in range(9):
            if direction[j][i] == 1:
                num1 += 1
            else:
                num2 += 1

        pf[j] = num1 / 9
        nf[j] = num2 / 9

    # MENYIMPAN FEATURE EXTRACTION METHOD I
    with open("M1F2_PSAX.csv", "a") as myfile:
        for j in range((jumlah * 2) - 1):
            myfile.write(f"{str(pf[j])},{str(nf[j])},")
            if j == (jumlah * 2) - 2:
                myfile.write(f"{str(pf[j + 1])},{str(nf[j + 1])}\n")

def sort_by_second(elem):
    return elem[1]

def goodFeaturesVisualization(jumlah, goodFeatures, rawImages):
    output_dir = '9.GoodFeatures'
    os.makedirs(output_dir, exist_ok=True)
    for framecount, image in rawImages.items():
        if framecount == 0:
            for i in range(jumlah*2):
                x, y = goodFeatures[framecount][i][0]
                output_path = os.path.join(output_dir, 'GF.png')
                cv2.circle(image, (int(x), int(y)), 1, (255, 255, 255), 2, 8, 0)
                cv2.imwrite(output_path, image)
            break

def track_visualization(jumlah, images, goodFeatures):
    output_dir = '10.Tracking'
    os.makedirs(output_dir, exist_ok=True)
    trackingresult = {}
    # Visualize Tracking
    vect1 = [[] for _ in range(10)]
    vect2 = [[] for _ in range(10)]
    coordinate = np.zeros((50, 50, 2), dtype=np.float32)

    # Sorting data for the left and right sides
    for i in range(len(images)):
        for j in range(jumlah):
            vect1[i].append(tuple(goodFeatures[i][j][0]))
            vect2[i].append(tuple(goodFeatures[i][j + jumlah][0]))
        vect1[i] = sorted(vect1[i], key=sort_by_second)
        vect2[i] = sorted(vect2[i], key=sort_by_second)

    # Transfer sorted data to the coordinate variable
    for i in range(len(images)):
        temp1 = -1
        for j in range(jumlah - 1, -1, -1):
            temp1 += 1
            coordinate[i][temp1] = np.array(vect1[i][j])
            if j == jumlah - 1:
                for k in range(jumlah):
                    coordinate[i][k + jumlah] = np.array(vect2[i][k])


    # Draw lines and circles for visualization
    for i, image in images.items():
        # image = cv2.cvtColor(image, cv2.COLOR_GRAY2BGR)
        for j in range(jumlah * 2 - 1):
            a = tuple(map(int, coordinate[i][j]))
            b = tuple(map(int, coordinate[i][j + 1]))
            # cv2.line(image, tuple(map(int, coordinate[i][j])), tuple(map(int, coordinate[i][j + 1])), (255, 255, 255), 2)
            cv2.line(image, a, b, (0, 255, 0), 1)

        for j in range(jumlah * 2):
            x, y = goodFeatures[i][j][0]
            cv2.circle(image, (int(x), int(y)), 1, (255, 255, 255), 2, 8, 0)
            trackingresult[i] = image
        output_path = os.path.join(output_dir, f"tracking_{i}.png")
        cv2.imwrite(output_path, image)

    return trackingresult

def track_visualization2(jumlah, images, goodFeatures):
    for i in range(len(images)-1):
        for j in range(jumlah * 2):
            output_path = os.path.join('10.Tracking', f'TrackingLK.png')
            gfx_awal = int(goodFeatures[0][j][0][0])
            gfy_awal = int(goodFeatures[0][j][0][1])
            gfx_akhir = int(goodFeatures[len(images) - 1][j][0][0])
            gfy_akhir = int(goodFeatures[len(images) - 1][j][0][1])
            cv2.circle(images[0], (gfx_awal, gfy_awal), 1, (255, 255, 255), 2, 8, 0)
            cv2.line(images[0], (gfx_awal, gfy_awal), (gfx_akhir, gfy_akhir), (255, 255, 255), 1)
            cv2.imwrite(output_path, images[0])

def classification():
    df = pd.read_csv('M1F2_PSAX.csv')
    X = df.drop('CLASS', axis=1)
    X = preprocessing.StandardScaler().fit(X).transform(X.astype(float))
    temp = X.shape[0]
    filename = 'modelSVM'
    loaded_model = joblib.load(filename)
    model = pickle.dumps(loaded_model)
    prediction = pickle.loads(model)
    print(X[temp-1:temp])
    result = prediction.predict(X[temp-1:temp])

    with open("M1F2_PSAX.csv", "r") as data:
        lines = data.readlines()
        lines = lines[:-1]
    with open("M1F2_PSAX.csv", "w") as data:
        for line in lines:
            data.write(line)

    if result == 0:
        print("Tidak Normal")
        return 'Tidak Normal'
    else:
        print("Normal")
        return 'Normal'

def frames2video(images, uid):
    img_array = []
    for i, img in images.items():
        height, width, layers = img.shape
        size = (width,height)
        img_array.append(img)
    out = cv2.VideoWriter(f'result_{uid}.mp4',cv2.VideoWriter_fourcc(*'mp4v'), 20, size)
   #kasih print
    print("Menyimpan hasil video ...")
    for i in range(len(img_array)):
        out.write(img_array[i])
    out.release()


# PUNYA AYLA

def init_csv(csv_filename):
    if not os.path.exists(csv_filename):
        with open(csv_filename, mode='w', newline='') as file:
            writer = csv.writer(file)
            writer.writerow([
                "area_total", "num_contours", "avg_area", "centroid_x_mean",
                "aspect_ratio_avg", "extent_avg",
                "hue_bin_1", "hue_bin_2", "hue_bin_3", "hue_bin_4", "label"
            ])
def detect_color(hsv, lower, upper):
    return cv2.inRange(hsv, lower, upper)

def detect_two_images(frame):
    h, w = frame.shape[:2]
    roi_yellow = frame[0:h//4, (w//2 - w//10):(w//2 + w//10)]
    gray = cv2.cvtColor(roi_yellow, cv2.COLOR_BGR2GRAY)
    _, binary = cv2.threshold(gray, 127, 255, cv2.THRESH_BINARY)
    return cv2.countNonZero(binary) <= 200

def video2frame_ayla(video_path):
    cap = cv2.VideoCapture(video_path)
    frame_idx = 0
    processed_frames = 0
    total_frame_to_process = 10
    # Resolusi output video
    IM_WIDTH, IM_HEIGHT = 640, 480
    frames_with_features = []
    while cap.isOpened() and processed_frames < total_frame_to_process:
        ret, frame = cap.read()
        if not ret:
            break

        frame_idx += 1
        frame = cv2.resize(frame, (IM_WIDTH, IM_HEIGHT))

        two_images = detect_two_images(frame)
        if two_images:
            TL_Zone1 = (int(IM_WIDTH * 0.43), int(IM_HEIGHT * 0.3))
            BR_Zone1 = (IM_WIDTH, int(IM_HEIGHT * 0.5))
        else:
            TL_Zone1 = (int(IM_WIDTH * 0.2), int(IM_HEIGHT * 0.3))
            BR_Zone1 = (int(IM_WIDTH * 0.75), int(IM_HEIGHT * 0.5))

        roi = frame[TL_Zone1[1]:BR_Zone1[1], TL_Zone1[0]:BR_Zone1[0]]
        hsv = cv2.cvtColor(roi, cv2.COLOR_BGR2HSV)

        masks = [
            detect_color(hsv, np.array([35,100,100]), np.array([85,255,255])),
            detect_color(hsv, np.array([26,100,100]), np.array([34,255,255])),
            detect_color(hsv, np.array([11,150,150]), np.array([25,255,255])),
        ]
        combined_mask = cv2.bitwise_or(masks[0], cv2.bitwise_or(masks[1], masks[2]))

        contours, _ = cv2.findContours(combined_mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        all_contours = [c for c in contours if cv2.contourArea(c) > 100]

        h_mask, w_mask = combined_mask.shape
        left_count = cv2.countNonZero(combined_mask[:, :w_mask//2])
        right_count = cv2.countNonZero(combined_mask[:, w_mask//2:])

        if left_count > 0 and right_count > 0:
            kondisi = "detected_both_sides"
            label = 0
        elif left_count > right_count:
            kondisi = "dominant_left"
            label = 0
        elif right_count > 0 and left_count == 0:
            kondisi = "only_right"
            label = 1
        else:
            kondisi = "unknown"
            label = 1

        # Tambahkan kotak hijau hanya untuk kondisi bocor
        if kondisi in ["detected_both_sides", "dominant_left"]:
            if all_contours:
                x_all, y_all, w_all, h_all = cv2.boundingRect(np.vstack(all_contours))
                cv2.rectangle(frame, (x_all + TL_Zone1[0], y_all + TL_Zone1[1]),
                            (x_all + w_all + TL_Zone1[0], y_all + h_all + TL_Zone1[1]),
                            (0, 255, 0), 2)

        # Ekstraksi fitur
        area_total = sum([cv2.contourArea(c) for c in all_contours])
        num_contours = len(all_contours)
        avg_area = area_total / num_contours if num_contours else 0
        cx_list, aspect_ratios, extents = [], [], []

        for c in all_contours:
            x, y, w, h = cv2.boundingRect(c)
            aspect_ratios.append(w / h if h != 0 else 0)
            extents.append(cv2.contourArea(c) / (w * h) if w * h != 0 else 0)
            M = cv2.moments(c)
            if M["m00"] != 0:
                cx_list.append(M["m10"] / M["m00"])

        centroid_x_mean = np.mean(cx_list) if cx_list else 0
        aspect_ratio_avg = np.mean(aspect_ratios) if aspect_ratios else 0
        extent_avg = np.mean(extents) if extents else 0

        hue = hsv[:, :, 0]
        hist = cv2.calcHist([hue], [0], combined_mask, [4], [0, 180])
        hist = cv2.normalize(hist, hist).flatten()

        feature_row = [
            area_total, num_contours, avg_area, centroid_x_mean,
            aspect_ratio_avg, extent_avg, *hist[:4]
        ]
        frames_with_features.append((frame.copy(), feature_row))
        processed_frames += 1

    cap.release()
    return frames_with_features

def simpanekstraksifitur_ayla(frames_with_features):
    csv_filename="data_uji_baru.csv"
    
    # Cek apakah frames_with_features berisi pasangan (frame, fitur)
    if isinstance(frames_with_features[0], (tuple, list)) and len(frames_with_features[0]) == 2:
        fitur_list = [f for _, f in frames_with_features]
    else:
        fitur_list = frames_with_features
    #print("Tipe data fitur baris 0:", type(fitur_list[0]))
    #print("Panjang fitur baris 0:", len(fitur_list[0]))
    #print("Isi fitur baris 0:", fitur_list[0])

    # Opsional: Validasi panjang setiap fitur
    """for i, fitur in enumerate(fitur_list):
        if not isinstance(fitur, (list, np.ndarray)):
            raise ValueError(f"Data fitur baris {i} bukan list/array")
        if len(fitur) != 10:
            raise ValueError(f"Data fitur baris {i} panjangnya {len(fitur)}, harus 10")"""
    
    df_features = pd.DataFrame(fitur_list,
        columns=["area_total", "num_contours", "avg_area", "centroid_x_mean",
                 "aspect_ratio_avg", "extent_avg",
                 "hue_bin_1", "hue_bin_2", "hue_bin_3", "hue_bin_4"])

    # Append atau tulis CSV
    if os.path.exists(csv_filename):
        df_features.to_csv(csv_filename, mode='a', header=False, index=False)
    else:
        df_features.to_csv(csv_filename, index=False)
    """df_features = pd.DataFrame([f for _, f in frames_with_features],
                              columns=["area_total", "num_contours", "avg_area", "centroid_x_mean",
                                       "aspect_ratio_avg", "extent_avg",
                                       "hue_bin_1", "hue_bin_2", "hue_bin_3", "hue_bin_4"])

    # Append ke CSV
    if os.path.exists(csv_filename):
        df_features.to_csv(csv_filename, mode='a', header=False, index=False)
    else:
        df_features.to_csv(csv_filename, index=False)"""
    """# Jika frames_with_features berisi (frame, fitur), ambil fitur saja:
    if isinstance(frames_with_features[0], (tuple, list)) and len(frames_with_features[0]) == 2:
        fitur_list = [f for _, f in frames_with_features]
    else:
        fitur_list = frames_with_features

    # Periksa apakah semua fitur sudah dalam bentuk list/array 1D dengan panjang kolom yang sama
    for i, fitur in enumerate(fitur_list):
        if not isinstance(fitur, (list, np.ndarray)):
            raise ValueError(f"Data fitur baris {i} bukan list/array")
        if len(fitur) != 10:
            raise ValueError(f"Data fitur baris {i} panjangnya {len(fitur)}, harus 10")

    df_features = pd.DataFrame(fitur_list,
        columns=["area_total", "num_contours", "avg_area", "centroid_x_mean",
                 "aspect_ratio_avg", "extent_avg",
                 "hue_bin_1", "hue_bin_2", "hue_bin_3", "hue_bin_4"])
    #df_features = pd.DataFrame(frames_with_features,
        columns=["area_total", "num_contours", "avg_area", "centroid_x_mean",
                 "aspect_ratio_avg", "extent_avg",
                 "hue_bin_1", "hue_bin_2", "hue_bin_3", "hue_bin_4"])"""
    #df_features.to_csv(csv_filename, index=False)

def classify_frames_ayla(frames_with_features, model_path="svm_model_terbaru2.pkl", scaler_path="scaler_terbaru2.pkl"):
   
    model = joblib.load(model_path)
    scaler = joblib.load(scaler_path)
    if isinstance(frames_with_features[0], (tuple, list)) and len(frames_with_features[0]) == 2:
        fitur_list = [f for _, f in frames_with_features]
    else:
        fitur_list = frames_with_features
    df_features = pd.DataFrame(fitur_list,
        columns=["area_total", "num_contours", "avg_area", "centroid_x_mean",
                 "aspect_ratio_avg", "extent_avg",
                 "hue_bin_1", "hue_bin_2", "hue_bin_3", "hue_bin_4"])
    X_test_scaled = scaler.transform(df_features.values)
    y_pred = model.predict(X_test_scaled)
    label_mapping = {0: "Bocor", 1: "Normal"}
    y_pred_labels = pd.Series(y_pred).map(label_mapping).values
    return y_pred_labels

def save_result_video_ayla(frames_with_features, y_pred_labels, uid):
    IM_WIDTH=640 
    IM_HEIGHT=480
    out_video = cv2.VideoWriter(f'result_{uid}.mp4',cv2.VideoWriter_fourcc(*'mp4v'), 20.0, (IM_WIDTH, IM_HEIGHT))

    normal_ctr = 0
    bocor_ctr = 0

    for i, (frame, _) in enumerate(frames_with_features):
        label = y_pred_labels[i]
        print(f"Frame {i+1:02d}: {label}")
        out_video.write(frame)  # tulis frame

        if label == "Normal":
            normal_ctr += 1
        else:
            bocor_ctr += 1

    out_video.release()

    if bocor_ctr >= 4:
        hasil = 'Bocor'
    elif normal_ctr > 7:   
        hasil = 'Normal'
    else:
        hasil = 'Bocor'

    print("Hasil deteksi mayoritas:", hasil)
    return hasil
