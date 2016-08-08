### Author: @floppy
### Description: 3d rotating polyhedra
### Category: Graphics
### License: MIT
### Appname : 3D Spin

import ugfx
import buttons
import pyb
import math
import ure
import uos

app_path = "apps/3dspin/"
matrix = __import__(app_path + "matrix")
            
ugfx.init()
buttons.init()
ugfx.clear(ugfx.BLACK)

vertices = []
faces = []

viewport_x = 320
viewport_y = 240

proj = matrix.Matrix(4, 4)	

fov = 130.0
zfar = 100.0
znear = 0.1
s = 1/(math.tan(math.radians(fov/2)))
proj.m[0][0] = s
proj.m[1][1] = s
proj.m[2][2] = -zfar/(zfar-znear)
proj.m[3][2] = -1.0
proj.m[2][3] = -(zfar*znear)/(zfar-znear)

def loadObject(filename):
    global vertices
    global faces
    vertices = []
    faces = []
    path = app_path + "models/"+filename
    f = open(path)
    for line in f:
        if line[:2] == "v ":
            parts = line.split(" ")
            vertices.append(
                matrix.Vector3D(
                    float(parts[1]),
                    float(parts[2]),
                    float(parts[3])
                )
            )
        elif line[:2] == "f ":
            parts = line.split(" ")
            face = []
            for part in parts[1:]:
                face.append(int(part.split("/",1)[0])-1)
            faces.append(face)
    f.close()

def toScreenCoords(pv):
	px = ((pv.x+1)*0.5*viewport_x)
	py = ((1-(pv.y+1)*0.5)*viewport_y)
	return matrix.Vector3D(int(px), int(py), 1)

def render(x_rotation, y_rotation, z_rotation):

    rot_x = matrix.Matrix(4,4)
    rot_x.m[1][1] = math.cos(math.radians(x_rotation))
    rot_x.m[1][2] = -math.sin(math.radians(x_rotation))
    rot_x.m[2][1] = math.sin(math.radians(x_rotation))
    rot_x.m[2][2] = math.cos(math.radians(x_rotation))

    rot_y = matrix.Matrix(4,4)
    rot_y.m[0][0] = math.cos(math.radians(y_rotation))
    rot_y.m[0][2] = math.sin(math.radians(y_rotation))
    rot_y.m[2][0] = -math.sin(math.radians(y_rotation))
    rot_y.m[2][2] = math.cos(math.radians(y_rotation))

    rot_z = matrix.Matrix(4,4)
    rot_z.m[0][0] = math.cos(math.radians(z_rotation))
    rot_z.m[0][1] = -math.sin(math.radians(z_rotation))
    rot_z.m[1][0] = math.sin(math.radians(z_rotation))
    rot_z.m[1][1] = math.cos(math.radians(z_rotation))

    rot = rot_x * rot_y * rot_z

    polys = []
    for i in range(len(faces)):
    	poly = [] #transformed polygon
    	for j in range(len(faces[0])):
    		v = vertices[faces[i][j]]
    		# Rotate 
    		r = rot*v
    		# Transform the point from 3D to 2D
    		ps = proj*r
    		# Put the screenpoint in the list of transformed vertices
    		p = toScreenCoords(ps)
    		x = int(p.x)
    		y = int(p.y)
    		poly.append([x, y])
    	polys.append(poly)

    # Render
    ugfx.clear(ugfx.BLACK)
    for poly in polys:	
    	# Render polygon
     	ugfx.polygon(0,0, poly, ugfx.WHITE) 
		
objects = uos.listdir(app_path+"models")
selected = 0
loadObject(objects[selected])
x_rotation = 0
y_rotation = 0
z_rotation = 0
while not buttons.is_pressed("BTN_MENU"):
    render(x_rotation, y_rotation, z_rotation)
    x_rotation += 1
    if x_rotation >= 360:
        x_rotation = 0
    y_rotation += 2
    if y_rotation >= 360:
        y_rotation = 0
    z_rotation += 3
    if z_rotation >= 360:
        z_rotation = 0
    if buttons.is_pressed("BTN_B"):
        selected += 1
        if selected >= len(objects):
            selected = 0
        loadObject(objects[selected])
    if buttons.is_pressed("BTN_A"):
        selected -= 1
        if selected < 0:
            selected =  len(objects) - 1
        loadObject(objects[selected])