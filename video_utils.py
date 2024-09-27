import cv2
import numpy as np
import time
from ultralytics import YOLO
from threading import Lock, Thread

# Configurações
ROI_POINTS = np.array([[65, 640], [250, 640], [250, 720], [45, 720]], dtype=np.int32)
ROI_COLOR = (0, 0, 255)  # Cor da borda da ROI
lock = Lock()

motorSensor = 0  # Variável global

def load_yolo_model(model_path):
    """Carregar o modelo YOLO a partir do caminho especificado."""
    return YOLO(model_path, task='detect')

def process_frame(frame, model):
    """Processar o frame com a ROI e YOLO."""
    # Criar uma máscara para a ROI
    mask = np.zeros_like(frame)
    cv2.fillConvexPoly(mask, ROI_POINTS, (255, 255, 255))
    roi_frame = cv2.bitwise_and(frame, mask)

    # Processar o frame com YOLO
    results = model(roi_frame)

    if isinstance(results, list):
        results = results[0]

    boxes = results.boxes

    cv2.polylines(frame, [ROI_POINTS], isClosed=True, color=ROI_COLOR, thickness=2)

    dets = []
    if boxes is not None:
        for box in boxes.xyxy.cpu().numpy():
            dets.append(box)

            x1, y1, x2, y2 = map(int, box)
            cv2.rectangle(frame, (x1, y1), (x2, y2), (0, 255, 0), 2)

    return frame, dets

def is_object_in_roi(object_bbox, roi_points):
    """Verifica se um objeto está dentro da ROI."""
    x1, y1, x2, y2 = map(int, object_bbox)  # Converte coordenadas da bounding box para inteiros
    bbox_points = np.array([[x1, y1], [x2, y1], [x2, y2], [x1, y2]])
    roi_polygon = cv2.convexHull(roi_points)
    for point in bbox_points:
        if cv2.pointPolygonTest(roi_polygon, (int(point[0]), int(point[1])), False) >= 0:
            return True
    return False


def track_objects(frame, model):
    global motorSensor
    frame, detections = process_frame(frame, model)

    motorSensor = 0  # Inicializar como 0 (nenhum objeto)
    
    for detection in detections:
        if len(detection) >= 4:
            xmin, ymin, xmax, ymax = map(int, detection[:4])

            # Desenhar as bounding boxes no frame original
            cv2.rectangle(frame, (xmin, ymin), (xmax, ymax), (0, 255, 0), 2)

            # Verifica se o objeto está na ROI
            if is_object_in_roi([xmin, ymin, xmax, ymax], ROI_POINTS):
                motorSensor = 1  # Atualizar se houver objeto na ROI
                break



def get_motor_sensor_value():
    global motorSensor
    with lock:  # Bloquear ao acessar a variável global
        return motorSensor


def generate_frames(model, camera_url):
    """Gerar frames para transmissão via HTTP e contabilizar o tempo de objetos na ROI."""
    cap = cv2.VideoCapture(camera_url)
    if not cap.isOpened():
        raise Exception("Não foi possível abrir a câmera.")

    while True:
        success, frame = cap.read()
        if not success:
            break

        # Processar frame e detectar objetos
        track_objects(frame, model)

        # Codificar o frame para transmissão
        _, buffer = cv2.imencode('.jpg', frame)
        frame_bytes = buffer.tobytes()

        yield (b'--frame\r\n'
               b'Content-Type: image/jpeg\r\n\r\n' + frame_bytes + b'\r\n')


""" 
                            Função sem o uso de uma ROI

def generate_frames(model, camera_url):
    cap = cv2.VideoCapture(camera_url)
    if not cap.isOpened():
        raise Exception("Não foi possível abrir a câmera.")

    while True:
        success, frame = cap.read()
        if not success:
            break

        # Rodar a detecção de objetos em uma thread separada
        detection_thread = Thread(target=track_objects, args=(frame, model))
        detection_thread.start()

        # Codificar o frame para transmissão
        _, buffer = cv2.imencode('.jpg', frame)
        frame_bytes = buffer.tobytes()

        yield (b'--frame\r\n'
               b'Content-Type: image/jpeg\r\n\r\n' + frame_bytes + b'\r\n')

"""