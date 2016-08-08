import klibs

__author__ = "A Hurst"

from klibs import Params
from klibs import KLDraw as kld
from klibs import KLNumpySurface
from klibs import KLUtilities as util
from klibs.KLConstants import *
from klibs.KLEventInterface import EventTicket as ET
from klibs import KLNumpySurface as npsurf
import random
import time # for debugging missing targets
import aggdraw # only because lines aren't working


GREY = [128,128,128]
DARKGREY = [64,64,64]
LIGHTGREY = [192,192,192]
WHITE = [255,255,255]
BLACK = [0,0,0]
TOMATO_RED = [255,99,71]

circle_width = 650
default_stroke = 5
articulation_length = 70
articulation_colour = TOMATO_RED


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

	def __init__(self, *args, **kwargs):
		super(ArticulationCircle, self).__init__(*args, **kwargs)
		
	def setup(self):
		Params.key_maps['articulation_circle_response'] = klibs.KeyMap('articulation_circle_response', [], [], [])
		self.fixation = kld.FixationCross(25, 4, fill=DARKGREY).render()
		#self.circle = kld.Ellipse(circle_width, stroke=[default_stroke, DARKGREY, 2])
		self.circle = kld.Annulus(circle_width + 24, 24, fill=WHITE).render()
		self.circle_outline = kld.Annulus(circle_width + 28, 28, fill=DARKGREY).render()
		#self.articulation = kld.Ellipse(70, fill=LIGHTGREY)
		self.target = kld.Asterisk(10, color=TOMATO_RED, stroke=default_stroke).render()
		for angle in [0, 45, 90, -45]:
			if angle == 0:
				angles = [0, 180]
			if angle == 45:
				angles = [45, 225]
			if angle == 90:
				angles = [90, 270]
			if angle == -45:
				angles = [135, 325]
			line = self.line(angle, articulation_length, [(64,64,64), default_stroke]).render()
			for a in angles:
				self.lines.append([line, util.point_pos(Params.screen_c, circle_width / 2.0, a)])
		self.response_circle = kld.Annulus(circle_width + 24, 24, fill=GREY)
		
		self.next_trial_circle = kld.Ellipse(20, fill=DARKGREY)
		self.add_boundary("center", [Params.screen_c, 20], CIRCLE_BOUNDARY)

	def block(self):
		pass

	def setup_response_collector(self):
		self.rc.display_callback = self.articulation_callback
		self.rc.terminate_after = [10, TK_S]
		self.rc.uses([RC_COLORSELECT])
		self.rc.color_listener.interrupts = True
		self.rc.color_listener.add_boundary("color ring", [Params.screen_c, self.response_circle.radius - 32, self.response_circle.radius], "anulus")
		self.rc.color_listener.set_target(self.response_circle, Params.screen_c, 5)

	def trial_prep(self):
		
		events = [[400, 'circle_on']]
		events.append([events[-1][0] + 600, 'target_on']) 
		events.append([events[-1][0] + int(self.duration), 'target_off'])
		#events.append([events[-1][0] + 500, 'target_off']) # for debugging target location
		events.append([events[-1][0] + 600, 'circle_off'])
		events.append([events[-1][0] + 800, 'response_circle_on'])
		for e in events:
			Params.clock.register_event(ET(e[1], e[0]))
			
		self.angle = random.choice(range(0, 359, 1))
		self.response_circle.rotation = self.angle
		self.target_displayed = "no"
		
		# enter trial with screen already at desired state
		self.fill(WHITE)
		self.blit(self.fixation, 5, Params.screen_c)
		self.flip()
		
	def trial(self):

		self.trial_time = time.time()
		self.target_displayed = "no"
		self.target_already_on = False
		
		print(self.circle_type, self.duration)

		while self.evi.before('circle_on', True):
			self.display_refresh()
			
		while self.evi.before('circle_off', True):
			self.start_time = time.time()
			target_on = self.evi.after('target_on', True) and self.evi.before('target_off', True)
			#target_on = 1 < (self.start_time - self.trial_time) <= 1.050
			if target_on:
				print "target on! %.3f" % (time.time() - self.trial_time)
			circle_on = self.circle_type != "none"
			lines_on = self.circle_type == "articulated"
			self.display_refresh(circle_on, lines_on, target_on)
			self.elapsed = time.time() - self.start_time
			#if self.elapsed >= 0.020:
			if 0.9 < (self.start_time - self.trial_time) <= 1.100:
				print "init: %.3f" % (self.init_time - self.trial_time)
				if lines_on:
					print "line: %.3f" % (self.line_time - self.trial_time)
				if circle_on:
					print "circle: %.3f" % (self.circle_time - self.trial_time)
				print "total: %.3f" % (self.elapsed)
					
		
		while self.evi.before('response_circle_on', True):
			self.display_refresh()
		
		self.blit(self.fixation, 5, Params.screen_c)
		self.blit(self.response_circle, 5, Params.screen_c) # necessary due to some weird antialiasing issue.
		self.flip()
		self.blit(self.fixation, 5, Params.screen_c)
		self.blit(self.response_circle, 5, Params.screen_c)
		self.rc.collect()
		self.fill()
		self.flip()
		
		self.response = self.rc.color_listener.response(True, False)

		try:
			self.deg_err = self.response if self.response < 180 else self.response - 360
		except TypeError:
			self.deg_err = NA
		
		self.click_to_continue()
		
		#self.blit(self.line_90, 5, Params.screen_c)
		

		return {
			"block_num": Params.block_number,
			"trial_num": Params.trial_number,
			"circle_type": self.circle_type,
			"duration": self.duration,
			"rt": self.rc.color_listener.response(False, True),
			"target_displayed": self.target_displayed,
			"target_loc": self.angle,
			"response_loc": self.response,
			"deg_err": self.deg_err
		}
	
	def display_refresh(self, circle=False, lines=False, target=False):
		self.fill(WHITE)
		self.blit(self.fixation, 5, Params.screen_c)
		self.init_time = time.time()
		
		if lines:
			for l in self.lines:
				self.blit(l[0], 5, l[1])
			self.line_time = time.time()
# 			for deg in [0, 180]:
# 				self.blit(self.line_0, 5, line_pos)
# 			for deg in [45, 225]:
# 				self.blit(self.line_45, 5, line_pos)
# 			for deg in [90, 270]:
# 				self.blit(self.line_90, 5, line_pos)
# 			for deg in [135, 315]:
# 				self.blit(self.line_135, 5, line_pos)

		if circle:
			self.blit(self.circle_outline, 5, Params.screen_c)
			self.blit(self.circle, 5, Params.screen_c)
			self.circle_time = time.time()
		
		#before_target = time.time()
		if target:
			line_pos = util.point_pos(Params.screen_c, (circle_width / 2), self.angle)
			self.blit(self.target, 5, line_pos)
			#after_target = time.time()
			#print(self.angle)
			#print("Loop time after target:", after_target - start)
			#print("Loop time to draw target:", after_target - before_target)
			self.target_displayed = "yes"
		self.flip()
		if target and not self.target_already_on:
			self.target_ontime = time.time()
			self.target_already_on = True
		if not target and self.target_already_on:
			print "total target on-time: %.3f" % (time.time() - self.target_ontime)
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
		#self.blit(self.articulation, 5, Params.screen_c)
		#self.blit(self.line_0, 5, Params.screen_c)
		#self.blit(self.line_45, 5, Params.screen_c)
		#self.blit(self.line_90, 5, Params.screen_c)
		#self.blit(self.line_135, 5, Params.screen_c)
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
		surface_width = canvas_width #+ int(round(stroke[1] // 2))
		
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
		
