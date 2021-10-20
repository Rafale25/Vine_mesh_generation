import random
import math

import glm

from utils import *

class TreeNode:
    def __init__(self, parent, pos):
        self.pos = glm.vec3(pos) #glm.vec3()
        self.pos_smooth = glm.vec3(pos) #glm.vec3()

        self.parent = parent
        self.childs = []

    def __str__(self):
        return "[{}: {}]".format(self.pos, self.childs)

class Tree:
    MAX_LEN = 5.0
    MAX_DEPTH = 4
    MIN_CHILDS = 2
    MAX_CHILDS = 2

    def __init__(self):
        self.root = TreeNode(parent=None, pos=glm.vec3(0, 0, 0))
        self.nodes = [] #[TreeNode]

    def __str__(self):
        return "\n".join(str(node) for node in self.nodes)

    def _generate(self, parent, n):
        if n <= 0: return
        nb_childs = random.randint(Tree.MIN_CHILDS, Tree.MAX_CHILDS)

        for i in range(nb_childs):
            offset = random_uniform_vec3()
            offset.y = math.fabs(offset.y)
            node = TreeNode(parent=parent, pos=parent.pos + offset)

            self._generate(parent=node, n=n-1)
            parent.childs.append(node)
            self.nodes.append(node)

    def size(self):
        return len(self.nodes)

    def clear(self):
        self.root = TreeNode(parent=None, pos=glm.vec3(0, 0, 0))
        self.nodes = [] #[TreeNode]

    def update(self):
        for node in self.nodes:
            node.pos_smooth.x = node.pos_smooth.x + (node.pos.x - node.pos_smooth.x) * 0.07
            node.pos_smooth.y = node.pos_smooth.y + (node.pos.y - node.pos_smooth.y) * 0.07

    def grow(self):
        for node in self.nodes:
            v = random_uniform_vec3() * 1.0
            v.y = abs(v.y)
            node.pos += v

    def generate(self):
        self.clear()
        self._generate(parent=self.root, n=Tree.MAX_DEPTH)
