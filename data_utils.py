""" 
A logica desse script nao funciona, o valor da minha variavel anterior sera mudado logo
na sua segunda requisição do servidor flask.Quais sao os posiveis soluçoes ?

Utilizar um serviço flask.socket ?

Alterar a logica do progrma para salvar o estado da variavel idependente do numero de
requisição, como o valor de sensor provem de um função sendo 0 e 1

Atual x Anterior x Get
1		0		  1  - Primeira requisição logo nao havia valor anterior
0		1		  2
1		0		  3

"""

from video_utils import get_motor_sensor_value
from threading import Lock
from datetime import datetime

class MotorTracker:
    def __init__(self):
        self.lock = Lock()
        self.sensorValue = 0
        self.sensorValueAnterior = 0
        self.qtdMotor = 0
        self.data = None
        self.hora = None
        self.horaAnterior = None
        self.log = None
        

    def incrementMotor(self):
        # Verifica se o valor mudou de 0 para 1 (indicando a presença de um motor)
        if self.sensorValue == 1 and self.sensorValueAnterior == 0:
            self.qtdMotor += 1
            self.data = datetime.now()
            self.hora = self.data.strftime('%Y-%m-%d %H:%M:%S')

    def verificarStatus(self):
        self.sensorValue = get_motor_sensor_value()
        
        with self.lock:
            if self.sensorValue == 0:
                self.sensorValueAnterior = 1
            else:
                self.incrementMotor()
                self.sensorValueAnterior = 0
                self.log = 'Nao houverao mudanças'


    def get_tracking_info(self):        

        self.verificarStatus()
        
        # Guarda a hora anterior
        self.horaAnterior = self.hora

        # Retorna as informações em formato de dicionário
        return {
            'Sensor': self.sensorValue,
            'Sensor Anterior': self.sensorValueAnterior,
            'Quantidade de Motor': self.qtdMotor,
            'data': self.hora,
            'hora_anterior': self.horaAnterior,
            'log': self.log 
        }

# Exemplo de uso
tracker = MotorTracker()

# Para chamar a função, você usaria:
info = tracker.get_tracking_info()
print(info)
