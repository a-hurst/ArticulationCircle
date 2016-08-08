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

circle_width = 650
default_stroke = 5
articulation_angles = [0, 45, 90, 135, 180, 225, 270, 315]


class articulation_circle(klibs.Experiment):

	def __init__(self, *args, **kwargs):
		super(articulation_circle, self).__init__(*args, **kwargs)
		
		

	def setup(self):
		Params.key_maps['articulation_circle_response'] = klibs.KeyMap('articulation_circle_response', [], [], [])
		self.fixation = kld.FixationCross(25, 4, fill=DARKGREY)
		self.circle = kld.Ellipse(circle_width, stroke=[default_stroke, DARKGREY, 2])
		#self.circle = kld.Annulus(circle_width, stroke=[default_stroke, DARKGREY, 2])
		self.target = kld.Asterisk(25, color=TOMATO_RED, stroke=default_stroke) # Placeholder for now
		
		#self.articulations = [kld.Line(25, DARKGREY, default_stroke, i) for i in articulation_angles]
		#self.articulations = []
		#for i in articulation_angles:
		#	x = kld.Line(25, DARKGREY, default_stroke, i)
		#	self.articulations.append(x)
		
		#self.articulation_line_a = kld.Line(25, DARKGREY, default_stroke)
		#self.articulation_line_b = kld.Line(25, DARKGREY, default_stroke, 45)
		#self.articulation_line_c = kld.Line(25, DARKGREY, default_stroke, 90)
		#self.articulation_line_d = kld.Line(25, DARKGREY, default_stroke, 135)
		#self.articulation_line_e = kld.Line(25, DARKGREY, default_stroke, 180)
		#self.articulation_line_f = kld.Line(25, DARKGREY, default_stroke, 225)
		#self.articulation_line_g = kld.Line(25, DARKGREY, default_stroke, 270)
		#self.articulation_line_h = kld.Line(25, DARKGREY, default_stroke, 315)
			
		self.articulation = kld.Ellipse(25, fill=BLACK)
		
		self.response_circle = kld.Annulus(circle_width + 32, 32, fill=GREY)
		#self.response_circle = kld.Ellipse(circle_width, stroke=[25, GREY, 3])
		#self.response_circle = kld.ColorWheel(circle_width + 16)
		
		
		
	def block(self):
		pass

	def setup_response_collector(self):
		
		self.rc.display_callback = self.articulation_callback
		self.rc.terminate_after = [10]
		self.rc.uses([RC_COLORSELECT])
		self.rc.color_listener.interrupts = True
		self.rc.color_listener.add_boundary("color ring", [Params.screen_c, self.response_circle.radius - 32, self.response_circle.radius], "anulus")
		self.rc.color_listener.set_target(self.response_circle, Params.screen_c, 5)

	def trial_prep(self):
		
		events = [[400, 'circle_on']]
		events.append([events[-1][0] + 600, 'target_on']) 
		events.append([events[-1][0] + int(self.duration), 'target_off'])
		events.append([events[-1][0] + 600, 'circle_off'])
		events.append([events[-1][0] + 400, 'response_circle_on'])
		for e in events:
			Params.clock.register_event(ET(e[1], e[0]))
			
		self.angle = random.choice(range(0, 359, 1))
		self.rc.color_listener.rotation(self.angle)
		
	def trial(self):
		
		#list(self.articulations)

		while self.evi.before('response_circle_on', True):
			self.fill(WHITE)
			self.blit(self.fixation, 5, Params.screen_c)
			
			if self.evi.after('circle_on', True) and self.evi.before('circle_off', True):
				
				if self.circle_type != "none":
					self.blit(self.circle, 5, Params.screen_c)
					
					if self.circle_type == "articulated":
						for deg in articulation_angles:
							self.blit(self.articulation, 5, util.point_pos(Params.screen_c, (circle_width / 2), deg))
						
			
			if self.evi.after('target_on', True) and self.evi.before('target_off', True):
				self.blit(self.target, 5, util.point_pos(Params.screen_c, (circle_width / 2), self.angle))
				print(self.angle)
			self.flip()
		
		self.fill(WHITE)
		self.blit(self.fixation, 5, Params.screen_c)
		
		self.blit(self.response_circle, 5, Params.screen_c) # necessary due to some weird antialiasing issue.
		self.flip()
		self.blit(self.response_circle, 5, Params.screen_c)
		self.rc.collect()
		
		self.response_angle = self.rc.color_listener.response(True, False)
		
		self.fill(WHITE)
		self.blit(self.fixation, 5, Params.screen_c)
		self.flip()

		return {
			"block_num": Params.block_number,
			"trial_num": Params.trial_number,
			"circle_type": self.circle_type,
			"duration": self.duration,
			"target_loc": self.angle,
			"deg_err": self.rc.color_listener.response(True, False)
		}

	def trial_clean_up(self):
		pass

	def clean_up(self):
		pass

	def articulation_callback(self):
		self.flip()
