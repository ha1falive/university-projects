import cv2 as cv
import numpy as np
import matplotlib.pyplot as plt
import pandas as pd


# Создадим класс детекторов
class Detector:
 
    def __init__(self, x, y):
        self.detX = x
        self.detY = y
        self.avgColour = []
        self.detections = []
 
    def addAVGColourSum(self, value):
        self.avgColour.append(value)
 
 
drawing = False
mouseX, mouseY = -1, -1
size = 20
 
number_of_lanes = 3
detectors_per_lane = 2
 
lanes = []
detectors = [] 


# Создадим фукнцию для фильтра дескритизации полученных данных с детекторов
def detectorsDiscretizationFilter(detectors, frameCounter):
    for i in range(0, len(detectors)):
        for j in range(0, frameCounter - 1):
            frames_unite = 10
            frames_count = 0
            for k in range(1, frames_unite):
                if (detectors[i].detections[j] == 1 and ((j + k) < (frameCounter - k - 1)) and (
                        detectors[i].detections[j + k] == 1)):
                    frames_count = frames_count + 1
                for l in range(j, j + frames_count):
                    detectors[i].detections[l] = 1
 
    for i in range(0, len(detectors)):
        for j in range(0, frameCounter - 2):
            neighboursSum = detectors[i].detections[j - 1] + detectors[i].detections[j + 1]
            if detectors[i].detections[j] == 1 and neighboursSum == 0:
                detectors[i].detections[j] = 0


# Создадим фукнцию для дискретезации полученных данных
def detectorsDiscretization(detectors, frameCounter):
    for detector in detectors:
        detector.detections = [0] * frameCounter
 
    for i in range(0, len(detectors)):
        for j in range(0, frameCounter - 1):
            test = abs((detectors[i].avgColour[j] - detectors[i].avgColour[j + 1]) / detectors[i].avgColour[j]) * 100
            if test > 1.5:
                detectors[i].detections[j + 1] = 1


# Функция получения среднего цвета
def getAVGcolourSum(gray, detectors):
    cv.namedWindow('detector', cv.WINDOW_NORMAL)
    for detector in detectors:
        detectorZone = gray[int((detector.detY - (size / 2))):int((detector.detY + (size / 2))),
                       int((detector.detX - (size / 2))):int((detector.detX + (size / 2)))]
        avg_color_per_row = np.average(detectorZone, axis=0)
        avg_color = np.average(avg_color_per_row, axis=0)
        # detector.avgColour.append(avg_color)
        detector.addAVGColourSum(avg_color)
        print(avg_color)
        cv.imshow('detector', detectorZone)


# Функция для отрисовки детекторов
def draw_detector(x, y, lane_number):
    colours = [[0, 0, 255], [0, 255, 0], [255, 0, 0], [0, 0, 127], [0, 127, 0], [127, 0, 0]]
    cv.rectangle(frame, (int(x - (size / 2)), int(y - (size / 2))),
                 (int(x + (size / 2)), int(y + (size / 2))), colours[lane_number], 2)


# Функция для установки детекторов
def set_detector(event, x, y, flags, param, count_of_lanes=0):
    global mouseX, mouseY, drawing
 
    if event == cv.EVENT_LBUTTONDOWN:
        if len(lanes) != 0 and len(lanes) * len(lanes[0]) == number_of_lanes * detectors_per_lane:
            print("Max number of detectors reached")
        else:
            mouseX, mouseY = x, y
            draw_detector(mouseX, mouseY, len(lanes))
            cv.imshow('Frame', frame)
            print(str(mouseX) + " " + str(mouseY))
            if len(detectors) < detectors_per_lane:
                detectors.append(Detector(mouseX, mouseY))
            if len(detectors) == detectors_per_lane:
                lanes.append(detectors.copy())
                detectors.clear()


