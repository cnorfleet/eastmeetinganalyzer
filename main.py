from flask import Flask
from flask import render_template
import csv
from flask import request

from flask_bootstrap import Bootstrap

def create_app():
  a = Flask(__name__)
  Bootstrap(a)
  return a


app = create_app()

def load_data():
	data = []
	print("Loading initial data")
	with open('data.csv', 'rb') as csvfile:
		reader = csv.reader(csvfile, delimiter=',', quotechar='|')
		for row in reader:
			data += [row]
	return data

@app.route('/')
def main_page():
	meeting = 0
	if ('meeting' in request.args):
		meeting = int(request.args['meeting'])
	data = load_data()
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
					meme[-1] += int(row[i]) if row[i] != '' else 0
				else:
					real[-1] += int(row[i]) if row[i] != '' else 0
		else:
			real += [int(row[meeting*2-1]) if row[meeting*2-1] != '' else 0]
			meme += [int(row[meeting*2]) if row[meeting*2] != '' else 0]
	buttons = [[0, "All Meetings"]]
	for i in range(numMeetings):
		buttons += [[i+1, "Meeting "+str(i+1)]]
	return render_template('main.html', names=names, real=real, meme=meme, buttons=buttons, numButtons=numMeetings+1, meeting=meeting)


