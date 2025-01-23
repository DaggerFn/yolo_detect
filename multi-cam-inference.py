import cv2
from ultralytics import YOLO
from time import time, sleep
from threading import Lock, Thread
from numpy import zeros, uint8, ceil, hstack, vstack
import numpy as np
from flask import Flask, Response, jsonify
from flask_cors import CORS
from data_utils import infObjects, updateAPI, pass_class_api, objects_counter
from config import camera_urls, rois, roi_points_worker

app = Flask(__name__)
CORS(app)

# Inicializa os frames e frames anotados globais
global_frames = [None] * len(camera_urls)

#Frame para deteção e contagem de motor
annotated_frames = [None] * len(camera_urls)

#Trheding Incializador
frame_lock = Lock()

#Frame para corte da area de contagem
global_cropped_frames = [None] * len(camera_urls)

#Frame para area de Status de Operação 
frames_worker = [None] * len(camera_urls)

#Frame com Deteções da Area de status de Operação
annotated_frames_worker = [None] * len(camera_urls)

contador = {}
ultimo_tempo = {}
estado_anterior = {}


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
                crop_frames_by_rois()
                crop_frames_by_rois_worker()  
        else:
            cap.grab()


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


def crop_frames_by_rois_worker():
    """
    Realiza o corte nos frames armazenados em global_frames com base nas ROIs definidas.
    Atualiza a lista global_cropped_frames.
    """
    with frame_lock:
        for idx, frame in enumerate(global_frames):
            if frame is not None:
                roi_points = roi_points_worker[idx]['point']
                mask = zeros(frame.shape[:2], dtype=uint8)
                cv2.fillPoly(mask, [roi_points], 255)
                masked_frame = cv2.bitwise_and(frame, frame, mask=mask)
                x, y, w, h = cv2.boundingRect(roi_points)
                cropped_frame_worker = masked_frame[y:y+h, x:x+w]
                frames_worker[idx] = cropped_frame_worker
            else:
                frames_worker[idx] = None

"""
def draw_roi(camera_id ,frame, rois, detections):
    
    Desenha uma retangulo  no frame na posição especificada.
    
    roi_count = 0
    isClosed=True
    color=(0, 0, 255)
    thickness=4
    
    #Desenha a ROI no frame
    cv2.polylines(frame, [rois],isClosed , color, thickness)
    #print('roi desenhada na camera',camera_id)
    return frame
"""

"""
def objects_counter(camera_id, detected_classes, detections):
    global contador, estado_anterior

    # Inicializa o contador e o estado anterior para a câmera, se necessário
    if camera_id not in contador:
        contador[camera_id] = {'Quantidade': 0}
    if camera_id not in estado_anterior:
        estado_anterior[camera_id] = False  # Nenhuma detecção inicialmente

    # Verifica se há alguma classe "motor" nas classes detectadas
    tem_motor = any('motor' in cls.lower() for cls in detected_classes)

    # Determina o status atual de detecção (considera apenas classes "motor")
    tem_deteccao = len(detections) > 0 and tem_motor

    # Incrementa o contador apenas na transição de "sem detecção" para "com detecção"
    if tem_deteccao and not estado_anterior[camera_id]:
        contador[camera_id]['Quantidade'] += 1
        #print(f"Objeto 'motor' detectado na câmera {camera_id}. Quantidade: {contador[camera_id]['Quantidade']}")

    # Atualiza o estado anterior
    estado_anterior[camera_id] = tem_deteccao

    # Exibe o status atual
    if tem_deteccao:
        None
        #print(f"Objeto 'motor' detectado na câmera {camera_id}. Quantidade: {contador[camera_id]['Quantidade']}")
"""
        
def count_motor(id):
    global global_frames
    global annotated_frames
    global rois
    global contador    
    
    #pt model
    model = YOLO(r'/home/sim/code/models/modelo_linha/linha_11m.pt').to('cuda')
    
    #OpenVino model
    #model = YOLO('/home/sim/code/models/linha_11m_openvino_model/')#.to('cpu')
    
    
    while True:
        start = time()
        try:
            with frame_lock:
                frame = global_cropped_frames[id]
                #frame = global_frames[id]
            if frame is not None:
                annotated_frame = frame
                
                #OpenVino
                #results = model.predict(frame, augment=True, task="detect", visualize=False, verbose=False, conf=0.7, iou=0.5,imgsz=640)
                
                #GPU
                results = model.predict(frame, augment=True, visualize=False, verbose=False, conf=0.7, iou=0.1, imgsz=544)
                
                detected_classes = [model.names[int(cls)] for cls in results[0].boxes.cls]
                annotated_frame = results[0].plot(conf=True, labels=True, line_width=1)
                
                rois_camera = rois[id]['points']
                
                detections = results[0].boxes.xyxy.cpu().numpy().tolist()
                objects_counter(id ,detected_classes ,detections)
                
                #print(detected_classes)
                #print(objects_couter(id , detections))
                #detections = list(results[0].boxes.xyxy)
                #boxes = annotated_frame.boxes
                #converter_detes(boxes)
                #in_roi = detections_in_rois(id ,detections, detected_classes, rois)
                #print(in_roi)
                #annotated_frame = draw_roi(id ,annotated_frame, rois_camera, detections)
                #print(f"Câmera {id}: Classes detectadas -> {detected_classes}")
                
                infObjects(id)

                
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


