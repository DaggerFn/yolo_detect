from video_utils import get_motor_sensor_value

def get_tracking_info():
    # Passe o frame e o model ao chamar a função
    motor = get_motor_sensor_value()

    if motor == 1:
        print("Objeto detectado na ROI.")
        return {'valor': motor}
    else:
        print("Nenhum objeto na ROI.")
        return {'valor': motor}