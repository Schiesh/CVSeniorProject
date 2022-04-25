from copy import deepcopy
from tkinter import *
from tkinter import filedialog
import cv2
import pickle
import cvzone
import numpy as np


homeWindow = Tk()
homeWindow.title("Parking Spot Locator")
homeWindow.geometry("1000x275")

def openFileDirectory():
    global directory
    homeWindow.directory = filedialog.askdirectory(title="Select a directory")
    directoryLabel = Label(homeWindow, text=homeWindow.directory, fg="black").grid(row=6, column=2)

# Opens the file dialogue and allows user to select what parking lot file they want to view
def chooseViewFile():
    global viewFilePath
    homeWindow.viewFile = filedialog.askopenfilename(title="Select the viewing file", initialdir=homeWindow.directory, filetypes=(('image files', '*.img'), ('mp4 files', '*.mp4')))
    viewFilePath = str(homeWindow.viewFile)
    viewFileLabel = Label(homeWindow, text=homeWindow.viewFile, fg="black").grid(row=7, column=2)

# Passes the viewFile to main.py
def getViewFile():
    return viewFilePath

# Opens the file dialogue for choosing a configure file.
def chooseConfigureFile():
    global configureFilePath
    homeWindow.configureFile = filedialog.askopenfilename(title="Select the configuration file", initialdir=homeWindow.directory, filetypes=(('image files', '*.png'),('image files', '*.jpg') ))
    configureFilePath = str(homeWindow.configureFile)
    configureFileLabel = Label(homeWindow, text=homeWindow.configureFile, fg="black").grid(row=8, column=2)

def getConfigureFile():
    return configureFilePath

# Opens the file dialogue for choosing the parking positions' file.
def chooseParkingPositions():
    global parkingPositionsFilePath
    homeWindow.parkingPositions = filedialog.askopenfilename(title="Select the parking positions", initialdir=homeWindow.directory)
    parkingPositionsFilePath = str(homeWindow.parkingPositions)
    parkingPositionsLabel = Label(homeWindow, text=homeWindow.parkingPositions, fg="black").grid(row=9, column=2)

def getParkingPositions():
    return parkingPositionsFilePath


#Opens up the GUI for viewing the parking lot and seeing what spaces are open
def viewLot():

    capture = cv2.VideoCapture(getViewFile())

    with open(getParkingPositions(), 'rb') as file:
        position_list = pickle.load(file)

    width, height = 45, 20

    position_list_copy = np.array(position_list, dtype=None, copy=True, order='K', subok=False, ndmin=0)

    # Method to check processed frame from video feed
    def check_parking_space(img_processed):

        space_counter = 0

        # Looping through each segment created for video feed
        for pos in position_list_copy:

            pts = np.array([pos[0], pos[1], pos[2], pos[3]])
            rect = cv2.boundingRect(pts)
            x, y, w, h = rect

            img_crop = img_processed[y:y + h, x:x + w]
            count = cv2.countNonZero(img_crop)

            # When the pixel count is less than the threshold's set amount then there is no car.
            if count < 230:
                color = (0, 255, 0)
                thickness = 3
                space_counter += 1
            else:
                color = (0, 0, 255)
                thickness = 2

            # Color and thickness of segmented area is set by previous if, else statement.
            cv2.line(img, pos[0], pos[1], color, thickness)
            cv2.line(img, pos[1], pos[2], color, thickness)
            cv2.line(img, pos[2], pos[3], color, thickness)
            cv2.line(img, pos[3], pos[0], color, thickness)

        # This is a counter that shows how many open parking spots are available.
        cvzone.putTextRect(img, f'Free: {space_counter}/{len(position_list)}', (20, 30), scale=2, thickness=3,
                           offset=10, colorR=(0, 200, 0))

    while True:
        # Statement setting the video back to the beginning to create a loop for testing and experimenting.
        if capture.get(cv2.CAP_PROP_POS_FRAMES) == capture.get(cv2.CAP_PROP_FRAME_COUNT):
            capture.set(cv2.CAP_PROP_POS_FRAMES, 0)

        # Reading each frame of the video.
        success, img = capture.read()

        # Processing the frame into a blurry grayscale image.
        img_gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        img_blur = cv2.GaussianBlur(img_gray, (3, 3), 1)
        img_thresh = cv2.adaptiveThreshold(img_blur, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY_INV, 25, 16)

        # Processing the grayscale frame into a binary threshold image.
        img_median = cv2.medianBlur(img_thresh, 5)
        kernel = np.ones((3, 3), np.uint8)
        img_dilate = cv2.dilate(img_median, kernel, iterations=1)

        # Method to check each segment in the binary image for empty parking spots.
        check_parking_space(img_dilate)

        # All used to show all segments and full images.
        # for pos in position_list:
        cv2.imshow("image", img)
        # cv2.imshow('imgage_blur', img_blur)
        # cv2.imshow('imgage_thresh', img_median)
        key = cv2.waitKey(10)
        quitKey = ord("q")
        if key == quitKey:
            cv2.destroyWindow("image")
            break


