__author__ = 'jono'
from klibs.KLIndependentVariable import IndependentVariableSet, IndependentVariable


# Initialize object containing project's independant variables

ArticulationCircle_ind_vars = IndependentVariableSet()


# Define project variables and variable types

ArticulationCircle_ind_vars.add_variable("circle_type", str, ["none", "plain", "articulated"])
ArticulationCircle_ind_vars.add_variable("duration",    int, [48, 96]) # 3 or 6 refreshes @ 60hz
ArticulationCircle_ind_vars.add_variable("opacity",     str, ["full", "med", "low"])


# Add values for variables
#
#ArticulationCircle_ind_vars['circle_type'].add_value("none")
#ArticulationCircle_ind_vars['circle_type'].add_value("plain")
#ArticulationCircle_ind_vars['circle_type'].add_value("articulated")
#
#ArticulationCircle_ind_vars['duration'].add_value(48) # 3 refreshes @ 60hz
#ArticulationCircle_ind_vars['duration'].add_value(96) # 6 refreshes @ 60hz
#
#ArticulationCircle_ind_vars['opacity'].add_value("full")
#ArticulationCircle_ind_vars['opacity'].add_value("med")
#ArticulationCircle_ind_vars['opacity'].add_value("low")