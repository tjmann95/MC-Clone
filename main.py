import glfw
import numpy as np

from OpenGL.GL import *
from camera import Camera
from shader_loader import Shader
from skybox import Skybox
from PIL import Image

camera = Camera()
camera_speed = .1
delta_time = 0
window_width, window_height = 800, 600
last_x, last_y = window_width / 2, window_height / 2
first_mouse = True
keys = [False] * 1024

def framebuffer_size_callback(window, width, height):
    glViewport(0, 0, width, height)


def key_callback(window, key, scancode, action, mode):
    if key == glfw.KEY_ESCAPE and action == glfw.PRESS:
        glfw.set_window_should_close(window, True)

    if key >= 0 and key < 1024:
        if action == glfw.PRESS:
            keys[key] = True
        if action == glfw.RELEASE:
            keys[key] = False


def move():
    if keys[glfw.KEY_W]:
        camera.process_keyboard("FORWARD", camera_speed * delta_time)
    if keys[glfw.KEY_S]:
        camera.process_keyboard("BACKWARD", camera_speed * delta_time)
    if keys[glfw.KEY_A]:
        camera.process_keyboard("LEFT", camera_speed * delta_time)
    if keys[glfw.KEY_D]:
        camera.process_keyboard("RIGHT", camera_speed * delta_time)
    if keys[glfw.KEY_SPACE]:
        camera.process_keyboard("UP", camera_speed * delta_time)
    if keys[glfw.KEY_LEFT_SHIFT]:
        camera.process_keyboard("DOWN", camera_speed * delta_time)


def mouse_callback(window, xpos, ypos):
    global first_mouse, last_x, last_y
    sensitivity = 1.2

    if first_mouse:
        last_x = xpos
        last_y = ypos
        first_mouse = False

    x_offset = xpos - last_x
    y_offset = last_y - ypos
    last_x = xpos
    last_y = ypos
    x_offset *= sensitivity
    y_offset *= sensitivity

    camera.process_mouse_movement(x_offset, y_offset)





def main():

    maps = [
        "resources\\left.png",
        "resources\\right.png",
        "resources\\top.png",
        "resources\\bottom.png",
        "resources\\front.png",
        "resources\\back.png",
    ]
    skymap = Skybox(maps)