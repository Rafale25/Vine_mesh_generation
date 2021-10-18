import random
import math

import glm

from utils import *

class TreeNode:
    def __init__(self, parent, pos):
        self.pos = pos #glm.vec3()
        self.parent = parent
        self.childs = []

    def __str__(self):
        return "[{}: {}]".format(self.pos, self.childs)

class Tree:
    MAX_LEN = 5.0
    MAX_DEPTH = 3
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

    def generate(self):
        self._generate(parent=self.root, n=Tree.MAX_DEPTH)
