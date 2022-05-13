from .TextTexture import TextTexture, Alignment
from PIL import Image, ImageFont
import math

class TextInput():
	def __init__(self, rect_pos, rect_size, viewport, text = " ", image_path = None,
				font ="Font/OpenSans-Regular.ttf", font_size = 16, text_color = (0, 0, 0),
				alignment = Alignment.LEFT, bg_color = (255, 255, 255, 255), o_width = 2):
		self.text_color = text_color
		self.__text = text
		self.viewport = viewport
		self.rect_size = rect_size
		self.rect_pos = tuple(map(lambda a,b: a+b, rect_pos, viewport.rect_pos))
		self.rect_rel_pos = rect_pos
		self.bg_color = bg_color
		self.width = o_width
		self.image_path = image_path
		self.font = ImageFont.truetype(font, font_size) if "\\" in font or "/" in font else ImageFont.load(font, font_size)
		self.__visible = True
		self.texture = TextTexture(rect_pos, rect_size, text, image_path, font, font_size, text_color, alignment,
		 				(10, (self.rect_size[1]- (sum(self.font.getmetrics())) - 1) // 2), bg_color)
		self.focused = False
		self.__clicked = False
		
		self.viewport.elements.append(self)

	def set_text(self, value):
		self.__text = value
		self.texture.text = value 
		
	def get_text(self):
		return self.__text
		
	text = property(get_text, set_text)
	
	def set_visible(self, value):
		self.__visible = value
		self.texture.visible = value
		if not self.viewport.visible:
			self.__visible = False
			self.texture.visible = False
			
	def get_visible(self):
		return self.__visible
		
	visible = property(get_visible, set_visible)

	def set_clicked(self, value):
		if (self.__clicked != value):
			self.__clicked = value
		if value:
			self.focused = True

	def get_clicked(self):
		return self.__clicked
	
	clicked = property(get_clicked, set_clicked)
		
