from OpenGL.GL import *
import pyrr
import numpy

class Shader(object):

    def __init__(self, vertex, fragment):
        self.vertex_path = vertex
        self.fragment_path = fragment

        self.shader_program = self.compile_shader()

    def load_source(self, file):
        f = open(file, "r")
        source = f.read()
        f.close()

        return source

    def compile_shader(self):
        vertex_shader_source = self.load_source(self.vertex_path)
        fragment_shader_source = self.load_source(self.fragment_path)

        # Compile vertex shader
        vertex_shader = glCreateShader(GL_VERTEX_SHADER)
        glShaderSource(vertex_shader, vertex_shader_source)
        glCompileShader(vertex_shader)

        # Check vertex compilation success
        error_message = glGetShaderInfoLog(vertex_shader)
        if "No errors." not in str(error_message) and len(str(error_message)) > 0:
            print("ERROR: Vertex shader failed to compile:\n" + str(error_message))

        # Compile fragment shader
        fragment_shader = glCreateShader(GL_FRAGMENT_SHADER)
        glShaderSource(fragment_shader, fragment_shader_source)
        glCompileShader(fragment_shader)

        # Check fragment compilation success
        error_message = glGetShaderInfoLog(fragment_shader)
        if "No errors." not in str(error_message) and len(str(error_message)) > 0:
            print("ERROR: Fragment shader failed to compile:\n" + str(error_message))

        # Creating shader program
        shader_program = glCreateProgram()
        glAttachShader(shader_program, vertex_shader)
        glAttachShader(shader_program, fragment_shader)
        glLinkProgram(shader_program)

        # Check shader program success
        error_message = glGetProgramInfoLog(shader_program)
        if "No errors." not in str(error_message) and len(str(error_message)) > 0:
            print("ERROR: Shader program failed:\n" + str(error_message))

        glDeleteShader(vertex_shader)
        glDeleteShader(fragment_shader)

        return shader_program

    def set_vec3(self, uniform, values):
        if type(values) != pyrr.objects.vector3.Vector3:
            raise Exception("Must input a Vector3")
        location = glGetUniformLocation(self.shader_program, uniform)
        glUniform3f(location, values.x, values.y, values.z)

    def set_float(self, uniform, value):
        if type(value) != float:
            raise Exception("Must input a float")
        location = glGetUniformLocation(self.shader_program, uniform)
        glUniform1f(location, value)

    def set_Matrix44f(self, uniform, matrix):
        if matrix.dtype != "float32" or type(matrix) != numpy.ndarray or matrix.shape != (4, 4):
            raise Exception("Must input a 4x4 float32 array")
        location = glGetUniformLocation(self.shader_program, uniform)
        glUniformMatrix4fv(location, 1, GL_FALSE, matrix)

    def set_int(self, uniform, value):
        if type(value) != int:
            raise Exception("Must input a float")
        location = glGetUniformLocation(self.shader_program, uniform)
        glUniform1i(location, value)

    def use(self):
        glUseProgram(self.shader_program)