from OpenGL.GL import *
import numpy as np

vaos = {}
vbos = {}


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
