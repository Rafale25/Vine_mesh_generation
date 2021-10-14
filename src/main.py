#! /usr/bin/python3

import sys
import math
import random
import struct
import time
import pathlib

from pprint import pprint

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
from _config import Camera, CameraFree

# TREE
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
		self.buffer = self.ctx.buffer(data=array('f', self.gen_tree_skeleton()))

		self.vao_lines = self.ctx.vertex_array(
			self.program["LINE"],
			[
				(self.buffer, '3f', 'in_vert'),
			],
		)
		# -----------------------------

		## mesh ----------------
		# data_vertices = []
		# data_normals = []
		# data_indices = []
		data = []

		self.gen_tree_mesh(data)
		# print(len(data_vertices))
		# print(len(data_normals))

		# self.buffer_vertices = self.ctx.buffer(data=array('f', data_vertices))
		# self.buffer_normals = self.ctx.buffer(data=array('f', data_normals))
		self.buffer = self.ctx.buffer(data=array('f', data))

		# self.buffer_indices = self.ctx.buffer(data=array('i', data_indices))


		self.vao_mesh = self.ctx.vertex_array(
			self.program["TREE"],
			[(
				# (self.buffer_vertices, '3f', 'in_vert'),
				self.buffer, '3f 3f', 'in_vert', 'in_normal',
			)],
			# self.buffer_indices
		)
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
	def gen_tree_mesh(self, data, NB=8, branch_thickness=0.05):
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

				# triangle 2
				b1 = mat_translate_parent * mat_rotate * p1
				b3 = mat_translate_self * mat_rotate * p2
				b2 = mat_translate_parent * mat_rotate * p2

				a_normal = triangle_normal(a0, a1, a2).xyz

				data.extend(a0.xyz)
				data.extend(a_normal) # one for each of the 3 vertices

				data.extend(a1.xyz)
				data.extend(a_normal) # one for each of the 3 vertices

				data.extend(a2.xyz)
				data.extend(a_normal) # one for each of the 3 vertices

				b_normal = triangle_normal(b1, b2, b3).xyz

				data.extend(b1.xyz)
				data.extend(b_normal)

				data.extend(b2.xyz)
				data.extend(b_normal)

				data.extend(b3.xyz)
				data.extend(b_normal)

	# vertex, indices
	# def gen_tree_mesh(self, vertices, indices, NB=8, branch_thickness=0.05):
	# 	## indices
	# 	total_vertices = NB*2
	#
	# 	for i in range(self.tree.size()):
	# 		start_branch_index = i*total_vertices
	#
	# 		for j in range(NB - 1):
	# 			index = start_branch_index + j*2
	#
	# 			# 2 triangles
	# 			indices.extend((index, index+1, index+2))
	# 			indices.extend((index+1, index+3, index+2))
	#
	# 		index = start_branch_index + (NB-1)*2
	# 		indices.extend((index, index+1, start_branch_index))
	# 		indices.extend((index+1, start_branch_index+1, start_branch_index))
	#
	# 	# vertices
	# 	for j, node in enumerate(self.tree.nodes):
	# 		dir = glm.sub(node.parent.pos, node.pos)
	#
	# 		mat_translate_parent = glm.translate(glm.mat4(), node.parent.pos)
	# 		mat_translate_self = glm.translate(glm.mat4(), node.pos)
	# 		mat_rotate = glm.orientation(dir, vec3(0,1,0))
	#
	# 		for i in range(NB):
	# 			angle = (math.pi*2.0 / NB) * i
	# 			x = cos(angle) * branch_thickness
	# 			z = sin(angle) * branch_thickness
	#
	# 			p = vec4(x, 0, z, 1.0)
	#
	# 			p_self = mat_translate_self * mat_rotate * p
	# 			p_parent = mat_translate_parent * mat_rotate * p
	#
	# 			vertices.extend(p_self.xyz)
	# 			vertices.extend(p_parent.xyz)


	def gen_tree_skeleton(self):
		for node in self.tree.nodes:
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
		# self.ctx.enable_only(moderngl.CULL_FACE | moderngl.DEPTH_TEST | moderngl.PROGRAM_POINT_SIZE)
		self.ctx.enable_only(moderngl.DEPTH_TEST | moderngl.PROGRAM_POINT_SIZE)

		if self.draw_debug_lines:
			self.vao_lines.render(mode=moderngl.LINES)

		self.vao_mesh.render(mode=moderngl.TRIANGLES)

		self.imgui_newFrame()
		self.imgui_render()


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
