__author__ = 'jono'
from klibs.KLIndependentVariable import IndependentVariableSet, IndependentVariable


# Initialize object containing project's independant variables

ArticulationCircle_ind_vars = IndependentVariableSet()


# Define project variables and variable types

ArticulationCircle_ind_vars.add_variable("circle_type", str, ["none", "plain", "articulated"])
ArticulationCircle_ind_vars.add_variable("duration",    int, [50, 100]) # 3 or 6 refreshes @ 60hz
ArticulationCircle_ind_vars.add_variable("opacity",     str, ["high", "med", "low"])
