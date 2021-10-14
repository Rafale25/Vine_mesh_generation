import imgui

def imgui_newFrame(self):
	imgui.new_frame()
	imgui.begin("Properties", True)

	c, self.draw_debug_lines = imgui.checkbox("debug lines", self.draw_debug_lines)
	c, self.ctx.wireframe = imgui.checkbox("Wireframe", self.ctx.wireframe)

	imgui.end()

def imgui_render(self):
	imgui.render()
	self.imgui.render(imgui.get_draw_data())
