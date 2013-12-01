import csv
from PIL import Image

from crowdart import *


def export_grid_image(id):
	grid = db.gridbits.find_one({"id": id})
	if not grid:
		return False
	pixels = unpack_pixels(grid["pixels"])

	scale = 6

	def swap(c):
		return 0 if c else 1
	data = [swap(x) for row in pixels for x in row]

	im = Image.new("1", (50, 50))

	im.putdata(data)
	im = im.resize((50*scale, 50*scale))
	name = "export/%d-%s-%s.png" % (id, grid["task"], grid["branch"])
	im.save(name)


def export_all_images():
	grids = db.gridbits.find({})
	for grid in grids:
		if "visible" not in grid or grid["visible"]:
			export_grid_image(grid["id"])


def export_csv():
	writer = csv.writer(open("export/data.csv", 'w'))
	writer.writerow(["id", "task", "branch", "parent", "ip"])

	grids = db.gridbits.find({})
	for grid in grids:
		ip = grid["ip"] if "ip" in grid else "UNKNOWN"
		if "visible" not in grid or grid["visible"]:
			writer.writerow([int(grid["id"]), grid["task"], grid["branch"], grid["parent"], ip])

