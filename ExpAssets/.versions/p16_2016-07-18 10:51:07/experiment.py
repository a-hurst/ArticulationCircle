import klibs

__author__ = "A Hurst"

from klibs import Params
from klibs import KLDraw as kld
from klibs import KLNumpySurface
from klibs import KLUtilities as util
import random

GREY = [128,128,128]
DARKGREY = [64,64,64]
WHITE = [255,255,255]
BLACK = [0,0,0]
TOMATO_RED = [255,99,71]

circle_width = 550
default_stroke = 5
articulations = [0, 45, 90, 135, 180, 225, 270, 315]

class articulation_circle(klibs.Experiment):

	def __init__(self, *args, **kwargs):
		super(articulation_circle, self).__init__(*args, **kwargs)
		
		

	def setup(self):
		Params.key_maps['articulation_circle_response'] = klibs.KeyMap('articulation_circle_response', [], [], [])
		self.fixation = kld.FixationCross(25, 4, fill=DARKGREY)
		self.circle = kld.Circle(circle_width, stroke=[default_stroke, DARKGREY, 2])
		self.target = kld.Asterisk(25, color=TOMATO_RED, stroke=default_stroke) # Placeholder for now
		self.articulation = kld.Line(25, DARKGREY, default_stroke) # For whatever reason this doesn't work, maybe bug.
		#self.articulation = kld.Rectangle(25, fill=DARKGREY, height=default_stroke)
		
		
		
	def block(self):
		pass

	def setup_response_collector(self):
		pass

	def trial_prep(self):
		self.clear(WHITE)

	def trial(self):
		
		self.angle = random.choice(range(0, 359, 1))

		self.blit(self.fixation, 5, Params.screen_c)
		self.blit(self.circle, 5, Params.screen_c)
		self.flip(1.000)
		
		self.blit(self.fixation, 5, Params.screen_c)
		self.blit(self.circle, 5, Params.screen_c)
		self.blit(self.target, 5, util.point_pos(Params.screen_c, (circle_width / 2), self.angle))
		self.flip(0.100)
		
		self.blit(self.fixation, 5, Params.screen_c)
		self.blit(self.circle, 5, Params.screen_c)
		self.flip()
		self.any_key()
		
		
		self.blit(self.articulation, 5, Params.screen_c)
		self.blit(self.circle, 5, Params.screen_c)
		for deg in articulations:
			self.blit(self.articulation, 5, util.point_pos(Params.screen_c, (circle_width / 2), deg))			
		self.flip(1.000)
		
		self.blit(self.fixation, 5, Params.screen_c)
		self.blit(self.circle, 5, Params.screen_c)
		for deg in articulations:
			self.blit(self.articulation, 5, util.point_pos(Params.screen_c, (circle_width / 2), deg))
		self.flip(0.100)
		
		self.blit(self.fixation, 5, Params.screen_c)
		self.blit(self.circle, 5, Params.screen_c)
		for deg in articulations:
				self.blit(self.articulation, 5, util.point_pos(Params.screen_c, (circle_width / 2), deg))
		self.flip()
		self.any_key()

		return {
			"block_num": Params.block_number,
			"trial_num": Params.trial_number
		}

	def trial_clean_up(self):
		pass

	def clean_up(self):
		pass
