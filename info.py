from datetime import datetime
from threading import Lock
import time
from proccess_video import is_object_in_roi, process_frame

# Variáveis globais para controle de tempo e contagem
lock = Lock()
qtdMotrs = 0
previous_value = 0
no_detection_time = 0
last_update_time = None
last_update_date = None
time_for_save = None
tempo_decorrido = "00:00:00.000"
tempo_planejado = "00:00:43.000"
roi_object_count = 0

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

# Função para obter informações de rastreamento
def get_tracking_info():
    global qtdMotrs, previous_value, last_update_time, last_update_date, time_for_save, tempo_decorrido, roi_object_count

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
