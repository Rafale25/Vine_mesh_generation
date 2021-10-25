import random
import math

import glm

from utils import *

class TreeNode:
    def __init__(self, parent, pos, depth):
        self.pos = glm.vec3(pos)
        self.pos_smooth = glm.vec3(pos)

        self.radius = max(0.02, 0.3 - depth*0.01)
        # self.radius = 0.15
        self.depth = depth #how many nodes from root

        self.parent = parent
        self.childs = []

    def length(self):
        return glm.distance(self.pos, self.parent.pos)

    def __str__(self):
        return "[{}: {}]".format(self.pos, self.childs)

class Tree:
    MAX_LEN = 2.0
    MAX_DEPTH = 1
    MIN_CHILDS = 1
    MAX_CHILDS = 1
    NB_SEGMENTS = 16

    def __init__(self):
        self.root = TreeNode(parent=None, pos=glm.vec3(0, 0, 0), depth=0)
        self.nodes = [] #[TreeNode]

    def __str__(self):
        return "\n".join(str(node) for node in self.nodes)

    def _generate(self, parent, n, depth=0):
        if n <= 0: return
        nb_childs = random.randint(Tree.MIN_CHILDS, Tree.MAX_CHILDS)

        for i in range(nb_childs):
            offset = random_uniform_vec3()
            offset.y = math.fabs(offset.y)
            node = TreeNode(parent=parent, pos=parent.pos + offset, depth=depth+1)

            self._generate(parent=node, n=n-1)
            parent.childs.append(node)
            self.nodes.append(node)

    def size(self):
        return len(self.nodes)

    def clear(self):
        self.root = TreeNode(parent=None, pos=glm.vec3(0, 0, 0), depth=0)
        self.nodes = [] #[TreeNode]

    def update(self):
        speed = 1.0
        for node in self.nodes:
            node.pos_smooth.x = node.pos_smooth.x + (node.pos.x - node.pos_smooth.x) * speed
            node.pos_smooth.y = node.pos_smooth.y + (node.pos.y - node.pos_smooth.y) * speed
            # node.pos_smooth.x = node.pos.x
            # node.pos_smooth.y = node.pos.y

    def grow(self):
        for node in self.nodes:
            if len(node.childs) > 0 and node.length() >= Tree.MAX_LEN:
                continue

            if node.length() < Tree.MAX_LEN:
                dir = glm.normalize(glm.sub(node.pos, node.parent.pos))
                node.pos += dir * 0.2
            else:
                nb_childs = random.randint(Tree.MIN_CHILDS, Tree.MAX_CHILDS)
                if self.size() > 20:
                    nb_childs = 1
                if node.depth > 25:
                    continue

                offset = random_uniform_vec3() * 0.1
                # offset.y = math.fabs(offset.y)

                for i in range(nb_childs):
                    new_child_node = TreeNode(parent=node, pos=node.pos + offset, depth=node.depth+1)
                    node.childs.append(new_child_node)
                    self.nodes.append(new_child_node)

    def generate(self):
        self.clear()
        self._generate(parent=self.root, n=Tree.MAX_DEPTH)