def count_operation(id):
    global global_frames
    global frames_worker
    global annotated_frames_worker
    object_counter = set() 
    global rois
    dets = []
    
    #pt model
    #model = YOLO(r'/home/sim/code/models/modelo_linha/linha_11m.pt').to('cuda')
    
    #OpenVino model
    model = YOLO('/home/sim/code/models/linha_11m_openvino_model/')#.to('cpu')
    
    
    while True:
        start = time()
        try:
            with frame_lock:
                #frame = global_cropped_frames[id]
                frame = frames_worker[id]
            if frame is not None:
                annotated_frame = frame
                
                #OpenVino
                results = model.predict(frame, augment=True, task="detect", visualize=False, verbose=False, conf=0.7, iou=0.5,imgsz=640)
                
                #GPU
                #results = model.predict(frame, augment=True, visualize=False, verbose=False, conf=0.6, iou=0.1, imgsz=544)
                
                detected_classes = [model.names[int(cls)] for cls in results[0].boxes.cls]
                annotated_frame = results[0].plot(conf=True, labels=True, line_width=1)
                pass_class_api(detected_classes)
                rois_camera = rois[id]['points']
                detections = results[0].boxes.xyxy.cpu().numpy().tolist()                
                
                #print(detected_classes)
                #annotated_frame = draw_roi(id ,annotated_frame, rois_camera, detections)
                
                with frame_lock:
                    annotated_frames_worker[id] = annotated_frame
            else:
                with frame_lock:
                    annotated_frames_worker[id] = zeros((320, 480, 3), dtype=uint8)  # Adicione um frame vazio se não houver frame

        except Exception as e:
            print(e)
            pass
        inference_time = time() - start
        # print(f'{inference_time=}')


def generate_raw_camera(camera_id):
    encode_param = [int(cv2.IMWRITE_JPEG_QUALITY), 50]

    while True:
        sleep(0.05)
        with frame_lock:
            frame = global_frames[camera_id]
            if frame is not None:
                _, jpeg = cv2.imencode('.jpg', frame, encode_param)
                frame_bytes = jpeg.tobytes()
                yield (b'--frame\r\n'
                       b'Content-Type: image/jpeg\r\n\r\n' + frame_bytes + b'\r\n')
            else:
                yield (b'--frame\r\n'
                       b'Content-Type: text/plain\r\n\r\n' + b'Aguardando o frame...\r\n')


@app.route('/api')
def getAPI():
    info = updateAPI()
    return jsonify(info)

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

"""
"""
def generate_cropped_frames(camera_id):
    encode_param = [int(cv2.IMWRITE_JPEG_QUALITY), 50]

    while True:
        sleep(0.05)
        with frame_lock:
            frame = annotated_frames_worker[camera_id]
            if frame is not None:
                _, jpeg = cv2.imencode('.jpg', frame, encode_param)
                frame_bytes = jpeg.tobytes()
                yield (b'--frame\r\n'
                       b'Content-Type: image/jpeg\r\n\r\n' + frame_bytes + b'\r\n')
            else:
                yield (b'--frame\r\n'
                       b'Content-Type: text/plain\r\n\r\n' + b'Waiting for the cropped frame...\r\n')
        
                
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
"""

@app.route('/video_raw<camera_id>')
def video_raw_camera_feed(camera_id):
    try:
        camera_id = int(camera_id)
        if 0 <= camera_id < len(camera_urls):
            return Response(generate_raw_camera(camera_id), mimetype='multipart/x-mixed-replace; boundary=frame')
        else:
            return f"ID da câmera inválido: {camera_id}", 404
    except ValueError:
        return "O ID da câmera deve ser um inteiro.", 400


if __name__ == '__main__':
    # Inicializa threads de atualização de frames para cada câmera
    threads = []
    for idx, url in enumerate(camera_urls):
        thread = Thread(target=imageUpdater, kwargs={'id': idx, 'video_path': url, 'interval': 0.01})
        thread.start()
        threads.append(thread)
    
    # Inicializa threads de detecção para cada câmera
    for idx in range(len(camera_urls)):
        thread = Thread(target=count_motor, args=(idx,))
        thread.start()
        threads.append(thread)
    
    for idx in range(len(camera_urls)):
        thread = Thread(target=count_operation, args=(idx,))
        thread.start()
        threads.append(thread)
    

    # Inicializa o servidor Flask
    app.run(host='0.0.0.0', port=4000)
