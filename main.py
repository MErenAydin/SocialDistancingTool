import cv2
import sdl2
import ctypes
import argparse
import moderngl
import numpy as np
from pyrr import Matrix44, Quaternion, Vector3, Vector4
import pyrr
from time import time

from GUI import Transform, Model, Mesh, Camera, Light, Viewport, Manager, Button,\
	 Texture, TextTexture, Gizmo, Settings
from GUI.Window import context, window
from Processor import Processor

from scipy.spatial import distance as dist


# argparser used for taking input video
ap = argparse.ArgumentParser()
ap.add_argument("-i", "--input", type=str, default="")
args = vars(ap.parse_args())

# settings import
settings = Settings()
width = settings.width
height = settings.height

# setting window width and height
context.viewport = (0, 0, width, height)

# empty object initializing method
def empty(empty_list, transform):
    # Returns numpy array of vertices of empty object which shows axis
    empty_list.append(Model(Mesh(np.array([[1.0,0.0,0.0],[-1.0,0.0,0.0],[0.0,1.0,0.0],[0.0,-1.0,0.0],[0.0,0.0,1.0],[0.0,0.0,-1.0]])), transform.copy()))

def grid(size, steps):
	# Returns numpy array of vertices of square grid which has given size and steps
	u = np.repeat(np.linspace(-size, size, steps), 2)
	v = np.tile([-size, size], steps)
	w = np.zeros(steps * 2)
	return np.concatenate([np.dstack([u, v, w])[:][:][0], np.dstack([v, u, w])[:][:][0]])

# screen manager 
manager = Manager()
viewport = Viewport(manager)

# taking video stream from camera or input video
vs = cv2.VideoCapture(args["input"] if args["input"] else 0)

# list of all cylinders
mesh_list = []
# list of all empties
empty_list = []


# initialization of grid object
grid = Model(Mesh(grid(5.0,11)), color = (0,0,0,1))

# camera and light settings
init_camera_pos = Vector3(settings.camera_pos)
origin = (0.0,0.0,0.0)
camera = Camera(init_camera_pos, origin)
light = Light(Vector3([10,-10,10]))

# OpenGL texture display 
frame_texture = Button((0,0), (width, height), "Frame", viewport)

# processor object for detecting people
prc = Processor()
# frame count
f = 0
# time interval variable for frequency calculating
last_time = time()

