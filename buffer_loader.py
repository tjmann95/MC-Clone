from OpenGL.GL import *
import numpy as np
from main import window_width, window_height

vaos = {}
vbos = {}
fbos = {}
rbos = {}
tex_buffers = {}


def load_vao(name_, data):
    if type(name_) == str and type(data) == np.ndarray and data.dtype == np.float32:
        vaos[name_] = glGenVertexArrays(1)
        vbos[name_] = glGenBuffers(1)
        glBindVertexArray(vaos[name_])
        glBindBuffer(GL_ARRAY_BUFFER, vbos[name_])
        glBufferData(GL_ARRAY_BUFFER, data.nbytes, data, GL_STATIC_DRAW)
    else:
        print("ERROR: Must input a string and float32 array")

    return vaos[name_]


def unbind_buffers():
    glBindBuffer(GL_ARRAY_BUFFER, 0)
    glBindVertexArray(0)


def load_framebuffer(name_):
    if type(name_) == str:
        fbos[name_] = glGenFramebuffers(1)
        glBindFramebuffer(GL_FRAMEBUFFER, fbos[name_])

        tex_buffers[name_] = glGenTextures(1)
        glBindTexture(GL_TEXTURE_2D, tex_buffers[name_])
        glTexImage2D(GL_TEXTURE_2D, 0, GL_RGB, window_width, window_height, 0, GL_RGB, GL_UNSIGNED_BYTE, None)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_LINEAR)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_LINEAR)
        glBindTexture(GL_TEXTURE_2D, 0)

        glFramebufferTexture2D(GL_FRAMEBUFFER, GL_COLOR_ATTACHMENT0, GL_TEXTURE_2D, tex_buffers[name_], 0)

        rbos[name_] = glGenRenderbuffers(1)
        glBindRenderbuffer(GL_RENDERBUFFER, rbos[name_])
        glRenderbufferStorage(GL_RENDERBUFFER, GL_DEPTH24_STENCIL8, window_width, window_height)
        glBindRenderbuffer(GL_RENDERBUFFER, 0)

        glFramebufferRenderbuffer(GL_FRAMEBUFFER, GL_DEPTH_STENCIL_ATTACHMENT, GL_RENDERBUFFER, rbos[name_])

        if glCheckFramebufferStatus(GL_FRAMEBUFFER) != GL_FRAMEBUFFER_COMPLETE:
            print("ERROR: FRAMEBUFFER: Framebuffer is not complete!")
        glBindFramebuffer(GL_FRAMEBUFFER, 0)

        return fbos[name_], tex_buffers[name_]
