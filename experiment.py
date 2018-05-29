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
import numpy as np
from PIL import Image

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

BRIGHTNESS_MIN = 227
BRIGHTNESS_MAX = 237


class ArticulationCircle(Experiment, BoundaryInspector):    
        
    debug_mode = False

    def __init__(self, *args, **kwargs):
        Experiment.__init__(self, *args)
        BoundaryInspector.__init__(self)      
        
    def setup(self):
        
        # Determine stimulus sizes
        
        self.default_stroke = util.deg_to_px(0.1, even=True)
        
        self.circle_radius = util.deg_to_px(8.0)
        circle_width = self.circle_radius * 2
        
        ring_stroke = util.deg_to_px(0.55, even=True)
        ring_radius = self.circle_radius + ring_stroke/2
        ring_width = ring_radius * 2
        
        articulation_len = ring_stroke * 3
        
        self.fixation_width = util.deg_to_px(0.65, even=True)
        self.target_width = util.deg_to_px(0.25)
        self.nexttrial_width = util.deg_to_px(0.5)
        
        # Create Stimulus Drawbjects
        
        self.fixation = kld.FixationCross(self.fixation_width, self.default_stroke, fill=DARKGREY).render()
        self.fixation_light = kld.FixationCross(self.fixation_width, self.default_stroke, fill=LIGHTGREY).render()
        self.articulations = self.draw_articulations(8, articulation_len, ring_radius-ring_stroke/2, self.default_stroke/2, ring_stroke)
        self.response_ring = kld.Annulus(ring_width, ring_stroke, fill=LIGHTGREY)
        self.next_trial_circle = kld.Ellipse(self.nexttrial_width, fill=DARKGREY)
        
        # Define boundary for the next-trial circle
        
        self.add_boundary("center", [P.screen_c, self.nexttrial_width], CIRCLE_BOUNDARY)
        
        # If in development mode, print refresh info and stimulus sizes
        
        if P.development_mode:
            
            print("\nRefresh Rate: {:.1f} Hz".format(P.refresh_rate))
            print("Time per refresh: {:.2f}ms\n".format(P.refresh_time))
            
            print("circle_width:", circle_width)
            print("ring_width:", ring_width)
            print("ring_thickness:", ring_stroke)
            print("outer_ring_thickness:", ring_stroke + self.default_stroke)
            print("target_size:", util.px_to_deg(10))
            print("default_stroke:", self.default_stroke)
            print("articulation_length:", util.px_to_deg(70))
            print("")

    def block(self):
        if P.block_number == int(math.ceil(P.blocks_per_experiment/2.0))+1:
			util.flush()
			msg_text = "Whew! You're halfway done.\nTake a break, then press any key to continue."
			msg = message(msg_text, align="center", blit_txt=False)
			fill()
			blit(msg, registration=5, location=P.screen_c)
			flip()
			any_key()

    def setup_response_collector(self):
        self.rc.uses([RC_COLORSELECT])
        self.rc.terminate_after = [10, TK_S]
        self.rc.display_callback = self.articulation_callback
        self.rc.color_listener.interrupts = True
        self.rc.color_listener.set_wheel(self.response_ring)

    def trial_prep(self):
		
        # Define timecourse of events for the trial
             
        target_on = random.choice(range(500, 2050, 50))

        events = [[400-P.refresh_time, 'lines_on']]
        events.append([events[-1][0] + target_on, 'target_on']) 
        events.append([events[-1][0] + self.duration, 'target_off'])
        events.append([events[-1][0] + 1000, 'response_circle_on'])
        for e in events:
            self.evm.register_ticket(ET(e[1], e[0]))
        
        # Randomly select angle of target for the trial, and configure response collector accordingly
        
        self.angle = random.choice(range(0, 360, 1))
        self.response_ring.rotation = self.angle
        self.target_pos = util.point_pos(P.screen_c, self.circle_radius, -90, self.angle)
        self.rc.color_listener.set_target(self.target_pos)
        
        # Initialize target asterisk with random opacity within range
        
        self.target_brightness = random.choice(range(BRIGHTNESS_MIN, BRIGHTNESS_MAX+1, 1))
        target_colour = [self.target_brightness]*3 + [255]
        #self.target = kld.Asterisk(self.target_width, fill=target_colour, thickness=self.default_stroke/2).render()
        self.target = kld.Ellipse(self.target_width, fill=target_colour).render()

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
        print(self.trial_articulations, self.response_articulations, self.duration, self.target_brightness)

        while self.evm.before('lines_on', True):
            fill()
            blit(self.fixation_light, 5, P.screen_c)
            flip()
            
        while self.evm.before('response_circle_on', True):
            self.start_time = time.time()
            target_on = self.evm.after('target_on') and self.evm.before('target_off')
            self.display_refresh(target_on)
            
            # Debug code for target timing, disabled by default
            self.elapsed = time.time() - self.start_time
            if 0.9 < (self.start_time - self.trial_time) <= 1.100 and self.debug_mode:
                print("init: %.3f" % (self.init_time - self.trial_time))
                if lines_on:
                    print("line: %.3f" % (self.line_time - self.trial_time))
                print("total: %.3f" % (self.elapsed))
        
        # Collect localization response and save response RT and response angle
        self.rc.collect()
        self.response_rt = self.rc.color_listener.response(False, True)
        self.deg_err = self.rc.color_listener.response(True, False)
        try:
            self.response_loc = (self.angle + self.deg_err) % 360
            print("Response accuracy: %.1f" % self.deg_err)
        except TypeError:
            self.response_loc = NA
        
        # Require participant to click center of screen to continue to next trial
        self.click_to_continue()

        return {
            "block_num": P.block_number,
            "trial_num": P.trial_number,
            "trial_articulations": self.trial_articulations,
            "response_articulations": self.response_articulations,
            "target_brightness": self.target_brightness,
            "duration": str(self.duration),
            "rt": self.response_rt,
            "target_refreshes": self.target_refreshes,
            "target_loc": self.angle,
            "response_loc": self.response_loc,
            "deg_err": self.deg_err
        }
    
    def display_refresh(self, target=False): 
        fill()
        blit(self.fixation, 5, P.screen_c)
        self.init_time = time.time() # for debug
        
        if self.trial_articulations:
            blit(self.articulations, 5, P.screen_c)
            self.line_time = time.time() # for debug
        
        if target:
            blit(self.target, 5, self.target_pos)
            self.target_refreshes += 1
        flip()
        
        if target and not self.target_already_on:
            self.target_ontime = time.time()
            print("target on! %.3f" % (self.target_ontime - self.trial_time))
            self.target_already_on = True   
        if not target and self.target_already_on:
            print("total target on-time: %.3f " % (time.time() - self.target_ontime))
            print("refreshes: {0} \n".format(self.target_refreshes))
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
        
    
    def draw_articulations(self, count, length, radius, line_thickness, ring_thickness):
        canvas_size = radius * 2 + length
        canvas_c = (canvas_size / 2.0, canvas_size / 2.0)
        half_len = length / 2.0
        theta = 360.0 / count
        
        canvas = Image.new("RGB", [canvas_size, canvas_size], tuple(LIGHTGREY[:3]))
        mask = Image.new('L', [canvas_size, canvas_size], 0)
        mask_surf = aggdraw.Draw(mask)

        line_pen = aggdraw.Pen(255, line_thickness)
        ring_pen = aggdraw.Pen(0, ring_thickness)
        transparent_brush = aggdraw.Brush((255, 0, 0), 0)
        
        # Draw articulations
        for i in range(0, count):
            start = util.point_pos(canvas_c, radius-half_len, angle=theta*i)
            end = util.point_pos(canvas_c, radius+half_len, angle=theta*i)
            mask_surf.line((start[0], start[1], end[0], end[1]), line_pen)
        
        # Draw ring mask for articulations
        xy_1 = canvas_c[0] - radius
        xy_2 = canvas_c[0] + radius
        mask_surf.ellipse([xy_1, xy_1, xy_2, xy_2], ring_pen, transparent_brush)
        mask_surf.flush()
        
        # Apply ring mask to articulations
        canvas.putalpha(mask)
        
        return np.asarray(canvas)
        
        
    def articulation_callback(self):
        fill()
        blit(self.fixation, 5, P.screen_c)
        if self.response_articulations == True:
            blit(self.articulations, 5, P.screen_c)
        blit(self.response_ring, 5, P.screen_c)
        flip()