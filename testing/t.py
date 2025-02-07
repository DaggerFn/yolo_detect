var1 = {0 :{'Quantidade': 1},
       1 :{'Quantidade': 0},
       }       

var2 = {0 :{'Operacao': 0},
       1 :{'Operacao': 1},
       }       

posto = {}
posto2 = {}

def varReturn():
    global var1, var2
    
    return var1, var2

def loop():
    global posto, posto2
    
    status, quantidade = varReturn()
    
    while True:
        
        
        posto = {
            'op': status[0],#['Operacao'],
            'qtd': quantidade[0],#['Quantidade'],
        }
            
        posto2 = {
            'op': status[1],#['Operacao'],
            'qtd': quantidade[1],#['Quantidade'],
        }
            
        print('posto1',posto) 
        print('posto2',posto2)
        
        
        '''
        except:
            print('Not OK')
       ''' 





if __name__ == '__main__':

    loop()
    print(posto, posto2)


    """
    Output:

    Posto1 : {
        Data: 11/09/2001
        Status: 1
        Quantidade: 2
    }

    """