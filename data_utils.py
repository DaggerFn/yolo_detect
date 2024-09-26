from video_utils import get_motor_sensor_value

sensorValue = (int) 
qtdMotor = 0

def incrementMotor():
    global qtdMotor  
    
    if sensorValue == True:
        qtdMotor += 1

def get_tracking_info():
    
    incrementMotor()
    global sensorValue 
    sensorValue = get_motor_sensor_value()
    
    return {
        'Sensor': sensorValue,
        'Quantidade de Motor': qtdMotor
    }
    

"""
def get_tracking_info():
    # Passe o frame e o model ao chamar a função
    motor = get_motor_sensor_value()

    if motor == 1:
        print("Objeto detectado na ROI.")
        return {'valor': motor}
    else:
        print("Nenhum objeto na ROI.")
        return {'valor': motor}
""" 