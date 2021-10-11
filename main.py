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

"""
- tree
	- data structure
	- generate it

- model
	- generate it
"""

class Camera:
	z = -8.0
	rotx = 0.0
	roty = 0.0

class CameraFree:
	x = 0
	y = 0
	z = 0
	fov = 80

class TreeNode:
	def __init__(self, parent, pos):
		self.pos = pos #glm.vec3()
		self.parent = parent
		self.childs = []

	def __str__(self):
		return "[{}: {}]".format(self.pos, self.childs)

class Tree:
	MAX_LEN = 5.0
	MAX_DEPTH = 4
	MIN_CHILDS = 1
	MAX_CHILDS = 1

	def __init__(self):
		self.root = TreeNode(parent=None, pos=vec3(0, 0, 0))
		self.nodes = [] #[TreeNode]

	def __str__(self):
		return "\n".join(str(node) for node in self.nodes)

	def _generate(self, parent, n):
		if n <= 0: return
		nb_childs = random.randint(Tree.MIN_CHILDS, Tree.MAX_CHILDS)

		for i in range(nb_childs):
			offset = random_uniform_vec3()
			offset.y = fabs(offset.y)
			node = TreeNode(parent=parent, pos=parent.pos + offset)

			self._generate(parent=node, n=n-1)
			parent.childs.append(node)
			self.nodes.append(node)

	def size(self):
		return len(self.nodes) - 1

	def generate(self):
		self._generate(parent=self.root, n=Tree.MAX_DEPTH)


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

		self.tree = Tree()
		self.tree.generate()

		self.program = self.load_program(
			vertex_shader="./tree.vert",
			fragment_shader="./tree.frag")

		## LINES ----------
		self.buffer = self.ctx.buffer(reserve=(self.tree.size()+1) * 24)

		vertices = self.gen_tree_vertices()
		self.buffer.write(array('f', vertices))

		self.vao = self.ctx.vertex_array(
			self.program,
			[
				(self.buffer, '3f', 'in_vert'),
			],
			# index buffer
			# the index buffer define each triangles
		)
		# -----------------------------

		## mesh ----------------
		# self.mesh_buffer = self.ctx.buffer(reserve=24 * 1024)
		# self.mesh_buffer.write(array('f', self.gen_tree_debug_points()))
		self.mesh_buffer = self.ctx.buffer(data=array('f', self.gen_tree_debug_points()))
		self.vao_mesh = self.ctx.vertex_array(
			self.program,
			[
				(self.mesh_buffer, '3f', 'in_vert'),
			],
		)
		# ------------------

	def gen_tree_debug_points(self):
		for node in self.tree.nodes:
			# unit vector director
			dir = glm.sub(node.parent.pos, node.pos)

			mat_translate_parent = glm.translate(glm.mat4(), node.parent.pos)
			mat_translate_self = glm.translate(glm.mat4(), node.pos)
			mat_rotate = glm.orientation(dir, vec3(0,1,0))

			NB = 32
			for i in range(NB):
				angle = (math.pi*2.0 / NB) * i
				x = cos(angle) * 0.2
				z = sin(angle) * 0.2

				p = vec4(x, 0, z, 1.0)
				# p_self = mat_translate_self * p
				# p_parent = mat_translate_parent * p

				p_self = mat_translate_self * mat_rotate * p
				p_parent = mat_translate_parent * mat_rotate * p

				# p = mat_translate * mat_rotate * p

				yield p_self.x
				yield p_self.y
				yield p_self.z

				yield p_parent.x
				yield p_parent.y
				yield p_parent.z


	def gen_tree_vertices(self, ):
		for node in self.tree.nodes:
			# unit vector director
			v = glm.sub(node.parent.pos, node.pos)

			# find size of circle
			# size = 1.0

			# generate circle vertices
			yield node.pos.x
			yield node.pos.y
			yield node.pos.z

			yield node.parent.pos.x
			yield node.parent.pos.y
			yield node.parent.pos.z


	def update_uniforms(self, frametime):
		mat_rotx = glm.rotate(glm.mat4(1.0), -Camera.roty, glm.vec3(1.0, 0.0, 0.0))
		mat_roty = glm.rotate(glm.mat4(1.0), Camera.rotx, glm.vec3(0.0, 1.0, 0.0))
		mat_rotz = glm.rotate(glm.mat4(1.0), 0.0, glm.vec3(0.0, 0.0, 1.0))

		translate = glm.translate(glm.mat4(1.0), glm.vec3(0.0, 0.0, Camera.z))
		modelview = translate * mat_rotx * mat_roty * mat_rotz

		aspect_ratio = self.width / self.height
		perspective = glm.perspective(-80, aspect_ratio, 0.1, 1000)

		self.program['mvp'].write(perspective * modelview)

	def update(self, time, frametime):
		self.update_uniforms(frametime)

	def render(self, time, frametime):
		self.update(time, frametime)

		self.ctx.clear(0.0, 0.0, 0.0)
		# self.ctx.enable_only(moderngl.CULL_FACE | moderngl.DEPTH_TEST | moderngl.PROGRAM_POINT_SIZE)
		self.ctx.enable_only(moderngl.DEPTH_TEST | moderngl.PROGRAM_POINT_SIZE)


		self.vao.render(mode=moderngl.LINES)
		# self.vao_mesh.render(mode=moderngl.TRIANGLES)
		self.vao_mesh.render(mode=moderngl.POINTS)

		self.imgui_newFrame()
		self.imgui_render()


	# -------------------------------------------------------------------------
	# IMGUI
	def imgui_newFrame(self):
		imgui.new_frame()
		imgui.begin("Properties", True)

		imgui.end()

	def imgui_render(self):
		imgui.render()
		self.imgui.render(imgui.get_draw_data())

	# -------------------------------------------------------------------------
	# EVENTS
	def resize(self, width: int, height: int):
		self.imgui.resize(width, height)

	def key_event(self, key, action, modifiers):
		self.imgui.key_event(key, action, modifiers)

	def mouse_position_event(self, x, y, dx, dy):
		self.imgui.mouse_position_event(x, y, dx, dy)

	def mouse_drag_event(self, x, y, dx, dy):
		self.imgui.mouse_drag_event(x, y, dx, dy)

		Camera.rotx += dx * 0.002
		Camera.roty += -dy * 0.002

		Camera.rotx %= 2*pi
		Camera.roty = fclamp(Camera.roty, -pi/2, pi/2)

	def mouse_scroll_event(self, x_offset, y_offset):
		self.imgui.mouse_scroll_event(x_offset, y_offset)

		Camera.z += y_offset
		Camera.z = fclamp(Camera.z, -10000, 0)

	def mouse_press_event(self, x, y, button):
		self.imgui.mouse_press_event(x, y, button)

	def mouse_release_event(self, x: int, y: int, button: int):
		self.imgui.mouse_release_event(x, y, button)

	def unicode_char_entered(self, char):
		self.imgui.unicode_char_entered(char)


def main():
	# sys.setrecursionlimit(10_000)
	MyWindow.run()

if __name__ == "__main__":
	main()
