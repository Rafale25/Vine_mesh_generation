from array import array

import moderngl
import glm
import math

def init_debug_draw(self):
    self.program["_DEBUG"] = self.load_program(
        vertex_shader="./line.vert",
        fragment_shader="./line.frag"
    )

    # change every time you draw something; is reset on draw
    self._debug_buffer_offset = 0
    self._debug_buffer_size = 4096*64

    self._debug_buffer = self.ctx.buffer(reserve=self._debug_buffer_size)

    self._debug_vao = self.ctx.vertex_array(
        self.program["_DEBUG"],
        [
            (self._debug_buffer, '3f', 'in_vert'),
        ],
    )

def debug_line(self, x1, y1, z1, x2, y2, z2):
    data = (x1, y1, z1, x2, y2, z2)
    self._debug_buffer.write(array('f', data), offset=self._debug_buffer_offset)
    self._debug_buffer_offset += len(data) * 4 # 1 float is 4 bytes

def debug_sphere(self, px, py, pz, radius=1.0):
    data = []

    NB = 32
    for i in range(NB):
        angle = (math.pi*2.0 / NB) * i
        angle_next = (math.pi*2.0 / NB) * (i+1)

        x = math.cos(angle) * radius
        z = math.sin(angle) * radius

        x_next = math.cos(angle_next) * radius
        z_next = math.sin(angle_next) * radius

        # horizontal circle
        data.extend((px+x, py, pz+z))
        data.extend((px+x_next, py, pz+z_next))

        # vertical circle x
        data.extend((px+x, py+z, pz))
        data.extend((px+x_next, py+z_next, pz))

        # vertical circle z
        data.extend((px, py+z, pz+x))
        data.extend((px, py+z_next, pz+x_next))

    self._debug_buffer.write(array('f', data), offset=self._debug_buffer_offset)
    self._debug_buffer_offset += len(data) * 4 # 1 float is 4 bytes

def debug_draw(self):
    self._debug_vao.render(mode=moderngl.LINES)
    self._debug_buffer.clear()
    self._debug_buffer_offset = 0
