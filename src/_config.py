import glm
from glm import vec3
from math import cos, sin, pi

class CameraOrbit:
    x = 0.0
    y = 0.0
    z = -8.0
    rotx = 0.0
    roty = 0.0

    x_smooth = x
    y_smooth = y
    z_smooth = z
    rotx_smooth = rotx
    roty_smooth = roty

class Camera:
    def __init__(self):
        self.pos = vec3(0, 0, -8)
        self.rot = vec3(0, 0, 0)

        self.near = 0.1
        self.far = 100.0
        self.fov = glm.radians(70)
        self.speed = 0.1

    def getPos(self):
        return -vec3(self.pos)

    def move_forward(self, value):
        self.pos.x += cos(self.rot.y + pi/2) * value
        self.pos.z += sin(self.rot.y + pi/2) * value

    def move_sideways(self, value):
        self.pos.x += cos(self.rot.y) * value
        self.pos.z += sin(self.rot.y) * value

    def view_matrix(self):
        view = glm.mat4(1.0)
        view = glm.rotate(view, self.rot.x, vec3(1, 0, 0))
        view = glm.rotate(view, self.rot.y, vec3(0, 1, 0))

        view = glm.translate(view, self.pos)

        return view
        # return glm.lookAt(self.pos, self.pos + self.dir, vec3(0, 1, 0))

class Light:
    x = 0
    y = 0
    z = 0
