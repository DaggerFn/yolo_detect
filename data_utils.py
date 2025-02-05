"""
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


def export_var_contador():
    #if len(contador) >= 5:
    return contador
    

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
    Atualiza o estado e a quantidade de objetos detectados para um posto específico.

    Args:
        id (str): Identificador da câmera.
        detected_classes (list): Classes detectadas pelo modelo.
        contador (dict): Dicionário global com as contagens por câmera.
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
    Retorna o estado atualizado dos postos.

    Returns:
        dict: Dicionário contendo os dados dos postos.
    global postos
    
    with frame_lock:
        return postos
"""

'''
from datetime import datetime, timedelta
from threading import Lock, Thread

frame_lock = Lock()
postos = {}
percentage = 1
status = 1
time_val = 2 
date_val = 2

pending_status = {}
last_status_time = {}
validation_time = timedelta(seconds=3) 

def updateDateAndTime():
    now = datetime.now()
    return now.strftime('%Y-%m-%d %H:%M:%S')

def updateStatus(detected_classes):
    if 'motor' in detected_classes and 'hand' in detected_classes:
        return "Operando"
    else:
        return "Parado"

def infObjects(id, detected_classes, objects_counter):
    global postos, pending_status, last_status_time, validation_time
    
    current_status = updateStatus(detected_classes)
    posto_key = f"Posto{id + 1}"
    now = datetime.now()

    with frame_lock:
        if posto_key not in postos:
            postos[posto_key] = {
                "Data": updateDateAndTime(),
                "Status": current_status,
                "Quantidade": objects_counter,
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
                    postos[posto_key]["Quantidade"] = objects_counter
                    pending_status[posto_key] = current_status
                    last_status_time[posto_key] = now
            else:
                pending_status[posto_key] = current_status
                last_status_time[posto_key] = now

def updateAPI():
    global postos
    with frame_lock:
        return postos
        


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

# Funções auxiliares
def updateDateAndTime():
    now = datetime.now()
    return now.strftime('%Y-%m-%d %H:%M:%S')

def pass_class_api(detected_classes):
    global status
    if 'motor' in detected_classes and 'hand' in detected_classes:
        status = "Operando"
    else:
        status = "Parado"


def infObjects(id, contador):

    global postos, pending_status, last_status_time, validation_time
    
    current_status = status #pass_class_api(detected_classes)
    posto_key = f"Posto {id}"# + 1}"
    now = datetime.now()

    # Obtém a quantidade atual do contador para a câmera
    quantidade_atual = contador.get(id, {}).get("Quantidade", 0)

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

    global postos
    with frame_lock:
        return postos

'''

#from processing_video import contador, operacao
from datetime import datetime, timedelta
from threading import Lock

frame_lock = Lock()

postos = {}

pending_status = {}
last_status_time = {}
validation_time = timedelta(seconds=3) 


def updateDateAndTime():
    now = datetime.now()
    return now.strftime('%Y-%m-%d %H:%M:%S')

def makeJson(id, contador, operacao):
    #contador, operacao = [0]
    global postos    
    
    posto_id = f'Posto {id + 1}'
    current_status = operacao[id]['Operação']#(int[None])
    quantidade_atual = contador[id]['Qtd']#,(int[None])
    now = updateDateAndTime()
    
    with frame_lock:

        if posto_id not in postos:
            
            postos[posto_id] = {
                "Data": updateDateAndTime(),
                "Quantidade": contador[id]['Quantidade'],
                "Status": operacao[id]['Operação'],
            }
            
    '''
    
    with frame_lock:
        
        if posto_id not in postos:
            postos[posto_id] = {
                "Data": now,
                "Status": current_status,
                "Quantidade": quantidade_atual,
            }
            pending_status[posto_id] = current_status
            last_status_time[posto_id] = now
            return

        stable_status = postos[posto_id]["Status"]
        
        if current_status == stable_status:
            pending_status[posto_id] = stable_status
            last_status_time[posto_id] = now
        else:
            if pending_status.get(posto_id) == current_status:
                if now - last_status_time[posto_id] >= validation_time:
                    postos[posto_id]["Data"] = now
                    postos[posto_id]["Status"] = current_status
                    postos[posto_id]["Quantidade"] = quantidade_atual,
                    pending_status[posto_id] = current_status
                    last_status_time[posto_id] = now
            else:
                pending_status[posto_id] = current_status
                last_status_time[posto_id] = now
    '''    

def updateAPI():
    global postos
    
    with frame_lock:
        return postos



""""
{
	"Data": "2025-02-03 15:38:33",
	"Quantidade": {
		"Operação": 0
	},
	"Status": {
		"Quantidade": 1
	}
}

{'Posto 1': {'Data': '2025-02-04 13:45:17', 'Status': {'Quantidade': 1}, 'Quantidade': {'Operação': 1}}}
{'Posto 1': {'Data': '2025-02-04 13:47:39', 'Status': 0, 'Quantidade': {'Operação': 0}}}
"""