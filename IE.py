import json
from utils import get_tracking_info

# Chamar a função para obter as informações de rastreamento
data_json = get_tracking_info()

# Carregar o JSON
data = json.loads(json.dumps(data_json))  # Converter o dicionário para JSON e depois de volta

# Extrair dados
qtd_motor = data['QtdMotor']
tempo_decorrido = data['tempo_decorrido']
tempo_planejado = data['tempo_planejado']  # Corrigido o nome da chave

# Converter tempos para segundos
def tempo_para_segundos(tempo):
   h, m, s = map(float, tempo.split(':'))
   return h * 3600 + m * 60 + s

tempo_decorrido_segundos = tempo_para_segundos(tempo_decorrido)
tempo_planejado_segundos = tempo_para_segundos(tempo_planejado)

# Calcular IE
produção_real = qtd_motor
produção_ideal = (tempo_planejado_segundos / tempo_decorrido_segundos) #* produção_real

# IE = (produção_real / produção_ideal) * 100
IE = (produção_real / produção_ideal) * 100 if produção_ideal > 0 else 0  # Evitar divisão por zero

print(f"Índice de Eficiência (IE): {IE:.2f}%")

def retornaIE():
    return IE