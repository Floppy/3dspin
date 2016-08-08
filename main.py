### Author: @floppy
### Description: 3d rotating polyhedra
### Category: Graphics
### License: MIT
### Appname : 3D Spin

import ugfx
import buttons
import pyb
import matrix

ugfx.init()
buttons.init()
ugfx.clear(ugfx.BLACK)

viewport_x = 320
viewport_y = 240
aspect = viewport_x / viewport_y

cube = [
	Vector3D(-0.5,0.5,-0.5),
	Vector3D(0.5,0.5,-0.5),
	Vector3D(0.5,-0.5,-0.5),
	Vector3D(-0.5,-0.5,-0.5),
	Vector3D(-0.5,0.5,0.5),
	Vector3D(0.5,0.5,0.5),
	Vector3D(0.5,-0.5,0.5),
	Vector3D(-0.5,-0.5,0.5)
]
cubefaces = [(0,1,2,3),(1,5,6,2),(5,4,7,6),(4,0,3,7),(0,4,5,1),(3,2,6,7)] 

proj = Matrix(4, 4)	
rot = Matrix(4,4)

fov = 110.0
zfar = 100.0
znear = 0.1
s = 1/(math.tan(math.radians(fov/2)))
proj.m[0][0] = s
proj.m[1][1] = s
proj.m[2][2] = -zfar/(zfar-znear)
proj.m[3][2] = -1.0
proj.m[2][3] = -(zfar*znear)/(zfar-znear)

# def project(vector):    
#     return [
#         int(viewport_x/2) + (vector[0]*100),
#         int(viewport_y/2) + (vector[1]*100)
#     ]
# 
# for edge in cube_edges:
#     start = project(edge[0])
#     end = project(edge[1])
#     ugfx.line(start[0],
#               start[1],
#               end[0],
#               end[1],
#               ugfx.WHITE)
#     
def toScreenCoords(pv):
	px = ((pv.x+1)*0.5*viewport_x)
	py = ((1-(pv.y+1)*0.5)*viewport_y)
	return Vector3D(int(px), int(py), 1)

def render(y_rotation):
		
	rot.m[0][0] = math.cos(math.radians(y_rotation))
	rot.m[0][2] = math.sin(math.radians(y_rotation))
	rot.m[2][0] = -math.sin(math.radians(y_rotation))
	rot.m[2][2] = math.cos(math.radians(y_rotation))

	ugfx.clear(ugfx.BLACK)
	for i in range(len(cubefaces)):
		poly = [] #transformed polygon
		for j in range(len(cubefaces[0])):
			v = cube[cubefaces[i][j]]
			# Rotate 
			r = rot*v
			# Transform the point from 3D to 2D
			ps = proj*r
			# Put the screenpoint in the list of transformed vertices
			p = toScreenCoords(ps)
			x = int(p.x)
			y = int(p.y)
			poly.append([x, y])
			
		# Render polygon
	 	ugfx.polygon(0,0, poly, ugfx.WHITE) 
		
y_rotation = 0
while not buttons.is_pressed("BTN_MENU"):
	render(y_rotation)
	y_rotation += 1
	if y_rotation >= 360:
		y_rotation = 0