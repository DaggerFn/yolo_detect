import cv2
import numpy as np
import time
from ultralytics import YOLO
from threading import Lock

# Configurações
ROI_POINTS = np.array([[625, 220], [880, 200], [890, 450], [685, 460]], dtype=np.int32)
ROI_COLOR = (0, 0, 255)  # Cor da borda da ROI
OBJECT_TIMEOUT = 2  # Tempo de timeout para objetos em segundos

'''
 [100, 100]
   ->   |
'''
'''
Coordenadas atuais:
Ponto Vermelho (superior esquerdo): [0, 0]
Ponto Verde (superior direito): [140, 0]
Ponto Azul (inferior direito): [80, 720]
Ponto Amarelo (inferior esquerdo): [0, 720]
'''

# Inicializar variáveis globais 
object_times = {}
last_detection_time = time.time()
no_detection_time = 0
roi_object_count = 0  # Adicionar uma variável para contar objetos na ROI
lock = Lock()

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
           # Adiciona a caixa à lista de detecções
           dets.append(box)

           # Desenhar as bounding boxes no frame original
           x1, y1, x2, y2 = map(int, box)  # Convertendo as coordenadas para inteiros
           cv2.rectangle(frame, (x1, y1), (x2, y2), (0, 255, 0), 2)  # Desenhar a caixa em verde

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
    """Rastrear objetos e contabilizar o tempo em e fora da ROI."""
    global object_times, last_detection_time, no_detection_time, roi_object_count

    current_time = time.time()
    frame, detections = process_frame(frame, model)

    detected_objects = []
    roi_count = 0  # Contador de objetos na ROI

    with lock:
        for detection in detections:
            try:
                if len(detection) == 4:
                    xmin, ymin, xmax, ymax = detection
                    confidence = 0.0
                    class_id = -1
                else:
                    xmin, ymin, xmax, ymax, confidence, class_id = detection[:6]

                if is_object_in_roi([xmin, ymin, xmax, ymax], ROI_POINTS):
                    obj_id = f"{xmin}_{ymin}_{xmax}_{ymax}"  # Gerar um ID único para o objeto
                    detected_objects.append(obj_id)
                    roi_count += 1  # Incrementar o contador de objetos na ROI

            except Exception as e:
                print(f"Erro ao processar detecção: {e}")

        if detected_objects:
            for obj_id in detected_objects:
                if obj_id not in object_times:
                    object_times[obj_id] = {'entry_time': current_time, 'total_time': 0}
                else:
                    object_times[obj_id]['total_time'] += current_time - object_times[obj_id]['entry_time']
                    object_times[obj_id]['entry_time'] = current_time
            no_detection_time = 0
        else:
            for obj_id in object_times.keys():
                object_times[obj_id]['total_time'] += current_time - object_times[obj_id]['entry_time']
                object_times[obj_id]['entry_time'] = current_time
            no_detection_time += current_time - last_detection_time

        last_detection_time = current_time
        roi_object_count = roi_count  # Atualizar a contagem de objetos na ROI

    return {
        'object_times': object_times,
        'no_detection_time': no_detection_time,
        'roi_object_count': roi_object_count  # Retornar a contagem de objetos na ROI
    }

def generate_frames(model, camera_url):
    """Gerar frames para transmissão via HTTP e contabilizar o tempo de objetos na ROI."""
    cap = cv2.VideoCapture(camera_url)
    if not cap.isOpened():
        raise Exception("Não foi possível abrir a câmera.")

    while True:
        success, frame = cap.read()
        if not success:
            break

        # Contabilizar o tempo de objetos e tempo sem detecção
        track_objects(frame, model)

        # Codificar o frame como JPEG
        _, buffer = cv2.imencode('.jpg', frame)
        frame_bytes = buffer.tobytes()
        
        # Enviar o frame codificado como resposta HTTP
        yield (b'--frame\r\n'
               b'Content-Type: image/jpeg\r\n\r\n' + frame_bytes + b'\r\n')

def get_tracking_info():
    """Retornar as informações de rastreamento para geração de JSON."""
    try:
        with lock:
            return {
                'object_times': {k: v for k, v in object_times.items()},
                'no_detection_time': no_detection_time,
                'roi_object_count': roi_object_count  # Adicionar contagem de objetos na ROI
            }
    except Exception as e:
        print(f"Erro ao obter informações de rastreamento: {e}")
        return {
            'object_times': {},
            'no_detection_time': 0,
            'roi_object_count': 0  # Retornar 0 se houver erro
        }




__________________________________________________________________________________________________________
def get_tracking_info():
   """Retornar as informações de rastreamento para geração de JSON."""
   global qtdMotrs, previous_value, roi_object_count  # Certifique-se de que essas variáveis são globais

   try:
       with lock:
           # Verifica se o valor mudou de 0 para 1
           if roi_object_count == 1 and previous_value == 0:
               qtdMotrs += 1  # Incrementa apenas uma vez

           # Atualiza o valor anterior
           previous_value = roi_object_count
           
           now = datetime.now()
           dt_string = now.strftime("%d/%m/%Y %H:%M:%S")
              
           # Retorna as informações de rastreamento
           posto1 = {
               'QtdMotor': qtdMotrs,
               'hora' : dt_string,
               'no_detection_time': no_detection_time,
               'roi_object_count': roi_object_count
           }
           return posto1

   except Exception as e:
       print(f"Erro ao obter informações de rastreamento: {e}")
       return {
           'object_times': {},
           'no_detection_time': 0,
           'roi_object_count': 0  # Retornar 0 se houver erro
       }