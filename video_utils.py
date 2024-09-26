import cv2
import numpy as np
import time
from ultralytics import YOLO
from threading import Lock

# Configurações
ROI_POINTS = np.array([[65, 620], [210, 620], [210, 720], [45, 720]], dtype=np.int32)
ROI_COLOR = (0, 0, 255)  # Cor da borda da ROI
lock = Lock()

motorSensor = 0  

def load_yolo_model(model_path):
    """Carregar o modelo YOLO a partir do caminho especificado."""
    return YOLO(model_path)

def process_frame(frame, model):
    """Processar o frame com a ROI e YOLO."""
    # Criar uma máscara para a ROI
    mask = np.zeros_like(frame)
    cv2.fillConvexPoly(mask, ROI_POINTS, (255, 255, 255))
    roi_frame = cv2.bitwise_and(frame, mask)

    # Processar o frame com YOLO
    results = model(roi_frame)

    # Se for uma lista, acesse o primeiro item
    if isinstance(results, list):
        results = results[0]

    # Obter as detecções (bounding boxes)
    boxes = results.boxes  # Isso retorna as caixas delimitadoras

    # Desenhar a ROI no frame original
    cv2.polylines(frame, [ROI_POINTS], isClosed=True, color=ROI_COLOR, thickness=2)

    # Converter as caixas para um formato utilizável
    dets = []
    if boxes is not None:
        for box in boxes.xyxy.cpu().numpy():
            dets.append(box)

            # Desenhar as bounding boxes no frame original
            x1, y1, x2, y2 = map(int, box)
            cv2.rectangle(frame, (x1, y1), (x2, y2), (0, 255, 0), 2)

    return frame, dets

def is_object_in_roi(object_bbox, roi_points):
    """Verifica se um objeto está dentro da ROI."""
    x1, y1, x2, y2 = object_bbox
    bbox_points = np.array([[x1, y1], [x2, y1], [x2, y2], [x1, y2]])
    roi_polygon = cv2.convexHull(roi_points)
    for point in bbox_points:
        if cv2.pointPolygonTest(roi_polygon, tuple(point), False) >= 0:
            return True
    return False

def track_objects(frame, model):
    #Rastrear objetos e verificar se há um objeto na ROI.
    global  motorSensor #Atualiza a variavel para escopo global
    
    # Processa o frame para obter as detecções
    frame, detections = process_frame(frame, model)

    # Inicializa o motorSensor como 0 (nenhum objeto)

    for detection in detections:
        try:
            if len(detection) >= 4:  # Verifica se a detecção contém pelo menos 4 valores
                xmin, ymin, xmax, ymax = detection[:4]

                # Verifica se o objeto está na ROI
                if is_object_in_roi([xmin, ymin, xmax, ymax], ROI_POINTS):
                    motorSensor = 1  # Define motorSensor como 1 se houver pelo menos um objeto
                    break  # Sai do loop já que encontramos um objeto na ROI
                else:#Se nao tiver objeto na roi altera para zero 
                    motorSensor -= 1
                    break
            else:#Se nao tiver objeto na roi altera para zero 
                motorSensor -= 1
                break
        except Exception as e:
            print(f"Erro ao processar detecção: {e}")


def get_motor_sensor_value():
    """Função para obter o valor do motorSensor chamando track_objects."""
    
    global motorSensor
    
    return  motorSensor

def generate_frames(model, camera_url):
    """Gerar frames para transmissão via HTTP e contabilizar o tempo de objetos na ROI."""
    cap = cv2.VideoCapture(camera_url)
    if not cap.isOpened():
        raise Exception("Não foi possível abrir a câmera.")

    while True:
        success, frame = cap.read()
        if not success:
            break

        track_objects(frame, model)

        _, buffer = cv2.imencode('.jpg', frame)
        frame_bytes = buffer.tobytes()

        yield (b'--frame\r\n'
               b'Content-Type: image/jpeg\r\n\r\n' + frame_bytes + b'\r\n')
