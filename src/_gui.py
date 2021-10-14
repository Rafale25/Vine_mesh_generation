import imgui

def imgui_newFrame(self, frametime):
	imgui.new_frame()
	imgui.begin("Properties", True)

	imgui.text("fps: {}".format(int(1.0 / frametime)))

	c, self.ctx.wireframe = imgui.checkbox("Wireframe", self.ctx.wireframe)
	c, self.cull_face = imgui.checkbox("Cull Face", self.cull_face)

	c, self.draw_debug = imgui.checkbox("debug lines", self.draw_debug)
	c, self.draw_mesh = imgui.checkbox("mesh", self.draw_mesh)

	imgui.end()

def imgui_render(self):
	imgui.render()
	self.imgui.render(imgui.get_draw_data())
