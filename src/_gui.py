import imgui
from tree import Tree

def imgui_newFrame(self, frametime):
    imgui.new_frame()
    imgui.begin("Properties", True)

    imgui.text("fps: {:.2f}".format(self.fps_counter.get_fps()))
    for query, value in self.query_debug_values.items():
        imgui.text("{}: {:.2f} ms".format(query, value))

    imgui.text("branches: {}".format(self.tree.size()))

    imgui.spacing(); imgui.spacing()

    c, self.ctx.wireframe = imgui.checkbox("Wireframe", self.ctx.wireframe)
    c, self.cull_face = imgui.checkbox("Cull Face", self.cull_face)

    c, self.draw_mesh = imgui.checkbox("mesh", self.draw_mesh)
    c, self.draw_skeleton = imgui.checkbox("skeleton", self.draw_skeleton)
    # c, self.draw_normals = imgui.checkbox("normals", self.draw_normals)

    c, self.isGrowing = imgui.checkbox("isGrowing", self.isGrowing)
    c, self.updateTreeAndBuffer = imgui.checkbox("updateTreeAndBuffer", self.updateTreeAndBuffer)

    imgui.spacing(); imgui.spacing()
    imgui.text("Tree Settings");
    imgui.begin_group()
    c, Tree.MAX_DEPTH = imgui.slider_int(
        label="Max Depth",
        value=Tree.MAX_DEPTH,
        min_value=1,
        max_value=100)
    c, Tree.MAX_DIVISION_DEPTH = imgui.slider_int(
        label="Max division depth",
        value=Tree.MAX_DIVISION_DEPTH,
        min_value=1,
        max_value=100)
    c, Tree.MIN_CHILDS = imgui.slider_int(
        label="Min childs",
        value=Tree.MIN_CHILDS,
        min_value=1,
        max_value=4)
    c, Tree.MAX_CHILDS = imgui.slider_int(
        label="Max childs",
        value=Tree.MAX_CHILDS,
        min_value=1,
        max_value=4)
    imgui.end_group()

    imgui.spacing(); imgui.spacing()
    if imgui.button("regenerate"):
        self.tree.clear()
        self.update_tree_buffer()
    if imgui.button("grow"):
        self.tree.grow()
        self.update_tree_buffer()

    c, self.color1 = imgui.color_edit3(
        "color 1", *self.color1
    )
    c, self.color2 = imgui.color_edit3(
        "color 2", *self.color2
    )

    imgui.end()

def imgui_render(self):
    imgui.render()
    self.imgui.render(imgui.get_draw_data())
