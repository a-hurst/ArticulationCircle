import klibs

__author__ = "A Hurst"

from klibs import Params
from klibs import KLDraw as kld
from klibs import KLNumpySurface
from klibs import KLUtilities

GREY = [128,128,128]
DARKGREY = [64,64,64]
WHITE = [255,255,255]
BLACK = [0,0,0]
TOMATO_RED = [255,99,71]

class articulation_circle(klibs.Experiment):

	def __init__(self, *args, **kwargs):
		super(articulation_circle, self).__init__(*args, **kwargs)

	def setup(self):
		Params.key_maps['articulation_circle_response'] = klibs.KeyMap('articulation_circle_response', [], [], [])
		self.fixation = kld.FixationCross(25, 5, fill=DARKGREY)
		self.circle = kld.Annulus(300, 5, fill=DARKGREY)
		self.target = kld.Asterisk(25, color=TOMATO_RED, stroke=5) # Placeholder for now
		
	def block(self):
		pass

	def setup_response_collector(self):
		pass

	def trial_prep(self):
		self.clear(WHITE)
		self.any_key()

	def trial(self):

		self.blit(self.fixation, 5, Params.screen_c)
		self.blit(self.circle, 5, Params.screen_c)
		self.flip(1.000)
		
		self.blit(self.fixation, 5, Params.screen_c)
		self.blit(self.circle, 5, Params.screen_c)
		self.blit(self.target, 5, point_pos(Params.screen_c, 150, 45))
		self.flip(0.100)
		
		self.blit(self.fixation, 5, Params.screen_c)
		self.blit(self.circle, 5, Params.screen_c)
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
