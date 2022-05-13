import fractions
import cv2
import numpy as np
from scipy.spatial import distance as dist

from GUI import Settings


settings = Settings()

class Processor():

    def __init__(self):

        # load the COCO class labels our YOLO model was trained on
        labelsPath = "Model/coco.names"
        LABELS = open(labelsPath).read().strip().split("\n")
        self.person_index = LABELS.index("person")
        # derive the paths to the YOLO weights and model configuration
        weightsPath = "Model/yolov3.weights"
        configPath = "Model/yolov3.cfg"

        self.net = cv2.dnn.readNetFromDarknet(configPath, weightsPath)
        # check if we are going to use GPU
        if settings.use_gpu:
            # set CUDA as the preferable backend and target
            self.net.setPreferableBackend(cv2.dnn.DNN_BACKEND_CUDA)
            self.net.setPreferableTarget(cv2.dnn.DNN_TARGET_CUDA)

        self.ln = self.net.getLayerNames()
        self.ln = [self.ln[i - 1] for i in self.net.getUnconnectedOutLayers()]


    def detect_people(self, frame):
        (H, W) = frame.shape[:2]
        
        results = []
        # construct a blob from the input frame
        blob = cv2.dnn.blobFromImage(frame, 1 / 255.0, (416, 416), swapRB=True, crop=False)

        # perform a forward pass of the YOLO object detector
        self.net.setInput(blob)
        layerOutputs = self.net.forward(self.ln)
        # initialize our lists of detected bounding boxes, centroids, and
        # confidences, respectively
        boxes = []
        centroids = []
        confidences = []

        for output in layerOutputs:
            for detection in output:

                scores = detection[5:]
                classID = np.argmax(scores)
                confidence = scores[classID]
                if classID == self.person_index and confidence > settings.min_confidence:

                    box = detection[0:4] * np.array([W, H, W, H])
                    (centerX, centerY, width, height) = box.astype("int")
                    x = int(centerX - (width / 2))
                    y = int(centerY - (height / 2))
                    boxes.append([x, y, int(width), int(height)])
                    centroids.append((centerX, centerY))
                    confidences.append(float(confidence))

        # applying non-maxima suppression to suppress weak, overlapping bounding boxes
        idxs = cv2.dnn.NMSBoxes(boxes, confidences, settings.min_confidence, settings.nms_treshold)
        # ensure at least one detection exists
        if len(idxs) > 0:
            # loop over the indexes we are keeping
            for i in idxs.flatten():
                # extract the bounding box coordinates
                (x, y) = (boxes[i][0], boxes[i][1])
                (w, h) = (boxes[i][2], boxes[i][3])
                r = (confidences[i], (x, y, x + w, y + h), centroids[i], (centroids[i][0], y+h))
                results.append(r)
        return results
