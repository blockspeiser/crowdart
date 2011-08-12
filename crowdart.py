#!/usr/bin/python

import sys
import pymongo
import cgi
import simplejson
from os import getenv 
from datetime import datetime

connection = pymongo.Connection()
db = connection.crowdart
grids = db.grids


def getGrid(name=None):
	"""
	Take a name (which can be an id, task, or branch id) 
	
	Return a dictionary or array dictionaries of matching grids
	"""
		
	response = {}

	# name is an ID - return single grid
	if isinstance(name, int): 
		grid = db.gridbits.find_one({"id": name})
		if not grid:
			return None
		del grid["_id"]
		frames = getFrames(name)
		if frames:
			grid["frames"] = frames
			
		return grid
	else:		
		# name is a task - return all matching
		if isinstance(name, str):
			findMap = {"children": 0, "task": name}
		# no name - return all branches
		else:
			findMap = {"children": 0, "visible": {"$ne": 0}}
		cursor = db.gridbits.find(findMap).sort([["_id", -1]])
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
	
	return response

def getBranches(task=None):
	"""
	Returns an array of terminal nodes (excluding pixels)
	"""
	
	branches = []
	
	# Find all visible grids with 0 children
	if task:
		findMap = {"children": 0, "task": task}
	else:
		findMap = {"children": 0, "visible": {"$ne": 0}}
		
	cursor = db.gridbits.find(findMap).sort([["_id", -1]])
	for i in range(cursor.count()):
		branch = cursor[i]
		del branch["pixels"]
		del branch["_id"]
		branches.append(branch)
	
	
	return branches

def getFrames(gridId):
	"""
	Take a grid ID and return an array of all preceding frames.
	"""
	
	frame = db.gridbits.find_one({"id": gridId})
	frames = []
	while frame:
		frames.insert(0, frame["pixels"])
		frame = db.gridbits.find_one({"id": frame["parent"]})
	
	return frames

def assignGrid(task=None):
		
	findMap = {"children": 0, "active": {"$ne": 0}}
	if task:
		findMap["task"] = task
	else:
		findMap["visible"] = {"$ne": 0}
	
	cursor = db.gridbits.find(findMap).sort([["lastAssigned", 1]]).limit(1)
		
	if cursor.count(): 
		next = cursor.next()
		next["lastAssigned"] = datetime.now().isoformat();
		db.gridbits.save(next)
		del next["_id"]

	else:
		next = {"error": "No active drawings found."}
	
	return next


def saveGrid(grid):
	
	for key in ("parent", "pixels"):
		if not key in grid:
			return {"error": "%s not set." % (key)}
	
	# Give it an ID
	lastId = db.gridbits.find().sort([['id', -1]]).limit(1)
	grid["id"] = lastId.next()["id"] + 1
	
	grid["children"] = 0
	grid["active"] = 1
	grid["pixels"] = packPixels(grid["pixels"])
	grid["lastAssigned"] = datetime.now().isoformat()
	
	ipaddr = (getenv("HTTP_CLIENT_IP") or getenv("HTTP_X_FORWARDED_FOR") or getenv("HTTP_X_FORWARDED_FOR") or getenv("REMOTE_ADDR") or "UNKNOWN")
	grid["ip"] = ipaddr
	
	
	parent = db.gridbits.find_one({"id": grid["parent"]})
	
	if not parent:
		grid["branch"] = 0
		grid["depth"] = 1
		if not "visible" in grid:
			grid["visible"] = 1
		
	else:	
		parent["children"] = parent["children"] + 1
		grid["depth"] = parent["depth"] + 1
		if parent["children"] == 1:
			grid["branch"] = parent["branch"]
		else:
			grid["branch"] = "%d.%d" % (parent["branch"], parent["children"]) 
		if "active" in parent:
			grid["active"] = parent["active"]
		if "visible" in parent:
			grid["visible"] = parent["visible"]
	
	
	if parent:
		db.gridbits.save(parent)
		
	db.gridbits.insert(grid)

	return ({"result": {"id": grid["id"]}})

def newGrid(name):

	grid  = {
		"task": name,
		"parent": 0,
		"branch": 0,
	}
	
	p = {}
	for i in range(50):
		p[str(i)] = []
		for k in range(50):
			p[str(i)].append(0)
	
	grid["pixels"] = p
	
	return saveGrid(grid)

def packPixels(pixels):
	
	bits = []
	
	for row in sorted(pixels.keys(), key=int):
	
		rowBits = ""
		
		for i in pixels[row]:
			rowBits += "1" if i == 1 else "0"
		dec = int("1" + rowBits,2)	
		
		bits.append(dec)		
	
	return bits

def unpackPixels(bitsArray):

	pixelsArray = []
	
	for i in range(len(bitsArray)):
		bitsString = baseN(bitsArray[i],2)[1:]
		pixels = []
		while(bitsString): 
			bit =  bitsString[0]			
			pixels.append(1 if bit == "1" else 0)
			bitsString = bitsString[1:]
		
		for k in range(len(pixels),50):
			pixels.append(0)
				
		pixelsArray.append(pixels)

	return pixelsArray

def baseN(num,b):
  return ((num == 0) and  "0" ) or ( baseN(num // b, b).lstrip("0") + "0123456789abcdefghijklmnopqrstuvwxyz"[num % b])	
		
def makeBits():
	
	grids = db.grids.find()
	db.gridbits.remove()
	grid = grids.next()
	
	while grid:
		del grid["_id"]
		try:
			grid["pixels"] = packPixels(grid["pixels"])
		except KeyError:
			print "No pixels in grid %d" % (grid["id"])
		db.gridbits.save(grid)
		grid = grids.next()
	