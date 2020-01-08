import urllib.request
import json
import random
import numpy as np



# bodys = [{'ID': "1", 'latitude': "40.794862", 'longitude': "-73.966423"},
#         {'ID': "2", 'latitude': "40.797990", 'longitude': "-73.959204"},
#         {'ID': "3", 'latitude': "40.803790", 'longitude': "-73.962098"},
#         {'ID': "4", 'latitude': "40.723721", 'longitude': "-73.999197"},
#         {'ID': "5", 'latitude': "40.764939", 'longitude': "-73.947335"},
#         {'ID': "6", 'latitude': "40.783256", 'longitude': "-73.953727"},
#         {'ID': "7", 'latitude': "40.803569", 'longitude': "-73.943383"},
#         {'ID': "8", 'latitude': "40.784356", 'longitude': "-73.976498"},
#         {'ID': "9", 'latitude': "40.768952", 'longitude': "-73.977770"},
#         {'ID': "10", 'latitude': "40.809368", 'longitude': "-73.959995"},
#         {'ID': "11", 'latitude': "40.806889", 'longitude': "-73.964007"}]
#
# for body in bodys:
#     myurl = "http://3.87.68.197:8099/sensornumber/insert"
#     req = urllib.request.Request(myurl)
#     req.add_header('Content-Type', 'application/json; charset=utf-8')
#     jsondata = json.dumps(body)
#     jsondataasbytes = jsondata.encode('utf-8')   # needs to be bytes
#     req.add_header('Content-Length', len(jsondataasbytes))
#     print (jsondataasbytes)
#     response = urllib.request.urlopen(req, jsondataasbytes)



mu_t = [10, 12, 11, 11, 13, 9, 9, 8, 10, 7, 23.2]
var_t = [0.5, 0.5, 0.4, 0.3, 0.5, 0.45, 0.2, 0.1, 0.3, 0.5, 0.5]
mu_h = [11, 16, 18, 17.5, 16.8, 17.3, 17.9, 20, 22, 19, 20.1]
var_h = [0.5, 0.5, 0.6, 0.4, 0.3, 0.2, 0.15, 0.2, 0.3, 0.5, 0.5]
mu_m = [0.5, 0.3, 0.35, 0.41, 0.47, 0.32, 0.44, 0.51, 0.60, 0.58, 0.60]
var_m = [0.02, 0.05, 0.03, 0.02, 0.01, 0.04, 0.02, 0.01, 0.04, 0.03, 0.02]

for id in range(11):

    tempreture = np.random.normal(mu_t[id], var_t[id], 200)
    humidity = np.random.normal(mu_h[id], var_h[id], 200)
    moisture = np.random.normal(mu_m[id], var_m[id], 200)

    tempreture = [round(tmp,2) for tmp in tempreture]
    humidity = [round(tmp, 2) for tmp in humidity]
    moisture = [round(tmp, 2) for tmp in moisture]


    bodys = [{"Datetime":(1576156200+i*10),"ID":"{}".format(id+1),"humidity":"{}".format(humidity[i]),"soil_moisture":"{}".format(moisture[i]),"temperature":"{}".format(tempreture[i])} for i in range(200)]
    for body in bodys:
        myurl = "http://3.87.68.197:8099/sensordata/post"
        req = urllib.request.Request(myurl)
        req.add_header('Content-Type', 'application/json; charset=utf-8')
        jsondata = json.dumps(body)
        jsondataasbytes = jsondata.encode('utf-8')   # needs to be bytes
        req.add_header('Content-Length', len(jsondataasbytes))
        print (jsondataasbytes)
        response = urllib.request.urlopen(req, jsondataasbytes)
