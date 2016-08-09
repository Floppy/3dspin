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

app_path = "apps/floppy~3dspin"
matrix = __import__(app_path + "/matrix")

# Rendering modes
BACKFACECULL = 1
FLAT = 2
WIREFRAME = 3

def loadObject(filename):
    global vertices
    global faces
    vertices = []
    faces = []
    path = app_path + "/" + filename
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

    return rot_x * rot_z

def render(mode, rotation):
    polys = []
    for face in faces:
        # Transform face
        poly = []
        for vertex_index in face:
            v = vertices[vertex_index]
            # Rotate 
            v = rotation * v
            # Camera Translation + Projection in one go
            poly.append(camera_projection * v)
        # Work out the face normal for backface culling
        normal = (poly[1]-poly[0]).cross(poly[2]-poly[0])
        # Only render things facing towards us (unless we're in wireframe mode)
        if (normal.z > 0) | (mode == WIREFRAME):
            # Convert to screen coordinates
            screenpoly = [toScreenCoords(p) for p in poly]
            # Store transformed polygon for final rendering,
            # and normal for lighting calculation
            polys.append([screenpoly, normal.z])

    # Render the transformed polygons to the screen.
    # We're doing all the maths, keeping transformed
    # copies of the object faces, and then rendering after
    # This reduces tearing, but doubles the memory requirements for
    # the object as we make a copy of the object every frame.
    # (only half if backface culling).
    vsync()
    ugfx.clear(ugfx.BLACK)
    for poly in polys:
        if mode == FLAT:
            # Rubbish lighting calculation
            colour = int(min(poly[1], 1.0) * 255)
            ugcol = ugfx.html_color((colour << 16) | (colour << 8) | colour)
            # Render polygon        
            ugfx.fill_polygon(0,0, poly[0], ugcol)
        else:
            ugfx.polygon(0,0, poly[0], ugfx.WHITE)
	
def vsync():
    while(tear.value() == 0):
        pass
    while(tear.value()):
        pass
    
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
vertices = []
faces = []
objects = [x for x in listdir(app_path) if ((".obj" in x) & (x[0] != "."))]
selected = 0
loadObject(objects[selected])

# We'll track each axis separately
x_rotation = 0
z_rotation = 0
pi_2 = math.pi / 2

mode = BACKFACECULL

# Main loop
run = 1
while run:
    # Update rotation matrix and render the scene
    rotation = createRotationMatrix(x_rotation, z_rotation)
    render(mode, rotation)
    # Handle the various inputs
    accel = imu.get_acceleration()
    x_rotation = -accel['z'] * pi_2
    z_rotation = accel['x'] * pi_2
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
