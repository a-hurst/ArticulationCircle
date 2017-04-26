import klibs

__author__ = "A Hurst"

from klibs import Params
from klibs import KLDraw as kld
from klibs import KLNumpySurface
from klibs import KLUtilities as util
from klibs.KLConstants import *
from klibs.KLEventInterface import EventTicket as ET
from klibs import KLNumpySurface as npsurf
import math
import random
import time # for debugging missing targets
import aggdraw # only because lines aren't working


GREY = [128,128,128]
DARKGREY = [64,64,64]
LIGHTGREY = [192,192,192]
WHITE = [255,255,255]
BLACK = [0,0,0]
BLACK_MED = [0,0,0,32]
BLACK_LOW = [0,0,0,24]
TOMATO_RED = [255,99,71]
TOMATO_RED_LOW = [255,99,71,32]

circle_width = 16
default_stroke = 0.1
ring_stroke = 0.55


class ArticulationCircle(klibs.Experiment, klibs.BoundaryInspector):	
	fixation = None
	circle = None
	circle_outline = None
	target = None
	lines = []
	response_circle = None
	next_trial_circle = None
	response = None
	trial_time = None
	target_displayed = None
	target_already_on = None
	start_time = None
	elapsed = None
	deg_err = None
	angle = None
	
	debug_mode = False

	def __init__(self, *args, **kwargs):
		super(ArticulationCircle, self).__init__(*args, **kwargs)
		self.circle_width = util.deg_to_px(circle_width)
		self.ring_width = util.deg_to_px(circle_width + ring_stroke)
		self.ring_stroke = util.deg_to_px(ring_stroke)
		self.articulation_len = util.deg_to_px(3 * (ring_stroke + default_stroke))
		# ensure default stroke isn't lopsided by rounding it up to nearest multiple of 2
		self.default_stroke = int(math.ceil(float(util.deg_to_px(default_stroke)) / 2.0) * 2)
		self.fixation_width = util.deg_to_px(0.65)
		self.target_width = util.deg_to_px(0.25)
		# self.target_width_small = util.deg_to_px(0.15)
		self.nexttrial_width = util.deg_to_px(0.5)
		
		
	def setup(self):	
		Params.key_maps['articulation_circle_response'] = klibs.KeyMap('articulation_circle_response', [], [], [])
		
		self.fixation = kld.FixationCross(self.fixation_width, self.default_stroke, fill=DARKGREY).render()
		self.fixation_light = kld.FixationCross(self.fixation_width, self.default_stroke, fill=LIGHTGREY).render()
		
		self.circle = kld.Annulus(self.ring_width, self.ring_stroke, fill=WHITE).render()
		self.circle_outline = kld.Annulus(self.ring_width + self.default_stroke, self.ring_stroke + self.default_stroke, fill=DARKGREY).render()
		
		for angle in [0, 45, 90, -45]:
			if angle == 0:
				angles = [0, 180]
			if angle == 45:
				angles = [45, 225]
			if angle == 90:
				angles = [90, 270]
			if angle == -45:
				angles = [135, 325]
			line = self.line(angle, self.articulation_len, [(64,64,64), self.default_stroke]).render()
			for a in angles:
				self.lines.append([line, util.point_pos(Params.screen_c, self.circle_width / 2.0, a)])
				
		self.target_full_m = kld.Asterisk(self.target_width, color=BLACK, stroke=self.default_stroke).render()
		#self.target_full_s = kld.Asterisk(self.target_width_small, color=TOMATO_RED, stroke=self.default_stroke).render()
		self.target_med_m = kld.Asterisk(self.target_width, color=BLACK_MED, stroke=self.default_stroke).render()
		self.target_low_m = kld.Asterisk(self.target_width, color=BLACK_LOW, stroke=self.default_stroke).render()
		#self.target_low_s = kld.Asterisk(self.target_width_small, color=TOMATO_RED_LOW, stroke=self.default_stroke).render()
					
		self.response_ring = kld.Annulus(self.ring_width, self.ring_stroke, fill=GREY)
		
		self.next_trial_circle = kld.Ellipse(self.nexttrial_width, fill=DARKGREY)
		self.add_boundary("center", [Params.screen_c, self.nexttrial_width], CIRCLE_BOUNDARY)
		
		# sizes
		
		print("circle_width:", util.px_to_deg(650))
		print("ring_thickness:", util.px_to_deg(24))
		print("outer_ring_thickness:", util.px_to_deg(28))
		print("target_size:", util.px_to_deg(10))
		print("default_stroke:", util.px_to_deg(5))
		print("articulation_length:", util.px_to_deg(70))
		print("")
		print(self.circle_width)
		print(self.ring_width)
		print(self.ring_stroke)
		print(self.articulation_len)
		print(self.default_stroke, util.px_to_deg(self.default_stroke))
		print(self.fixation_width)
		print(self.target_width)
		print(self.nexttrial_width)
		

	def block(self):
		pass

	def setup_response_collector(self):
		self.rc.display_callback = self.articulation_callback
		self.rc.terminate_after = [10, TK_S]
		self.rc.uses([RC_COLORSELECT])
		self.rc.color_listener.interrupts = True
		self.rc.color_listener.add_boundary("color ring", [Params.screen_c, self.response_ring.radius - self.ring_stroke, self.response_ring.radius], "anulus")
		self.rc.color_listener.set_target(self.response_ring, Params.screen_c, 5)

	def trial_prep(self):
		events = [[400, 'circle_on']]
		print("prep circle_on")
		events.append([events[-1][0] + 600, 'target_on']) 
		print("prep target_on")
		events.append([events[-1][0] + int(self.duration), 'target_off'])
		print("prep target_off")
		events.append([events[-1][0] + 1000, 'response_circle_on'])
		print("prep response_circle)")
		for e in events:
			Params.clock.register_event(ET(e[1], e[0]))
			
		self.angle = random.choice(range(0, 360, 1))
		self.response_ring.rotation = self.angle
			
		#if self.opacity == "full":
		#	self.target = self.target_full_m if self.size == "med" else self.target_full_s
		#else:
		#	self.target = self.target_low_m if self.size == "med" else self.target_low_s
		self.target = self.target_full_m if self.opacity == "full" else self.target_med_m if self.opacity == "med" else self.target_low_m	
		self.target_displayed = "no"
		
		# enter trial with screen already at desired state
		self.fill(WHITE)
		self.blit(self.fixation_light, 5, Params.screen_c)
		self.flip()
		
		
	def trial(self):
		self.trial_time = time.time()
		self.target_already_on = False
		
		print("")
		print(self.circle_type, self.duration, self.opacity)

		while self.evi.before('circle_on', True):
			
			self.fill(WHITE)
			self.blit(self.fixation_light, 5, Params.screen_c)
			self.flip()
			
		while self.evi.before('response_circle_on', True):
			
			self.start_time = time.time()
			target_on = self.evi.after('target_on', True) and self.evi.before('target_off', True)
			circle_on = self.circle_type != "none"
			lines_on = self.circle_type == "articulated"
			self.display_refresh(circle_on, lines_on, target_on)
			
			# Debug code for target timing, disabled by default
			self.elapsed = time.time() - self.start_time
			if 0.9 < (self.start_time - self.trial_time) <= 1.100 and self.debug_mode:
				print "init: %.3f" % (self.init_time - self.trial_time)
				if lines_on:
					print "line: %.3f" % (self.line_time - self.trial_time)
				if circle_on:
					print "circle: %.3f" % (self.circle_time - self.trial_time)
				print "total: %.3f" % (self.elapsed)
					
		
		self.clear(WHITE)
		
		self.blit(self.fixation, 5, Params.screen_c)
		self.blit(self.response_ring, 5, Params.screen_c) # necessary due to some weird antialiasing issue.
		self.flip()
		if self.debug_mode:
			self.any_key() # to debug antialiasing issue with response ring
		self.blit(self.fixation, 5, Params.screen_c)
		self.blit(self.response_ring, 5, Params.screen_c)
		self.response_starttime = time.time()
		self.rc.collect()
		self.response_rt = time.time() - self.response_starttime
		
		self.response = self.rc.color_listener.response(True, False)

		try:
			self.deg_err = self.response if self.response < 180 else self.response - 360
			self.response_loc = self.angle + self.deg_err
		except TypeError:
			self.deg_err = NA
			self.response_loc = NA
		
		self.click_to_continue()

		return {
			"block_num": Params.block_number,
			"trial_num": Params.trial_number,
			"circle_type": self.circle_type,
			"opacity": self.opacity,
			"duration": self.duration,
			"rt": self.response_rt, #self.rc.color_listener.response(False, True),
			"target_displayed": self.target_displayed,
			"target_loc": self.angle,
			"response_loc": self.response_loc,
			"deg_err": self.deg_err
		}
	
	def display_refresh(self, circle=False, lines=False, target=False):	
		self.fill(WHITE)
		self.blit(self.fixation, 5, Params.screen_c)
		self.init_time = time.time() # for debug
		
		if lines:
			for l in self.lines:
				self.blit(l[0], 5, l[1])
			self.line_time = time.time() # for debug

		if circle:
			self.blit(self.circle_outline, 5, Params.screen_c)
			self.blit(self.circle, 5, Params.screen_c)
			self.circle_time = time.time() # for debug
		
		if target:
			line_pos = util.point_pos(Params.screen_c, (self.circle_width / 2), self.angle)
			self.blit(self.target, 5, line_pos)
			self.target_displayed = "yes"
		self.flip()
		
	
		if target and not self.target_already_on:
			self.target_ontime = time.time()
			print "target on: %.3f" % (self.target_ontime - self.trial_time)
			self.target_already_on = True	
		if not target and self.target_already_on:
			print "total target on-time: %.3f \n" % (time.time() - self.target_ontime)
			self.target_already_on = False


	def trial_clean_up(self):
		pass


	def clean_up(self):
		pass


	def articulation_callback(self):
		self.flip()
		
		
	def click_to_continue(self):		
		self.fill(WHITE)
		self.blit(self.next_trial_circle, 5, Params.screen_c)
		self.flip()
		
		util.show_mouse_cursor()
		
		wait_for_click = True
		while wait_for_click:
			for e in util.pump(True):
				if e.type == sdl2.SDL_MOUSEBUTTONUP:
					pos = [e.button.x, e.button.y]
					if self.within_boundary("center", pos):
						self.fill(WHITE)
						self.flip()
						wait_for_click = False
						
		util.hide_mouse_cursor()
					
						
	def line(self, rotation, canvas_width, stroke):
		start = (0, 0)
		end = (canvas_width, canvas_width)
		
		canvas_center = (canvas_width // 2, canvas_width // 2)
		surface_width = canvas_width
		
		if rotation % 90 != 0:
			start = util.point_pos(canvas_center, canvas_width // 2, rotation)
			end = util.point_pos(canvas_center, canvas_width // 2, rotation - 180)
		if rotation in [90, 270]:
			start = (canvas_width // 2, 0)
			end = (canvas_width // 2, canvas_width)
		if rotation in [0, 180]:
			start = (0, canvas_width // 2)
			end = (canvas_width, canvas_width // 2)
    	
		surf = aggdraw.Draw("RGBA", [canvas_width, canvas_width], (0, 0, 0, 0))
		surf.setantialias(True)
		p_str = "M{0} {1} L{2} {3}".format(*start+end)
		sym = aggdraw.Symbol(p_str)
		surf.symbol((0, 0), sym, aggdraw.Pen(*stroke))
		line_numpy = npsurf.aggdraw_to_numpy_surface(surf)
		return line_numpy
		
