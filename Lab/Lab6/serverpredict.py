# Created by Chenye Yang, Haokai Zhao, Zhuoyue Xing on 2019/10/26.
# Copyright © 2019 Chenye Yang, Haokai Zhao, Zhuoyue Xing . All rights reserved.

from pymongo import MongoClient
import pickle


client = MongoClient(host='localhost', port=27017)
db = client.coordinates
collection = db.predict

x_list = []
y_dic = {1:'C', 2:'O', 3:'L', 4:'U', 5:'M', 6:'B', 7:'I', 8:'A'}
latest = collection.find().sort([('_id', -1)]).limit(20)
for i in range(19,-1,-1):
	# x_list.extend([item['x1'], item['x2'], item['y1'], item['y2'], item['z1'], item['z2']])
	x_list.extend([latest[i]['x1']/255, latest[i]['x2']/255, latest[i]['y1']/255, latest[i]['y2']/255, latest[i]['z1']/255, latest[i]['z2']/255])


# load model and do predict
filename = 'finalized_model_6axis.sav'
loaded_model = pickle.load(open(filename, 'rb'))
result = loaded_model.predict([x_list])
print(y_dic[result[0]])


