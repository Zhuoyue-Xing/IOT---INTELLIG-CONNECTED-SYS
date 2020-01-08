# Created by Chenye Yang, Haokai Zhao, Zhuoyue Xing on 2019/10/26.
# Copyright  2019 Chenye Yang, Haokai Zhao, Zhuoyue Xing . All rights reserved.

from flask import Flask, render_template,Response
from flask import jsonify
from flask import request,send_from_directory
from flask_pymongo import PyMongo
import json
import pickle
import requests
import csv
import os
import time
from flask_cors import CORS
import smtplib
from email.mime.text import MIMEText

gmail_user = 'iot2019temp@gmail.com'
gmail_password = 'aleoxwrprndhangm' # your gmail password
app = Flask(__name__)
CORS(app)
app.config['MONGO_DBNAME']= 'project'
app.config['MONGO_URI']= 'mongodb://localhost:27017/coordinates'
# put name of database at the end of URL
mongo = PyMongo(app)
_host = "0.0.0.0"
_port = 8099
# If the output port is different for the port above, it does not matter, the port output is the real port this program runs on.


@app.route('/sensornumber/getall', methods=['GET'])
def get_all():
	location = mongo.db.sensornumber
	output = []
	for c in location.find():
		output.append({'ID': c['ID'],'longitude':c['longitude'],'latitude':c['latitude']})
	return jsonify({'result' : output})

@app.route('/sensornumber/get/<ID>', methods=['GET'])
def get_by_sensornumber(ID):
	result = None
	output = []
	try:
		if request.method == 'GET':
			location = mongo.db.sensornumber
			q = {"ID": ID}
			for c in location.find(q):
							output.append({'ID': c['ID'],'longitude':c['longitude'],'latitude':c['latitude']})
			return jsonify({'result': output})
		else:
			result = "Invalid request."
			return result, 400, {'Content-Type': 'text/plain; charset=utf-8'}
	except Exception as e:
		print(e)
		return handle_error(e, result)

@app.route('/sensornumber/delete/<ID>', methods=['DELETE'])
def delete_by_sensornumber(ID):
	result = None
	try:
		if request.method == 'DELETE':
			location = mongo.db.sensornumber
			q = {"ID": ID}
			location.delete_one(q)
			res = "Delete successfully"
			rsp = Response(json.dumps(res), status=200, content_type="application/json")
			return rsp
		else:
			result = "Invalid request."
			return result, 400, {'Content-Type': 'text/plain; charset=utf-8'}
	except Exception as e:
		print(e)
		return handle_error(e, result)

@app.route('/sensordata/deleteall', methods=['DELETE'])
def delete_sensordata_all():
	result = None
	try:
		if request.method == 'DELETE':
			location = mongo.db.sensordata
			location.remove({})
			res = "Delete all successfully"
			rsp = Response(json.dumps(res), status=200, content_type="application/json")
			return rsp
		else:
			result = "Invalid request."
			return result, 400, {'Content-Type': 'text/plain; charset=utf-8'}
	except Exception as e:
		print(e)
		return handle_error(e, result)

@app.route('/sensornumber/update/<ID>', methods=['POST'])
def update_by_sensornumber(ID):
	result=None
	try:
		if request.method == 'POST':
			data = None
			try:
				if request.data is not None:
					data = request.json
				else:
					data = None
			except Exception as e:
				# This would fail the request in a more real solution.
				data = "You sent something but I could not get JSON out of it."
			location = mongo.db.sensornumber
			q = {"ID": ID}
			newvalue={"$set":data}
			location.update_one(q,newvalue)
			res ="Update Successfully"
			rsp = Response(json.dumps(res), status=200, content_type="application/json")
			return rsp
		else:
			result = "Invalid request."
			return result, 400, {'Content-Type': 'text/plain; charset=utf-8'}
	except Exception as e:
		print(e)
		return handle_error(e, result)