# Откроем видео и обработаем его покадрово
# 
# проверим время работы алгоритма
from datetime import datetime
t1 = datetime.now()
# image_path = r'E:\PyProjects\pythonProject\Brain.jpg'
# directory = r'E:\PyProjects\pythonProject\new folder'
frameCounter = 0
 
cap = cv.VideoCapture('C:/Users/pasha/Downloads/07.30.00-07.35.00[R][0@0][0].mp4')
 
if not cap.isOpened():
    print("Error opening file")
 
cv.namedWindow('Frame', cv.WINDOW_NORMAL)
cv.setMouseCallback('Frame', set_detector)
 
cv.resizeWindow('Frame', 1920, 1080)
# os.chdir(directory)
 
# cap.set(1, 0)
ret, frame = cap.read()
 
cv.imshow('Frame', frame)
cv.waitKey(0)
cv.namedWindow('Frame', cv.WINDOW_NORMAL)
cv.resizeWindow('Frame', 800, 600)


# Обработка видео до последнего кадра
while (cap.isOpened()):
    # plt.axis([0, frameCounter, 0, 100])
    ret, frame = cap.read()
    if not ret:
        print("Can't receive frame (stream end?). Exiting ...")
        break
    # Переводим в градации серого
    gray = cv.cvtColor(frame, cv.COLOR_BGR2GRAY)
    # Если считался очередной кадр
    if ret == True:
        # Выводим номер кадра в верхнем левом углу
        cv.putText(frame, "Frame " + str(frameCounter), (50, 50), cv.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255), 2,
                   cv.LINE_AA)
        # Отрисовка детекторов
        colour_counter = 0
        for lane in lanes:
            for detector in lane:
                draw_detector(detector.detX, detector.detY, colour_counter)
            colour_counter += 1
            getAVGcolourSum(gray, lane)
        cv.imshow('Frame', frame)
        # if frameCounter % 10 == 0:
        # cv.imwrite("Frame_" + str(frameCounter) + ".png",frame)
        frameCounter += 1
        if cv.waitKey(25) & 0xFF == ord('q'):
            break
    else:
        break
cap.release()
cv.destroyAllWindows()
# plt.axes[(1 , 1000) , (1,255)]
 
# print(detectors[0].avgColour[0])
t2 = datetime.now()


# Заполняем csv файл координатами детекторов
data = dict()
lane_counter = 1
for lane in lanes:
    detectorNumber = 1
    for detector in lane:
        new_dict = {"lane" + str(lane_counter) + " det" + str(detectorNumber) + " X": [detector.detX], "lane" + str(lane_counter) + " det" + str(detectorNumber) + " Y": [detector.detY]}
        data.update(new_dict)
        detectorNumber += 1
    lane_counter += 1
df = pd.DataFrame(data)
df.to_csv(r'Coordinates.csv', sep=';', index=False)


# Заполняем csv файл средними цветами с детекторов
data = dict()
lane_counter = 1
for lane in lanes:
    detectorNumber = 1
    for detector in lane:
        new_dict = {"lane" + str(lane_counter) + " det" + str(detectorNumber): detector.avgColour}
        data.update(new_dict)
        detectorNumber += 1
    lane_counter += 1
df = pd.DataFrame(data)
df.to_csv(r'AvgColours.csv', sep=';', index=False)
 
for lane in lanes:
    detectorsDiscretization(lane, frameCounter)


# Заполняем csv файл дискретными значениями с детекторов
data = dict()
lane_counter = 1
for lane in lanes:
    detectorNumber = 1
    for detector in lane:
        new_dict = {"lane" + str(lane_counter) + " det" + str(detectorNumber): detector.detections}
        data.update(new_dict)
        detectorNumber += 1
    lane_counter += 1
df = pd.DataFrame(data)
df.to_csv(r'RawDetections.csv', sep=';', index=False)
 
for lane in lanes:
    detectorsDiscretizationFilter(lane, frameCounter)


