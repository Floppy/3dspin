# Taken from https://sites.google.com/site/3dprogramminginpython/

from math import sqrt

class Vector3D:
	def __init__(self, x=0.0, y=0.0, z=0.0):
		self.x = x
		self.y = y
		self.z = z

	def magnitude(self):
		return math.sqrt(self.x*self.x+self.y*self.y+self.z*self.z)

	def __sub__(self, v):
		return Vector3D(self.x-v.x, self.y-v.y, self.z-v.z)

	def normalize(self):
		mag = self.magnitude()
		if (mag > 0.0):
			self.x /= mag
			self.y /= mag
			self.z /= mag
		else:
			raise Exception('*** Vector: error, normalizing zero vector! ***')

	def cross(self, v): #cross product
		return Vector3D(self.y*v.z-self.z*v.y, self.z*v.x-self.x*v.z, self.x*v.y-self.y*v.x)


#The layout of the matrix (row- or column-major) matters only when the user reads from or writes to the matrix (indexing). For example in the multiplication function we know that the first components of the Matrix-vectors need to be multiplied by the vector. The memory-layout is not important
class Matrix:
	''' Column-major order '''

	def __init__(self, rows, cols, createidentity=True):# (2,2) creates a 2*2 Matrix
		# if rows < 2 or cols < 2:
		# 	raise Exception('*** Matrix: error, getitem((row, col)), row, col problem! ***')
		self.rows = rows
		self.cols = cols
		self.m = [[0.0]*rows for x in range(cols)]

		#If quadratic matrix then create identity one
		if self.isQuadratic() and createidentity:
			for i in range(self.rows):
				self.m[i][i] = 1.0

	def isQuadratic(self):
		return self.rows == self.cols

	def __mul__(self, right):
		if isinstance(right, Matrix):
			if self.cols == right.rows:
				r = Matrix(self.rows, right.cols, False)
				for i in range(self.rows):
					for j in range(right.cols):
						for k in range(self.cols):
							r.m[i][j] += self.m[i][k]*right.m[k][j]
				return r
			else:
				raise Exception('*** Matrix: error, matrix multiplication with incompatible matrix! ***')
		elif isinstance(right, Vector3D): #Translation: the last column of the matrix. Remains unchanged due to the the fourth coord of the vector (1).
#			if self.cols == 4:
			r = Vector3D()
			addx = addy = addz = 0.0
			if self.rows == self.cols == 4:
				addx = self.m[0][3]
				addy = self.m[1][3]
				addz = self.m[2][3]
			r.x = self.m[0][0]*right.x+self.m[0][1]*right.y+self.m[0][2]*right.z+addx
			r.y = self.m[1][0]*right.x+self.m[1][1]*right.y+self.m[1][2]*right.z+addy
			r.z = self.m[2][0]*right.x+self.m[2][1]*right.y+self.m[2][2]*right.z+addz

			#In 3D game programming we use homogenous coordinates instead of cartesian ones in case of Vectors in order to be able to use them with a 4*4 Matrix. The 4th coord (w) is not included in the Vector-class but gets computed on the fly
			if self.rows == self.cols == 4:
				w = self.m[3][0]*right.x+self.m[3][1]*right.y+self.m[3][2]*right.z+self.m[3][3]
				if (w != 1 and w != 0):
					r.x = r.x/w;
					r.y = r.y/w;
					r.z = r.z/w;
			return r
#			else:
#				raise Exception('*** Matrix: error, matrix multiplication with incompatible vector! ***')
		elif isinstance(right, int) or isinstance(right, float):
			r = Matrix(self.rows, self.cols, False)
			for i in range(self.rows):
				for j in range(self.cols):
					r.m[i][j] = self.m[i][j]*right
			return r
		else:
			raise Exception('*** Matrix: error, matrix multiply with not matrix, vector or int or float! ***')
