### Author: @floppy
### Description: 3d rotating polyhedra
### Category: Graphics
### License: MIT
### Appname : 3DSpin

import ugfx
import buttons
import math
from uos import listdir
from utime import sleep_ms
from imu import IMU
import gc       
import pyb
                
app_path = "apps/floppy~3dspin"
matrix = __import__(app_path + "/matrix")

# Rendering modes
BACKFACECULL = 1
FLAT = 2
WIREFRAME = 3

def loadObject(filename):
    global obj_vertices
    global obj_faces
    obj_vertices = []
    obj_faces = []
    f = open(app_path + "/" + filename)
    for line in f:
        if line[:2] == "v ":
            parts = line.split(" ")
            obj_vertices.append(
                matrix.Vector3D(
                    float(parts[1]),
                    float(parts[2]),
                    float(parts[3])
                )
            )
            gc.collect()
        elif line[:2] == "f ":
            parts = line.split(" ")
            face = []
            for part in parts[1:]:
                face.append(int(part.split("/",1)[0])-1)
            obj_faces.append(face)
            gc.collect()
    f.close()

def toScreenCoords(pv):
	px = int((pv.x+1)*0.5*320)
	py = int((1-(pv.y+1)*0.5)*240)
	return [px, py]

def createCameraMatrix(x,y,z):
    camera_transform = matrix.Matrix(4, 4)
    camera_transform.m[0][3] = x
    camera_transform.m[1][3] = y
    camera_transform.m[2][3] = z
    return camera_transform

def createProjectionMatrix(horizontal_fov, zfar, znear):
    s = 1/(math.tan(math.radians(horizontal_fov/2)))
    proj = matrix.Matrix(4, 4)
    proj.m[0][0] = s * (240/320) # inverse aspect ratio
    proj.m[1][1] = s
    proj.m[2][2] = -zfar/(zfar-znear)
    proj.m[3][2] = -1.0
    proj.m[2][3] = -(zfar*znear)/(zfar-znear)
    return proj

def createRotationMatrix(x_rotation, z_rotation):
    rot_x = matrix.Matrix(4,4)
    rot_x.m[1][1] = rot_x.m[2][2] = math.cos(x_rotation)
    rot_x.m[2][1] = math.sin(x_rotation)
    rot_x.m[1][2] = -rot_x.m[2][1]

    # rot_y = matrix.Matrix(4,4)
    # rot_y.m[0][0] = rot_y.m[2][2] = math.cos(y_rotation)
    # rot_y.m[0][2] = math.sin(y_rotation)
    # rot_y.m[2][0] = -rot_y.m[0][2]
    # 
    rot_z = matrix.Matrix(4,4)
    rot_z.m[0][0] = rot_z.m[1][1] = math.cos(z_rotation)
    rot_z.m[1][0] = math.sin(z_rotation)
    rot_z.m[0][1] = -rot_z.m[1][0]

    return rot_z * rot_x

def normal(face, vertices, normalize = True):
    # Work out the face normal for lighting
    normal = (vertices[face[1]]-vertices[face[0]]).cross(vertices[face[2]]-vertices[face[0]])
    if normalize == True:
        normal.normalize()
    return normal

def render(mode, rotation):
    # Rotate all the vertices in one go
    vertices = [rotation * vertex for vertex in obj_vertices]
    # Calculate normal for each face (for lighting)
    if mode == FLAT:
        face_normal_zs = [normal(face, vertices).z for face in obj_faces]
    # Project (with camera) all the vertices in one go as well
    vertices = [camera_projection * vertex for vertex in vertices]
    # Calculate projected normals for each face
    if mode != WIREFRAME:
        proj_normal_zs = [normal(face, vertices, False).z for face in obj_faces]
    # Convert to screen coordinates all at once
    # We could do this faster by only converting vertices that are
    # in faces that will be need rendered, but it's likely that test
    # would take longer.
    vertices = [toScreenCoords(v) for v in vertices]
    # Render the faces to the screen
    vsync()
    ugfx.clear(ugfx.BLACK)
    for index in range(len(obj_faces)):
        # Only render things facing towards us (unless we're in wireframe mode)
        if (mode == WIREFRAME) or (proj_normal_zs[index] > 0):
            # Convert polygon
            poly = [vertices[v] for v in obj_faces[index]]
            # Calculate colour and render
            ugcol = ugfx.WHITE
            if mode == FLAT:
                # Simple lighting calculation
                colour5 = int(face_normal_zs[index] * 31)
                colour6 = int(face_normal_zs[index] * 63)
                # Create a 5-6-5 grey
                ugcol = (colour5 << 11) | (colour6 << 5) | colour5
                # Render polygon        
                ugfx.fill_polygon(0,0, poly, ugcol)
            # Always draw the wireframe in the same colour to fill gaps left by the
            # fill_polygon method
            ugfx.polygon(0,0, poly, ugcol)
            	
def vsync():
    while(tear.value() == 0):
        pass
    while(tear.value()):
        pass

def calculateRotation(smoothing, accelerometer):
    # Keep a list of recent rotations to smooth things out
    global x_rotations
    global z_rotations
    # First, pop off the oldest rotation
    if len(x_rotations) >= smoothing:
        x_rotations = x_rotations[1:]
    if len(z_rotations) >= smoothing:
        z_rotations = z_rotations[1:]
    # Now append a new rotation
    pi_2 = math.pi / 2
    x_rotations.append(-accelerometer['z'] * pi_2)
    z_rotations.append(accelerometer['x'] * pi_2)
    # Calculate rotation matrix
    return createRotationMatrix(
        # this averaging isn't correct in the first <smoothing> frames, but who cares
        sum(x_rotations) / smoothing, 
        sum(z_rotations) / smoothing
    )        

# Initialise hardware
ugfx.init()
imu=IMU()
buttons.init()

# Enable tear detection for vsync
ugfx.enable_tear()
tear = pyb.Pin("TEAR", pyb.Pin.IN)
ugfx.set_tear_line(1)

# Set up static rendering matrices
camera_transform = createCameraMatrix(0, 0, -5.0)
proj = createProjectionMatrix(45.0, 100.0, 0.1)
camera_projection = proj * camera_transform

# Get the list of available objects, and load the first one
obj_vertices = []
obj_faces = []
objects = [x for x in listdir(app_path) if ((".obj" in x) & (x[0] != "."))]
selected = 0
loadObject(objects[selected])

# We'll track each axis separately
x_rotations = []
z_rotations = []
smoothing = 5

mode = BACKFACECULL

# Main loop
run = 1
while run:
    gc.collect()
    # Render the scene
    render(
        mode, 
        calculateRotation(smoothing, imu.get_acceleration())
    )
    # Button presses
    if buttons.is_pressed("BTN_B"):
        selected += 1
        if selected >= len(objects):
            selected = 0
        loadObject(objects[selected])
        sleep_ms(500) # Wait a while to avoid skipping ahead if the user still has the button down
    if buttons.is_pressed("BTN_A"):
        mode += 1
        if mode > 3:
            mode = 1
        sleep_ms(500) # Wait a while to avoid skipping ahead if the user still has the button down
    if buttons.is_pressed("BTN_MENU"):
        run = 0