@app.route('/sensornumber/insert', methods=['POST'])
def insert_by_sensornumber():
	result = None
	try:
		if request.method == 'POST':
			data = None
			try:
				if request.data is not None:
					data = request.json
				else:
					data = None
			except Exception as e:
				# This would fail the request in a more real solution.
				data = "You sent something but I could not get JSON out of it."
			location = mongo.db.sensornumber

			location.insert_one(data)
			res = "Insert successfully"
			rsp = Response(json.dumps(res), status=200, content_type="application/json")
			return rsp
		else:
			result = "Invalid request."
			return result, 400, {'Content-Type': 'text/plain; charset=utf-8'}
	except Exception as e:
		print(e)
		return handle_error(e, result)

@app.route('/sensordata/getall', methods=['GET'])
def get_all_sensordata():
	sensordata = mongo.db.sensordata
	output = []
	for c in sensordata.find():
		output.append({'Datetime': c['Datetime'], 'ID': c['ID'],  'temperature': c['temperature'], 'soil_moisture': c['soil_moisture'], 'humidity': c['humidity']})
	return jsonify({'result' : output})

def timestamp_datetime(value):
	format = '%Y-%m-%d %H:%M:%S'
	value = time.localtime(value)
	dt = time.strftime(format, value)
	return dt


@app.route('/sensordata/post', methods=['POST'])
def add_sensordata():
	ID = None
	datetime=None
	temperature=None
	soil_moisture=None
	humidity=None
	dataresource= mongo.db.sensordata
	gaptime=10
	
	ID = request.json["ID"]
	datetime = timestamp_datetime(request.json["Datetime"])
	temperature = request.json["temperature"]
	soil_moisture= request.json["soil_moisture"]
	humidity = request.json["humidity"]

	location = mongo.db.sensornumber
	ID_str=[]
	q = {"ID": ID}
	for c in location.find(q):
		ID_str.append({'longitude': c['longitude'], 'latitude': c['latitude']})
	tr_temperature = float(temperature)
	tr_soil_moisture= float(soil_moisture)
	tr_humidity = float(humidity)
	for c in dataresource.find(q).sort([('Datetime', -1)]).limit(int(1)):    
		tmp_ID=c['ID']
		tmp_Datetime=timestamp_datetime(datetime_timestamp(c['Datetime'])+int(gaptime))
	url = 'http://3.87.68.197:8099/sensordata/get/'+ID+'/10'
	r = requests.get(url)
	co = json.loads(r.text)['result']
	H=[]
	S=[]
	T=[]
	for item in co:
		H.append(float(item.get('humidity')))
		S.append(float(item.get('soil_moisture')))
		T.append(float(item.get('temperature')))
	
	tmp_tempe = float(sum(T)/10)
	tmp_hum=float(sum(H)/10)
	tmp_soilmoi=float(sum(S)/10)
	try:
		if (abs(tr_temperature-tmp_tempe)/abs(tmp_tempe))>0.2:
			msg = MIMEText('Alert: A sensor node collect abnormal temperature data\nTime: {}\nNode number: {}\nNode location: {}\nAbnormal data: Temperature: {}\n'.format(datetime,ID,ID_str,temperature))
			msg['Subject'] = 'Alert: A sensor node collect abnormal data'
			msg['From'] = gmail_user
			msg['To'] = 'iot2019temp@gmail.com'

			server = smtplib.SMTP_SSL('smtp.gmail.com', 465)
			server.ehlo()
			server.login(gmail_user, gmail_password)
			server.send_message(msg)
			server.quit()

			print('Email sent!')
	except ZeroDivisionError:
		print("ZeroDivisionError")
	
	try:
		if (abs(tr_humidity-tmp_hum)/abs(tmp_hum))>0.2:
			msg = MIMEText('Alert: A sensor node collect abnormal humidity data\nTime: {}\nNode number: {}\nNode location: {}\nAbnormal data: Humidty {}\n'.format(datetime,ID,ID_str,humidity))
			msg['Subject'] = 'Alert: A sensor node collect abnormal data'
			msg['From'] = gmail_user
			msg['To'] = 'iot2019temp@gmail.com'

			server = smtplib.SMTP_SSL('smtp.gmail.com', 465)
			server.ehlo()
			server.login(gmail_user, gmail_password)
			server.send_message(msg)
			server.quit()

			print('Email sent!')
	except ZeroDivisionError:
		print("ZeroDivisionError")

	try:
		if (abs(tr_soil_moisture-tmp_soilmoi)/abs(tmp_soilmoi))>0.2:
			msg = MIMEText('Alert: A sensor node collect abnormal soil moisture data\nTime:{}\nNode number:{}\nNode location:{}\nAbnormal data: Soil moisture :{}\n'.format(datetime,ID,ID_str,soil_moisture))
			msg['Subject'] = 'Alert: A sensor node collect abnormal data'
			msg['From'] = gmail_user
			msg['To'] = 'iot2019temp@gmail.com'

			server = smtplib.SMTP_SSL('smtp.gmail.com', 465)
			server.ehlo()
			server.login(gmail_user, gmail_password)
			server.send_message(msg)
			server.quit()

			print('Email sent!')
	except ZeroDivisionError:
		print("ZeroDivisionError")
	data = {'Datetime': datetime, 'ID': ID, 'temperature': temperature, 'soil_moisture': soil_moisture, 'humidity': humidity}
	dataresource.insert(data)
	res = "Post data Successfully"
	rsp = Response(json.dumps(res), status=200, content_type="application/json")
	return rsp

