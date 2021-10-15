from array import array

import moderngl

def init_debug_draw(self):
    self.program["_DEBUG"] = self.load_program(
        vertex_shader="./line.vert",
        fragment_shader="./line.frag"
    )

    # change every time you draw something; is reset on draw
    self._debug_buffer_offset = 0
    self._debug_buffer_size = 1024

    self._debug_buffer = self.ctx.buffer(reserve=self._debug_buffer_size)

    self._debug_vao = self.ctx.vertex_array(
        self.program["_DEBUG"],
        [
            (self._debug_buffer, '3f', 'in_vert'),
        ],
    )

def debug_line(self, x1, y1, z1, x2, y2, z2):
    data = array('f', [x1, y1, z1, x2, y2, z2])
    self._debug_buffer.write(data, offset=self._debug_buffer_offset)
    # self._debug_buffer_offset
    print(len(data))

def debug_draw(self):
    self._debug_vao.render(mode=moderngl.LINES)
    self._debug_buffer.clear()
