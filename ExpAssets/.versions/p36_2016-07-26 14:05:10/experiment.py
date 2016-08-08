import klibs

__author__ = "A Hurst"

from klibs import Params
from klibs import KLDraw as kld
from klibs import KLNumpySurface
from klibs import KLUtilities as util
from klibs.KLConstants import *
from klibs.KLEventInterface import EventTicket as ET
import random

GREY = [128,128,128]
DARKGREY = [64,64,64]
WHITE = [255,255,255]
BLACK = [0,0,0]
TOMATO_RED = [255,99,71]

circle_width = 550
circle_radius = (circle_width + 15) // 2
response_bounds = [Params.screen_c, (circle_radius - 30, circle_radius)]
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
		
		self.response_circle = kld.Annulus(circle_width + 15, 30, fill=GREY)
		
		
		
	def block(self):
		pass

	def setup_response_collector(self):
		self.rc.display_callback = self.articulation_callback
		self.rc.terminate_after = [10]
		self.rc.uses([RC_COLORSELECT])
		self.rc.color_listener.interrupts = True
		self.rc.color_listener.add_boundary("response_circle", response_bounds, ANULUS_BOUNDARY)
		self.rc.color_listener.set_target(self.response_circle, Params.screen_c, 5)

	def trial_prep(self):
		
		events = [[400, 'circle_on']]
		events.append([events[-1][0] + 600, 'target_on']) 
		events.append([events[-1][0] + int(self.duration), 'target_off'])
		events.append([events[-1][0] + 400, 'circle_off'])
		events.append([events[-1][0] + 600, 'response_circle_on'])
		for e in events:
			Params.clock.register_event(ET(e[1], e[0]))
			
		self.angle = random.choice(range(0, 359, 1))
			
		self.clear(WHITE)

	def trial(self):
		
		while self.evi.before('response_circle_on', True):
			self.fill(WHITE)
			self.blit(self.fixation, 5, Params.screen_c)
			
			if self.evi.after('circle_on', True) and self.evi.before('circle_off', True) and self.circle_type != "none":
				self.blit(self.circle, 5, Params.screen_c)
			
			if self.evi.after('target_on', True) and self.evi.before('target_off', True):
				self.blit(self.target, 5, util.point_pos(Params.screen_c, (circle_width / 2), self.angle))
				
			self.flip()
		
		self.fill(WHITE)
		self.blit(self.fixation, 5, Params.screen_c)
		
		self.rc.collect()
		
		self.fill(WHITE)
		self.blit(self.fixation, 5, Params.screen_c)
		
		self.any_key()

		return {
			"block_num": Params.block_number,
			"trial_num": Params.trial_number
		}

	def trial_clean_up(self):
		pass

	def clean_up(self):
		pass

	def articulation_callback(self):
		self.blit(self.response_circle, 5, Params.screen_c)
		self.flip()