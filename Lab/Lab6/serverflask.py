# Created by Chenye Yang, Haokai Zhao, Zhuoyue Xing on 2019/10/26.
# Copyright © 2019 Chenye Yang, Haokai Zhao, Zhuoyue Xing . All rights reserved.

from flask import Flask, render_template
from flask import jsonify
from flask import request
from flask_pymongo import PyMongo
import json
import pickle

app = Flask(__name__)

app.config['MONGO_DBNAME']= 'coordinates'
app.config['MONGO_URI']= 'mongodb://localhost:27017/coordinates'
# put name of database at the end of URL
mongo = PyMongo(app)
_host = "0.0.0.0"
_port = 8099
# If the output port is different for the port above, it does not matter, the port output is the real port this program runs on.

@app.route('/post', methods=['POST'])
def add_coordinate():   
	label = "C"
	ID = 0
	seq = 0
	x1 = 0
	x2 = 0
	y1 = 0
	y2 = 0
	z1 = 0
	z2 = 0
	coordinate= mongo.db.coordinates
	
	label = request.json["label"]
	ID = request.json["ID"]
	seq = request.json["seq"]
	x1 = request.json["x1"]
	x2 = request.json["x2"]
	y1 = request.json["y1"]
	y2 = request.json["y2"]
	z1 = request.json["z1"]
	z2 = request.json["z2"]
	
	data = {'label': label, 'ID': ID, 'seq': seq, 'x1': x1, 'x2': x2, 'y1': y1, 'y2': y2, 'z1': z1, 'z2': z2}

	coordinate.insert(data)
	new_coordinate=coordinate.find_one({'label': label} and {'ID': ID} and {'seq': seq} and {'x1': x1} and {'x2': x2} and {'y1': y1} and {'y2': y2} and {'z1': z1} and {'z2': z2})
	output = {'label': new_coordinate['label'], 'ID':new_coordinate['ID'], 'seq':new_coordinate['seq'], 'x1':new_coordinate['x1'], 'x2':new_coordinate['x2'], 'y1':new_coordinate['y1'], 'y2':new_coordinate['y2'], 'z1':new_coordinate['z1'], 'z2':new_coordinate['z2'] }                 
	return jsonify({'result':output})


@app.route('/predict/post', methods=['POST'])
def add_predict_coordinate():   
	label = "NA"
	ID = 0
	seq = 0
	x1 = 0
	x2 = 0
	y1 = 0
	y2 = 0
	z1 = 0
	z2 = 0
	prd = mongo.db.predict
	
	label = request.json["label"]
	ID = request.json["ID"]
	seq = request.json["seq"]
	x1 = request.json["x1"]
	x2 = request.json["x2"]
	y1 = request.json["y1"]
	y2 = request.json["y2"]
	z1 = request.json["z1"]
	z2 = request.json["z2"]
	
	data = {'label': label, 'ID': ID, 'seq': seq, 'x1': x1, 'x2': x2, 'y1': y1, 'y2': y2, 'z1': z1, 'z2': z2}
	prd.insert(data)

	new_prd=prd.find_one({'label': label} and {'ID': ID} and {'seq': seq} and {'x1': x1} and {'x2': x2} and {'y1': y1} and {'y2': y2} and {'z1': z1} and {'z2': z2})
	output = {'label': new_prd['label'], 'ID':new_prd['ID'], 'seq':new_prd['seq'], 'x1':new_prd['x1'], 'x2':new_prd['x2'], 'y1':new_prd['y1'], 'y2':new_prd['y2'], 'z1':new_prd['z1'], 'z2':new_prd['z2'] }

	return jsonify({'result':output})


@app.route('/predict/order/post', methods=['POST'])
def do_predict():   
	prd = mongo.db.predict

	x_list = []
	y_dic = {1:'C', 2:'O', 3:'L', 4:'U', 5:'M', 6:'B', 7:'I', 8:'A'}
	latest = prd.find().sort([('_id', -1)]).limit(20)
	for i in range(19,-1,-1):
		# x_list.extend([item['x1'], item['x2'], item['y1'], item['y2'], item['z1'], item['z2']])
		x_list.extend([latest[i]['x1']/255, latest[i]['x2']/255, latest[i]['y1']/255, latest[i]['y2']/255, latest[i]['z1']/255, latest[i]['z2']/255])


	# load model and do predict
	filename = 'finalized_model_6axis.sav'
	loaded_model = pickle.load(open(filename, 'rb'))
	result = loaded_model.predict([x_list])
	# print(y_dic[result[0]])

	return jsonify({'result':y_dic[result[0]]})


@app.route('/get', methods=['GET'])
def get_coordinate():
	coordinate = mongo.db.coordinates
	output = []
	for c in coordinate.find():
		output.append({'label': c['label'], 'ID': c['ID'], 'seq': c['seq'], 'x1': c['x1'], 'x2': c['x2'], 'y1': c['y1'], 'y2': c['y2'], 'z1': c['z1'], 'z2': c['z2']})
	return jsonify({'result' : output})


@app.route('/predict/get', methods=['GET'])
def get_predict_coordinate():
	prd = mongo.db.predict
	output = []
	for c in prd.find():
		output.append({'label': c['label'], 'ID': c['ID'], 'seq': c['seq'], 'x1': c['x1'], 'x2': c['x2'], 'y1': c['y1'], 'y2': c['y2'], 'z1': c['z1'], 'z2': c['z2']})
	return jsonify({'result' : output})

if __name__== '__main__':
	app.run(debug=True, host=_host, port=_port)