running = True
while running:
    # read the frame from video stream
    (grabbed, frame) = vs.read()
    if not grabbed:
        break
    # increase frame count and print frame count and FPS to console
    f += 1
    interval = time() - last_time
    last_time = time()
    #print("frame: {}\tFPS: {:.2f}        ".format(f, 1 / interval), end="\r")

    # resize frame as window size for true calculation
    frame = cv2.resize(frame, (width,height))

    # detect people inside the frame and return (probability, bounding box, centroid, ground point)
    results = prc.detect_people(frame)

    # get all ground points
    ground_points = [item[3] for item in results]
    
    # Up vector
    normal = Vector3([0.0,0.0,1.0])
    # create ground plane
    plane = pyrr.plane.create_from_position(position = Vector3([0.0,0.0,0.0]), normal = normal)

    # calculate all the groundpoints real world coordinates according to camera
    world_coordinates = [camera.ray_cast(camera.screen_to_world_coordinates(point) - camera.pos, plane) for point in ground_points]

    # set of social distance violating people indices
    violate = set()

    # if there are more than 2 detected people in frame
    if len(results) >= 2:
        # calculate all the distances between all people in the frame
        world_coordinates = np.array(world_coordinates)
        D = dist.cdist(world_coordinates, world_coordinates, metric="euclidean")
        for i in range(0, D.shape[0]):
            for j in range(i + 1, D.shape[1]):
                # if detected people violates the distance threshold add them to violate set 
                if D[i, j] < settings.min_distance_m:
                    violate.add(i)
                    violate.add(j)

    for (i, (prob, bbox, centroid, ground)) in enumerate(results):
        (startX, startY, endX, endY) = bbox
        (cX, cY) = centroid
        (gX, gY) = ground
        color_rgba = (0, 1, 0, settings.obj_alpha)
        color_bgr = (0, 255, 0)
        # if the index pair exists within the violation set, then update the color
        if i in violate:
            color_rgba = (1, 0, 0, settings.obj_alpha)
            color_bgr = (0, 0, 255)
        

        if settings.render_empty:
            if len(empty_list) < len(world_coordinates):
                for _ in range(len(world_coordinates) - len(empty_list)):
                    empty(empty_list, Transform([-1000.0,-1000.0,100.0]))

            elif len(empty_list) > len(world_coordinates):
                for _ in range(len(empty_list) - len(world_coordinates)):
                    empty_list.pop(1)

            if i < len(world_coordinates):
                empty_list[i].transform = Transform(world_coordinates[i])
            else:
                empty_list[i].transform = Transform([-1000.0,-1000.0,100.0])

        # if cylinders not rendering, just use cv2 rectangle
        if not settings.render_cylinder:
            cv2.rectangle(frame, (startX, startY), (endX, endY), color_bgr, 2)

        else:
            # generate mesh if necessary
            if len(mesh_list) < len(world_coordinates):
                for _ in range(len(world_coordinates) - len(mesh_list)):
                    mesh_list.append(Model(Mesh.from_file(settings.init_obj_path), Transform([-1000.0,-1000.0,100.0]), color = color_rgba))

            elif len(mesh_list) > len(world_coordinates):
                for _ in range(len(mesh_list) - len(world_coordinates)):
                    mesh_list.pop(1)
            
            if i < len(world_coordinates):
                mesh_list[i].transform = Transform(world_coordinates[i])
            else:
                mesh_list[i].transform = Transform([-1000.0,-1000.0,100.0])
            mesh_list[i].color = color_rgba

        cv2.circle(frame, (gX, gY), 5, (0,0,255), 1)

    text = "Violating People: {}".format(len(violate))
    cv2.putText(frame, text, (10, height - 25), cv2.FONT_HERSHEY_SIMPLEX, 0.85, (255, 0, 0), 3)
    text = "frame: {}   FPS: {:.2f}".format(f, 1 / interval) + (" NO_GPU" if not settings.use_gpu else "")
    cv2.putText(frame, text, (10, 25), cv2.FONT_HERSHEY_SIMPLEX, 0.85, (255, 0, 0), 3)
    
    # render the altered frame 
    frame_texture.texture.image = frame

    # screen and key adjusments
    event = sdl2.SDL_Event()
    sdl2.SDL_CaptureMouse(10)
    while sdl2.SDL_PollEvent(ctypes.byref(event)) != 0:
        UI_clicked = manager.update(event, viewport)
        if event.type == sdl2.SDL_QUIT:
            running = False
        
        elif event.type == sdl2.SDL_MOUSEBUTTONDOWN:
            pos = (event.motion.x, event.motion.y)
            button = event.button.button
			
            if button == 1 and settings.debug:
                normal = Vector3([0.0,0.0,1.0]) 
                plane = pyrr.plane.create_from_position(position = Vector3([0.0,0.0,0.0]), normal = normal)
                transform = Transform(camera.ray_cast(camera.screen_to_world_coordinates(pos) - camera.pos, plane))
                empty(empty_list, transform)

        elif event.type == sdl2.SDL_WINDOWEVENT:
            button = event.window.event
            if button == sdl2.SDL_WINDOWEVENT_CLOSE:
                running = False

        elif event.type == sdl2.SDL_KEYDOWN:
            key = event.key.keysym.sym
				
            if key == sdl2.SDLK_ESCAPE:
                running = False
        
    # clean the screen for next frame
    context.clear(0.68, 0.87, 1)
    # render the frame
    viewport.render()

    # if render_cylinder flag is true, then render cylinder
    if settings.render_cylinder:
        for i,mesh in enumerate(mesh_list):
            mesh.render(camera, light, render_type = moderngl.TRIANGLES)
    if settings.render_empty or settings.debug:
        for i,empty_obj in enumerate(empty_list):
            empty_obj.render(camera, light, render_type = moderngl.LINES)
    if settings.render_grid:
        grid.render(camera, light, render_type = moderngl.LINES)
    
    sdl2.SDL_GL_SwapWindow(window.window)
    #sdl2.SDL_Delay(1)


sdl2.SDL_GL_DeleteContext(window.sdl_context)
sdl2.SDL_DestroyWindow(window.window)
sdl2.SDL_Quit()