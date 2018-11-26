from flask import Flask
from flask import render_template
import csv
from flask import request
from flask import jsonify
import math
import os

from flask_bootstrap import Bootstrap

def create_app():
  a = Flask(__name__)
  Bootstrap(a)
  return a


app = create_app()

def load_data():
	filename = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'data.csv')
	data = []
	with open(filename, 'r') as csvfile:
		reader = csv.reader(csvfile, delimiter=',', quotechar='|')
		next(reader, None) # skip header
		for row in reader:
			data += [[row[0]]+[int(x) if x != "" else 0 for x in row[1:]]]
	return data

@app.route('/')
def main_page():
	data = load_data()
	numMeetings = int((len(data[0])-1)/2)
	buttons = [[0, "All Meetings"]]
	for i in range(numMeetings):
		buttons += [[i+1, "Meeting "+str(i+1)]]
	json = get_main_data(data, 0)
	return render_template('main.html', data=json, buttons=buttons, numButtons=numMeetings+1, numpeople=len(json['names']))

@app.route('/individual')
def individual_page():
	data = load_data()
	names = []
	for row in data:
		names += [row[0]]
	return render_template('individual.html', names=names, nummeetings=(len(data[0])-1)/2, numPeople=len(names), methods=methods)

@app.route('/person')
def get_person_data():
	if ('person' in request.args):
		person = int(request.args['person'])
		if ('metric' in request.args):
			metric = int(request.args['metric'])
			data = load_data()
			json = {}
			json['values'], json['ranks'] = getValuesAndRanks(data, person, metric)
			json['meetings'] = ["Meeting "+str(i+1) for i in range(len(json['values']))]
			json['min'] = methods[metric][4]
			json['max'] = methods[metric][5]
			return jsonify(json)

@app.route('/all')
def reload_main_data():
	meeting = 0
	if ('meeting' in request.args):
		meeting = int(request.args['meeting'])
	data = load_data()
	return jsonify(get_main_data(data, meeting))

def get_main_data(data, meeting=0):
	names = []
	real = []
	meme = []
	numMeetings = 0
	for row in data:
		names += [row[0]]
		if ((len(row)-1)/2 > numMeetings):
			numMeetings = (len(row)-1)/2
		if (meeting == 0):
			meme += [0]
			real += [0]
			for i in range(1, len(row)):
				if i%2 == 0:
					meme[-1] -= int(row[i]) if row[i] != '' else 0
				else:
					real[-1] += int(row[i]) if row[i] != '' else 0
		else:
			real += [int(row[meeting*2-1]) if row[meeting*2-1] != '' else 0]
			meme += [-1*int(row[meeting*2]) if row[meeting*2] != '' else 0]
	json = {}
	json['names'] = names
	json['real'] = real
	json['meme'] = meme
	return json

def binom(x, y, p):
	score = math.factorial(x+y)/math.factorial(y)/math.factorial(x)
	score *= math.pow(p, x)
	score *= math.pow(p, y)
	return score
def balance(x, y):
	if x+y <= 0: return 0
	raw = int(math.log((x+y)*binom(x, y, 0.5))*100)
	return math.copysign(math.log(abs(raw)), raw) if raw != 0 else 0

methods = [
	(0, "Total Comments", "The total number of comments made", lambda x, y: x+y, 0, 150),
	(1, "Real Comments", "The total number of real comments made", lambda x, y: x, 0, 100),
	(2, "Meme Comments", "The total number of meme comments made", lambda x, y: y, 0, 100),
	(3, "Productivity", "The productivity, weighted by total comments", lambda x, y: (x-y)*abs(x-y)/(x+y+1), -100, 100),
	(4, "Meme-ness", "The memeosity, weighted by total comments", lambda x, y: (y-x)*abs(x-y)/(x+y+1), -100, 100),
	(5, "Balance", "How perfectly balanced, as all things should be", balance, -10, 10),
	(6, "Productive Purity", "Percentage of comments which are productive", lambda x, y: int(x/(x+y+1e-100)*100), 0, 100),
	(7, "Mematic Purity", "Percentage of comments which are memes", lambda x, y: int(y/(x+y+1e-100)*100), 0, 100),

]

@app.route('/leaderboard')
def leaderboard_page():
	method = 0
	if ('method' in request.args):
		method = int(request.args['method'])
	data = load_data()
	names = []
	real = []
	meme = []
	numMeetings = 0
	for row in data:
		names += [row[0]]
		meme += [0]
		real += [0]
		for i in range(1, len(row)):
			if i%2 == 0:
				meme[-1] += int(row[i]) if row[i] != '' else 0
			else:
				real[-1] += int(row[i]) if row[i] != '' else 0
	table = []
	for i in range(len(names)):
		table += [[i+1, names[i], methods[method][3](real[i], meme[i]), real[i], meme[i]]]
	table.sort(key = lambda x: (x[2], x[3]+x[4]), reverse=True)
	for i in range(len(names)):
		table[i][0] = i+1
	return render_template('leaderboard.html', table=table, methods=methods, numButtons=len(methods), method=method)

@app.route('/about')
def about_page():
	return render_template('about.html')


def generateMetricTable(data, metric):
	table = []
	for person in data:
		row = [person[0]]
		for week in range(int((len(person)-1)/2)):
			score = 0
			if (person[2*week+1] + person[2*week+2] > 0):
				score = methods[metric][3](person[2*week+1], person[2*week+2])
			row += [score]
		table += [row]
	return table


def getValuesAndRanks(data, person, metric):
	name = data[person][0]
	data = sorted(data, key= lambda x: sum(x[1:]))
	metricTable = generateMetricTable(data, metric)
	values = next(x for x in metricTable if x[0] == name)[1:]
	ranks = []
	for week in range(1, len(metricTable[0])):
		table = sorted(metricTable, key = lambda x: x[week], reverse=True)
		ranks += [next(i for i in range(len(table)) if table[i][0] == name)+1]
	return values, ranks

