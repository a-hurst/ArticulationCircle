__author__ = "A Hurst"

# Import required KLibs functions and objects

from klibs.KLConstants import *
from klibs import P
from klibs.KLKeyMap import KeyMap
from klibs import KLUtilities as util
from klibs.KLUserInterface import ui_request, any_key
from klibs.KLGraphics import KLDraw as kld
from klibs.KLGraphics import aggdraw_to_numpy_surface, fill, flip, blit, clear
from klibs.KLGraphics.KLNumpySurface import NumpySurface as npsurf
from klibs.KLEventInterface import TrialEventTicket as ET
from klibs.KLBoundary import BoundaryInspector
from klibs.KLCommunication import message
from klibs import Experiment

# Import other required libraries

import random
import math
import time # for debugging missing targets
import aggdraw # for drawing articulations in single texture
import sdl2

# Define some useful constants and colours for the experiment

GREY = [128,128,128,255]
DARKGREY = [64,64,64,255]
LIGHTGREY = [192,192,192,255]
WHITE = [255,255,255,255]
#BLACK_HIGH = [0,0,0,64]
#BLACK_MED  = [0,0,0,32]
#BLACK_LOW  = [0,0,0,24]
TOMATO_RED = [255,99,71,255]
TOMATO_RED_LOW = [255,99,71,32]

OPACITY_MIN = 12
OPACITY_MAX = 48
TARGET_DUR_MIN = (1000.0/60)*2 # 33.333ms
TARGET_DUR_MAX = (1000.0/60)*6 # 100ms

circle_radius = 8
default_stroke = 0.1
ring_stroke = 0.55



