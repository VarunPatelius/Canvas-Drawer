import cv2 as cv
from time import sleep
from pynput.mouse import Button, Controller
from pynput.keyboard import Key, Listener
from random import shuffle
from threading import Thread
from skimage import io
import numpy as np
from datetime import timedelta, datetime
from itertools import groupby
from operator import itemgetter

CORNER_ONE = (261, 237)
CORNER_TWO = (1039, 237)

CORNER_THREE = (261, 807)
CORNER_FOUR = (1039, 807)

WINDOW_HEIGHT = 807 - 237
WINDOW_WIDTH = 1039 - 261

class ImageDrawer:
    def __init__(self):
        self.mouse = Controller()
        self.coloring = True
        self.rerun = True
        self.CLICK_SPEED = timedelta(microseconds=7500)

        drawingThread = Thread(target=self.run, daemon=True)
        drawingThread.start()

        with Listener(on_press=self.keyStop) as listener:   
            listener.join()


    def rescaleImage(self, image, scalingFactor):
        newWidth = int(image.shape[1] * scalingFactor)
        newHeight = int(image.shape[0] * scalingFactor)

        newDimensions = (newWidth, newHeight)
        return cv.resize(image, newDimensions, interpolation=cv.INTER_AREA)


    def keyStop(self, key):
            if key == Key.esc:
                self.rerun = False
                self.coloring = False
                return False

            elif key == Key.shift:
                self.coloring = False


    def imageProcessing(self):
        self.colorPoints = []
        self.coloredColumns = {}
        fileToOpen = input("\nPlease type in the name of the file that you would like to open: ")

        if "https" in fileToOpen:
            img = io.imread(fileToOpen)
        else:
            img = cv.imread(f"images/{fileToOpen}")

        grayscale = cv.cvtColor(img, cv.COLOR_BGR2GRAY)
        thresh, blackWhite = cv.threshold(grayscale, 127, 255, cv.THRESH_OTSU)

        height, width = blackWhite.shape[:2]

        if width >= height:
            factor = WINDOW_WIDTH / width
            scaledImage = self.rescaleImage(self.rescaleImage(blackWhite, factor), 0.80)
        else:
            factor = WINDOW_HEIGHT / height
            scaledImage = self.rescaleImage(self.rescaleImage(blackWhite, factor), 0.80)

        finalHeight, finalWidth = scaledImage.shape[:2]

        for i in range(finalHeight):
            self.coloredColumns[i] = []
            for j in range(finalWidth):
                if scaledImage[i, j] == 0:
                    self.coloredColumns[i].append(j)

        for yVal, xVals in self.coloredColumns.items():
            for k, g in groupby(enumerate(xVals), lambda x:x[0]-x[1]):
                numberRange = list(map(itemgetter(1), g))

                totalDistance = numberRange[-1] - numberRange[0]
                self.colorPoints.append((numberRange[0], yVal, totalDistance))


    def run(self):
        while self.rerun:
            self.coloring = True

            self.imageProcessing()
            print(f"Estimated Completion Time: {self.CLICK_SPEED * len(self.colorPoints*2)} for {len(self.colorPoints)} points.")
            sleep(5)

            start = datetime.now()
            for colorPoint in self.colorPoints:
                x, y, end = colorPoint[0], colorPoint[1], colorPoint[2]

                self.mouse.position = (CORNER_ONE[0] + x, CORNER_ONE[1] + y)
                sleep(0.0055)
                self.mouse.press(Button.left)
                
                self.mouse.position = (CORNER_ONE[0] + x + end, CORNER_ONE[1] + y)
                sleep(0.0055)
                self.mouse.release(Button.left)

                if self.coloring == False:
                    break
            end = datetime.now()
            print(f"Completion Time: {end - start}.")


ImageDrawer()