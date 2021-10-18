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

import moderngl_window
from moderngl_window.integrations.imgui import ModernglWindowRenderer
from moderngl_window.opengl.projection import Projection3D
from moderngl_window.opengl.vao import VAO
from moderngl_window import geometry

from glm import vec3, vec4
from math import pi, cos, sin, fabs
from random import uniform
from array import array

from utils import *
from _config import CameraOrbit, Camera, Light

from tree import Tree, TreeNode

"""
first pass:
    - geometry shader for the mesh
    - draw normally with colors and toons shader

    - draw to color texture (different color for every branch, passed from geometry shader)
    - draw to depth texture

seconde pass:
    add outline to texture using depth and color texture
"""

class MyWindow(moderngl_window.WindowConfig):
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
        self.projection = glm.perspective(self.camera.fov, self.wnd.aspect_ratio, self.camera.near, self.camera.far)

        self.tree = Tree()
        self.tree.generate()

        self.program = {
            "TREE":
                self.load_program(
                    vertex_shader="./tree.vert",
                    geometry_shader="./tree_normal.geom",
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

        ## skeleton --
        self.buffer_skeleton = self.ctx.buffer(data=array('f', self.gen_tree_skeleton()))

        self.vao_skeleton = VAO(name="skeleton", mode=moderngl.LINES)
        self.vao_skeleton.buffer(self.buffer_skeleton, '3f', ['in_vert'])
        # --


        ## mesh --
        # self.buffer_mesh = self.ctx.buffer(data=array('f', self.gen_tree_mesh()))

        # self.vao_mesh = VAO(name="mesh", mode=moderngl.TRIANGLES)
        # self.vao_mesh.buffer(self.buffer_mesh, '3f 3f', ['in_vert', 'in_normal'])
        # --


        # depth --
        self.quad_depth = geometry.quad_2d(size=(0.5, 0.5), pos=(0.75, 0.75))


        self.depth_texture = self.ctx.depth_texture(self.wnd.buffer_size)
        self.offscreen = self.ctx.framebuffer(
            depth_attachment=self.depth_texture,
        )

        self.geometry_program = self.load_program('geometry.glsl')

        self.linearize_depth_program = self.load_program('linearize_depth.glsl')
        self.linearize_depth_program['texture0'].value = 0
        self.linearize_depth_program['near'].value = self.camera.near
        self.linearize_depth_program['far'].value = self.camera.far
        # --

        self.init_debug_draw()

    # vertex, normals (not indices because normals need duplicated vertex data)
    def gen_tree_mesh(self, NB=16, branch_thickness=0.1):
        data = []

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

        return data

    def gen_tree_skeleton(self):
        for node in self.tree.nodes:
            yield node.pos.x
            yield node.pos.y
            yield node.pos.z

            yield node.parent.pos.x
            yield node.parent.pos.y
            yield node.parent.pos.z

    def update_uniforms(self, frametime):
        modelview = self.camera.view_matrix()

        for str, program in self.program.items():
            if 'modelview' in program:
                program['modelview'].write(modelview)
            if 'projection' in program:
                program['projection'].write(self.projection)

        self.geometry_program['modelview'].write(modelview)
        self.geometry_program['projection'].write(self.projection)

        # self.program["TREE"]["lightPosition"].write(vec3(Light.x, Light.y, Light.z))
        # self.program["TREE"]["resolution"].write(glm.vec2(self.width, self.height))
        # self.program["TREE"]['near'].value = self.camera.near
        # self.program["TREE"]['far'].value = self.camera.far

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

        self.ctx.clear(0.5, 0.5, 0.5)
        self.ctx.enable_only(moderngl.CULL_FACE * self.cull_face | moderngl.DEPTH_TEST)

        ## draw to depth_buffer --
        # self.offscreen.clear()
        # self.offscreen.use()

        # self.vao_mesh.render(program=self.geometry_program)

        # self.ctx.screen.use()

        # self.depth_texture.use(location=0)
        if self.draw_mesh:
            self.vao_skeleton.render(program=self.program["TREE"])
        # if self.draw_normals:
            # self.vao_mesh.render(program=self.program["TREE_NORMAL"])
        if self.draw_skeleton:
            self.vao_skeleton.render(program=self.program["LINE"])

        # self.debug_line(0, 0, 0, 0.5, 0, 0)
        # self.debug_line(0, 0, 0, 0, 0.5, 0)
        # self.debug_line(0, 0, 0, 0, 0, 0.5)
        # self.debug_sphere(Light.x, Light.y, Light.z, 0.5)
        # self.debug_draw()

        ## draw debug depthbuffer --
        # self.ctx.disable(moderngl.DEPTH_TEST)
        # self.quad_depth.render(self.linearize_depth_program)

        self.imgui_newFrame(frametime)
        self.imgui_render()

    def cleanup(self):
        print("Cleaning up ressources.")
        # self.buffer_skeleton.release()
        # self.buffer_mesh.release()
        # self.depth_texture.release()
        # self.offscreen.release()
        # self.geometry_program.release()
        # self.linearize_depth_program.release()

        for str, program in self.program.items():
            program.release()

    def __del__(self):
        self.cleanup()

    # DEBUG
    from _debug_draw import\
        init_debug_draw,\
        debug_line,\
        debug_sphere,\
        debug_draw

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
    MyWindow.run()

if __name__ == "__main__":
    main()

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
