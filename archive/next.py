#!/usr/bin/python

import sys
sys.path.insert(0, "/home5/brettloc/lib/python/")
sys.path.insert(0, '/home5/brettloc/lib/python/pymongo-1.9-py2.4-linux-x86_64.egg')
sys.path.insert(0, '/home5/brettloc/lib/python/simplejson-2.0.9-py2.4-linux-x86_64.egg')
import pymongo
import cgi
import simplejson
from datetime import datetime

connection = pymongo.Connection()
db = connection.crowdart
grids = db.grids

form = cgi.FieldStorage()

findMap = {"children": 0, "active": {"$ne": 0}}
if "task" in form:
	findMap["task"] = form["task"].value
else:
	findMap["visible"] = {"$ne": 0}

cursor = grids.find(findMap).sort([["lastAssigned", 1]]).limit(1)

next = {}

if cursor.count(): 
	nextDoc = cursor.next()
	next["pixels"] = nextDoc["pixels"]
	next["id"] = nextDoc["id"]
	next["task"] = nextDoc["task"]
	if "active" in nextDoc:
		 next["active"] = nextDoc["active"] 
	if "visible" in nextDoc:
		 next["visible"] = nextDoc["visible"]
	nextDoc["lastAssigned"] = datetime.now().isoformat();
	grids.save(nextDoc)
elif "task" in form: 
	next["task"] = form["task"].value
	next["id"] = 0
	next["pixels"] = []
	if "visible" in form:
		next["visible"] = int(form["visible"].value)
	else: 
		next["visible"] = 0
else:
	next["error"] = "No active drawings found."


print "Content-type: application/json\n\n"
print simplejson.dumps(next)
