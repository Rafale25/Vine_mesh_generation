import glm
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
        self.pos = glm.vec3(0, 0, -8)
        self.rot = glm.vec3(0, 0, 0)
        self.fov = glm.radians(80)
        self.speed = 0.05

    def move_forward(self, value):
        self.pos.x += cos(self.rot.y + pi/2) * value
        self.pos.z += sin(self.rot.y + pi/2) * value

    def move_sideways(self, value):
        self.pos.x += cos(self.rot.y) * value
        self.pos.z += sin(self.rot.y) * value

    def view_matrix(self):
        view = glm.mat4(1.0)
        view = glm.rotate(view, self.rot.x, glm.vec3(1, 0, 0))
        view = glm.rotate(view, self.rot.y, glm.vec3(0, 1, 0))

        view = glm.translate(view, self.pos)

        return view
        # return glm.lookAt(self.pos, self.pos + self.dir, glm.vec3(0, 1, 0))

class Light:
    x = 0
    y = 0
    z = 0
