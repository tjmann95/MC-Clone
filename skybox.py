from OpenGL.GL import *
from PIL import Image
from shader_loader import Shader


class Skybox:

    def __init__(self, locations):

        self.locations = locations
        self.shader = Shader("shaders\\skybox_vertex.vs", "shaders\\skybox_fragment.fs")

    def load_cubemap(self):
        tex_id = glGenTextures(1)
        glBindTexture(GL_TEXTURE_CUBE_MAP, tex_id)

        for i in range(0, len(self.locations), 1):
            cubemap_image = Image.open(self.locations[i])
            cubemap_data = cubemap_image.convert("RGBA").tobytes()

            if cubemap_data:
                glTexImage2D(GL_TEXTURE_CUBE_MAP_POSITIVE_X + i,
                             0, GL_RGBA, cubemap_image.width, cubemap_image.height,
                             0, GL_RGBA, GL_UNSIGNED_BYTE, cubemap_data)
            else:
                raise Exception("Cubemap texture failed to load at path: " + self.locations[i])

            glTexParameteri(GL_TEXTURE_CUBE_MAP, GL_TEXTURE_MIN_FILTER, GL_LINEAR)
            glTexParameteri(GL_TEXTURE_CUBE_MAP, GL_TEXTURE_MAG_FILTER, GL_LINEAR)
            glTexParameteri(GL_TEXTURE_CUBE_MAP, GL_TEXTURE_WRAP_S, GL_CLAMP_TO_EDGE)
            glTexParameteri(GL_TEXTURE_CUBE_MAP, GL_TEXTURE_WRAP_T, GL_CLAMP_TO_EDGE)
            glTexParameteri(GL_TEXTURE_CUBE_MAP, GL_TEXTURE_WRAP_R, GL_CLAMP_TO_EDGE)

    def draw_skybox(self):
        glDepthFunc(GL_LEQUAL)
        self.shader.use()
        view_matrix =