from video_utils import get_motor_sensor_value
import time

# Inicialize as variáveis
sensorValue = get_motor_sensor_value()
sensorValueAnterior = sensorValue  # Inicialmente, ambos têm o mesmo valor

while True:
    sensorValueAnterior = sensorValue  # Armazena o valor atual como "anterior"
    sensorValue = get_motor_sensor_value()  # Atualiza o valor com o novo sensorValue
    
    # Aqui você pode fazer verificações ou processar os valores
    if sensorValue != sensorValueAnterior:
        print(f"Valor anterior: {sensorValueAnterior}, Novo valor: {sensorValue}")
    
    # Aguarde um tempo antes da próxima verificação (para simular um ciclo)
    time.sleep(1)
