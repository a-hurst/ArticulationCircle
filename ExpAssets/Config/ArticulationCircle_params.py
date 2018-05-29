import random
# KlibsTesting Param overrides
#
# Any param that is commented out by default is either deprecated or else not yet implemented--don't uncomment or use
#
#########################################
# Available Hardware
#########################################
eye_tracker_available = False
eye_tracking = False
labjack_available = False
labjacking = False

#########################################
# Environment Aesthetic Defaults
#########################################
default_fill_color = (255, 255, 255, 255)
default_color = (0, 0, 0, 255)
default_font_size = 23
default_font_unit = 'px'
default_font_name = 'Frutiger'

#########################################
# EyeLink Sensitivities
#########################################
saccadic_velocity_threshold = 20
saccadic_acceleration_threshold = 5000
saccadic_motion_threshold = 0.15

#########################################
# Experiment Structure
#########################################
view_distance = 57
multi_session_project = True
collect_demographics = True
practicing = False
trials_per_block = 48
blocks_per_experiment = 6
trials_per_participant = 0
table_defaults = {}
#
#########################################
# Development Mode Settings
#########################################
dm_trial_show_mouse = False
dm_auto_threshold = True
dm_ignore_local_overrides = False

#
#########################################
# Data Export Settings
#########################################
data_columns = None
default_participant_fields = [["userhash", "participant"], "gender", "age", "handedness"]
default_participant_fields_sf = [["userhash", "participant"], "random_seed", "gender", "age", "handedness"]

#
#########################################
# PROJECT-SPECIFIC VARS
#########################################

