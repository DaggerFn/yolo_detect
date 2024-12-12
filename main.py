import cv2
from ultralytics import YOLO
from time import time, sleep
from threading import Lock, Thread
from numpy import zeros, uint8, ceil, hstack, vstack
from flask import Flask, Response, jsonify
import numpy as np
from data_utils import infObjects, updateAPI
# Define a lista de URLs das câmeras
camera_urls = [
    "rtsp://admin:fabrica1@192.168.0.131:554/1/1",  # Indice 0
    "rtsp://admin:fabrica1@192.168.0.132:554/1/1",  # Indice 1
    "rtsp://admin:fabrica1@192.168.0.133:554/1/1",  # Indice 2
    "rtsp://admin:fabrica1@192.168.0.134:554/1/1",  # Indice 3
    "rtsp://admin:fabrica1@192.168.0.135:554/1/1",  # Indice 4
    "rtsp://admin:fabrica1@192.168.0.136:554/1/1",  # Indice 5
]


rois = [
    {'points': np.array([[155, 155], [300, 155], [315, 275], [155, 275]], dtype=np.int32), 'color': (255, 0, 0)},
    {'points': np.array([[30, 160], [130, 160], [130, 270], [30, 270]], dtype=np.int32), 'color': (0, 255, 0)},
    {'points': np.array([[105, 175], [305, 175], [305, 270], [105, 285]], dtype=np.int32), 'color': (255, 0, 0)},
    {'points': np.array([[75, 230], [210, 230], [220, 300], [75, 310]], dtype=np.int32), 'color': (0, 255, 0)},
    {'points': np.array([[235, 195], [420, 100], [465, 210], [320, 320]], dtype=np.int32), 'color': (255, 0, 0)},
    {'points': np.array([[165, 227], [330, 140], [370, 210], [180, 320]], dtype=np.int32), 'color': (0, 255, 0)},
]

app = Flask(__name__)

# Inicializa os frames e frames anotados globais
global_frames = [None] * len(camera_urls)
global_frames2 = [None] * len(camera_urls)
annotated_frames = [None] * len(camera_urls)
frame_lock = Lock()
detected_classes = [None] * len(camera_urls)


# Inicializa os frames cortados para ROI
global_cropped_frames = [None] * len(camera_urls)

def crop_frames_by_rois():
    """
    Realiza o corte nos frames armazenados em global_frames com base nas ROIs definidas.
    Atualiza a lista global_cropped_frames.
    """
    with frame_lock:
        for idx, frame in enumerate(global_frames):
            if frame is not None:
                roi_points = rois[idx]['points']
                mask = zeros(frame.shape[:2], dtype=uint8)
                cv2.fillPoly(mask, [roi_points], 255)
                masked_frame = cv2.bitwise_and(frame, frame, mask=mask)
                x, y, w, h = cv2.boundingRect(roi_points)
                cropped_frame = masked_frame[y:y+h, x:x+w]
                global_cropped_frames[idx] = cropped_frame
            else:
                global_cropped_frames[idx] = None

def imageUpdater(id, video_path, interval):
    global global_frames
    cap = cv2.VideoCapture(video_path)
    last_time = 0
    while True:
        current_time = time()
        if current_time - last_time >= interval:
            last_time = current_time
            success, frame = cap.read()
            if success:
                frame = cv2.resize(frame, (480, 320))  # Redimensiona o frame
                with frame_lock:
                    global_frames[id] = frame
                crop_frames_by_rois()  # Atualiza os frames cortados após cada frame novo
        else:
            cap.grab()

def detection_loop(id):
    global global_frames
    global annotated_frames
    global global_cropped_frames
    global detected_classes

    model = YOLO(r'/home/sim/code/models/gutavo_augmentations.pt') .to('cuda')
    processed_frame_id = None

    while True:
        start = time()
        try:
            with frame_lock:
                frame = global_cropped_frames[id]
                original_frame = global_frames[id]

            # Evita processar o mesmo frame novamente
            if frame is not None and original_frame is not processed_frame_id:
                annotated_frame = frame.copy()
                results = model.predict(frame, classes=[0], visualize=False, verbose=False, conf=0.3, imgsz=320)
                annotated_frame = results[0].plot(conf=False, labels=False, line_width=2)
                detected_classes = [model.names[int(cls)] for cls in results[0].boxes.cls]
                #print(detected_classes)
                #print(f"Câmera {id}: Classes detectadas -> {detected_classes}")
                infObjects(id, detected_classes)
                

                
                # Atualiza os frames anotados
                with frame_lock:
                    annotated_frames[id] = annotated_frame

                # Desenha no frame original
                draw_detections_on_original_frames(id, results[0].boxes.xyxy, rois[id]['points'])

                # Marca o frame como processado
                processed_frame_id = id
            else:
                with frame_lock:
                    annotated_frames[id] = zeros((320, 480, 3), dtype=uint8)  # Adicione um frame vazio se não houver frame

        except Exception as e:
            print(e)
            pass
        inference_time = time() - start


