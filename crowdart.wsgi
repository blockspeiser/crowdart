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

	# response_body = response_body.replace('</body>', "%s</body>" % open(PATH + '/social.html', 'r').read())
	
	return response_body	

@route("/grids")
@route("/grids/")
def showAll():
	f = open(PATH + '/view_all.html', 'r')
	response_body = f.read()
	f.close()
	
	response_body = response_body.replace('branch = [];', "branch = %s;" % json.dumps(get_grid()["branches"]));
	# response_body = response_body.replace('</body>', "%s</body>" % open(PATH + '/social.html', 'r').read())

	return response_body


@route("/grids/view/:name")
def showOneGrid(name):
	f = open(PATH + '/view.html', 'r')
	response_body = f.read()
	f.close()

	response_body = response_body.replace('branches = []', "branches = %s" % json.dumps(get_grid(name)))
	response_body = response_body.replace('task = ""', 'task = "%s"' % name)
	# response_body = response_body.replace('</body>', "%s</body>" % open(PATH + '/social.html', 'r').read())

	return response_body		
	

@route("/grids/draw")	
@route("/grids/draw/")
def showDraw():
	f = open(PATH + '/draw.html', 'r')
	response_body = f.read()
	f.close()
	response_body = response_body.replace('"ASSIGNMENT"', json.dumps(assign_grid()))
	# response_body = response_body.replace('</body>', "%s</body>" % open(PATH + '/social.html', 'r').read())

	return response_body
	

@route("/grids/draw/:name")
def showOneDraw(name):
	f = open(PATH + '/draw.html', 'r')
	response_body = f.read()
	f.close()
	
	try:
		gridId = int(name)
		grid = get_grid(gridId)
	except ValueError:
		grid = assign_grid(name)
	response_body = response_body.replace('"ASSIGNMENT"', json.dumps(grid))
	# response_body = response_body.replace('</body>', "%s</body>" % open(PATH + '/social.html', 'r').read())

	return response_body


# ------------- API ----------------

@get("/api/grids/")
def gridListAPI():
	return get_grid()

	
@get("/api/grids/assign/")
def assign_gridAPI():
	return assign_grid()	


@get("/api/grids/new/:name")
def newGridAPI(name):
	return new_grid(name)


@get("/api/grids/branches/")
def branchesAPI():
	"""
	Return a list of branches without frames
	"""
	return {"branches": json.dumps(get_branches())}
	

@get("/api/grids/bits/")
def gridListBitsAPI():
	return get_grid()

@get("/api/grids/bits/:name")
def gridBitsAPI(name):
	try:
		gridId = int(name)
		return get_grid(gridId)
	except ValueError:
		return get_grid(name)
		

@get("/api/grids/id/:gridId")
def gridAPI(gridId):
	try:
		gridId = int(gridId)
		grid = get_grid(gridId)
		if not grid:
			return {"error": "No grid #%s" % gridId}
		grid["pixels"] = unpack_pixels(grid["pixels"])
		for i in range(len(grid["frames"])):
			grid["frames"][i] = unpack_pixels(grid["frames"][i])
		return grid
		
	except ValueError:
		return {"error": "Expected an integer ID, got %s" % gridId}

@post("/api/grids/")
def saveGridAPI():
	j = request.POST.get("json")
	if not j:
		return {"error": "No postdata."}
	return save_grid(json.loads(j))


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
