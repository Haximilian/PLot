import flask
import json

import scheduler

app = flask.Flask(__name__)

# todo:
# add metrics for schedule / solve method
# remove time global variable
# update schedule endpoint to be post method
# update js in schedule.htm to get length dynamically
# stress test schedule endpoint
time = [0, 10, 20, 30, 40, 50]

@app.route('/schedule')
def schedule():
    file = open('./mock-data/user-input1.mock')
    constraints = json.loads(file.read())
    content = scheduler.solve(constraints, time)
    return content

@app.route('/requests')
def requests():
    file = open('./mock-data/user-input0.mock')
    content = file.read()
    return json.loads(content)

@app.route('/<path:path>')
def send_report(path):
    return flask.send_from_directory('static', path)

app.run(host='localhost', port='8080')