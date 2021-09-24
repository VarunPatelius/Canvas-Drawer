import cv2 as cv                                #This is a computer vision library which allows for image manipulation
from time import sleep                          #Used to stop the program for short periods of time to allow for mouse to move to location
from pynput.mouse import Button, Controller     #Used to control the mouse so that it clicks the coordinate to draw on
from pynput.keyboard import Key, Listener       #Used to listen for keys being pressed so that the program can be either restarted or halted
from random import shuffle                      #Used to shuffle up all colored points so that the image is randomly created
from threading import Thread                    #Used for the thread which will be actually running the drawing function
from skimage import io                          #Used to easily download images from the internet without any hassle (HTTPS only)
from datetime import timedelta, datetime        #Used to calculate and measure the time performance of the drawing function

CORNER_ONE = (261, 237)                         #These are the corners of the area which the drawing function will draw within (TOP LEFT)
CORNER_TWO = (1039, 237)                        #(TOP RIGHT)

CORNER_THREE = (261, 807)                       #(BOTTOM LEFT)
CORNER_FOUR = (1039, 807)                       #(BOTTOM RIGHT)

WINDOW_HEIGHT = CORNER_THREE[1] - CORNER_ONE[1] #The height of the canvas is calculated by finding the distance between the top two corners and bottom two
WINDOW_WIDTH = CORNER_FOUR[0] - CORNER_THREE[0] #The width of the canvas is calculated by finding the distance between the rightmost and leftmost corners

class ImageDrawer:
    def __init__(self):
        self.mouse = Controller()                               #Mouse controller which allows for the mouse to be moved and clicked
        self.coloring = True                                    #When true, this will keep the drawing function in a drawing state
        self.rerun = True                                       #When true, this will allow the program to restart when the shift key is pressed
        self.CLICK_SPEED = timedelta(microseconds=7500)         #The estimated time for a click to take place, used to create an estimated completion time

        drawingThread = Thread(target=self.run, daemon=True)    #This is the thread in which the drawing function will be running
        drawingThread.start()                                   #This thread is started

        with Listener(on_press=self.keyStop) as listener:       #In the main thread, the keyboard listener object listens for any stoppage keys (shift, esc)  
            listener.join()


    def rescaleImage(self, image, scalingFactor):
        '''
        Simply used to rescale an image so that it may fit on the canvas if its too large
        '''
        newWidth = int(image.shape[1] * scalingFactor)
        newHeight = int(image.shape[0] * scalingFactor)

        newDimensions = (newWidth, newHeight)
        return cv.resize(image, newDimensions, interpolation=cv.INTER_AREA)


    def keyStop(self, key):
            '''
            This is the function which the key listener runs whenever it detects that a key has been pressed
            '''
            if key == Key.esc:          #When the escape key is pressed, it will close the drawing and main threads by setting exit flags
                self.rerun = False
                self.coloring = False
                return False

            elif key == Key.shift:      #When the shift key is pressed, the program will stop drawing and you can go ahead and add a new input image link
                self.coloring = False


    def imageProcessing(self):
        '''
        This is the function which loads in an input image, converts it to a gray scale and then uses Otsu Thresholding to convert it to black and white
        '''
        self.colorPoints = []           #This is a list which will contain the coordinate points of all the colored points
        fileToOpen = input("\nPlease type in the name of the file that you would like to open: ")

        if "https" in fileToOpen:
            img = io.imread(fileToOpen) #Scikit-image is then used to load the image from a URL, an error will be raised if this is not successful, works with
                                        #DuckDuckGo links, not tested with Google image links

        grayscale = cv.cvtColor(img, cv.COLOR_BGR2GRAY)                         #Image is then converted into a grayscale using opencv-python
        thresh, blackWhite = cv.threshold(grayscale, 127, 255, cv.THRESH_OTSU)  #Is then converted to an image using thresholding

        height, width = blackWhite.shape[:2]            #The height and width of the image are then retrieved to ensure that they aren't going to be too long/high

        if width >= height:                             #This basically scales the image once to make sure it fits in the boundaries and once more to make it draw faster
            factor = WINDOW_WIDTH / width
            scaledImage = self.rescaleImage(self.rescaleImage(blackWhite, factor), 0.75)
        else:
            factor = WINDOW_HEIGHT / height
            scaledImage = self.rescaleImage(self.rescaleImage(blackWhite, factor), 0.75)

        finalHeight, finalWidth = scaledImage.shape[:2]

        for i in range(finalHeight):                    #Iterates over every point in the scaled, processed image and if the point is colored, it is added to the list
            for j in range(finalWidth):
                if scaledImage[i, j] == 0:
                    self.colorPoints.append((j, i))


    def run(self):
        '''
        This function is run by the created thread
        '''
        while self.rerun:
            self.coloring = True

            self.imageProcessing()          #Image is first processed
            print(f"Estimated Completion Time: {self.CLICK_SPEED * len(self.colorPoints)} for {len(self.colorPoints)} points.")
            sleep(5)                        #The user is given 5 seconds to switch tabs to the drawing canvas of choice

            shuffle(self.colorPoints)       #The colored points are all shuffled so that they are added at random
            start = datetime.now()          #The draw time timer begins
            for colorPoint in self.colorPoints:
                self.mouse.position = (CORNER_ONE[0] + colorPoint[0], CORNER_ONE[1] + colorPoint[1])
                sleep(0.0055)
                self.mouse.click(Button.left)   #Every point is then dotted out

                if self.coloring == False:      #Whenever the shift key is pressed, this will stop the drawing
                    break
            end = datetime.now()
            print(f"Completion Time: {end - start}.")


ImageDrawer()