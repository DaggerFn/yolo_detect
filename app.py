import time
from flask import Flask, render_template, Response, jsonify
from flask_cors import CORS
import requests
from threading import Thread
from utils import load_yolo_model, generate_frames, get_tracking_info
from database import inserir_no_postgres
from download import export_to_excel

app = Flask(__name__)
CORS(app)

# Configurações
MODEL_PATH = "P1_final_v2.pt"
CAMERA_URL = 'http://10.1.60.155:4000/video_feed'

# Carregar o modelo YOLOv10
model = load_yolo_model(MODEL_PATH)

@app.route('/video_feed')
def video_feed():
    """Rota do Flask para transmitir o vídeo processado."""
    return Response(generate_frames(model, CAMERA_URL),
                    mimetype='multipart/x-mixed-replace; boundary=frame')

@app.route('/tracking_info', methods=['GET'])
def tracking_info():
    """Rota do Flask para obter as informações de rastreamento no formato JSON."""
    info = get_tracking_info()
    return jsonify(info)

@app.route('/tracking')
def tracking():
    """Rota do Flask para servir a página de tracking info."""
    return render_template('tracking.html')

@app.route('/download_excel')
def download_excel():
    return export_to_excel()

def consumir_json():
    """Função que consome os dados JSON da API."""
    url = "http://10.1.30.100:5000/tracking_info"  # Altere para o URL correto
    try:
        response = requests.get(url)
        if response.status_code == 200:
            return response.json()
        else:
            print(f"Erro na resposta da API. Status Code: {response.status_code}")
            return None
    except requests.exceptions.RequestException as e:
        print(f"Erro ao fazer a requisição: {e}")
        return None

def main():
    """Função principal para iniciar o servidor Flask e consumir JSON."""
    ultimo_json = None

    while True:
        novo_json = consumir_json()

        # Verificar se o novo JSON é diferente do anterior
        if novo_json is not None:
            print("Novo JSON recebido:", novo_json)  # Adiciona esta linha para depuração
            
            if novo_json != ultimo_json:
                inserir_no_postgres(novo_json)
                ultimo_json = novo_json  # Atualiza o último JSON inserido

        # Aguarda 1 segundo antes de verificar novamente
        time.sleep(1)

if __name__ == '__main__':
    # Rodar o Flask em um thread separado
    Thread(target=main).start()  # Inicia a função main em um thread separado
    app.run(host='0.0.0.0', port=5000, threaded=True)

