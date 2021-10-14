import imgui

from utils import *
from _config import CameraOrbit, CameraFree

def resize(self, width: int, height: int):
	self.imgui.resize(width, height)

def key_event(self, key, action, modifiers):
	self.imgui.key_event(key, action, modifiers)

def mouse_position_event(self, x, y, dx, dy):
	self.imgui.mouse_position_event(x, y, dx, dy)

def mouse_drag_event(self, x, y, dx, dy):
	self.imgui.mouse_drag_event(x, y, dx, dy)

	io = imgui.get_io()
	if io.want_capture_mouse: return

	CameraOrbit.rotx += dx * 0.002
	CameraOrbit.roty += -dy * 0.002
	CameraOrbit.roty = fclamp(CameraOrbit.roty, -pi/2, pi/2)
	# CameraOrbit.rotx %= 2*pi

def mouse_scroll_event(self, x_offset, y_offset):
	self.imgui.mouse_scroll_event(x_offset, y_offset)

	CameraOrbit.z += y_offset * 0.1
	CameraOrbit.z = fclamp(CameraOrbit.z, -10000, 0)

def mouse_press_event(self, x, y, button):
	self.imgui.mouse_press_event(x, y, button)

def mouse_release_event(self, x: int, y: int, button: int):
	self.imgui.mouse_release_event(x, y, button)

def unicode_char_entered(self, char):
	self.imgui.unicode_char_entered(char)
