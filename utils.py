import cv2
import numpy as np
import time
from ultralytics import YOLO
from threading import Lock
from datetime import datetime


# Configurações                     -           +

ROI_POINTS = np.array([[380, 380], [600, 380], [600, 590], [380, 590]], dtype=np.int32)

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
detected_classes = None
lock = Lock()

# URL da API onde o JSON é fornecido
url = "http://10.1.30.105:5000/tracking_info"  # Substitua pelo URL correto
 

def load_yolo_model(model_path):
   """Carregar o modelo YOLO a partir do caminho especificado."""
   return YOLO(model_path)

def process_frame(frame, model):
   """Processar o frame com a ROI e YOLO."""
   global detected_classes
   # Criar uma máscara para a ROI
   mask = np.zeros_like(frame)
   cv2.fillConvexPoly(mask, ROI_POINTS, (255, 255, 255))
   roi_frame = cv2.bitwise_and(frame, mask)

   # Processar o frame com YOLO
   results = model(roi_frame)

   # Se for uma lista, acesse o primeiro item
   if isinstance(results, list):
        results = results[0]

   #Chama função para retorno de classe 
   detected_classes = get_detected_classes(results)
   
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


def track_objects(frame, model):
   """Rastrear objetos e contabilizar o tempo em e fora da ROI."""
   global no_detection_time, roi_object_count, last_detection_time  # Adicione last_detection_time aqui

   current_time = time.time()
   frame, detections = process_frame(frame, model)

   roi_count = 0  # Contador de objetos na ROI

   with lock:
       for detection in detections:
           try:
               if len(detection) >= 4:  # Verifica se a detecção contém pelo menos 4 valores
                   xmin, ymin, xmax, ymax = detection[:4]

                   if is_object_in_roi([xmin, ymin, xmax, ymax], ROI_POINTS):
                       roi_count += 1  # Incrementar o contador de objetos na ROI

           except Exception as e:
               print(f"Erro ao processar detecção: {e}")

       # Se houver detecções, resetar o tempo sem detecções
       if roi_count > 0:
           no_detection_time = 0
       else:
           no_detection_time += current_time - last_detection_time  # Agora last_detection_time está acessível

       last_detection_time = current_time
       roi_object_count = roi_count  # Atualizar a contagem de objetos na ROI

   return {
       'object_times': {},  # Retornar um dicionário vazio
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

""" 
_______________________________________________________________________________________________________________________________________________________________________________________________________
|______________________________________________________________________________________________________________________________________________________________________________________________________|

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

def calcular_ie(tempo_planejado, tempo_decorrido):
    try:
        # Converter ambos os tempos para milissegundos
        tempo_planejado_ms = time_str_to_milliseconds(tempo_planejado)
        tempo_decorrido_ms = time_str_to_milliseconds(tempo_decorrido)
        
        # Evitar divisão por zero
        if tempo_decorrido_ms == 0:
            return 0
        
        # Calcular o Índice de Eficiência
        ie = (tempo_planejado_ms / tempo_decorrido_ms) * 100
        return ie
    
    except Exception as e:
        print(f"Erro ao calcular o Índice de Eficiência: {e}")
        return None

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

            class_names = ['Normal', 'W12']  # Substitua pelos nomes corretos

            # Exibir os nomes das classes detectadas
            detected_class_names = [class_names[class_id] for class_id in detected_classes]
            #print("Classes detectadas:", detected_class_names)
            
            if detected_classes == 1:
                tempo_planejado = "00:00:39.660"
            elif detected_classes == 2:
                tempo_planejado = "00:00:50.420"
            else:
                tempo_planejado = "00:00:39.660"
            # Retorna as informações de rastreamento
            
            val = calcular_ie(tempo_planejado, tempo_decorrido)
            
            posto1 = {
                'QtdMotor': qtdMotrs,
                'hora': last_update_time,
                'data': last_update_date,
                'tempo_decorrido': tempo_decorrido,
                'tempo_planejado': tempo_planejado,
                'Classe Detectada': detected_class_names,
                'IE': val
            }

            return posto1

    except Exception as e:
        print(f"Erro ao obter informações de rastreamento: {e}")
        return {
        }
