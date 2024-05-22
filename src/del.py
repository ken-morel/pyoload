from pyoload import *
import pyoload

assert pyoload.__version__ == '1.0.2'

@annotate
class foo:
	fa:'str'
	def __init__(self: 'foo', bar: Cast(dict[int, list[float]])):
		self.foo = bar
		print(bar)
		self.fa = 3


b = foo({'1':['1.0', 3]})



"""
mentor-no = 694190032
"""