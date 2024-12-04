import numpy as np
import cv2


model = r"C:/usr"

# Lista com várias ROIs e suas respectivas cores
rois = [
    {'points': np.array([[380, 380], [600, 380], [600, 590], [380, 590]], dtype=np.int32), 'color': (255, 0, 0)},  # Vermelho
    {'points': np.array([[700, 100], [900, 100], [900, 300], [700, 300]], dtype=np.int32), 'color': (0, 255, 0)},  # Verde
    {'points': np.array([[100, 700], [300, 700], [300, 900], [100, 900]], dtype=np.int32), 'color': (0, 0, 255)},  # Azul
]


ipLinks =  {
    "10.1.30.105"   
    "10.1.30.105"   
    "10.1.30.105"   
    "10.1.30.105"   
    "10.1.30.105"   
    "10.1.30.105"   
    "10.1.30.105"   
    "10.1.30.105"   
}
