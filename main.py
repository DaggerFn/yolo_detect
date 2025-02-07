from threading import Lock, Thread
from processing_video import imageUpdater, count_motor, count_operation, generate_raw_camera
from processing_video import generate_camera_motor, varReturn
#from processing_video import contador, operacao#, varReturn
from config import camera_urls
import logging
from flask import Flask, Response, jsonify, render_template
from flask_cors import CORS
from data_utils import makeJson, updateAPI



log = logging.getLogger('werkzeug')
log.setLevel(logging.ERROR)  # Ou logging.CRITICAL para menos logs


app = Flask(__name__)
CORS(app)


@app.route('/api')
def getAPI():
    info = updateAPI()
    return jsonify(info)


'''
@app.route('/video<camera_id>')
def video_camera_feed(camera_id):
    try:
        camera_id = int(camera_id)
        if 0 <= camera_id < len(camera_urls):
            return Response(generate_camera_motor(camera_id), mimetype='multipart/x-mixed-replace; boundary=frame')
        else:
            return f"Invalid camera ID: {camera_id}", 404
    except ValueError:
        return "Camera ID must be an integer.", 400

               
@app.route('/cropped_frames<camera_id>')
def cropped_frames_feed(camera_id):
    try:
        camera_id = int(camera_id)
        if 0 <= camera_id < len(camera_urls):
            return Response(generate_cropped_frames(camera_id), mimetype='multipart/x-mixed-replace; boundary=frame')
        else:
            return f"Invalid camera ID: {camera_id}", 404
    except ValueError:
        return "Camera ID must be an integer.", 400
'''


@app.route('/video_raw<camera_id>')
def video_raw_camera_feed(camera_id):
    try:
        camera_id = int(camera_id)
        if 0 <= camera_id < len(camera_urls):
            #returnJson()
            
            return Response(generate_raw_camera(camera_id), mimetype='multipart/x-mixed-replace; boundary=frame')
        else:
            return f"ID da câmera inválido: {camera_id}", 404
    except ValueError:
        return "O ID da câmera deve ser um inteiro.", 400



if __name__ == '__main__':
    
    # Inicializa threads de atualização de frames para cada câmera
    threads = []
    
    
    for idx, url in enumerate(camera_urls):
        thread = Thread(target=imageUpdater, kwargs={'id': idx, 'video_path': url, 'interval': 0.01})
        thread.start()
        threads.append(thread)
    
    # Inicializa threads de detecção para cada câmera
    for idx in range(len(camera_urls)):
        thread = Thread(target=count_motor, args=(idx,))
        thread.start()
        threads.append(thread)
    
    for idx in range(len(camera_urls)):
        thread = Thread(target=count_operation, args=(idx,))
        #print(idx)
        thread.start()
        threads.append(thread)

    thread = Thread(target=makeJson, args=(varReturn,))
    thread.start()
    threads.append(thread)
    
    # Inicializa o servidor Flask
    app.run(host='0.0.0.0', port=5000)