# Заполняем csv файл дискретными отфильтрованными значениями с детекторов
data = dict()
lane_counter = 1
for lane in lanes:
    detectorNumber = 1
    for detector in lane:
        new_dict = {"lane" + str(lane_counter) + " det" + str(detectorNumber): detector.detections}
        data.update(new_dict)
        detectorNumber += 1
    lane_counter += 1
df = pd.DataFrame(data)
df.to_csv(r'FilteredDetections.csv', sep=';', index=False)


# Построим графики для среднего цвета по кадрам
x = []
for i in range(1, frameCounter + 1):
    x.append(i)

position = 1
 
fig, axs = plt.subplots(number_of_lanes, detectors_per_lane, figsize=(9, 9))
i = 0
for lane in lanes:
    j = 0
    for detector in lane:
        axs[i, j].plot(x, detector.avgColour)
        axs[i, j].set_title("Lane №" + str(i) + "detector №" + str(j))
        j += 1
    i += 1
for ax in axs.flat:
    ax.set(xlabel="Frames", ylabel="Average colour")
plt.show()


# Построим дискритизированные графики количества автомобилей
fig, axs = plt.subplots(number_of_lanes, detectors_per_lane, figsize=(12, 12))
i = 0
for lane in lanes:
    j = 0
    for detector in lane:
        axs[i, j].plot(x, detector.detections)
        axs[i, j].set_title("Lane №" + str(i) + "detector №" + str(j))
        j += 1
    i += 1
for ax in axs.flat:
    ax.set(xlabel="Frames", ylabel="Detections")
plt.show()


# Функция для вычисления интенсивности потока
frame_rate = 25
lane_density_per_sec = []
lanes_density_per_sec = []

def density_to_sec(density_lanes):
    for lane in density_lanes:
        frame_counter = 0
        second = 1
        while frame_counter <= len(lane):
            frame_sum = 0
            for i in range(frame_rate * (second - 1), frame_rate * second):
                if i < len(lane):
                    frame_sum += lane[i]
                frame_counter += 1
            lane_density_per_sec.append(frame_sum/frame_rate)
            second += 1
        lanes_density_per_sec.append(lane_density_per_sec.copy())
        lane_density_per_sec.clear()

number_of_lanes = 3  # количество полос
detectors_per_lane = 2  # количество детекторов на полосу


# Построим график интенсивности
df = pd.read_csv('FilteredDetections.csv')
 
for i in range(len(df)):
    single_line_values = df.values[i][0].split(';')
    m = 0
    for j in range(len(lanes)):
        for k in range(len(lanes[j])):
            lanes[j][k].detections.append(single_line_values[m])
            m += 1

print(single_line_values[5][0])
# плотность на полосу
density_per_lane = []
# плотность по полосам
density_lanes = []
 
detections_counter = 0
for i in range(len(lanes)):
    for k in range(len(lanes[i][0].detections)):
        for j in range(len(lanes[i])):
            if lanes[i][j].detections[k] == '1':
                detections_counter += 1.0
        density_per_lane.append(detections_counter / len(lanes[i]))
        detections_counter = 0
    density_lanes.append(density_per_lane.copy())
    density_per_lane.clear()

x = []
for i in range(0, len(lanes[0][0].detections)):
    x.append(i)


density_to_sec(density_lanes)

fig, axs = plt.subplots(number_of_lanes, figsize=(15, 15))
i = 0
for lane in density_lanes:
    j = 0
    axs[i].step(x, lane)
    axs[i].set_title("Lane №" + str(i))
    i += 1
for ax in axs.flat:
    ax.set(xlabel="Frames", ylabel="Detections")
plt.show()


# Подсчитаем количество автомобилей на каждом детекторе
lane_counter = 1
for lane in lanes:
    detectorNumber = 1
    for detector in lane:
        count = 0
        for i in range(0, len(detector.detections)):
            if detector.detections[i] == 1:
                count += 1
        print("lane" + str(lane_counter) + " det" + str(detectorNumber) + " = " + str(count))
        detectorNumber += 1
    lane_counter += 1

