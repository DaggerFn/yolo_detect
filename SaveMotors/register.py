"""
- Verificar o Status do JSON 0:1
- Salvar Informação como numero
- Disponibilizar Numero no JSON
- Eviar para JS o valor da variavel 
"""
import requests

# Send a GET request to the desired API URL
response = requests.get('http://10.1.60.155:4000/tracking_info')

# Parse the response and print it
data = response.json()
print(data)