@app.route('/sensordata/get/recent/<n>', methods=['GET'])
def get_n_sensordata(n):
	sensordata  = mongo.db.sensordata
	output = []
	for c in sensordata.find().sort([('Datetime', -1)]).limit(int(n)):
		output.append({'Datetime': c['Datetime'], 'ID': c['ID'],  'temperature': c['temperature'], 'soil_moisture': c['soil_moisture'], 'humidity': c['humidity']})
	return jsonify({'result' : output})

@app.route('/sensordata/get/<ID>', methods=['GET'])
def get_ID_sensordata(ID):
	sensordata  = mongo.db.sensordata
	output = []
	q = {"ID": ID}
	for c in sensordata.find(q):
		output.append({'Datetime': c['Datetime'], 'ID': c['ID'],  'temperature': c['temperature'], 'soil_moisture': c['soil_moisture'], 'humidity': c['humidity']})
	return jsonify({'result' : output})

@app.route('/sensordata/get/<ID>/<n>', methods=['GET'])
def get_ID_n_sensordata(ID,n):
	sensordata  = mongo.db.sensordata
	output = []
	q = {"ID": ID}
	for c in sensordata.find(q).sort([('Datetime', -1)]).limit(int(n)):
		output.append({'Datetime': c['Datetime'], 'ID': c['ID'],  'temperature': c['temperature'], 'soil_moisture': c['soil_moisture'], 'humidity': c['humidity']})
	return jsonify({'result' : output})

def datetime_timestamp(dt):
	time.strptime(dt, '%Y-%m-%d %H:%M:%S')
	s = time.mktime(time.strptime(dt, '%Y-%m-%d %H:%M:%S'))
	return int(s)


@app.route('/sensordata/get/predict/<ID>/<n>/<gaptime>', methods=['GET'])
def get_predict_ID_n_sensordata(ID,n,gaptime):
	sensordata  = mongo.db.sensordata
	output = []
	tmp_ID=str(ID)
	tmp_Datetime = 0
	q = {"ID": ID}
	for c in sensordata.find(q).sort([('Datetime', -1)]).limit(int(n)):
		output.append({'Datetime': c['Datetime'], 'ID': c['ID'], 'temperature': c['temperature'], 'soil_moisture': c['soil_moisture'], 'humidity': c['humidity']})
	for c in sensordata.find(q).sort([('Datetime', -1)]).limit(int(1)):    
		tmp_ID=c['ID']
		tmp_Datetime=timestamp_datetime(datetime_timestamp(c['Datetime'])+int(gaptime))
	url = 'http://3.87.68.197:8099/sensordata/get/'+tmp_ID+'/10'
	r = requests.get(url)
	co = json.loads(r.text)['result']
	H=[]
	S=[]
	T=[]
	for item in co:
		H.append(float(item.get('humidity')))
		S.append(float(item.get('soil_moisture')))
		T.append(float(item.get('temperature')))
	tmp_temp=str(sum(T)/10)
	tmp_hum=str(sum(H)/10)
	tmp_soilmoi=str(sum(S)/10)
	output.append({"Predict":{'Datetime': tmp_Datetime, 'ID': tmp_ID,  'temperature': tmp_temp, 'soil_moisture': tmp_soilmoi, 'humidity': tmp_hum}})
	return jsonify({'result' : output})




