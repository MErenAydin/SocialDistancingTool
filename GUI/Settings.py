import json

class Singleton (type):
	_instances = {}
	def __call__(cls, *args, **kwargs):
		if cls not in cls._instances:
			cls._instances[cls] = super(Singleton, cls).__call__(*args, **kwargs)
		return cls._instances[cls]

class Settings(metaclass = Singleton):
	def __init__(self):
		settings = {}
		try:
			settings = json.loads(open("settings.json", "r").read())
		except FileNotFoundError:
			#Initial Settings
			settings = {
				"window_title" : "Social Distancing Tool",
				"screen_size" : (1280, 720),
				"init_obj_path" : "Template/test.stl",
				"obj_alpha": 1,
				"render_grid": False,
				"render_empty": False,
				"render_cylinder": False,
				"camera_pos": [9.4, -22.5 , 9.45],
				"camera_fov": 20,
				"use_gpu": True,
    			"min_distance_m": 2.0,
    			"min_confidence": 0.3,
    			"nms_treshold": 0.3,
				"debug": False
			}
		
			open("settings.json", "w").write(json.dumps(settings, indent=4, sort_keys=True))
		except Exception as e:
			print(type(e).__name__, e.args)

		self.window_title = settings["window_title"]
		self.width, self.height = settings["screen_size"]
		self.init_obj_path = settings["init_obj_path"]
		self.obj_alpha = settings["obj_alpha"]
		self.render_grid =  settings["render_grid"]
		self.render_empty = settings["render_empty"]
		self.render_cylinder = settings["render_cylinder"]
		self.camera_pos = settings["camera_pos"]
		self.camera_fov = settings["camera_fov"]
		self.use_gpu = settings["use_gpu"]
		self.min_distance_m = settings["min_distance_m"]
		self.min_confidence = settings["min_confidence"]
		self.nms_treshold = settings["nms_treshold"]
		self.debug = settings["debug"]