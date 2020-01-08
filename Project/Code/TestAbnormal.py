import urllib.request
import json

body = {"Datetime":(1576156200+10),"ID":"1","humidity":"17.00","soil_moisture":"50.00","temperature":"30.00"}
myurl = "http://3.87.68.197:8099/sensordata/post"
req = urllib.request.Request(myurl)
req.add_header('Content-Type', 'application/json; charset=utf-8')
jsondata = json.dumps(body)
jsondataasbytes = jsondata.encode('utf-8')   # needs to be bytes
req.add_header('Content-Length', len(jsondataasbytes))
print (jsondataasbytes)
response = urllib.request.urlopen(req, jsondataasbytes)