class ArticulationCircle(Experiment, BoundaryInspector):    
        
    debug_mode = False

    def __init__(self, *args, **kwargs):
        Experiment.__init__(self, *args)
        BoundaryInspector.__init__(self)      
        
    def setup(self):
        
        # Determine stimulus sizes
        
        self.circle_radius = util.deg_to_px(circle_radius)
        self.ring_radius   = util.deg_to_px(circle_radius + ring_stroke/2)
        self.circle_width  = self.circle_radius * 2
        self.ring_width    = self.ring_radius * 2
        
        # ensure default stroke isn't lopsided by rounding it up to nearest multiple of 2
        self.default_stroke = int(math.ceil(util.deg_to_px(default_stroke) / 2.0) * 2)
        self.ring_stroke    = int(math.ceil(util.deg_to_px(ring_stroke) / 2.0) * 2)
        self.articulation_len = 3 * (self.ring_stroke + self.default_stroke)
        
        self.fixation_width = util.deg_to_px(0.65)
        self.target_width = util.deg_to_px(0.25)
        self.nexttrial_width = util.deg_to_px(0.5)
        
        # Create Stimulus Drawbjects
        
        self.fixation = kld.FixationCross(self.fixation_width, self.default_stroke, fill=DARKGREY).render()
        self.fixation_light = kld.FixationCross(self.fixation_width, self.default_stroke, fill=LIGHTGREY).render()
        self.circle = kld.Annulus(self.ring_width, self.ring_stroke, fill=WHITE).render()
        self.circle_outline = kld.Annulus(self.ring_width + self.default_stroke, self.ring_stroke + self.default_stroke, fill=DARKGREY).render()
        self.articulations = self.draw_articulations(8, self.articulation_len, self.circle_radius, self.default_stroke/2)
        self.response_ring = kld.Annulus(self.ring_width, self.ring_stroke, fill=GREY)
        self.next_trial_circle = kld.Ellipse(self.nexttrial_width, fill=DARKGREY)
        
        # Define boundary for the next-trial circle
        
        self.add_boundary("center", [P.screen_c, self.nexttrial_width], CIRCLE_BOUNDARY)
        
        # Define range of possible target durations based on refresh rate
        
        self.target_flips_range = int(round((TARGET_DUR_MAX-TARGET_DUR_MIN) / P.refresh_time))
        
        # If in development mode, print refresh info and stimulus sizes
        
        if P.development_mode:
            
            print("\nRefresh Rate: {:.1f} Hz".format(P.refresh_rate))
            print("Time per refresh: {:.2f}ms\n".format(P.refresh_time))
            
            print("circle_width:", self.circle_width)
            print("ring_width:", self.ring_width)
            print("ring_thickness:", self.ring_stroke)
            print("outer_ring_thickness:", self.ring_stroke + self.default_stroke)
            print("target_size:", util.px_to_deg(10))
            print("default_stroke:", self.default_stroke)
            print("articulation_length:", util.px_to_deg(70))
            print("")

    def block(self):
        pass

    def setup_response_collector(self):
        self.rc.uses([RC_COLORSELECT])
        self.rc.terminate_after = [10, TK_S]
        self.rc.display_callback = self.articulation_callback
        self.rc.color_listener.interrupts = True
        self.rc.color_listener.set_wheel(self.response_ring)

    def trial_prep(self):
		
        # Define timecourse of events for the trial
        
        self.target_duration = TARGET_DUR_MIN + (random.choice(range(0, self.target_flips_range+1, 1)) * P.refresh_time)

        events = [[400-P.refresh_time, 'circle_on']]
        events.append([events[-1][0] + 600, 'target_on']) 
        events.append([events[-1][0] + self.target_duration, 'target_off'])
        events.append([events[-1][0] + 1000, 'response_circle_on'])
        for e in events:
            self.evm.register_ticket(ET(e[1], e[0]))
        
        # Randomly select angle of target for the trial, and configure response collector accordingly
        
        self.angle = random.choice(range(0, 360, 1))
        self.response_ring.rotation = self.angle
        self.target_pos = util.point_pos(P.screen_c, self.circle_radius, -90, self.angle)
        self.rc.color_listener.set_target(self.target_pos)
		
        # Initialize target asterisk with random opacity within range
        
        self.target_opacity = random.choice(range(OPACITY_MIN, OPACITY_MAX+1, 1))
        target_colour = (0, 0, 0, self.target_opacity)
        self.target = kld.Asterisk(self.target_width, color=target_colour, stroke=self.default_stroke).render()
        
        # Reset debug flags before trial starts
        
        self.circle_already_on = False
        self.target_already_on = False
        self.target_refreshes = 0
        
        # Enter trial with screen already at desired state
        
        fill()
        blit(self.fixation_light, 5, P.screen_c)
        flip()
        
        
    def trial(self):
        
        self.trial_time = time.time()        
        print(self.circle_type, self.target_duration, self.target_opacity)

        while self.evm.before('circle_on', True):
            fill()
            blit(self.fixation_light, 5, P.screen_c)
            flip()
            
        while self.evm.before('response_circle_on', True):
            self.start_time = time.time()
            target_on = self.evm.after('target_on') and self.evm.before('target_off')
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
        
        # Collect localization response and save response RT and response angle
        self.rc.collect()
        self.response_rt = self.rc.color_listener.response(False, True)
        self.response = self.rc.color_listener.response(True, False)
        try:
            self.response_loc = (self.angle + self.deg_err) % 360
        except TypeError:
            self.response_loc = NA
        print "Response accuracy: %.1f" % self.deg_err
        
        # Require participant to click center of screen to continue to next trial
        self.click_to_continue()

        return {
            "block_num": P.block_number,
            "trial_num": P.trial_number,
            "circle_type": self.circle_type,
            "opacity": self.target_opacity,
            "duration": str(self.target_duration),
            "rt": self.response_rt,
            "target_refreshes": self.target_refreshes,
            "target_loc": self.angle,
            "response_loc": self.response_loc,
            "deg_err": self.deg_err
        }
    
    def display_refresh(self, circle=False, lines=False, target=False): 
        fill()
        blit(self.fixation, 5, P.screen_c)
        self.init_time = time.time() # for debug
        
        if lines:
            blit(self.articulations, 5, P.screen_c)
            self.line_time = time.time() # for debug

        if circle:
            blit(self.circle_outline, 5, P.screen_c)
            blit(self.circle, 5, P.screen_c)
            self.circle_time = time.time() # for debug
        
        if target:
            blit(self.target, 5, self.target_pos)
            self.target_refreshes += 1
        flip()
        
        if circle and not self.circle_already_on:
            self.circle_ontime = time.time()
            print "circle on! %.3f" % (self.circle_ontime - self.trial_time)
            self.circle_already_on = True
        if target and not self.target_already_on:
            self.target_ontime = time.time()
            print "target on! %.3f" % (self.target_ontime - self.trial_time)
            self.target_already_on = True   
        if not target and self.target_already_on:
            print "total target on-time: %.3f " % (time.time() - self.target_ontime)
            print "refreshes: {0} \n".format(self.target_refreshes)
            self.target_already_on = False


    def trial_clean_up(self):
        pass


    def clean_up(self):
        pass
        
        
    def click_to_continue(self):        
        util.show_mouse_cursor()
        wait_for_click = True
        while wait_for_click:
            fill()
            blit(self.next_trial_circle, 5, P.screen_c)
            flip()
            events = util.pump(True)
            ui_request(queue=events)
            for e in events:
                if e.type == sdl2.SDL_MOUSEBUTTONUP:
                    pos = (e.button.x, e.button.y)
                    if self.within_boundary("center", pos):
                        fill()
                        flip()
                        wait_for_click = False      
        util.hide_mouse_cursor()
        
    
    def draw_articulations(self, count, length, radius, thickness):
        canvas_size = radius * 2 + length
        canvas_c = (canvas_size // 2.0, canvas_size // 2.0)
        half_len = length // 2.0
        theta = 360.0 // count
        
        canvas = aggdraw.Draw("RGBA", [canvas_size, canvas_size], (0, 0, 0, 0))
        pen = aggdraw.Pen(tuple(DARKGREY[:3]), thickness, 255)
        canvas.setantialias(True)
        
        for i in range(0, count):
            start = util.point_pos(canvas_c, radius-half_len-1, angle=theta*i)
            end = util.point_pos(canvas_c, radius+half_len-1, angle=theta*i)
            canvas.line((start[0], start[1], end[0], end[1]), pen)
        
        return aggdraw_to_numpy_surface(canvas)
        
        
    def articulation_callback(self):
        fill()
        blit(self.fixation, 5, P.screen_c)
        blit(self.response_ring, 5, P.screen_c)
        flip()