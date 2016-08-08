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
import utime
from imu import IMU

app_path = "apps/floppy~3dspin/"
matrix = __import__(app_path + "matrix")
            
ugfx.init()
imu=IMU()
buttons.init()

vertices = []
faces = []

proj = matrix.Matrix(4, 4)	

camera_transform = matrix.Matrix(4, 4)
camera_transform.m[0][3] = 0
camera_transform.m[1][3] = 0
camera_transform.m[2][3] = -5

fov = 45.0
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
	px = ((pv.x+1)*0.5*ugfx.width())
	py = ((1-(pv.y+1)*0.5)*ugfx.height())
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
        # Transform face
    	poly = []
    	for j in range(len(faces[i])):
            v = vertices[faces[i][j]]
            # Rotate 
            p = rot*v
            # Camera Translation
            p = camera_transform * p
            # Project
            p = proj*p
            # Store
            poly.append(p)
        # Convert to screen coordinates
        screen_poly = []
        for p in poly:
            # Put the screenpoint in the list of transformed vertices
            sp = toScreenCoords(p)
            screen_poly.append([int(sp.x), int(sp.y)])
        # Work out the face normal for backface culling
        normal = (poly[1]-poly[0]).cross(poly[2]-poly[0])
        # Only render things facing towards us
    	if normal.z > 0:
            polys.append([screen_poly, normal])

    # Render
    ugfx.clear(ugfx.BLACK)
    ugfx.text(0,0, objects[selected], ugfx.GREEN)
    for poly in polys:	
        # Render polygon        
        ugfx.polygon(0,0, poly[0], ugfx.WHITE) 
		
objects = [x for x in uos.listdir(app_path+"models") if x[0] != '.']
selected = 0
loadObject(objects[selected])
x_rotation = 0
y_rotation = 0
z_rotation = 0
while not buttons.is_pressed("BTN_MENU"):
    render(x_rotation, y_rotation, z_rotation)
    accel = imu.get_acceleration()    
    x_rotation += accel['z']*10
    if x_rotation >= 360:
        x_rotation = 0
    y_rotation += accel['x']*10
    if y_rotation >= 360:
        y_rotation = 0
    z_rotation -= accel['x']*10
    if z_rotation >= 360:
        z_rotation = 0
    if buttons.is_pressed("BTN_B"):
        selected += 1
        if selected >= len(objects):
            selected = 0
        loadObject(objects[selected])
        utime.sleep_ms(500) # Wait a while to avoid skipping ahead if the user still has the button down
    if buttons.is_pressed("BTN_A"):
        selected -= 1
        if selected < 0:
            selected =  len(objects) - 1
        loadObject(objects[selected])
        utime.sleep_ms(500) # Wait a while to avoid skipping ahead if the user still has the button down
