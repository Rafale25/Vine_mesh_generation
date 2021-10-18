#! /usr/bin/python3

import moderngl
from pyrr import Matrix44
import moderngl_window
from moderngl_window import geometry
from moderngl_window.opengl.projection import Projection3D

class FragmentPicking(moderngl_window.WindowConfig):
    title = "Depth Test"
    gl_version = 3, 3
    window_size = 1280, 720
    aspect_ratio = None
    resizable = True
    resource_dir = "./ressources_test"

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        # Object rotation
        self.x_rot = 0
        self.y_rot = 0
        # Object position
        self.zoom = 0

        # Load scene cached to speed up loading!
        self.scene = self.load_scene('centered.obj', cache=True)
        # Grab the raw mesh/vertexarray
        self.mesh = self.scene.root_nodes[0].mesh.vao

        self.projection = Projection3D(
            fov=60,
            aspect_ratio=self.wnd.aspect_ratio,
            near=1.0,
            far=100.0,
        )

        # --- Offscreen render target
        # Texture for storing depth values
        self.offscreen_depth = self.ctx.depth_texture(self.wnd.buffer_size)
        self.offscreen = self.ctx.framebuffer(
            depth_attachment=self.offscreen_depth,
        )

        # A fullscreen quad just for rendering offscreen textures to the window
        self.quad_fs = geometry.quad_fs()

        # --- Shaders
        # Geomtry shader writing to two offscreen layers (color, normal) + depth
        self.geometry_program = self.load_program('geometry.glsl')

        # Shader for linearizing depth (debug visualization)
        self.linearize_depth_program = self.load_program('linearize_depth.glsl')
        self.linearize_depth_program['texture0'].value = 0
        self.linearize_depth_program['near'].value = self.projection.near
        self.linearize_depth_program['far'].value = self.projection.far

        self.quad_depth = geometry.quad_fs()

    def render(self, time, frametime):
        self.ctx.enable(moderngl.DEPTH_TEST | moderngl.CULL_FACE)

        translation = Matrix44.from_translation((0, 0, -45 + self.zoom), dtype='f4')
        rotation = Matrix44.from_eulers((self.y_rot, self.x_rot, 0), dtype='f4')
        modelview = translation * rotation

        # Render the scene to offscreen buffer
        self.offscreen.clear()
        self.offscreen.use()

        # Render the scene
        self.geometry_program['modelview'].write(modelview)
        self.geometry_program['projection'].write(self.projection.matrix)
        self.mesh.render(self.geometry_program)  # render mesh

        # Activate the window as the render target
        self.ctx.screen.use()
        # self.ctx.disable(moderngl.DEPTH_TEST)

        self.offscreen_depth.use(location=0)  # bind depth sampler to channel 0
        self.quad_depth.render(self.linearize_depth_program)


    def mouse_drag_event(self, x, y, dx, dy):
        self.x_rot -= dx / 100
        self.y_rot -= dy / 100

    def mouse_scroll_event(self, x_offset, y_offset):
        self.zoom += y_offset

if __name__ == '__main__':
    moderngl_window.run_window_config(FragmentPicking)
