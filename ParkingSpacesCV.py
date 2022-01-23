from copyreg import pickle
import cv2
import pickle


width, height = 45, 20

try:
    with open('parking_positions', 'rb') as file:
            position_list = pickle.load(file)
except:
    position_list = []

def position_click(events, x, y, flags, params):
    if events == cv2.EVENT_LBUTTONDOWN:
        position_list.append((x,y))
    if events == cv2.EVENT_RBUTTONDOWN:
        for i, pos in enumerate(position_list):
            x1, y1 = pos
            if x1 < x < x1 + width and y1 < y < y1 + height:
                position_list.pop(i)

    with open('parking_positions', 'wb') as file:
        pickle.dump(position_list, file)


while True:
    # cv2.rectangle(img,(20,65),(65,90),(255,0,255),2)
    img = cv2.imread("resources/frame_2.png")

    for pos in position_list:
        cv2.rectangle(img, pos, (pos[0] + width, pos[1] + height), (255, 0, 255), 2)
    
    cv2.imshow("image", img)
    cv2.setMouseCallback("image", position_click)
    cv2.waitKey(1)