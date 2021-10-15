#! /usr/bin/python3

import sys
import math
import random
import struct
import time
import pathlib

import moderngl
import imgui
import pyglet
import glm

import moderngl_window as mglw
from moderngl_window.integrations.imgui import ModernglWindowRenderer

from glm import vec3, vec4
from math import pi, cos, sin, fabs
from random import uniform
from array import array

from utils import *
from _config import CameraOrbit, Camera, Light

from tree import Tree, TreeNode

class MyWindow(mglw.WindowConfig):
    title = "Tree"
    gl_version = (4, 3)
    window_size = (1280, 720)
    fullscreen = False
    resizable = False
    vsync = True
    resource_dir = "./resources"

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        imgui.create_context()
        self.imgui = ModernglWindowRenderer(self.wnd)

        self.width, self.height = self.window_size

        self.ctx.wireframe = False

        self.cull_face = True
        self.draw_skeleton = False
        self.draw_normals = False
        self.draw_mesh = True

        self.camera = Camera()

        self.tree = Tree()
        self.tree.generate()

        self.program = {
            "TREE":
                self.load_program(
                    vertex_shader="./tree.vert",
                    fragment_shader="./tree.frag"),
            "TREE_NORMAL":
                self.load_program(
                    vertex_shader="./tree_normal.vert",
                    fragment_shader="./tree_normal.frag",
                    geometry_shader="./tree_normal.geom"),
            "LINE":
                self.load_program(
                    vertex_shader="./line.vert",
                    fragment_shader="./line.frag"),
        }

        ## LINES ----------
        self.buffer_debug = self.ctx.buffer(data=array('f', self.gen_tree_skeleton()))

        self.vao_lines = self.ctx.vertex_array(
            self.program["LINE"],
            [
                (self.buffer_debug, '3f', 'in_vert'),
            ],
        )
        # -----------------------------

        ## mesh ----------------
        data = []
        self.gen_tree_mesh(data)

        self.buffer_mesh = self.ctx.buffer(data=array('f', data))

        self.vao_mesh = self.ctx.vertex_array(
            self.program["TREE"],
            [
                (self.buffer_mesh, '3f 3f', 'in_vert', 'in_normal')
            ],
        )

        self.vao_mesh_normal = self.ctx.vertex_array(
            self.program["TREE_NORMAL"],
            [
                (self.buffer_mesh, '3f 3f', 'in_vert', 'in_normal')
            ],
        )

        self.init_debug_draw()

    from _debug_draw import\
        init_debug_draw,\
        debug_line,\
        debug_sphere,\
        debug_draw

