#!/usr/bin/python

import sys
sys.path.insert(0, "/home5/brettloc/lib/python/")
sys.path.insert(0, '/home5/brettloc/lib/python/pymongo-1.9-py2.4-linux-x86_64.egg')
sys.path.insert(0, '/home5/brettloc/lib/python/simplejson-2.0.9-py2.4-linux-x86_64.egg')
import pymongo
import cgi
from os import getenv 
import simplejson
from datetime import datetime

form = cgi.FieldStorage()
j = simplejson.loads(form["json"].value)


connection = pymongo.Connection()
db = connection.crowdart
grids = db.grids


lastId = grids.find().sort([['id', -1]]).limit(1)
j["id"] = lastId.next()["id"] + 1

j["children"] = 0
j["active"] = 1
j["lastAssigned"] = datetime.now().isoformat()

ipaddr = (getenv("HTTP_CLIENT_IP") or getenv("HTTP_X_FORWARDED_FOR") or getenv("HTTP_X_FORWARDED_FOR") or getenv("REMOTE_ADDR") or "UNKNOWN")
j["ip"] = ipaddr


parent = grids.find_one({"id": j["parent"]})

if not parent:
	j["branch"] = 0
	j["depth"] = 1
	if not "visible" in j:
		j["visible"] = 1
	
else:	
	parent["children"] = parent["children"] + 1
	j["depth"] = parent["depth"] + 1
	if parent["children"] == 1:
		j["branch"] = parent["branch"]
	else:
		j["branch"] = "%d.%d" % (parent["branch"], parent["children"]) 
	if "active" in parent:
		j["active"] = parent["active"]
	if "visible" in parent:
		j["visible"] = parent["visible"]

	
grids.insert(j)
if parent:
	grids.save(parent)

print "Content-type: application/json\n\n"
print simplejson.dumps({"result": {"id": j["id"]}})

