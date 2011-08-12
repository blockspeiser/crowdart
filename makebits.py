from crowdart import *

db.gridbits.remove()

cursor = db.grids.find()
next = cursor.next()

while next:
	if "id" in next:
		next["pixels"] = packPixels(next["pixels"])
		del next["_id"]
		db.gridbits.save(next)
	next = cursor.next()