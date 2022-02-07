import cv2
import imutils
   
# Initializing the Histograms of Oriented Gradients person detector
hog = cv2.HOGDescriptor()
hog.setSVMDetector(cv2.HOGDescriptor_getDefaultPeopleDetector())
   
cap = cv2.VideoCapture("test_assets/test2.mp4")
   
while cap.isOpened():
    # Reading the video stream
    ret, image = cap.read()
    if ret:

        # resizing for better performance but it reduces frame rate
        #image = imutils.resize(image, width=min(400, image.shape[1]))
        # Detecting on grayscale image is faster.
        gray = cv2.cvtColor(image,cv2.COLOR_BGR2GRAY)
   
        # Detecting all the regions in the Image that has a human inside it
        (regions, _) = hog.detectMultiScale(gray, winStride=(4, 4), padding=(4, 4), scale=1.05)
   
        # Drawing the regions in the coloured image
        for (x, y, w, h) in regions:
            cv2.rectangle(image, (x, y), (x + w, y + h), (0, 0, 255), 1)
   
        # Showing the output Image
        cv2.imshow("Output", image)
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break
    else:
        break
  
cap.release()
cv2.destroyAllWindows()