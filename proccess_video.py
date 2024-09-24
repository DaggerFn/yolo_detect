import cv2
import numpy as np
import time
from ultralytics import YOLO
from threading import Lock
from datetime import datetime


# Configurações                     -           +
# Zona para camera apontada para posto 1
#ROI_POINTS = np.array([[960, 220], [1120, 210], [1143, 360], [995, 380]], dtype=np.int32)

# Zona para camera apontada para posto 2
#ROI_POINTS = np.array([[0, 0], [1280, 0], [1280, 720], [0, 720]], dtype=np.int32)
#ROI_POINTS = np.array([[260, 220], [200, 210], [200, 360], [200, 380]], dtype=np.int32)
ROI_POINTS = np.array([[65, 590], [210, 590], [210, 720], [45, 720]], dtype=np.int32)

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

# Variáveis globais
last_detection_time = time.time()
no_detection_time = 0
roi_object_count = 0
lock = Lock()

# URL da API onde o JSON é fornecido
url = "http://10.1.30.105:5000/tracking_info"  # Substitua pelo URL correto
 

"""
________________________________________________________________________________________________________
Processamento de Video
________________________________________________________________________________________________________
"""

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

    
"""
________________________________________________________________________________________________________
Geração de Dados
________________________________________________________________________________________________________
"""

qtdMotrs = 0  # Inicializa a quantidade de motores
previous_value = 0  # Valor anterior de roi_object_count
no_detection_time = 0  # Inicializa o tempo sem detecções
last_update_time = None
last_update_date = None
time_for_save = None
tempo_decorrido = "00:00:00.000"  # Inicialização com tempo zero
tempo_planejado = "00:00:43.000"


# Converter hora no formato string para milissegundos desde meia-noite
def time_str_to_milliseconds(time_str):
    time_obj = datetime.strptime(time_str, "%H:%M:%S.%f")
    milliseconds = (time_obj.hour * 3600 + time_obj.minute * 60 + time_obj.second) * 1000 + time_obj.microsecond // 1000
    return milliseconds

# Converter milissegundos de volta para string no formato HH:MM:SS.mmm
def milliseconds_to_time_str(milliseconds):
    hours = milliseconds // (3600 * 1000)
    milliseconds %= (3600 * 1000)
    minutes = milliseconds // (60 * 1000)
    milliseconds %= (60 * 1000)
    seconds = milliseconds // 1000
    milliseconds %= 1000

    return f"{hours:02}:{minutes:02}:{seconds:02}.{milliseconds:03}"

def get_tracking_info():
    global qtdMotrs, previous_value, roi_object_count, last_update_time, last_update_date, time_for_save, tempo_decorrido

    try:
        with lock:
            # Verifica se o valor mudou de 0 para 1
            if roi_object_count == 1 and previous_value == 0:
                qtdMotrs += 1  # Incrementa apenas uma vez

                # Atualiza a hora e data somente quando há incremento
                now = datetime.now()
                last_update_time = now.strftime("%H:%M:%S.%f")
                
                # Se houve incremento, calcula o tempo decorrido
                if time_for_save is not None:
                    previous_time_ms = time_str_to_milliseconds(time_for_save)
                    current_time_ms = time_str_to_milliseconds(last_update_time)
                    calcule_time_ms = current_time_ms - previous_time_ms

                    # Congela o valor do tempo decorrido até o próximo incremento
                    tempo_decorrido = milliseconds_to_time_str(calcule_time_ms)
                
                # Atualiza o tempo de salvamento para o próximo cálculo
                time_for_save = last_update_time
                last_update_date = now.strftime("%d/%m/%Y")

            # Atualiza o valor anterior
            previous_value = roi_object_count

            # Retorna as informações de rastreamento
            posto1 = {
                'QtdMotor': qtdMotrs,
                'hora': last_update_time,
                'data': last_update_date,
                'tempo_decorrido': tempo_decorrido,
                'tempo_planejado': tempo_planejado
            }

            return posto1

    except Exception as e:
        print(f"Erro ao obter informações de rastreamento: {e}")
        return {
            'object_times': {},
            'no_detection_time': 0,
            'roi_object_count': 0  # Retornar 0 se houver erro
        }
