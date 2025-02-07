from ultralytics import YOLO

# Load a YOLOv8n PyTorch model
model = YOLO("linha_11m.pt")

# Export the model
model.export(format="openvino", imgsz = (384, 384))  # creates 'yolov8n_openvino_model/'

# Load the exported OpenVINO model
#ov_model = YOLO("openvino_354_size/")

# Run inference
#results = ov_model("https://ultralytics.com/images/bus.jpg")