# """
# 1 - 3 - 5
# | \ | \ |
# 0 - 2 - 4
#
# #indices for NB=3 ; GL_TRIANGLES
# 0 2 1
# 1 2 3
#
# 2 4 3
# 3 4 5
# """

    # vertex, normals (not indices because normals need duplicated vertex data)
    def gen_tree_mesh(self, data, NB=256, branch_thickness=0.1):
        for j, node in enumerate(self.tree.nodes):
            dir = glm.sub(node.parent.pos, node.pos)

            mat_translate_parent = glm.translate(glm.mat4(), node.parent.pos)
            mat_translate_self = glm.translate(glm.mat4(), node.pos)
            mat_rotate = glm.orientation(dir, vec3(0,1,0))

            for i in range(NB):
                angle1 = (math.pi*2.0 / NB) * i
                angle2 = (math.pi*2.0 / NB) * (i + 1)

                x1 = cos(angle1) * branch_thickness
                z1 = sin(angle1) * branch_thickness

                x2 = cos(angle2) * branch_thickness
                z2 = sin(angle2) * branch_thickness

                p1 = vec4(x1, 0, z1, 1.0)
                p2 = vec4(x2, 0, z2, 1.0)

                # triangle 1
                a0 = mat_translate_self * mat_rotate * p1
                a1 = mat_translate_parent * mat_rotate * p1
                a2 = mat_translate_self * mat_rotate * p2

                a_normal = triangle_normal(a0.xyz, a1.xyz, a2.xyz)
                # print(glm.normalize(a_normal))

                data.extend(a0.xyz)
                data.extend(a_normal) # one for each of the 3 vertices

                data.extend(a1.xyz)
                data.extend(a_normal)

                data.extend(a2.xyz)
                data.extend(a_normal)

                # triangle 2
                b1 = mat_translate_parent * mat_rotate * p1
                b3 = mat_translate_self * mat_rotate * p2
                b2 = mat_translate_parent * mat_rotate * p2

                b_normal = triangle_normal(b1.xyz, b2.xyz, b3.xyz)

                data.extend(b1.xyz)
                data.extend(b_normal)

                data.extend(b2.xyz)
                data.extend(b_normal)

                data.extend(b3.xyz)
                data.extend(b_normal)

    def gen_tree_skeleton(self):
        for node in self.tree.nodes:
            yield node.pos.x
            yield node.pos.y
            yield node.pos.z

            yield node.parent.pos.x
            yield node.parent.pos.y
            yield node.parent.pos.z

    def update_uniforms(self, frametime):
        view = self.camera.view_matrix()

        aspect_ratio = self.width / self.height
        projection = glm.perspective(self.camera.fov, aspect_ratio, 0.1, 1000)

        mvp = projection * view
        for str, program in self.program.items():
            if 'mvp' in program:
                program['mvp'].write(mvp)


        # view_r = glm.transpose(view)
        # view_dir = vec3(view_r[2][0], view_r[2][1], view_r[2][2])

        # print(self.camera.pos)
        self.program["TREE"]["view_position"].write(self.camera.pos)
        # self.program["TREE"]["view_direction"].write(view_dir)
        self.program["TREE"]["lightPosition"].write(vec3(Light.x, Light.y, Light.z))

    def update(self, time_since_start, frametime):
        Light.x = cos(time_since_start*0.2) * 6.0
        Light.y = 6.0
        Light.z = sin(time_since_start*0.2) * 6.0

        if self.wnd.is_key_pressed(self.wnd.keys.Z):
            self.camera.move_forward(self.camera.speed)
        if self.wnd.is_key_pressed(self.wnd.keys.S):
            self.camera.move_forward(-self.camera.speed)
        if self.wnd.is_key_pressed(self.wnd.keys.Q):
            self.camera.move_sideways(self.camera.speed)
        if self.wnd.is_key_pressed(self.wnd.keys.D):
            self.camera.move_sideways(-self.camera.speed)
        if self.wnd.is_key_pressed(self.wnd.keys.E):
            self.camera.pos.y -= self.camera.speed
        if self.wnd.is_key_pressed(self.wnd.keys.A):
            self.camera.pos.y += self.camera.speed

        self.update_uniforms(frametime)

    def render(self, time_since_start, frametime):
        self.update(time_since_start, frametime)

        self.ctx.clear(0.3, 0.3, 0.3)
        # self.ctx.enable_only(moderngl.NOTHING)
        # self.ctx.enable_only(moderngl.PROGRAM_POINT_SIZE)
        self.ctx.enable_only(
            moderngl.CULL_FACE * self.cull_face |
            moderngl.DEPTH_TEST)


        if self.draw_mesh:
            self.vao_mesh.render(mode=moderngl.TRIANGLES)
        if self.draw_normals:
            self.vao_mesh_normal.render(mode=moderngl.TRIANGLES)
        if self.draw_skeleton:
            self.vao_lines.render(mode=moderngl.LINES)

        self.debug_line(0, 0, 0, 0.5, 0, 0)
        self.debug_line(0, 0, 0, 0, 0.5, 0)
        self.debug_line(0, 0, 0, 0, 0, 0.5)
        self.debug_sphere(Light.x, Light.y, Light.z, 0.5)
        self.debug_draw()

        self.imgui_newFrame(frametime)
        self.imgui_render()

    def cleanup(self):
        print("Cleaning up ressources.")
        self.buffer_debug.release()
        self.buffer_mesh.release()
        for str, program in self.program.items():
            program.release()

    def __del__(self):
        self.cleanup()

    ## IMGUI
    from _gui import\
        imgui_newFrame,\
        imgui_render

    ## EVENTS
    from _event import \
        resize,\
        key_event,\
        mouse_position_event,\
        mouse_drag_event,\
        mouse_scroll_event,\
        mouse_press_event,\
        mouse_release_event,\
        unicode_char_entered

def main():
    # sys.setrecursionlimit(10_000)
    MyWindow.run()

if __name__ == "__main__":
    main()
