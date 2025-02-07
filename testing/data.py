frame_lock = Lock()
postos = {}


def updateDateAndTime():
    now = datetime.now()
    return now.strftime('%Y-%m-%d %H:%M:%S')


def makeJson(id, varReturn):
    #contador, operacao = [0]
    global postos    
    
    quantidade, status = varReturn()
    
    
    posto_id = f'Posto {id + 1}'
    
    if posto_id not in postos:
        
        postos[posto_id] = {
            "Data": updateDateAndTime(),
            "Quantidade": quantidade[id]['Quantidade'],
            "Status": status[id]['Operação'],
        }
           
            
    """
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
    """


def updateAPI():
    global postos
    with frame_lock:
        return postos


'''
from threading import Lock
from time import time, sleep
 

'''
quantidade = {0 :{'Quantidade': 1},
       1 :{'Quantidade': 0},
       }       

status = {0 :{'Operacao': 0},
       1 :{'Operacao': 1},
       }       

'''

lock_var = Lock()
postos = {}


def makeJson(varReturn):
    global postos
    
    while True:
        quantidade, status = varReturn()
        
        for i in range(len(status)):
            
            index_posto = f'posto {i + 1}'
            
            if index_posto not in postos:
            
                postos[index_posto] = {
                    'Status': status[i]['Operação'],
                    'Quantidade': quantidade[i]['Quantidade'],
                }
            else:
        
                postos[index_posto] = {
                    'Status': status[i]['Operação'],
                    'Quantidade': quantidade[i]['Quantidade'],
                }
            
        sleep(1)

def updateAPI():    
    global postos
    
    with lock_var:    
        return postos
'''