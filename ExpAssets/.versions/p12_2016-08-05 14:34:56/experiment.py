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


class articulation_circle(klibs.Experiment, klibs.BoundaryInspector):

	def __init__(self, *args, **kwargs):
		super(articulation_circle, self).__init__(*args, **kwargs)
		
		

	def setup(self):
		Params.key_maps['articulation_circle_response'] = klibs.KeyMap('articulation_circle_response', [], [], [])
		self.fixation = kld.FixationCross(25, 4, fill=DARKGREY).render()
		#self.circle = kld.Ellipse(circle_width, stroke=[default_stroke, DARKGREY, 2])
		self.circle = kld.Annulus(circle_width + 24, 24, fill=WHITE).render()
		self.circle_outline = kld.Annulus(circle_width + 28, 28, fill=DARKGREY).render()
		#self.articulation = kld.Ellipse(70, fill=LIGHTGREY)
		self.target = kld.Asterisk(10, color=TOMATO_RED, stroke=default_stroke).render() # Placeholder for now
		self.lines = []
		for angle in [90,45,0, -45]:
			if angle == 90:
				angles = [90, 270]
			if angle == 45:
				angles == [45, 225]
			if angles == -45:
				angles = [135, 325]		
			line = self.line(angle, articulation_length, [(64,64,64), default_stroke]).render()
			for a in angles:
				self.lines.append([line, util.point_pos(Params.screen_c, circle_width / 2.0, a)])
			
# 		self.line_0 = 
# 		self.line_45 = self.line(45, articulation_length, [(64,64,64), default_stroke]).render()
# 		self.line_90 = self.line(0, articulation_length, [(64,64,64), default_stroke]).render()
# 		self.line_135 = self.line(-45, articulation_length, [(64,64,64), default_stroke]).render()
# 		
		#self.line_0 = kld.NewNewLine(articulation_length, DARKGREY, default_stroke, 90)
		#self.line_45 = kld.NewNewLine(articulation_length, DARKGREY, default_stroke, 45)
		#self.line_90 = kld.NewNewLine(articulation_length, DARKGREY, default_stroke, 0)
		#self.line_135 = kld.NewNewLine(articulation_length, DARKGREY, default_stroke, 135)
		
		
		self.response_circle = kld.Annulus(circle_width + 24, 24, fill=GREY)
		
		self.nexttrial_circle = kld.Ellipse(20, fill=DARKGREY)
		self.add_boundary("center", [Params.screen_c, 20], CIRCLE_BOUNDARY)
		
		
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

		while self.evi.before('circle_on', True):
			self.display_refresh()
			
		while self.evi.before('circle_off', True):
			target_on = self.evi.after('target_on', True) and self.evi.before('target_off', True)
			circle_on = self.circle_type != "none"
			lines_on = self.circle_type == "articulated"
			self.display_refresh(circle_on, lines_on, target_on)
		
		self.clear(WHITE)
		self.blit(self.fixation, 5, Params.screen_c)
		self.blit(self.response_circle, 5, Params.screen_c) # necessary due to some weird antialiasing issue.
		self.flip()
		self.blit(self.fixation, 5, Params.screen_c)
		self.blit(self.response_circle, 5, Params.screen_c)
		self.rc.collect()
		
		self.response = self.rc.color_listener.response(True, False)
		self.deg_err = self.response if self.response < 180 else self.response - 360
		
		self.click_to_continue()
		
		self.blit(self.line_90, 5, Params.screen_c)
		

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
		#line_pos = util.point_pos(Params.screen_c, (circle_width / 2), deg)
		if lines:
			for l in self.lines:
				self.blit(l[0], 5, l[1])
# 			for deg in articulation_angles:
# 			self.blit(self.articulation, 5, util.point_pos(Params.screen_c, (circle_width / 2), deg))
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
		
		if target:
			line_pos = util.point_pos(Params.screen_c, (circle_width / 2), self.angle)
			self.blit(self.target, 5, line_pos)
			print(self.angle)
			self.target_displayed = "yes"
		self.flip()


	def trial_clean_up(self):
		pass

	def clean_up(self):
		pass

	def articulation_callback(self):
		self.flip()
		
	def click_to_continue(self):
		self.fill(WHITE)
		self.blit(self.nexttrial_circle, 5, Params.screen_c)
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
		if rotation in [0, 180]:
			start = (canvas_width // 2, 0)
			end = (canvas_width // 2, canvas_width)
		if rotation in [90, 270]:
			start = (0, canvas_width // 2)
			end = (canvas_width, canvas_width // 2)
    	
		surf = aggdraw.Draw("RGBA", [canvas_width, canvas_width], (0, 0, 0, 0))
		surf.setantialias(True)
		p_str = "M{0} {1} L{2} {3}".format(*start+end)
		sym = aggdraw.Symbol(p_str)
		surf.symbol((0, 0), sym, aggdraw.Pen(*stroke))
		line_numpy = npsurf.aggdraw_to_numpy_surface(surf)
		return line_numpy
		
