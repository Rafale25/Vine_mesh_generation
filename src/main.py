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

from fps_counter import FpsCounter
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

# debug
global_clock = None

def START_CLOCK():
    global global_clock
    global_clock = time.time()

def STOP_CLOCK(name):
    end_time = time.time()
    print("timer {}: {:.2f}ms".format(name, (end_time - global_clock) * 1000))


class MyWindow(moderngl_window.WindowConfig):
    title = 'Tree'
    gl_version = (4, 3)
    window_size = (1920, 1080)
    fullscreen = True
    resizable = False
    vsync = True
    resource_dir = './resources'

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        imgui.create_context()
        self.imgui = ModernglWindowRenderer(self.wnd)

        self.width, self.height = self.window_size

        self.ctx.wireframe = False

        self.cull_face = True
        self.draw_skeleton = False
        self.draw_mesh = True
        # self.draw_normals = False

        self.isGrowing = False
        self.updateTreeAndBuffer = True

        # for testing
        self.color1 = vec3(0.4, 0.7, 0.0)
        self.color2 = vec3(0.3, 0.3, 0.0)

        self.query_debug_values = {}
        self.fps_counter = FpsCounter()
        self.camera = Camera()
        self.projection = glm.perspective(self.camera.fov, self.wnd.aspect_ratio, self.camera.near, self.camera.far)

        self.tree = Tree()

        self.program = {
            'TREE':
                self.load_program(
                    vertex_shader='./tree.vert',
                    geometry_shader='./tree.geom',
                    fragment_shader='./tree.frag',
                    defines={
                        'NB_SEGMENTS': Tree.NB_SEGMENTS,
                        'NB_FACES': Tree.NB_FACES}),
            'LINE':
                self.load_program(
                    vertex_shader='./line.vert',
                    fragment_shader='./line.frag'),
            'FRAMEBUFFER':
                self.load_program(
                    vertex_shader='./framebuffer.vert',
                    fragment_shader='./framebuffer.frag'),
            'TREE_OUTLINE':
                self.load_program(
                    vertex_shader='./tree_outline.vert',
                    fragment_shader='./tree_outline.frag'),
            'LINEARIZE_DEPTH':
                self.load_program('./linearize_depth.glsl'),
        }

        ## skeleton --
        self.buffer_skeleton = self.ctx.buffer(reserve=12*6)
        self.tree.clear()
        self.update_tree_buffer()


        # self.vao_tree = VAO(name="skeleton", mode=moderngl.LINES)
        # self.vao_tree = VAO(name="skeleton", mode=moderngl.LINES_ADJACENCY)
        self.vao_tree = VAO(name="mesh", mode=moderngl.TRIANGLES_ADJACENCY)
        self.vao_tree.buffer(self.buffer_skeleton, '3f', ['in_vert'])

        # self.vao_tree_skeleton = VAO(name="skeleton", mode=moderngl.LINES)
        # self.vao_tree_skeleton.buffer(self.buffer_skeleton, '3f ', ['in_vert'])
        # --

        # depth --
        self.quad_screen = geometry.quad_fs()
        self.quad_branch_color = geometry.quad_2d(size=(0.5, 0.5), pos=(-0.25, 0.75))
        self.quad_color = geometry.quad_2d(size=(0.5, 0.5), pos=(0.25, 0.75))
        self.quad_depth = geometry.quad_2d(size=(0.5, 0.5), pos=(0.75, 0.75))

        self.color_texture = self.ctx.texture(self.wnd.buffer_size, 4)
        self.branch_color_texture = self.ctx.texture(self.wnd.buffer_size, 4)
        self.depth_texture = self.ctx.depth_texture(self.wnd.buffer_size)
        self.offscreen = self.ctx.framebuffer(
            color_attachments=[
                self.color_texture,
                self.branch_color_texture,
            ],
            depth_attachment=self.depth_texture,
        )

        self.depth_sampler = self.ctx.sampler(
            filter=(moderngl.LINEAR, moderngl.LINEAR),
            compare_func='',
        )
        # --

        self.init_debug_draw()

        self.query = self.ctx.query(samples=False, time=True)

    def gen_tree_skeleton(self):
        for node in self.tree.nodes:
            # node
            yield node.pos_smooth.x
            yield node.pos_smooth.y
            yield node.pos_smooth.z

            # node parent
            yield node.parent.pos_smooth.x
            yield node.parent.pos_smooth.y
            yield node.parent.pos_smooth.z

            # parent of parent for curve
            if node.parent.parent:
                yield node.parent.parent.pos_smooth.x
                yield node.parent.parent.pos_smooth.y
                yield node.parent.parent.pos_smooth.z
            else:
                yield node.parent.pos_smooth.x
                yield node.parent.pos_smooth.y
                yield node.parent.pos_smooth.z

            # node child for curve
            if len(node.childs) > 0:
                yield node.childs[0].pos_smooth.x
                yield node.childs[0].pos_smooth.y
                yield node.childs[0].pos_smooth.z
            else:
                yield node.pos_smooth.x
                yield node.pos_smooth.y
                yield node.pos_smooth.z

            yield node.radius
            yield node.parent.radius
            yield 0

            yield 0
            yield 0
            yield 0

    def update_tree_buffer(self):
        self.buffer_skeleton.orphan(self.tree.size() * 12*6)
        data = array('f', self.gen_tree_skeleton())
        self.buffer_skeleton.write(data)

    def update_uniforms(self, frametime):
        modelview = self.camera.view_matrix()

        for str, program in self.program.items():
            if 'modelview' in program:
                program['modelview'].write(modelview)
            if 'projection' in program:
                program['projection'].write(self.projection)

        self.program['TREE']['lightPosition'].write(vec3(Light.x, Light.y, Light.z))
        # self.program["TREE"]["resolution"].write(glm.vec2(self.width, self.height))
        # for debug --
        self.program['TREE']['color1'].write(vec3(self.color1))
        self.program['TREE']['color2'].write(vec3(self.color2))

        self.program['TREE_OUTLINE']['texture0'].value = 0
        # self.program['TREE_OUTLINE']['texture1'].value = 1
        self.program['TREE_OUTLINE']['texture2'].value = 2
        self.program['TREE_OUTLINE']['resolution'].write(glm.vec2(self.width, self.height))
        # self.program['TREE_OUTLINE']['near'].value = self.camera.near
        # self.program['TREE_OUTLINE']['far'].value = self.camera.far

        self.program['LINEARIZE_DEPTH']['texture0'].value = 0
        self.program['LINEARIZE_DEPTH']['near'].value = self.camera.near
        self.program['LINEARIZE_DEPTH']['far'].value = self.camera.far

    def update(self, time_since_start, frametime):
        Light.x = cos(time_since_start*0.2) * 6.0
        Light.y = 6.0
        Light.z = sin(time_since_start*0.2) * 6.0

        self.fps_counter.update(frametime)

        if self.isGrowing:
            self.tree.grow()
            self.update_tree_buffer()

        if self.updateTreeAndBuffer:
            self.tree.update()
            data = array('f', self.gen_tree_skeleton())
            self.buffer_skeleton.write(data)

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

        self.ctx.enable_only(moderngl.CULL_FACE * self.cull_face | moderngl.DEPTH_TEST)

        self.offscreen.clear(0.2, 0.2, 0.2)
        self.offscreen.use()

        if self.draw_mesh:
            with self.query:
                self.vao_tree.render(
                    program=self.program['TREE'],
                    vertices=self.tree.size() * 6,
                    instances=Tree.NB_SEGMENTS)
            self.query_debug_values['first render'] = self.query.elapsed * 10e-7
        if self.draw_skeleton:
            self.vao_tree.render(program=self.program['LINE'], vertices=self.tree.size() * 4)
        # if self.draw_normals:
            # self.vao_mesh.render(program=self.program['TREE_NORMAL'])

        self.ctx.screen.use()
        # self.ctx.clear(0.0, 0.0, 0.0)

        self.color_texture.use(location=0)
        self.depth_texture.use(location=1)
        self.branch_color_texture.use(location=2)

        with self.query:
            self.quad_screen.render(self.program['TREE_OUTLINE'])
        self.query_debug_values['second render'] = self.query.elapsed * 10e-7

        # problem, the previous texture depth are problematic

        ## draw debugs--
        self.ctx.disable(moderngl.DEPTH_TEST)
        for node in self.tree.nodes:
            self.debug_line(*node.pos.xyz, *node.parent.pos.xyz)

        self.debug_line(0, 0, 0, 0.5, 0, 0)
        self.debug_line(0, 0, 0, 0, 0.5, 0)
        self.debug_line(0, 0, 0, 0, 0, 0.5)
        self.debug_sphere(Light.x, Light.y, Light.z, 0.5)
        self.debug_draw()

        self.branch_color_texture.use(location=0)
        self.quad_branch_color.render(self.program['FRAMEBUFFER'])

        self.color_texture.use(location=0)
        self.quad_color.render(self.program['FRAMEBUFFER'])

        self.depth_texture.use(location=0)
        # self.depth_sampler.use(location=0)  # temp override the parameters
        self.quad_depth.render(self.program['LINEARIZE_DEPTH'])
        # self.depth_sampler.clear(location=0)  # Remove the override

        self.imgui_newFrame(frametime)
        self.imgui_render()

    def cleanup(self):
        print('Cleaning up ressources.')
        self.vao_tree.release()

        self.color_texture.release()
        self.branch_color_texture.release()
        self.depth_texture.release()
        self.offscreen.release()

        self.quad_screen.release()
        self.quad_branch_color.release()
        self.quad_color.release()
        self.quad_depth.release()

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
