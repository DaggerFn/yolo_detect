import time
from flask import Flask, render_template, Response, jsonify
from flask_cors import CORS
import requests 
from proccess_video import load_yolo_model, generate_frames
from info import get_tracking_info

app = Flask(__name__)
CORS(app)  # Adiciona CORS ao seu app Flask

# Configurações
MODEL_PATH = r'C:\Users\gustavonc\Documents\2-Programs\6-WSFM_Montagem\trasmisoes_linha_montagem\yolo_detect_v1\pt\8n_colab_p3_openvino_model'
CAMERA_URL = 'http://10.1.60.155:4000/video_feed'

# Carregar o modelo YOLOv8n
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

def consumir_json():
  """Função que consome os dados JSON da API."""
  url = "http://10.1.30.105:5000/tracking_info"  # Altere para o URL correto
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

           # Processar o JSON de acordo com sua lógica sem banco de dados
           ultimo_json = novo_json  # Atualiza o último JSON processado

       # Aguarda 1 segundo antes de verificar novamente
       time.sleep(1)

if __name__ == '__main__':
  # Rodar o Flask em um thread separado
  from threading import Thread
  Thread(target=main).start()  # Inicia a função main em um thread separado
  app.run(host='0.0.0.0', port=5000, threaded=True)
