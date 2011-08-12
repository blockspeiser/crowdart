#!/usr/bin/python

import sys
sys.path.insert(0, "/home5/brettloc/lib/python/")
sys.path.insert(0, '/home5/brettloc/lib/python/pymongo-1.9-py2.4-linux-x86_64.egg')
sys.path.insert(0, '/home5/brettloc/lib/python/simplejson-2.0.9-py2.4-linux-x86_64.egg')
import pymongo
import cgi
import simplejson

connection = pymongo.Connection()
db = connection.crowdart
grids = db.grids

form = cgi.FieldStorage()

response = {}

if "id" in form:
	response["frames"] = []
	frame = grids.find_one({"id": int(form["id"].value)})
	if frame:
		response["task"] = frame["task"]
		response["branch"] = frame["branch"]
		response["depth"] = frame["depth"]
	while frame:
		response["frames"].insert(0, frame["pixels"])
		frame = grids.find_one({"id": frame["parent"]})
		
	
else:
	if "task" in form:
		findMap = {"children": 0, "task": form["task"].value}
	else:
		findMap = {"children": 0, "visible": {"$ne": 0}}
	cursor = grids.find(findMap).sort([["_id", -1]])
	response["branches"] = []
	for i in range(cursor.count()):
		nextDoc = cursor[i]
		branch = {}
		branch["id"] = nextDoc["id"]
		branch["task"] = nextDoc["task"]
		branch["branch"] = nextDoc["branch"]
		branch["depth"] = nextDoc["depth"]
		branch["pixels"] = nextDoc["pixels"]
		response["branches"].append(branch)

	


print "Content-type: application/json\n\n"
print simplejson.dumps(response)
