""" 
motorSensor = 0 #Declaro o valor

def get_motor_sensor_value(): #Função para retornar o valor motorSensor 
    global motorSensor
    return motorSensor 

def converter_para_booleano(valor):#função que trasforma var em bool
   return bool(valor)#define que a funcao ira alterar a var em scopo global

sensorValue = get_motor_sensor_value() #

converter_para_booleano(sensorValue)

print(converter_para_booleano(sensorValue))

"""

import random
random.choice([True, False])

# Inicializa as variáveis
sensorAnterior = random.choice  # Nenhum valor anterior no início
sensorAtual = False

# Função para obter o valor do sensor
def get_motor_sensor_value():
   # Simulação de leitura do sensor (substitua pelo código real)
   return 1  # Exemplo de valor do sensor (pode ser 0 ou 1)

# Loop para monitorar o sensor
while True:
   # Obtém o valor do sensor
   sensorValue = get_motor_sensor_value()
   
   # Converte o valor para booleano
   sensorAtual = (sensorValue == 1)
   
   # Se sensorAnterior não for None, compare os estados
   if sensorAnterior is not None and sensorAtual != sensorAnterior:
       if sensorAtual:
           print("O sensor foi ativado.")
       else:
           print("O sensor foi desativado.")
   
   # Atualiza o estado anterior
   sensorAnterior = sensorAtual
   break
   # Adicione um delay ou condição de parada conforme necessário