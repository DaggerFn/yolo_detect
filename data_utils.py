from datetime import datetime, timedelta
from threading import Lock, Thread

# Variáveis globais
frame_lock = Lock()
postos = {}
percentage = 1
status = 1
time_val = 2 
date_val = 2
pending_status = {}
last_status_time = {}
validation_time = timedelta(seconds=3)
contador = {}
ultimo_tempo = {}
estado_anterior = {}

def objects_counter(camera_id, detected_classes, detections):
    """
    Verifica se há objetos detectados da classe 'motor' e atualiza o contador apenas
    quando o status de detecção muda.

    Args:
        camera_id (str): Identificador da câmera.
        detected_classes (list): Lista de classes identificadas pelo modelo.
        detections (list): Lista de detecções no formato de coordenadas (x1, y1, x2, y2).

    Returns:
        None
    """
    global contador, estado_anterior
    
    time_last_detec = None 

    time_now = None
    
    time_state =  timedelta(seconds=2)
    
    # Inicializa o contador e o estado anterior para a câmera, se necessário
    if camera_id not in contador:
        contador[camera_id] = {'Quantidade': 0}
    if camera_id not in estado_anterior:
        estado_anterior[camera_id] = False  # Nenhuma detecção inicialmente

    # Verifica se há alguma classe "motor" nas classes detectadas
    tem_motor = any('motor' in cls.lower() for cls in detected_classes)

    # Determina o status atual de detecção (considera apenas classes "motor")
    tem_deteccao = len(detections) > 0 and tem_motor
    
    
    time_now = datetime.now()
    
    
    # Incrementa o contador apenas na transição de "sem detecção" para "com detecção"
    if tem_deteccao and not estado_anterior[camera_id]:
        
        if time_last_detec is None or (time_now - time_last_detec) > time_state:

            time_last_detec = time_now  # Atualiza o último tempo detectado
            
            #print("Evento detectado!")
                    
            contador[camera_id]['Quantidade'] += 1
            #print(f"Objeto 'motor' detectado na câmera {camera_id}. Quantidade: {contador[camera_id]['Quantidade']}")

    # Atualiza o estado anterior
    estado_anterior[camera_id] = tem_deteccao

    # Exibe o status atual
    if tem_deteccao:
        None
        #print(f"Objeto 'motor' detectado na câmera {camera_id}. Quantidade: {contador[camera_id]['Quantidade']}")
 

def updateDateAndTime():
    now = datetime.now()
    return now.strftime('%Y-%m-%d %H:%M:%S')


def pass_class_api(detected_classes):
    global status
    if 'motor' in detected_classes and 'hand' in detected_classes:
        status = "Operando"
    else:
        status = "Parado"


def infObjects(id):
    """
    Atualiza o estado e a quantidade de objetos detectados para um posto específico.

    Args:
        id (str): Identificador da câmera.
        detected_classes (list): Classes detectadas pelo modelo.
        contador (dict): Dicionário global com as contagens por câmera.
    """
    global postos, pending_status, last_status_time, validation_time
    
    current_status = status #pass_class_api(detected_classes)
    posto_key = f"Posto{id + 1}"
    now = datetime.now()

    # Obtém a quantidade atual do contador para a câmera
    #quantidade_atual = contador.get(id, {}).get("Quantidade", 0)
    
    quantidade_atual = contador[id]['Quantidade']
    
    with frame_lock:
        if posto_key not in postos:
            postos[posto_key] = {
                "Data": updateDateAndTime(),
                "Status": current_status,
                "Quantidade": quantidade_atual,
            }
            pending_status[posto_key] = current_status
            last_status_time[posto_key] = now
            return

        stable_status = postos[posto_key]["Status"]
        
        if current_status == stable_status:
            pending_status[posto_key] = stable_status
            last_status_time[posto_key] = now
        else:
            if pending_status.get(posto_key) == current_status:
                if now - last_status_time[posto_key] >= validation_time:
                    postos[posto_key]["Data"] = updateDateAndTime()
                    postos[posto_key]["Status"] = current_status
                    postos[posto_key]["Quantidade"] = quantidade_atual
                    pending_status[posto_key] = current_status
                    last_status_time[posto_key] = now
            else:
                pending_status[posto_key] = current_status
                last_status_time[posto_key] = now


def updateAPI():
    """
    Retorna o estado atualizado dos postos.

    Returns:
        dict: Dicionário contendo os dados dos postos.
    """
    global postos
    
    with frame_lock:
        return postos
