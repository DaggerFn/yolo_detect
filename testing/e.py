'''
_______________________________________
Input =>

quantidade = {0 :{'Quantidade': 1},
       1 :{'Quantidade': 0},
       }       

status = {0 :{'Operacao': 0},
       1 :{'Operacao': 1},
       }       

_______________________________________
Output =>

Posto1 {
	data: updateTime()
	status: status[0]
	Quantidade:quantidade[0]
}

Posto2 {
	data: updateTime()
	status: status[1]
	Quantidade:quantidade[1]
}

Posto3 {....
_______________________________________
'''
quantidade = {0 :{'Quantidade': 1},
       1 :{'Quantidade': 2},
       2 :{'Quantidade': 0},
       }       

status = {0 :{'Operacao': 0},
       1 :{'Operacao': 2},
       2 :{'Operacao': 1},
       }       

postos = {}

def makeJson():
    tam_indices_sts = len(status)
    tam_indices_qtd = len(quantidade)
    
    
    for i in range(len(status)):
        
        index_posto= f'posto {i + 1}'
        
        if index_posto not in postos:
            postos[index_posto] = {
                'status': status[i]['Operacao'],       
                'Quantidade': quantidade[i]['Quantidade'],  
            }
        
            print('tamanho do status',i)
        
    
if __name__ == '__main__':
    makeJson()
    print(postos,'\n')
    