import glfw
import numpy as np
import pyrr
import texture_loader
import buffer_loader

from OpenGL.GL import *
from camera import Camera
from shader_loader import Shader
from PIL import Image
from obj_loader import ObjLoader
from in_view_detection import isect_line_plane_v3

camera = Camera()
camera_speed = 10
delta_time = 0
window_width, window_height = 800, 600
aspect_ratio = window_width / window_height
last_x, last_y = window_width / 2, window_height / 2
first_mouse = True
keys = [False] * 1024

maps = [
        "resources\\left.png",
        "resources\\right.png",
        "resources\\top.png",
        "resources\\bottom.png",
        "resources\\front.png",
        "resources\\back.png",
    ]
skybox_vertices = [
    -1.0, 1.0, -1.0,
    -1.0, -1.0, -1.0,
    1.0, -1.0, -1.0,
    1.0, -1.0, -1.0,
    1.0, 1.0, -1.0,
    -1.0, 1.0, -1.0,

    -1.0, -1.0, 1.0,
    -1.0, -1.0, -1.0,
    -1.0, 1.0, -1.0,
    -1.0, 1.0, -1.0,
    -1.0, 1.0, 1.0,
    -1.0, -1.0, 1.0,

    1.0, -1.0, -1.0,
    1.0, -1.0, 1.0,
    1.0, 1.0, 1.0,
    1.0, 1.0, 1.0,
    1.0, 1.0, -1.0,
    1.0, -1.0, -1.0,

    -1.0, -1.0, 1.0,
    -1.0, 1.0, 1.0,
    1.0, 1.0, 1.0,
    1.0, 1.0, 1.0,
    1.0, -1.0, 1.0,
    -1.0, -1.0, 1.0,

    -1.0, 1.0, -1.0,
    1.0, 1.0, -1.0,
    1.0, 1.0, 1.0,
    1.0, 1.0, 1.0,
    -1.0, 1.0, 1.0,
    -1.0, 1.0, -1.0,

    -1.0, -1.0, -1.0,
    -1.0, -1.0, 1.0,
    1.0, -1.0, -1.0,
    1.0, -1.0, -1.0,
    -1.0, -1.0, 1.0,
    1.0, -1.0, 1.0
]
skybox_vertices = np.array(skybox_vertices, dtype=np.float32)
screen_buffer_verts = [
    -1.0, 1.0, 0.0, 1.0,
    -1.0, -1.0, 0.0, 0.0,
    1.0, -1.0, 1.0, 0.0,
    -1.0, 1.0, 0.0, 1.0,
    1.0, -1.0, 1.0, 0.0,
    1.0, 1.0, 1.0, 1.0
]
screen_buffer_verts = np.array(screen_buffer_verts, dtype=np.float32)
reticule_verts = [
    -.1, 0, 0,
    0, 0, 0,
    0, .1, 0,
    0, 0, 0,
    .1, 0, 0,
    0, 0, 0,
    0, -.1, 0,
    0, 0, 0
]
reticule_verts = np.array([i * .5 for i in reticule_verts], dtype=np.float32)

block_obj = ObjLoader()
block_obj.load_model("models\\block.obj")
block_texture_offset = len(block_obj.vertex_index) * 12
block_normal_offset = len(block_obj.vertex_index) * 24

world = []
for x in range(0, 10):
    for z in range(0, 10):
        world.append(pyrr.Vector3([x * 2, 0, z * 2]))
block_positions = np.array(world, dtype=np.float32)
block_positions = np.array([0, 0, 0], dtype=np.float32)


def framebuffer_size_callback(window, width, height):
    glViewport(0, 0, width, height)


def key_callback(window, key, scancode, action, mode):
    if key == glfw.KEY_ESCAPE and action == glfw.PRESS:
        glfw.set_window_should_close(window, True)

    if 0 <= key < 1024:
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


def load_cubemap(maps_):
    tex_id = glGenTextures(1)
    glBindTexture(GL_TEXTURE_CUBE_MAP, tex_id)

    for i in range(0, len(maps_), 1):
        cubemap_image = Image.open(maps_[i])
        cubemap_data = cubemap_image.convert("RGBA").tobytes()

        if cubemap_data:
            glTexImage2D(GL_TEXTURE_CUBE_MAP_POSITIVE_X + i,
                         0, GL_RGBA, cubemap_image.width, cubemap_image.height,
                         0, GL_RGBA, GL_UNSIGNED_BYTE, cubemap_data)
        else:
            raise Exception("Cubemap texture failed to load at path: " + maps_[i])

        glTexParameteri(GL_TEXTURE_CUBE_MAP, GL_TEXTURE_MIN_FILTER, GL_LINEAR)
        glTexParameteri(GL_TEXTURE_CUBE_MAP, GL_TEXTURE_MAG_FILTER, GL_LINEAR)
        glTexParameteri(GL_TEXTURE_CUBE_MAP, GL_TEXTURE_WRAP_S, GL_CLAMP_TO_EDGE)
        glTexParameteri(GL_TEXTURE_CUBE_MAP, GL_TEXTURE_WRAP_T, GL_CLAMP_TO_EDGE)
        glTexParameteri(GL_TEXTURE_CUBE_MAP, GL_TEXTURE_WRAP_R, GL_CLAMP_TO_EDGE)

    return tex_id


