import random
import math

import glm

from utils import *

class TreeNode:
    ID = 0

    def __init__(self, parent, pos, depth, radius=0.04, body_id=0):
        self.pos = glm.vec3(pos)
        self.pos_smooth = glm.vec3(pos)

        self.vel = glm.vec3(0, 0, 0);

        # self.radius = max(0.02, 0.2 - depth*0.005)
        self.radius = radius
        self.radius_smooth = radius

        self.depth = depth #how many nodes from root
        self.body_id = body_id

        self.parent = parent
        self.childs = []

    def length(self):
        return glm.distance(self.pos, self.parent.pos)

    def dir(self):
        return glm.normalize(glm.sub(self.pos, self.parent.pos))

    def __str__(self):
        childs = "\n".join(str(e) for e in self.childs)
        return "{}\n{}{}".format(self.depth, " "*self.depth, childs)

class Tree:
    MAX_LEN = 2.0
    MAX_DEPTH = 50
    MAX_DIVISION_DEPTH = 20
    MIN_CHILDS = 1
    MAX_CHILDS = 1
    GROW_SPEED = 0.1
    OUTLINE_VISIBILITY = 1.0
    OUTLINE_THICKNESS = 1

    # CAN NOT BE CHANGED AT RUNTIME
    NB_SEGMENTS = 8
    NB_FACES = 8

    def __init__(self):
        self.root = TreeNode(parent=None, pos=glm.vec3(0, 0, 0), depth=0)
        self.nodes = [] #[TreeNode]

    def __str__(self):
        return "\n".join(str(node) for node in self.nodes)

    def size(self):
        return len(self.nodes)

    def clear(self):
        self.root = TreeNode(parent=None, pos=glm.vec3(0, 0, 0), depth=0)
        self.nodes = []

        first_node = TreeNode(parent=self.root, pos=glm.vec3(1, 1, 0), depth=1)
        self.root.childs.append(first_node)
        self.nodes.append(first_node)

    def update(self, camera_pos):
        Tree.MAX_CHILDS = max(Tree.MAX_CHILDS, Tree.MIN_CHILDS)

        speed = 0.08
        highest_depth = self.nodes[-1].depth

        START_RADIUS = 0.05
        RADIUS_STEP = 0.015
        BIGGEST_RADIUS = RADIUS_STEP * highest_depth

        self.root.radius = START_RADIUS + BIGGEST_RADIUS
        for node in self.nodes:
            node.radius = START_RADIUS + BIGGEST_RADIUS - fclamp(node.depth * 0.02, 0.0, BIGGEST_RADIUS)
            node.radius = fclamp(node.radius, 0.0, 0.6)
            node.radius_smooth = node.radius_smooth + (node.radius - node.radius_smooth) * speed

            # node.pos_smooth = node.pos_smooth + (node.pos - node.pos_smooth) * speed
            # node.vel *= 0.97;
            # node.pos += node.vel
            node.pos_smooth = glm.vec3(node.pos)

            # dst = glm.distance(camera_pos, node.pos)
            # if (dst < 3.0):
            #     dir = node.pos - camera_pos
            #     node.vel += dir * (3.0-dst) * 0.01;


    def grow(self):
        for node in self.nodes:
            if len(node.childs) > 0 and node.length() >= Tree.MAX_LEN:
                continue

            if node.length() < Tree.MAX_LEN:
                node.pos += node.dir() * Tree.GROW_SPEED
            else:
                nb_childs = random.randint(Tree.MIN_CHILDS, Tree.MAX_CHILDS)

                if node.depth > Tree.MAX_DIVISION_DEPTH:
                    nb_childs = 1
                if node.depth > Tree.MAX_DEPTH:
                    continue

                for i in range(nb_childs):

                    # dir = glm.normalize(glm.sub(node.pos, node.parent.pos))
                    offset = random_uniform_vec3() * 0.05
                    # offset.y = math.fabs(offset.y)
                    offset += node.dir() * 0.035

                    new_child_node = TreeNode(parent=node, pos=node.pos + offset, depth=node.depth+1, body_id=node.body_id)
                    if nb_childs > 1:
                        TreeNode.ID += 1
                        new_child_node.body_id = TreeNode.ID

                    node.childs.append(new_child_node)
                    self.nodes.append(new_child_node)