def get_classes():
    global detected_classes
    
    if detected_classes is not None:
        return detected_classes[camera_urls]


def draw_detections_on_original_frames(camera_id, detections, roi_points):
    """
    Desenha as detecções do YOLO e a ROI no frame original.
    :param camera_id: ID da câmera.
    :param detections: Caixas delimitadoras das detecções.
    :param roi_points: Pontos da ROI para desenhar.
    """
    with frame_lock:
        frame = global_frames[camera_id]
        if frame is not None:
            # Desenha a ROI
            cv2.polylines(frame, [roi_points], isClosed=True, color=(0, 255, 0), thickness=2)

            # Calcula o deslocamento da ROI
            x_offset, y_offset, _, _ = cv2.boundingRect(roi_points)

            # Desenha as detecções mapeadas para o frame original
            for box in detections:
                x1, y1, x2, y2 = map(int, box)
                x1 += x_offset
                y1 += y_offset
                x2 += x_offset
                y2 += y_offset
                cv2.rectangle(frame, (x1, y1), (x2, y2), color=(0, 0, 255), thickness=2)
            
            global_frames2[camera_id] = frame

def generate_camera(camera_id):
    encode_param = [int(cv2.IMWRITE_JPEG_QUALITY), 50]

    while True:
        sleep(0.05)
        with frame_lock:
            frame = global_frames2[camera_id]
            if frame is not None:
                _, jpeg = cv2.imencode('.jpg', frame, encode_param)
                frame_bytes = jpeg.tobytes()
                yield (b'--frame\r\n'
                       b'Content-Type: image/jpeg\r\n\r\n' + frame_bytes + b'\r\n')
            else:
                yield (b'--frame\r\n'
                       b'Content-Type: text/plain\r\n\r\n' + b'Waiting for the frame...\r\n')

def generate_cropped_frames(camera_id):
    encode_param = [int(cv2.IMWRITE_JPEG_QUALITY), 50]

    while True:
        sleep(0.05)
        with frame_lock:
            frame = global_cropped_frames[camera_id]
            if frame is not None:
                _, jpeg = cv2.imencode('.jpg', frame, encode_param)
                frame_bytes = jpeg.tobytes()
                yield (b'--frame\r\n'
                       b'Content-Type: image/jpeg\r\n\r\n' + frame_bytes + b'\r\n')
            else:
                yield (b'--frame\r\n'
                       b'Content-Type: text/plain\r\n\r\n' + b'Waiting for the cropped frame...\r\n')

@app.route('/video<camera_id>')
def video_camera_feed(camera_id):
    try:
        camera_id = int(camera_id)
        if 0 <= camera_id < len(camera_urls):
            return Response(generate_camera(camera_id), mimetype='multipart/x-mixed-replace; boundary=frame')
        else:
            return f"Invalid camera ID: {camera_id}", 404
    except ValueError:
        return "Camera ID must be an integer.", 400

@app.route('/cropped_frames<camera_id>')
def cropped_frames_feed(camera_id):
    try:
        camera_id = int(camera_id)
        if 0 <= camera_id < len(camera_urls):
            return Response(generate_cropped_frames(camera_id), mimetype='multipart/x-mixed-replace; boundary=frame')
        else:
            return f"Invalid camera ID: {camera_id}", 404
    except ValueError:
        return "Camera ID must be an integer.", 400

@app.route('/api')
def getAPI():
    info = updateAPI()
    return jsonify(info)

if __name__ == '__main__':
    threads = []
    for idx, url in enumerate(camera_urls):
        thread = Thread(target=imageUpdater, kwargs={'id': idx, 'video_path': url, 'interval': 0.01})
        thread.start()
        threads.append(thread)

    for idx in range(len(camera_urls)):
        thread = Thread(target=detection_loop, args=(idx,))
        thread.start()
        threads.append(thread)

    app.run(host='0.0.0.0', port=4000)