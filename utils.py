import cv2
import numpy as np
import time
from ultralytics import YOLO
from threading import Lock
from datetime import datetime
import pymongo
import requests

# Configurações                     -           +
ROI_POINTS = np.array([[960, 220], [1120, 210], [1143, 360], [995, 380]], dtype=np.int32)
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


# Conectar ao MongoDB
client = pymongo.MongoClient("mongodb://localhost:27017/")
db = client["meu_banco"]
collection = db["motores"]

# URL da API onde o JSON é fornecido
url = "http://10.1.30.105:5000/tracking_info"  # Substitua pelo URL correto
 

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

'''
def get_tracking_info():
   """Retornar as informações de rastreamento para geração de JSON."""
   try:
       with lock:
           return {
               'object_times': {},  # Retornar um dicionário vazio
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


qtdMotrs = 0
previous_value = 0
last_update_time = None
last_update_date = None
roi_object_count = 0  # Defina um valor inicial para testar
last_update_time_dict = {}  # Dicionário para armazenar os tempos de atualização

def get_tracking_info():
   global qtdMotrs, previous_value, roi_object_count, last_update_time, last_update_date

   try:
       with lock:
           now = datetime.now()
           time_oe = "00:00"  # Formato padrão para tempo

           # Verifica se houve mudança na quantidade de motores
           if roi_object_count != previous_value:
               # Se houve incremento em qtdMotrs
               if roi_object_count > previous_value:
                   qtdMotrs += 1
               else:
                   qtdMotrs -= 1
               
               # Atualiza o last_update_time e last_update_date
               last_update_time = now
               last_update_date = now.strftime("%d/%m/%Y")
               
               # Calcula time_oe se a quantidade de motores já foi registrada antes
               if previous_value in last_update_time_dict:
                   delta = (now - last_update_time_dict[previous_value]).total_seconds()
                   time_oe = str(datetime.utcfromtimestamp(delta).strftime("%H:%M:%S"))

               # Atualiza o dicionário com o tempo de atualização
               last_update_time_dict[qtdMotrs] = now

           # Atualiza o valor anterior
           previous_value = roi_object_count
           
           # Retorna as informações de rastreamento
           posto1 = {
               'QtdMotor': qtdMotrs,
               'hora': last_update_time.strftime("%H:%M:%S.%f") if last_update_time else None,
               'data': last_update_date,
               'time_oe': time_oe
           }
           return posto1
   except Exception as e:
       print(f"Erro: {e}")

'''

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
                'tempo_decorrido': tempo_decorrido,     #Mantém o último valor congelado até novo incremento
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


def consumir_json():
   """Função que consome os dados JSON da API"""
   try:
       response = requests.get(url)
       # Verificar se a resposta é válida
       if response.status_code == 200:
           return response.json()  # Tentativa de decodificar o JSON
       else:
           print(f"Erro na resposta da API. Status Code: {response.status_code}")
           return None
   except requests.exceptions.RequestException as e:
       print(f"Erro ao fazer a requisição: {e}")
       return None
   except ValueError as e:
       print(f"Erro ao decodificar o JSON: {e}")
       return None

def inserir_no_mongo(dados):
   """Função que insere os dados no MongoDB se forem diferentes"""
   try:
       # Verifica se o JSON já existe no banco de dados
       if not collection.find_one(dados):
           collection.insert_one(dados)
           print("Novos dados inseridos no MongoDB")
       else:
           print("Dados já existem no banco de dados, não inseridos.")
   except Exception as e:
       print(f"Erro ao inserir no MongoDB: {e}")

