# Created by Chenye Yang, Haokai Zhao, Zhuoyue Xing on 2019/10/26.
# Copyright © 2019 Chenye Yang, Haokai Zhao, Zhuoyue Xing . All rights reserved.

from sklearn import svm

import requests, json
import pickle
url = 'http://3.87.68.197:8099/get'
r = requests.get(url)
co = json.loads(r.text)['result']
lablelen=100
x1=[]
x2=[]
x3=[]
x4=[]
x5=[]
x6=[]
x7=[]
x8=[]
y1=[]
y2=[]
y3=[]
y4=[]
y5=[]
y6=[]
y7=[]
y8=[]
x_list=[]
y_list=[]
for i in range(1,lablelen+1):
	for labeldict in co:
		if (labeldict['label'] is'C' and labeldict['ID'] ==i):
			temc = [labeldict['x1']/255, labeldict['x2']/255, labeldict['y1']/255, labeldict['y2']/255, labeldict['z1']/255, labeldict['z2']/255]
			x1.extend(temc)
			y1.append(labeldict['label'])
	x_list.append(x1)
	y_list.append(1)
	x1=[]
	y1=[]
#2
for i in range(1,lablelen+1):
	for labeldict in co:
		if (labeldict['label'] is 'O' and labeldict['ID'] == i):
			temo = [labeldict['x1']/255, labeldict['x2']/255, labeldict['y1']/255, labeldict['y2']/255, labeldict['z1']/255, labeldict['z2']/255]
			x2.extend(temo)
			y2.append(labeldict['label'])
	x_list.append(x2)
	y_list.append(2)
	x2=[]
	y2=[]
#3
for i in range(1,lablelen+1):
	for labeldict in co:
		if (labeldict['label'] is 'L' and labeldict['ID'] == i):
			teml = [labeldict['x1']/255, labeldict['x2']/255, labeldict['y1']/255, labeldict['y2']/255, labeldict['z1']/255, labeldict['z2']/255]
			x3.extend(teml)
			y3.append(labeldict['label'])
	x_list.append(x3)
	y_list.append(3)
	x3=[]
	y3=[]
#4
for i in range(1,lablelen+1):
	for labeldict in co:
		if (labeldict['label'] is 'U' and labeldict['ID'] == i):
			temu = [labeldict['x1']/255, labeldict['x2']/255, labeldict['y1']/255, labeldict['y2']/255, labeldict['z1']/255, labeldict['z2']/255]
			x4.extend(temu)
			y4.append(labeldict['label'])
	x_list.append(x4)
	y_list.append(4)
	x4=[]
	y4=[]
#5
for i in range(1,lablelen+1):
	for labeldict in co:
		if (labeldict['label'] is 'M' and labeldict['ID'] == i):
			temm = [labeldict['x1']/255, labeldict['x2']/255, labeldict['y1']/255, labeldict['y2']/255, labeldict['z1']/255, labeldict['z2']/255]
			x5.extend(temm)
			y5.append(labeldict['label'])
	x_list.append(x5)
	y_list.append(5)
	x5=[]
	y5=[]
#6
for i in range(1,lablelen+1):
	for labeldict in co:
		if (labeldict['label'] is 'B' and labeldict['ID'] == i):
			temb = [labeldict['x1']/255, labeldict['x2']/255, labeldict['y1']/255, labeldict['y2']/255, labeldict['z1']/255, labeldict['z2']/255]
			x6.extend(temb)
			y6.append(labeldict['label'])
	x_list.append(x6)
	y_list.append(6)
	x6=[]
	y6=[]
#7
for i in range(1,lablelen+1):
	for labeldict in co:
		if (labeldict['label'] is 'I' and labeldict['ID'] == i):
			temi = [labeldict['x1']/255, labeldict['x2']/255, labeldict['y1']/255, labeldict['y2']/255, labeldict['z1']/255, labeldict['z2']/255]
			x7.extend(temi)
			y7.append(labeldict['label'])
	x_list.append(x7)
	y_list.append(7)
	x7=[]
	y7=[]
#8
for i in range(1,lablelen+1):
	for labeldict in co:
		if (labeldict['label'] is 'A' and labeldict['ID'] == i):
			tema = [labeldict['x1']/255, labeldict['x2']/255, labeldict['y1']/255, labeldict['y2']/255, labeldict['z1']/255, labeldict['z2']/255]
			x8.extend(tema)
			y8.append(labeldict['label'])
	x_list.append(x8)
	y_list.append(8)
	x8=[]
	y8=[]

clf = svm.SVC(gamma='scale', decision_function_shape='ovo', kernel='poly', degree=3)
clf.fit(x_list,y_list)
result = clf.score(x_list,y_list)
print(result)

filename = 'finalized_model_6axis.sav'
pickle.dump(clf, open(filename, 'wb'))
