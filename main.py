from threading import Lock, Thread
from processing_video import imageUpdater, count_motor, count_operation, generate_raw_camera
from config import camera_urls, rois, roi_points_worker
import logging
from flask import Flask, Response, jsonify, render_template
from flask_cors import CORS
from data_utils import updateAPI


log = logging.getLogger('werkzeug')
log.setLevel(logging.ERROR)  # Ou logging.CRITICAL para menos logs

app = Flask(__name__)
CORS(app)

"""
@app.route('/api')
def getAPI():
    info = updateAPI()
    return jsonify(info)
"""

@app.route('/api')
def getAPI():
    info = updateAPI()
    return jsonify(info)

@app.route('/cam')
def tracking():
    """Rota do Flask para servir a página de tracking info."""
    return render_template('index.html')


@app.route('/api_update')
def api_update():
    """Rota do Flask para servir a página de tracking info."""
    return render_template('tracking.html')


"""
def generate_camera(camera_id):
    encode_param = [int(cv2.IMWRITE_JPEG_QUALITY), 50]

    while True:
        sleep(0.05)
        with frame_lock:
            frame = annotated_frames[camera_id]
            if frame is not None:
                _, jpeg = cv2.imencode('.jpg', frame, encode_param)
                frame_bytes = jpeg.tobytes()
                yield (b'--frame\r\n'
                       b'Content-Type: image/jpeg\r\n\r\n' + frame_bytes + b'\r\n')
            else:
                yield (b'--frame\r\n'
                       b'Content-Type: text/plain\r\n\r\n' + b'Waiting for the frame...\r\n')


@app.route('/video<camera_id>')
def video_camera_feed(camera_id):
    try:
        camera_id = int(camera_id)
        if 0 <= camera_id < len(camera_urls):
            return Response(generate_camera(camera_id), mimetype='multipart/x-mixed-replace; boundary=frame')
        else:
            return f"Invalid camera ID: {camera_id}", 404
    except ValueError:
        return "Camera ID must be an integer.", 400


def generate_cropped_frames(camera_id):
    encode_param = [int(cv2.IMWRITE_JPEG_QUALITY), 50]

    while True:
        sleep(0.05)
        with frame_lock:
            frame = annotated_frames_worker[camera_id]
            if frame is not None:
                _, jpeg = cv2.imencode('.jpg', frame, encode_param)
                frame_bytes = jpeg.tobytes()
                yield (b'--frame\r\n'
                       b'Content-Type: image/jpeg\r\n\r\n' + frame_bytes + b'\r\n')
            else:
                yield (b'--frame\r\n'
                       b'Content-Type: text/plain\r\n\r\n' + b'Waiting for the cropped frame...\r\n')
        
                
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
"""

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
        thread.start()
        threads.append(thread)
    
    # Inicializa o servidor Flask
    app.run(host='0.0.0.0', port=4000)
    