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

	z_smooth = z
	rotx_smooth = rotx
	roty_smooth = roty

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
	MAX_DEPTH = 5
	MIN_CHILDS = 2
	MAX_CHILDS = 2

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
		return len(self.nodes)

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

		self.draw_debug_lines = True
		self.wireframe = False

		self.tree = Tree()
		self.tree.generate()


		self.program = {
			"TREE":
				self.load_program(
					vertex_shader="./tree.vert",
					fragment_shader="./tree.frag"),
			"LINE":
				self.load_program(
					vertex_shader="./line.vert",
					fragment_shader="./line.frag"),
		}

		## LINES ----------
		# self.buffer = self.ctx.buffer(reserve=(self.tree.size()) * 24)
		self.buffer = self.ctx.buffer(data=array('f', self.gen_tree_vertices()))

		self.vao_lines = self.ctx.vertex_array(
			self.program["LINE"],
			[
				(self.buffer, '3f', 'in_vert'),
			],
		)
		# -----------------------------

		## mesh ----------------
		data_vertices = []
		data_indices = []
		self.gen_tree_mesh_indices(data_vertices, data_indices)

		self.buffer_vertices = self.ctx.buffer(data=array('f', data_vertices))
		# self.buffer_normals = self.ctx.buffer(data=array('i', data_indices))
		self.buffer_indices = self.ctx.buffer(data=array('i', data_indices))

		self.vao_mesh = self.ctx.vertex_array(
			self.program["TREE"],
			[
				(self.buffer_vertices, '3f', 'in_vert'),
				# (self.buffer_normals, '3f', 'in_normal'),
			],
			self.buffer_indices
		)
		# ------------------
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
#
# """

	def gen_tree_mesh_indices(self, vertices, indices, NB=8, branch_thickness=0.05):
		## indices
		total_vertices = NB*2

		for i in range(self.tree.size()):
			start_branch_index = i*total_vertices

			for j in range(NB - 1):
				index = start_branch_index + j*2

				# 2 triangles
				indices.extend((index, index+1, index+2))
				indices.extend((index+1, index+3, index+2))

			index = start_branch_index + (NB-1)*2
			indices.extend((index, index+1, start_branch_index))
			indices.extend((index+1, start_branch_index+1, start_branch_index))

		# vertices
		for j, node in enumerate(self.tree.nodes):
			dir = glm.sub(node.parent.pos, node.pos)

			mat_translate_parent = glm.translate(glm.mat4(), node.parent.pos)
			mat_translate_self = glm.translate(glm.mat4(), node.pos)
			mat_rotate = glm.orientation(dir, vec3(0,1,0))

			for i in range(NB):
				angle = (math.pi*2.0 / NB) * i
				x = cos(angle) * branch_thickness
				z = sin(angle) * branch_thickness

				p = vec4(x, 0, z, 1.0)

				p_self = mat_translate_self * mat_rotate * p
				p_parent = mat_translate_parent * mat_rotate * p

				vertices.extend(p_self.xyz)
				vertices.extend(p_parent.xyz)



	def gen_tree_vertices(self, ):
		for node in self.tree.nodes:
			# unit vector director
			# dir = glm.sub(node.parent.pos, node.pos)

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
		mat_rotx = glm.rotate(glm.mat4(1.0), -Camera.roty_smooth, glm.vec3(1.0, 0.0, 0.0))
		mat_roty = glm.rotate(glm.mat4(1.0), Camera.rotx_smooth, glm.vec3(0.0, 1.0, 0.0))
		mat_rotz = glm.rotate(glm.mat4(1.0), 0.0, glm.vec3(0.0, 0.0, 1.0))

		translate = glm.translate(glm.mat4(1.0), glm.vec3(0.0, 0.0, Camera.z_smooth))
		modelview = translate * mat_rotx * mat_roty * mat_rotz

		aspect_ratio = self.width / self.height
		perspective = glm.perspective(-80, aspect_ratio, 0.1, 1000)

		self.program['TREE']['mvp'].write(perspective * modelview)

	def update(self, time, frametime):
		self.update_uniforms(frametime)

		Camera.z_smooth = Camera.z_smooth + (Camera.z - Camera.z_smooth) * 0.5
		Camera.rotx_smooth = Camera.rotx_smooth + (Camera.rotx - Camera.rotx_smooth) * 0.5
		Camera.roty_smooth = Camera.roty_smooth + (Camera.roty - Camera.roty_smooth) * 0.5

	def render(self, time, frametime):
		self.update(time, frametime)

		self.ctx.clear(0.0, 0.0, 0.0)
		self.ctx.enable_only(moderngl.DEPTH_TEST | moderngl.PROGRAM_POINT_SIZE)
		# self.ctx.enable_only(moderngl.DEPTH_TEST | moderngl.PROGRAM_POINT_SIZE)
		# self.ctx.wireframe = True
		# self.ctx.cull_face = True

		if self.draw_debug_lines:
			self.vao_lines.render(mode=moderngl.LINES)

		self.vao_mesh.render(mode=moderngl.TRIANGLES)

		self.imgui_newFrame()
		self.imgui_render()


	# -------------------------------------------------------------------------
	# IMGUI
	def imgui_newFrame(self):
		imgui.new_frame()
		imgui.begin("Properties", True)

		c, self.draw_debug_lines = imgui.checkbox("debug lines", self.draw_debug_lines)
		c, self.ctx.wireframe = imgui.checkbox("Wireframe", self.ctx.wireframe)

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

		# Camera.rotx %= 2*pi
		Camera.roty = fclamp(Camera.roty, -pi/2, pi/2)

	def mouse_scroll_event(self, x_offset, y_offset):
		self.imgui.mouse_scroll_event(x_offset, y_offset)

		Camera.z += y_offset * 0.1
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
