from flask import Flask
from flask import render_template
import csv
from flask import request
from flask import jsonify
import math

from flask_bootstrap import Bootstrap

def create_app():
  a = Flask(__name__)
  Bootstrap(a)
  return a


app = create_app()

def load_data():
	data = []
	with open('data.csv', 'rb') as csvfile:
		reader = csv.reader(csvfile, delimiter=',', quotechar='|')
		for row in reader:
			data += [row]
	return data

@app.route('/')
def main_page():
	data = load_data()
	numMeetings = (len(data[0])-1)/2
	buttons = [[0, "All Meetings"]]
	for i in range(numMeetings):
		buttons += [[i+1, "Meeting "+str(i+1)]]
	json = get_main_data(data, 0)
	return render_template('main.html', data=json, buttons=buttons, numButtons=numMeetings+1)

@app.route('/individual')
def individual_page():
	data = load_data()
	names = []
	for row in data[1:]:
		names += [row[0]]
	return render_template('individual.html', names=names)

@app.route('/person')
def get_person_data():
	if ('person' in request.args):
		person = int(request.args['person'])
		data = load_data()
		row = data[person+1]
		real = []
		meme = []
		for i in range(1, len(row)):
			if i%2 == 0:
				meme += [-1*int(row[i]) if row[i] != '' else 0]
			else:
				real += [int(row[i]) if row[i] != '' else 0] 
		meetings = ["Meeting "+str(i+1) for i in range(len(meme))]
		json = {}
		json['meetings'] = meetings
		json['real'] = real
		json['meme'] = meme
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
	for row in data[1:]:
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

methods = [
	(0, "Most Comments", "The total number of comments made", lambda x, y: x+y),
	(1, "Real Comments", "The total number of real comments made", lambda x, y: x),
	(2, "Meme Comments", "The total number of meme comments made", lambda x, y: y),
	(3, "Most Productive", "The productivity, weighted by total comments", lambda x, y: (x-y)*abs(x-y)/(x+y+1)),
	(4, "Most Memey", "The memeosity, weighted by total comments", lambda x, y: (y-x)*abs(x-y)/(x+y+1)),
	(5, "Most Balanced", "How perfectly balanced, as all things should be", lambda x, y: (x+y)*binom(x, y, 0.5)),
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
	for row in data[1:]:
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
	table.sort(key = lambda(x): x[2], reverse=True)
	for i in range(len(names)):
		table[i][0] = i+1
	return render_template('leaderboard.html', table=table, methods=methods, numButtons=len(methods), method=method)

@app.route('/about')
def about_page():
	return render_template('about.html')
