import numpy as np
import cv2
from threading import Lock

frame1 = None
frame2 = None
frame3 = None
frame4 = None
frame5 = None
frame6 = None
globalFrame = None

 
def imageUpdater(ipLinks, interval):
    global frame1, frame2, frame3, frame4, frame5, frame6
    
    

#E possivel passar para variavel um conjunto de frames visto que receberei 6 frames ?
 
def concatFrame():
    frame1, frame2, frame3, frame4, frame5, frame6
    
    
    

    return globalFrame



def detect_objects_in_roi(globalFrame, rois, model):
    roi_detections = []  # Lista de detecções em todas as ROIs

    for roi in rois:
        # Criar uma máscara para a ROI atual
        mask = np.zeros(globalFrame.shape[:2], dtype=np.uint8)
        cv2.fillPoly(mask, [roi['points']], 255)
        
        # Aplicar a máscara no frame global para extrair a ROI
        roi_frame = cv2.bitwise_and(globalFrame, globalFrame, mask=mask)
        
        # Recortar a ROI da imagem original
        x_min, y_min = np.min(roi['points'], axis=0)
        x_max, y_max = np.max(roi['points'], axis=0)
        roi_cropped = roi_frame[y_min:y_max, x_min:x_max]
        
        # Aplicar o YOLO na ROI recortada
        results = model(roi_cropped)
        detections = results.pandas().xyxy[0]
        
        # Armazenar as detecções e coordenadas de cada ROI
        roi_detections.append({'id': roi['id'], 'x_min': x_min, 'y_min': y_min, 'detections': detections})
    
    return roi_detections

def process_detections_in_rois(roi_detections):
    detections_by_roi = {}

    for roi_data in roi_detections:
        roi_id = roi_data['id']
        x_min = roi_data['x_min']
        y_min = roi_data['y_min']
        detections = roi_data['detections']

        detections_by_roi[roi_id] = []  # Lista de detecções para a ROI específica

        for _, detection in detections.iterrows():
            x1 = int(detection['xmin']) + x_min
            y1 = int(detection['ymin']) + y_min
            x2 = int(detection['xmax']) + x_min
            y2 = int(detection['ymax']) + y_min

            detections_by_roi[roi_id].append({
                'class': detection['name'],
                'confidence': detection['confidence'],
                'bbox': (x1, y1, x2, y2)
            })
    
    return detections_by_roi

def detect_objects_in_roi(roi_frame):
    # Detecção YOLO padrão, mas aplicando apenas ao `roi_frame`
    results = model(roi_frame)  # `model` é seu modelo YOLO
    # Processar e retornar detecções filtradas ou destacadas para cada ROI
    return results

def get_detected_classes(results):
    """
    Retorna as classes (labels) dos objetos detectados no frame.
    """
    detected_classes = []
    
    # Iterar sobre as detecções para obter as classes
    for result in results:
        if result.boxes is not None:  # Verifica se há detecções
            for box in result.boxes:
                class_id = int(box.cls)  # Obtém o índice da classe
                detected_classes.append(class_id)  # Adiciona o índice à lista

    return detected_classes
