import cv2 as cv
from glob import glob
import os
import random
from ultralytics import YOLO

# pick pre-trained model
model_pretrained = YOLO('./files/yolov8n.pt')

# read video by index
video_path = './files/Traffic Control CCTV.mp4'
video = cv.VideoCapture(video_path)

# get video dims
frame_width = int(video.get(3))
frame_height = int(video.get(4))
size = (frame_width, frame_height)

# Define the codec and create VideoWriter object
fourcc = cv.VideoWriter_fourcc(*'DIVX')
out = cv.VideoWriter('./files/output.avi', fourcc, 20.0, size)

# Frame skipping factor (adjust as needed for performance)
frame_skip = 3  # Skip every 3rd frame
frame_count = 0

# read frames
ret = True

while ret:
    ret, frame = video.read()

    if not ret:
        break  # Exit loop if there are no frames left

    # Skip frames
    if frame_count % frame_skip != 0:
        frame_count += 1
        continue  # Skip processing this frame
    
    # detect & track objects
    results = model_pretrained.track(frame, persist=True)

    # plot results
    composed = results[0].plot()

    # save video
    out.write(composed)

out.release()
video.release()