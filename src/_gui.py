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

    c, self.wireframe = imgui.checkbox("Wireframe", self.wireframe)
    c, self.cull_face = imgui.checkbox("Cull Face", self.cull_face)

    c, self.draw_mesh = imgui.checkbox("mesh", self.draw_mesh)
    c, self.debug_active = imgui.checkbox("debug", self.debug_active)

    c, self.isGrowing = imgui.checkbox("isGrowing", self.isGrowing)
    c, self.updateTreeAndBuffer = imgui.checkbox("updateTreeAndBuffer", self.updateTreeAndBuffer)

    imgui.spacing(); imgui.spacing()
    imgui.text("Tree Settings");
    imgui.begin_group()
    c, Tree.MAX_DEPTH = imgui.slider_int(
        label="Max Depth",
        value=Tree.MAX_DEPTH,
        min_value=1,
        max_value=1000)
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
    c, Tree.GROW_SPEED = imgui.slider_float(
        label="grow speed",
        value=Tree.GROW_SPEED,
        min_value=0.001,
        max_value=0.5)
    c, Tree.OUTLINE_VISIBILITY = imgui.slider_float(
        label="outline visibility",
        value=Tree.OUTLINE_VISIBILITY,
        min_value=0.0,
        max_value=1.0)
    c, Tree.OUTLINE_THICKNESS = imgui.slider_int(
        label="outline thickness",
        value=Tree.OUTLINE_THICKNESS,
        min_value=1,
        max_value=3)
    imgui.end_group()


    imgui.spacing(); imgui.spacing()
    if imgui.button("regenerate"):
        self.tree.clear()
        self.update_tree_buffer()
    if imgui.button("grow"):
        self.tree.grow()
        self.update_tree_buffer()

    # if imgui.button("transform"):
    #     self.buffer_mesh_tf.orphan(self.tree.size() * Tree.NB_SEGMENTS * Tree.NB_FACES * 2 * 3 * 11)
    #     self.vao_tree.transform(
    #         program=self.program["TREE_TRANSFORM"],
    #         buffer=self.buffer_mesh_tf)

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
