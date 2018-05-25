from klibs.KLIndependentVariable import IndependentVariableSet


# Initialize object containing project's independant variables

ArticulationCircle_ind_vars = IndependentVariableSet()


# Define project variables and variable types

ms_per_frame = 1000.0 / 60.0
durations = [2*ms_per_frame, 3*ms_per_frame, 4*ms_per_frame]

ArticulationCircle_ind_vars.add_variable("trial_articulations", bool, [True, False])
ArticulationCircle_ind_vars.add_variable("response_articulations", bool, [True, False])
ArticulationCircle_ind_vars.add_variable("duration", float, durations)
#ArticulationCircle_ind_vars.add_variable("opacity",     str, ["high", "med", "low"])