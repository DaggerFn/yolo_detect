import cv2
from ultralytics import YOLO
from time import time, sleep
from threading import Lock, Thread
from numpy import zeros, uint8, ceil, hstack, vstack
from flask import Flask, Response
 
# Define a lista de URLs das câmeras
camera_urls = [
    "rtsp://admin:fabrica1@192.168.0.131:554/1/1",  # Indice 0
    #"rtsp://admin:fabrica1@192.168.0.132:554/1/1",  # Indice 1
    "rtsp://admin:fabrica1@192.168.0.133:554/1/1",  # Indice 2
    "rtsp://admin:fabrica1@192.168.0.134:554/1/1",  # Indice 3
    "rtsp://admin:fabrica1@192.168.0.135:554/1/1",  # Indice 4
    "rtsp://admin:fabrica1@192.168.0.136:554/1/1",  # Indice 5
]
 
app = Flask(__name__)
 
# Inicializa os frames e frames anotados globais
global_frames = [None] * len(camera_urls)
annotated_frames = [None] * len(camera_urls)
frame_lock = Lock()
 
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
        else:
            cap.grab()
 
def detection_loop(id):
    global global_frames
    global annotated_frames
   
    #onnx model
    #model = YOLO(r'/home/sim/code/models/linha_11m.onnx')
   
    #pt model
    #model = YOLO(r'/home/sim/code/models/modelo_linha/linha_11m.pt').to('cuda')
   
    #OpenVino model
    model = YOLO('/home/sim/code/models/linha_11m_openvino_model/')#.to('cpu')
   
   
    while True:
        start = time()
        try:
            with frame_lock:
                frame = global_frames[id]
            if frame is not None:
                annotated_frame = frame
               
                #OpenVino
                results = model.predict(frame, augment=True, task="detect", visualize=False, verbose=False, conf=0.5, iou=0.5,imgsz=640)
               
                #GPU
                #results = model.predict(frame, augment=True, visualize=False, verbose=False, conf=0.6, iou=0.1, imgsz=544)
               
                detected_classes = [model.names[int(cls)] for cls in results[0].boxes.cls]
                annotated_frame = results[0].plot(conf=True, labels=True, line_width=3)
               
                print(f"Câmera {id}: Classes detectadas -> {detected_classes}")
               
               
               
                with frame_lock:
                    annotated_frames[id] = annotated_frame
            else:
                with frame_lock:
                    annotated_frames[id] = zeros((320, 480, 3), dtype=uint8)  # Adicione um frame vazio se não houver frame
 
        except Exception as e:
            print(e)
            pass
        inference_time = time() - start
        # print(f'{inference_time=}')
"""
def draw_detections_on_original_frames(camera_id, detections, classes):
    with frame_lock:
        frame = global_frames[camera_id]
        if frame is not None:
            # Desenha a ROI
            cv2.polylines(frame, [rois], isClosed=True, color=(0, 255, 0), thickness=2)
 
            # Calcula o deslocamento da ROI
            x_offset, y_offset, _, _ = cv2.boundingRect(rois)
 
            # Desenha as detecções mapeadas para o frame original
            for box, cls in zip(detections, classes):
                x1, y1, x2, y2 = map(int, box)
                x1 += x_offset
                y1 += y_offset
                x2 += x_offset
                y2 += y_offset
               
                #print(f"Classe detectada: {cls}")
               
                # Escolhe a cor com base na classe detectada
                color = CLASS_COLORS.get(cls, (255, 255, 255))  # Branco como padrão se a classe não estiver no dicionário
 
                # Desenha o retângulo com a cor da classe
                cv2.rectangle(frame, (x1, y1), (x2, y2), color=color, thickness=2)
 
                # Adiciona o nome da classe no retângulo
                cv2.putText(frame, cls, (x1, y1 - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, color, 1)
 
            global_frames[camera_id] = frame
"""
 
"""
def generate():
    global global_frames
    encode_param = [int(cv2.IMWRITE_JPEG_QUALITY), 50]
    fourcc = cv2.VideoWriter_fourcc(*'H264')
    out = cv2.VideoWriter('appsrc ! videoconvert ! x264enc tune=zerolatency bitrate=500 speed-preset=ultrafast ! rtph264pay ! udpsink host=127.0.0.1 port=5000', fourcc, 10, (880, 440))
 
    while True:
        sleep(0.05)
        with frame_lock:
            if global_frames:
                # Montar o grid
                grid_size = int(ceil(len(global_frames) ** 0.5))
                grid_frames = []
                for i in range(0, len(global_frames), grid_size):
                    row_frames = global_frames[i:i + grid_size]
                    while len(row_frames) < grid_size:
                        row_frames.append(zeros((480, 640, 3), dtype=uint8))
                    grid_frames.append(hstack(row_frames))
               
                grid_image = vstack(grid_frames)
               
                resized_frame = cv2.resize(grid_image, (880, 440))  # Reduzir a resolução
                out.write(resized_frame)
                _, jpeg = cv2.imencode('.jpg', resized_frame, encode_param)
                frame_bytes = jpeg.tobytes()
                yield (b'--frame\r\n'
                       b'Content-Type: image/jpeg\r\n\r\n' + frame_bytes + b'\r\n')
            else:
                yield (b'--frame\r\n'
                       b'Content-Type: text/plain\r\n\r\n' + b'Waiting for the frame...\r\n')
 
    out.release()
 
"""
def generate_camera(camera_id):
    encode_param = [int(cv2.IMWRITE_JPEG_QUALITY), 50]
 
    while True:
        sleep(0.05)
        with frame_lock:
            frame = annotated_frames[camera_id]
            if frame is not None:
                _, jpeg = cv2.imencode('.jpg', frame, encode_param)
                frame_bytes = jpeg.tobytes()
                yield (b'--frame\r\n'
                       b'Content-Type: image/jpeg\r\n\r\n' + frame_bytes + b'\r\n')
            else:
                yield (b'--frame\r\n'
                       b'Content-Type: text/plain\r\n\r\n' + b'Waiting for the frame...\r\n')
 
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
 
if __name__ == '__main__':
    # Inicializa threads de atualização de frames para cada câmera
    threads = []
    for idx, url in enumerate(camera_urls):
        thread = Thread(target=imageUpdater, kwargs={'id': idx, 'video_path': url, 'interval': 0.01})
        thread.start()
        threads.append(thread)
   
    # Inicializa threads de detecção para cada câmera
    for idx in range(len(camera_urls)):
        thread = Thread(target=detection_loop, args=(idx,))
        thread.start()
        threads.append(thread)
 
    # Inicializa o servidor Flask
    app.run(host='0.0.0.0', port=4000)