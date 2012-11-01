import sys
import os
PATH = os.path.dirname(__file__)
sys.path.insert(0, PATH)
import simplejson as json
from bottlez import *
from crowdart import *


# --------------- APP ---------------

@route("/")
def home():
	f = open(PATH + '/home.html', 'r')
	response_body = f.read()
	f.close()

	response_body = response_body.replace('</body>', "%s</body>" % open(PATH + '/social.html', 'r').read())
	
	return response_body	

@route("/grids")
@route("/grids/")
@route("/grids/view")
@route("/grids/view/")
@route("/grids/view.html")
def showGrids():
	f = open(PATH + '/view.html', 'r')
	response_body = f.read()
	f.close()

	response_body = response_body.replace('branches = []', "branches = %s" % json.dumps(getGrid()))
	response_body = response_body.replace('</body>', "%s</body>" % open(PATH + '/social.html', 'r').read())

	return response_body		
	

@route("/grids/view/all")
def showAll():
	f = open(PATH + '/view_all.html', 'r')
	response_body = f.read()
	f.close()
	
	response_body = response_body.replace('branch = [];', "branch = %s;" % json.dumps(getGrid()["branches"]));

	return response_body


@route("/grids/view/:name")
def showOneGrid(name):
	f = open(PATH + '/view.html', 'r')
	response_body = f.read()
	f.close()

	response_body = response_body.replace('branches = []', "branches = %s" % json.dumps(getGrid(name)))
	response_body = response_body.replace('task = ""', 'task = "%s"' % name)
	response_body = response_body.replace('</body>', "%s</body>" % open(PATH + '/social.html', 'r').read())

	return response_body		
	

@route("/grids/draw")	
@route("/grids/draw/")
@route("/grids/draw.html")
def showDraw():
	f = open(PATH + '/draw.html', 'r')
	response_body = f.read()
	f.close()
	response_body = response_body.replace('"ASSIGNMENT"', json.dumps(assignGrid()))
	response_body = response_body.replace('</body>', "%s</body>" % open(PATH + '/social.html', 'r').read())

	return response_body
	

@route("/grids/draw/:name")
def showOneDraw(name):
	f = open(PATH + '/draw.html', 'r')
	response_body = f.read()
	f.close()
	
	try:
		gridId = int(name)
		grid = getGrid(gridId)
	except ValueError:
		grid = assignGrid(name)
	response_body = response_body.replace('"ASSIGNMENT"', json.dumps(grid))
	response_body = response_body.replace('</body>', "%s</body>" % open(PATH + '/social.html', 'r').read())

	return response_body


# ------------- API ----------------

@get("/api/grids/")
def gridListAPI():
	return getGrid()

	
@get("/api/grids/assign/")
def assignGridAPI():
	return assignGrid()	


@get("/api/grids/new/:name")
def newGridAPI(name):
	return newGrid(name)


@get("/api/grids/branches/")
def branchesAPI():
	"""
	Return a list of branches without frames
	"""
	return {"branches": json.dumps(getBranches())}
	

@get("/api/grids/bits/")
def gridListBitsAPI():
	return getGrid()

@get("/api/grids/bits/:name")
def gridBitsAPI(name):
	try:
		gridId = int(name)
		return getGrid(gridId)
	except ValueError:
		return getGrid(name)
		

@get("/api/grids/id/:gridId")
def gridAPI(gridId):
	try:
		gridId = int(gridId)
		grid = getGrid(gridId)
		if not grid:
			return {"error": "No grid #%s" % gridId}
		grid["pixels"] = unpackPixels(grid["pixels"])
		for i in range(len(grid["frames"])):
			grid["frames"][i] = unpackPixels(grid["frames"][i])
		return grid
		
	except ValueError:
		return {"error": "Expected an integer ID, got %s" % gridId}

@post("/api/grids/")
def saveGridAPI():
	j = request.POST.get("json")
	if not j:
		return {"error": "No postdata."}
	return saveGrid(json.loads(j))


@get("/api/grids/deactivate/:gridId")
def deactivateAPI(gridId):
	grid = db.gridbits.find_one({"id": int(gridId)})
	grid["active"] = 0
	db.gridbits.save(grid)
	del grid["_id"]
	return grid


@get("/api/grids/activate/:gridId")
def deactivateAPI(gridId):
	grid = db.gridbits.find_one({"id": int(gridId)})
	grid["active"] = 1
	db.gridbits.save(grid)
	del grid["_id"]
	return grid


# ----------- ERROR ------------------

@error(404)
def error404(error):
    return 'Nothing here, sorry'


application = default_app()
