from math import pi, cos, sin, sqrt
from random import uniform

import glm

# def random_uniform_vec2():
# 	angle = uniform(-math.pi, math.pi);
# 	return cos(angle), sin(angle);

def triangle_normal(p1, p2, p3):
	"""
	So for a triangle p1, p2, p3,
	if the vector U = p2 - p1 and the vector V = p3 - p1
	then the normal N = U X V and can be calculated by:
	"""

	u = glm.sub(p2, p1)
	v = glm.sub(p3, p1)

	n = glm.vec3()

	n.x = u.y*v.z - u.z*v.y
	n.y = u.z*v.x - u.x*v.z
	n.z = u.x*v.y - u.y*v.x

	return n


def random_uniform_vec3():
	x, y, z = uniform(-1, 1), uniform(-1, 1), uniform(-1, 1)
	mag = sqrt(x*x + y*y + z*z)
	return glm.vec3(x/mag, y/mag, z/mag);

def degToRad(angle):
	return angle * (math.pi / 180.0)

def read_file(path):
	data = None
	with open(path, 'r') as file:
		data = file.read()
	return data

def fclamp(x, min_x, max_x):
	return (max(min(x, max_x), min_x))

# print all attributes and methods of object in console
def dump(obj):
	for attr in dir(obj):
		print("obj.%s = %r" % (attr, getattr(obj, attr)))