click_count = 0

def configureLot():
    width, height = 45, 20
    coords = []

    try:
        with open(getParkingPositions(), 'rb') as file:
            position_list = pickle.load(file)
    except:
        position_list = []

    def position_click(events, x, y, flags, params):
        global click_count
        if events == cv2.EVENT_LBUTTONDOWN:
            coords.append((x, y))
            click_count += 1

            if click_count >= 4:
                position_list.append(deepcopy(coords))
                coords.clear()
                click_count = 0


        if events == cv2.EVENT_RBUTTONDOWN:
            position_list.pop()

        with open(getParkingPositions(), 'wb') as file:
            pickle.dump(position_list, file)


    while True:
        global click_count
        # cv2.rectangle(img,(20,65),(65,90),(255,0,255),2)
        img = cv2.imread(getConfigureFile())
        quitKey = ord("q")
        key = cv2.waitKey(1)
        #print(click_count)

        for pos in position_list:
            cv2.line(img, pos[0], pos[1], 2)
            cv2.line(img, pos[1], pos[2], 2)
            cv2.line(img, pos[2], pos[3], 2)
            cv2.line(img, pos[3], pos[0], 2)

        cv2.imshow("image", img)
        cv2.setMouseCallback("image", position_click)

        if key == quitKey:
            cv2.destroyWindow("image")
            break




# Creating the buttons, and assigning them the their correlated functions that were created up above.
configureButton = Button(homeWindow, text="Configure", fg="black", command=configureLot)
viewButton = Button(homeWindow, text="View", fg="black", command=viewLot)
chooseDirectoryButton = Button(homeWindow, text="Choose Directory First", fg="black", command=openFileDirectory)
chooseViewFileButton = Button(homeWindow, text="Choose video of parking lot ", fg="black", command=chooseViewFile)
chooseConfigureFileButton = Button(homeWindow, text="Choose image of empty parking lot", fg="black", command=chooseConfigureFile)
chooseParkingPositionsButton = Button(homeWindow, text="Choose parking positions' text file", fg="black", command=chooseParkingPositions)
instructionMapSpotLabelOne =  Label(homeWindow, text="To map a parking spot, left click the 4 corners of the spot ", fg="black")
instructionMapSpotLabelTwo= Label(homeWindow, text="starting from one side of the parking spot to the other.", fg="black")
instructionDeleteSpotLabel =  Label(homeWindow, text="To delete the spot that was last mapped, right click.", fg="black")
instructionCloseLabel = Label(homeWindow, text="To quit out of the configure and view window press 'Q'.", fg="black")
instructionPositionFile = Label(homeWindow, text="If you do not have a parking position file, create an empty text file.", fg="black")
# Packing the buttons onto the window with their respective column and row.
instructionMapSpotLabelOne.grid(row=1, column=1)
instructionMapSpotLabelTwo.grid(row=2, column=1)
instructionDeleteSpotLabel.grid(row=3, column=1)
instructionCloseLabel.grid(row=4, column=1)
instructionPositionFile.grid(row=5, column=1)
chooseDirectoryButton.grid(row=6, column=1)
chooseViewFileButton.grid(row=7, column=1)
chooseConfigureFileButton.grid(row=8, column=1)
chooseParkingPositionsButton.grid(row=9, column=1)
configureButton.grid(row=10, column=1)
viewButton.grid(row=11, column=1)
mainloop()