from threading import Lock
from time import time, sleep
 

'''
quantidade = {0 :{'Quantidade': 1},
       1 :{'Quantidade': 0},
       }       

status = {0 :{'Operacao': 0},
       1 :{'Operacao': 1},
       }       
'''

lock_var = Lock()
postos = {}


def makeJson(varReturn):
    global postos
    
    while True:
        try:
            contador, operacao = varReturn()
            
            for i in range(len(operacao)):
                
                index_posto = f'posto {i + 1}'
                
                if index_posto not in postos:
                
                    postos[index_posto] = {
                        'Status': operacao[i]['Operação'],
                        'Quantidade': contador[i]['Quantidade'],
                    }
                    print('OK in JSON')
                print('Stoping Looking Variables')
                
        except:
            print('Waitig lenght correct')        
            sleep(15)


def updateAPI():    
    global postos
    
    #with lock_var:    
    #    return postos
    return postos
    