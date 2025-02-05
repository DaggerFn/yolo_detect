import numpy as np

camera_urls = [
    #"rtsp://admin:fabrica1@192.168.0.131:554/1/2",  # Indice 0/1
    #"rtsp://admin:fabrica1@192.168.0.132:554/1/2",  # Indice 0/2
    #"rtsp://admin:fabrica1@192.168.0.133:554/1/2",  # Indice 0/3
    #"rtsp://admin:fabrica1@192.168.0.134:554/1/2",  # Indice 0/4
    #"rtsp://admin:fabrica1@192.168.0.135:554/1/2",  # Indice 0/5
    #"rtsp://admin:fabrica1@192.168.0.136:554/1/2",  # Indice 0/6
    #"http://10.1.60.185:4000/video_raw0",
    #"http://10.1.60.185:4000/video_raw1",
    #"http://10.1.60.185:4000/video_raw2",
    #"http://10.1.60.185:4000/video_raw3",
    "http://10.1.60.185:4000/video_raw4",
    #"http://10.1.60.185:4000/video_raw5",
]


rois = [
    #Posto1
    #{'points': np.array([[290, 120], [440, 120], [445, 275], [290, 275]], dtype=np.int32), 'color': (255, 0, 0)},
    
    #Posto2
    #{'points': np.array([[351, 115], [480, 115], [480, 320], [351, 320]], dtype=np.int32), 'color': (255, 0, 0)},
    
    #Posto3
    #{'points': np.array([[420, 115], [480, 115], [480, 320], [420, 320]], dtype=np.int32), 'color': (255, 0, 0)},
    
    #Posto 4# 
    #{'points': np.array([[420, 115], [480, 115], [480, 320], [420, 320]], dtype=np.int32), 'color': (255, 0, 0)},
    
    #Posot 5                 R           G           B           Y
    {'points': np.array([[420, 50], [480, 50], [480, 230], [420, 230]], dtype=np.int32), 'color': (255, 0, 0)},
    
    #Posto 6
    #{'points': np.array([[330, 135], [370, 150], [370, 270], [330, 285]], dtype=np.int32), 'color': (255, 0, 0)},
]


roi_points_worker = [
    #Posto 1
    #{'point': np.array([[0, 115], [300, 115], [315, 320], [0, 320]], dtype=np.int32), 'color': (255, 0, 0)},
    
    #Posto 2
    #{'point': np.array([[0, 100], [450, 100], [450, 300], [0, 300]], dtype=np.int32), 'color': (255, 0, 0)},
    
    #Posto 3
    #{'point': np.array([[30, 105], [410, 90], [410, 320], [30, 320]], dtype=np.int32), 'color': (255, 0, 0)},
    
    #Posto 4
    #{'point': np.array([[0, 142], [450, 115], [450, 320], [0, 320]], dtype=np.int32), 'color': (255, 0, 0)},
    
    #Posto 5
    {'point': np.array([[0, 50], [450, 50], [450, 230], [0, 230]], dtype=np.int32), 'color': (255, 0, 0)},
    
    #Posto 6
    #{'point': np.array([[90, 227], [330, 140], [370, 320], [160, 320]], dtype=np.int32), 'color': (0, 255, 0)},
]