@app.route('/sensordata/delete/<ID>', methods=['DELETE'])
def delete_sensordata_by_ID(ID):
	result = None
	try:
		if request.method == 'DELETE':
			location = mongo.db.sensordata
			q = {"ID": ID}
			location.delete_many(q)
			res = "Delete successfully"
			rsp = Response(json.dumps(res), status=200, content_type="application/json")
			return rsp
		else:
			result = "Invalid request."
			return result, 400, {'Content-Type': 'text/plain; charset=utf-8'}
	except Exception as e:
		print(e)
		return handle_error(e, result)

@app.route('/sensordata/delete/<datatime>/<ID>', methods=['DELETE'])
def delete_sensordata_by_time_ID(datatime,ID):
	result = None
	try:
		if request.method == 'DELETE':
			location = mongo.db.sensordata
			q = {"ID": ID, 'Datetime':datatime}
			location.delete_many(q)
			res = "Delete successfully"
			rsp = Response(json.dumps(res), status=200, content_type="application/json")
			return rsp
		else:
			result = "Invalid request."
			return result, 400, {'Content-Type': 'text/plain; charset=utf-8'}
	except Exception as e:
		print(e)
		return handle_error(e, result)

@app.route("/download/<path:filename>")
def downloader(filename):
	if filename=="allsensordata.csv":
		sensordata = mongo.db.sensordata
		output = []
		for c in sensordata.find():
			output.append({'Datetime': c['Datetime'], 'ID': c['ID'], 'temperature': c['temperature'],
						   'soil_moisture': c['soil_moisture'], 'humidity': c['humidity']})
		with open(filename, 'w') as f:
			w = csv.writer(f)
			fieldnames = output[0].keys()  # solve the problem to automatically write the header
			w.writerow(fieldnames)
			for row in output:
				w.writerow(row.values())
		dirpath = os.path.join(app.root_path, '')
		return send_from_directory(dirpath, filename, as_attachment=True)
	else:
		res="Not found"
		rsp = Response(json.dumps(res), status=404, content_type="application/json")
		return rsp

@app.route('/sensordata/getbytime/<starttime>/<endtime>', methods=['GET'])
def get_all_by_time_sensordata(starttime,endtime):
	sensordata  = mongo.db.sensordata
	output = []
	q={'Datetime': {'$gte': starttime,'$lte': endtime}}
	for c in sensordata.find(q):
		output.append({'Datetime': c['Datetime'], 'ID': c['ID'],  'temperature': c['temperature'], 'soil_moisture': c['soil_moisture'], 'humidity': c['humidity']})
	return jsonify({'result' : output})	

@app.route('/sensordata/getbytimeid/<starttime>/<endtime>/<ID>', methods=['GET'])
def get_all_by_timeid_sensordata(starttime,endtime,ID):
	sensordata  = mongo.db.sensordata
	output = []
	q={'Datetime': {'$gte': starttime,'$lte': endtime},"ID": ID}
	for c in sensordata.find(q):
		output.append({'Datetime': c['Datetime'], 'ID': c['ID'],  'temperature': c['temperature'], 'soil_moisture': c['soil_moisture'], 'humidity': c['humidity']})
	return jsonify({'result' : output})

def handle_error(e, result):
	return "Internal error.", 504, {'Content-Type': 'text/plain; charset=utf-8'}

if __name__== '__main__':
	app.run(debug=True, host=_host, port=_port)