def main():
    global delta_time

    # Get projection matrix
    projection_matrix = np.array(pyrr.Matrix44.perspective_projection(45.0, aspect_ratio, 0.1, 500.0), dtype=np.float32)

    glfw.init()
    window = glfw.create_window(window_width, window_height, "Manncraft", None, None)
    if not window:
        glfw.terminate()
        return
    # GLFW initialization
    glfw.make_context_current(window)
    glfw.window_hint(glfw.CONTEXT_VERSION_MAJOR, 3)
    glfw.window_hint(glfw.CONTEXT_VERSION_MINOR, 3)
    glfw.window_hint(glfw.OPENGL_PROFILE, glfw.OPENGL_CORE_PROFILE)
    glfw.set_input_mode(window, glfw.CURSOR, glfw.CURSOR_DISABLED)
    glfw.set_framebuffer_size_callback(window, framebuffer_size_callback)
    glfw.set_key_callback(window, key_callback)
    glfw.set_cursor_pos_callback(window, mouse_callback)

    # OpenGL initialization
    glViewport(0, 0, window_width, window_height)
    glEnable(GL_DEPTH_TEST)
    glDepthFunc(GL_LESS)
    glEnable(GL_STENCIL_TEST)
    glStencilFunc(GL_NOTEQUAL, 1, 0xFF)
    glStencilOp(GL_KEEP, GL_KEEP, GL_REPLACE)
    glEnable(GL_CULL_FACE)
    glCullFace(GL_FRONT)
    glFrontFace(GL_CW)

    # Load shaders
    main_shader = Shader("shaders\\vertex.vs", "shaders\\fragment.fs")
    outline_shader = Shader("shaders\\outline_vertex.vs", "shaders\\outline_fragment.fs")
    skybox_shader = Shader("shaders\\skybox_vertex.vs", "shaders\\skybox_fragment.fs")
    screen_shader = Shader("shaders\\screen_vertex.vs", "shaders\\screen_fragment.fs")
    reticule_shader = Shader("shaders\\reticule_vertex.vs", "shaders\\reticule_fragment.fs")

    # Object buffers
    block_buffer = glGenVertexArrays(1)
    block_vbo = glGenBuffers(1)
    glBindVertexArray(block_buffer)
    glBindBuffer(GL_ARRAY_BUFFER, block_vbo)
    glBufferData(GL_ARRAY_BUFFER, block_obj.model.nbytes, block_obj.model, GL_STATIC_DRAW)
    glEnableVertexAttribArray(0)
    glVertexAttribPointer(0, 3, GL_FLOAT, GL_FALSE, block_obj.model.itemsize * 3, ctypes.c_void_p(0))
    glEnableVertexAttribArray(1)
    glVertexAttribPointer(1, 2, GL_FLOAT, GL_FALSE, block_obj.model.itemsize * 2, ctypes.c_void_p(block_texture_offset))
    glEnableVertexAttribArray(2)
    glVertexAttribPointer(2, 3, GL_FLOAT, GL_FALSE, block_obj.model.itemsize * 3, ctypes.c_void_p(block_normal_offset))

    # Instance buffer
    instance_vbo = glGenBuffers(1)
    glBindBuffer(GL_ARRAY_BUFFER, instance_vbo)
    glBufferData(GL_ARRAY_BUFFER, block_positions.nbytes, block_positions, GL_STATIC_DRAW)
    glEnableVertexAttribArray(3)
    glVertexAttribPointer(3, 3, GL_FLOAT, GL_FALSE, 0, ctypes.c_void_p(0))
    glVertexAttribDivisor(3, 1)
    buffer_loader.unbind_buffers()

    # Outline buffer
    outline_buffer = glGenVertexArrays(1)
    outline_vbo = glGenBuffers(1)
    glBindVertexArray(outline_buffer)
    glBindBuffer(GL_ARRAY_BUFFER, outline_vbo)
    glBufferData(GL_ARRAY_BUFFER, block_obj.model.nbytes, block_obj.model, GL_STATIC_DRAW)
    glEnableVertexAttribArray(0)
    glVertexAttribPointer(0, 3, GL_FLOAT, GL_FALSE, block_obj.model.itemsize * 3, ctypes.c_void_p(0))
    buffer_loader.unbind_buffers()

    # Skybox, screen buffers
    skybox_buffer = buffer_loader.load_vao("skybox_vao", skybox_vertices)
    glEnableVertexAttribArray(0)
    glVertexAttribPointer(0, 3, GL_FLOAT, GL_FALSE, 3 * skybox_vertices.itemsize, ctypes.c_void_p(0))
    buffer_loader.unbind_buffers()
    screen_buffer = buffer_loader.load_vao("screen_vao", screen_buffer_verts)
    glEnableVertexAttribArray(0)
    glVertexAttribPointer(0, 2, GL_FLOAT, GL_FALSE, 4 * screen_buffer_verts.itemsize, ctypes.c_void_p(0))
    glEnableVertexAttribArray(1)
    glVertexAttribPointer(1, 2, GL_FLOAT, GL_FALSE, 4 * screen_buffer_verts.itemsize, ctypes.c_void_p(2 * screen_buffer_verts.itemsize))
    buffer_loader.unbind_buffers()

    # Reticule buffer
    reticule_buffer = buffer_loader.load_vao("reticule_vao", reticule_verts)
    glEnableVertexAttribArray(0)
    glVertexAttribPointer(0, 3, GL_FLOAT, GL_FALSE, 3 * reticule_verts.itemsize, ctypes.c_void_p(0))
    buffer_loader.unbind_buffers()

    # Framebuffer
    main_fbo, tex_fbo = buffer_loader.load_framebuffer("screen_fbo")

    last_frame = 0.0

    # Sending initial data to shaders
    main_shader.use()
    main_shader.set_vec3("dirLight.direction", pyrr.Vector3([-.2, -1.0, -.3]))
    main_shader.set_vec3("dirLight.ambient", pyrr.Vector3([.05, .05, .05]))
    main_shader.set_vec3("dirLight.diffuse", pyrr.Vector3([.4, .4, .4]))
    main_shader.set_vec3("dirLight.specular", pyrr.Vector3([.5, .5, .5]))
    main_shader.set_int("diffuse", 0)
    main_shader.set_Matrix44f("projection", projection_matrix)
    glUseProgram(0)

    skybox_shader.use()
    skybox_shader.set_Matrix44f("projection", projection_matrix)
    skybox_shader.set_int("skybox", 0)
    glUseProgram(0)

    outline_shader.use()
    outline_shader.set_Matrix44f("projection", projection_matrix)
    glUseProgram(0)

    # Load skybox
    skybox_id = load_cubemap(maps)

    # Load textures
    wood = texture_loader.load_texture("resources\\wood_texture.png", True)

    front_pco = block_obj.vert_coords[1]
    front_pno = block_obj.norm_coords[2]
    right_pco = block_obj.vert_coords[0]
    right_pno = block_obj.norm_coords[3]
    back_pco = block_obj.vert_coords[3]
    back_pno = block_obj.norm_coords[4]
    left_pco = block_obj.vert_coords[2]
    left_pno = block_obj.norm_coords[5]
    top_pco = block_obj.vert_coords[5]
    top_pno = block_obj.norm_coords[1]
    bottom_pco = block_obj.vert_coords[13]
    bottom_pno = block_obj.norm_coords[0]

    block_in_view = pyrr.Vector3()

    while not glfw.window_should_close(window):
        glfw.poll_events()
        move()

        test_block = pyrr.Vector3([
            int(camera.camera_pos.x + 10 * camera.camera_front[0]),
            int(camera.camera_pos.y + 10 * camera.camera_front[1]),
            int(camera.camera_pos.z + 10 * camera.camera_front[2])
        ])
        print(test_block)
        # test_block[0] = int(test_block[0])
        # test_block[1] = int(test_block[1])
        # test_block[2] = int(test_block[2])

        # p0 = [camera.camera_pos.x,
        #       camera.camera_pos.y,
        #       camera.camera_pos.z]
        # p1 = [camera.camera_pos.x + camera.camera_front[0],
        #       camera.camera_pos.y + camera.camera_front[1],
        #       camera.camera_pos.z + camera.camera_front[2]]
        #
        # front_intersect = isect_line_plane_v3(p0, p1, front_pco, front_pno)
        # right_intersect = isect_line_plane_v3(p0, p1, right_pco, right_pno)
        # left_intersect = isect_line_plane_v3(p0, p1, left_pco, left_pno)
        # back_intersect = isect_line_plane_v3(p0, p1, back_pco, back_pno)
        # top_intersect = isect_line_plane_v3(p0, p1, top_pco, top_pno)
        # bottom_intersect = isect_line_plane_v3(p0, p1, bottom_pco, bottom_pno)
        #
        # print(front_intersect, right_intersect, left_intersect, back_intersect, top_intersect, bottom_intersect)
        #
        # if (-1.0 <= front_intersect[0] <= 1.0) and (-1.0 <= front_intersect[1] <= 1.0):
        #     front_in_view = True
        # else:
        #     front_in_view = False
        #
        # if (-1.0 <= right_intersect[2] <= 1.0) and (-1.0 <= right_intersect[1] <= 1.0):
        #     right_in_view = True
        # else:
        #     right_in_view = False
        #
        # if (-1.0 <= left_intersect[2] <= 1.0) and (-1.0 <= left_intersect[1] <= 1.0):
        #     left_in_view = True
        # else:
        #     left_in_view = False
        #
        # if (-1.0 <= back_intersect[0] <= 1.0) and (-1.0 <= back_intersect[1] <= 1.0):
        #     back_in_view = True
        # else:
        #     back_in_view = False
        #
        # if (-1.0 <= top_intersect[0] <= 1.0) and (-1.0 <= top_intersect[2] <= 1.0):
        #     top_in_view = True
        # else:
        #     top_in_view = False
        #
        # if (-1.0 <= bottom_intersect[0] <= 1.0) and (-1.0 <= bottom_intersect[2] <= 1.0):
        #     bottom_in_view = True
        # else:
        #     bottom_in_view = False
        #
        # if bottom_in_view or top_in_view or back_in_view or left_in_view or right_in_view or front_in_view:
        #     block_in_view = True
        # else:
        #     block_in_view = False
        #print(block_in_view)

        # Render to custom framebuffer
        glBindFramebuffer(GL_FRAMEBUFFER, main_fbo)

        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT | GL_STENCIL_BUFFER_BIT)

        # Adjust cam speed from fps
        time = glfw.get_time()
        delta_time = time - last_frame
        last_frame = time

        # Get view matrix
        view_matrix = camera.get_view_matrix()

        # Send view info to main shader
        main_shader.use()
        main_shader.set_vec3("viewPos", camera.camera_pos)
        main_shader.set_Matrix44f("view", view_matrix)

        # Draw blocks
        glStencilFunc(GL_ALWAYS, 1, 0xFF)
        glStencilMask(0xFF)
        glBindVertexArray(block_buffer)
        glBindTexture(GL_TEXTURE_2D, wood)
        glDrawArraysInstanced(GL_TRIANGLES, 0, len(block_obj.vertex_index), len(world))
        buffer_loader.unbind_buffers()
        glUseProgram(0)

        # Send view info to outline shader
        outline_shader.use()
        outline_shader.set_Matrix44f("view", view_matrix)
        outline_scale = pyrr.Matrix44.from_scale(pyrr.Vector3([1.5, 1.5, 1.5]))
        outline_trans = pyrr.Matrix44.from_translation(test_block)
        outline_model = outline_scale * outline_trans
        outline_model = np.array(outline_model, dtype=np.float32)
        outline_shader.set_Matrix44f("model", outline_model)

        # Draw outline
        glStencilFunc(GL_NOTEQUAL, 1, 0xFF)
        glStencilMask(0x00)
        glDisable(GL_DEPTH_TEST)
        glBindVertexArray(outline_buffer)
        glDrawArrays(GL_TRIANGLES, 0, 36)
        glStencilMask(0xFF)
        glEnable(GL_DEPTH_TEST)
        buffer_loader.unbind_buffers()
        glUseProgram(0)

        # Send view info to skybox shader
        skybox_shader.use()
        glDepthFunc(GL_LEQUAL)
        view_matrix = np.array(pyrr.Matrix44(pyrr.Matrix33.from_matrix44(view_matrix)), dtype=np.float32)
        skybox_shader.set_Matrix44f("view", view_matrix)

        # Draw skybox
        glBindVertexArray(skybox_buffer)
        glBindTexture(GL_TEXTURE_CUBE_MAP, skybox_id)
        glDrawArrays(GL_TRIANGLES, 0, 36)
        buffer_loader.unbind_buffers()
        glUseProgram(0)
        glDepthFunc(GL_LESS)

        # Unbind custom framebuffer
        glBindFramebuffer(GL_FRAMEBUFFER, 0)
        glDisable(GL_DEPTH_TEST)
        glClear(GL_COLOR_BUFFER_BIT)

        # Render to screen buffer
        screen_shader.use()
        glBindVertexArray(screen_buffer)
        glBindTexture(GL_TEXTURE_2D, tex_fbo)
        glDrawArrays(GL_TRIANGLES, 0, 6)

        # Draw reticule
        reticule_shader.use()
        glBindVertexArray(reticule_buffer)
        glDrawArrays(GL_LINE_LOOP, 0, 8)

        glfw.swap_buffers(window)

    glfw.terminate()

if __name__ == "__main__":
    main()