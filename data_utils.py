from datetime import datetime

# Dicionário global para armazenar informações de cada posto
postos = {}
percentage = 1
status = 1
time = 2
date = 2


# Função para atualizar data e hora
def updateDateAndTime():
    now = datetime.now()
    return now.strftime('%Y-%m-%d'), now.strftime('%H:%M:%S')

# Função para atualizar o status
def updateStatus(detected_classes):
    if 'motor' in detected_classes and 'motor' in detected_classes:
        return "Operando"
    else:
        return "Parado"

# Função chamada para cada câmera (ID)
def infObjects(id, detected_classes):
    global postos

    # Verificar se as classes 'motor' e 'hand' estão presentes
    if 'motor' in detected_classes and 'motor' in detected_classes:
        date, time = updateDateAndTime()
        status = updateStatus(detected_classes)
        percentage = f"{round((id + 1) * 10.5, 2)}%"

        # Atualizar ou criar entrada no dicionário de postos
        postos[f"Posto{id + 1}"] = {
            "Data": date,
            "Hora": time,
            "Status": status,
            "ID": percentage,
        }
    else:
        postos[f"Posto{id + 1}"] = {
            "Data": None,
            "Hora": None,
            "Status": None,
            "ID": None,
        }
        
# Função para retornar o estado atual dos postos (JSON-like)
def updateAPI():
    global postos
    return postos