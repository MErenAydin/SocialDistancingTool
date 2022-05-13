#from PIL import Image, ImageOps
import cv2
from .Settings import Settings
from .Window import context
import moderngl
import numpy as np

class Texture:
	def __init__(self, rect_pos, rect_size, image_or_path = None, bg_color = (0,0,0,0),
				v_shader_path = "Shaders/texture_v.shader", f_shader_path = "Shaders/texture_f.shader"):
		
		settings = Settings()

		
		if isinstance(image_or_path, str) or image_or_path is None:
			if image_or_path is not None :
				self.__image = self.get_image_from_file(image_or_path, rect_size)
			else:
				self.__image = np.zeros((rect_size[1], rect_size[0], 4), np.uint8)
				self.__image[:,:] = bg_color
			#self.__image = ImageOps.flip(self.get_image_from_file(image_or_path, rect_size)) if image_or_path is not None else Image.new("RGBA", rect_size, bg_color)
		else:
			self.__image = image_or_path
		self.rect_pos = rect_pos
		self.rect_size = rect_size
		#self.manager = manager
		#self.font = pygame.font.Font("Font/OpenSans-Regular.ttf", 16)
		flipped_y = settings.height - rect_pos[1]

		vertices = np.array([
			rect_pos[0] + rect_size[0],	flipped_y, 				1.0, 1.0,
			rect_pos[0], 				flipped_y, 				0.0, 1.0,
			rect_pos[0], 				flipped_y - rect_size[1],	0.0, 0.0,
			rect_pos[0] + rect_size[0],	flipped_y, 				1.0, 1.0,
			rect_pos[0], 				flipped_y - rect_size[1],	0.0, 0.0,
			rect_pos[0] + rect_size[0],	flipped_y - rect_size[1],	1.0, 0.0
		])
		
		self.program = context.program( 
			vertex_shader = open(v_shader_path).read(),
			fragment_shader = open(f_shader_path).read(),
			)
			
		self.visible = True
		self.texture = context.texture(self.__image.shape[:2], 4, self.__image.tobytes())
		self.texture.write(self.__image.tobytes())
		
		self.w_size = self.program["w_size"]
		self.w_size.write(np.array([settings.width,settings.height]).astype('f4').tobytes())
		
		self.vbo = context.buffer(vertices.astype('f4').tobytes())
		self.vao = context.simple_vertex_array(self.program, self.vbo, 'in_vert', 'in_text')

		#self.manager.textures.append(self)
		
	def get_image_from_file(self, path, size):
		image = cv2.imread(path)
		image = cv2.resize(image, tuple(size))
		image = cv2.cvtColor(image, cv2.COLOR_RGB2RGBA)
		image = np.flipud(image)
		#image = Image.open(path)
		#image = image.resize(size, Image.ANTIALIAS)
		return image

	def add_image(self, img, pos):
		temp = self.image.copy()
		temp.paste(img, pos)
		self.image = temp
		
	def get_image(self):	
		return self.__image
		
	def set_image(self, value):
		self.__image = cv2.resize(value, self.rect_size[::-1])
		self.__image = cv2.cvtColor(self.__image, cv2.COLOR_BGR2RGBA)
		self.__image = np.flipud(self.__image)
		#self.__image[:,:,3] = 0
		#self.__image = ImageOps.flip(value)
		self.texture.write(self.__image.tobytes())

	image = property(get_image, set_image)
	
	def render(self):
		if self.visible:
			self.texture.use()
			self.vao.render(moderngl.TRIANGLES)