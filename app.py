from flask import Flask, render_template, Response, jsonify
from video_utils import load_yolo_model, generate_frames
from data_utils import get_tracking_info
import cv2

app = Flask(__name__)

# Carregar o modelo YOLO
model_path = r'C:\Users\gustavonc\Documents\2-Programs\6-WSFM_Montagem\trasmisoes_linha_montagem\yolo_detect_v1\pt\8n_colab_p3_openvino_model'  # Substitua pelo caminho correto do seu modelo YOLO
model = load_yolo_model(model_path)

# URL da câmera
camera_url = 'http://10.1.60.155:4000/video_feed'  # Substitua pelo URL da câmera

cap = cv2.VideoCapture(camera_url)

@app.route('/tracking_info')
def tracking_info():
    """Rota para fornecer informações de rastreamento."""
    tracking_data = get_tracking_info()
    return jsonify(tracking_data)

@app.route('/tracking')
def tracking():
  """Rota do Flask para servir a página de tracking info."""
  return render_template('tracking.html')

@app.route('/video_feed')
def video_feed():   
    """Rota para fornecer o feed de vídeo com as detecções e ROI."""
    return Response(generate_frames(model, camera_url),
                    mimetype='multipart/x-mixed-replace; boundary=frame')

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)