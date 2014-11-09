*************************
Orbital Parameter Message
*************************

Reference
=========

This section is split into two part: the objects you will use to construct the OPM, and the enums used as parameters. Currently, the base classes etc. are only documented within the source files.

Main classes
------------

.. autoclass:: odmpy.opm.Header(originator, opm_version='2.0'[, creation_date[, comment]])
  :show-inheritance:
.. autoclass:: odmpy.opm.Metadata(object_name, object_id, center_name, ref_frame, time_system[, ref_frame_epoch[, comment]])
  :show-inheritance:
.. autoclass:: odmpy.opm.DataBlockStateVector(epoch, x, y, z, x_dot, y_dot, z_dot[, comment])
  :show-inheritance:
.. autoclass:: odmpy.opm.DataBlockKeplerianElements(semi_major_axis, eccentricity, inclination, ra_of_asc_node, arg_of_pericenter, gm[, true_anomaly[, mean_anomaly[, comment]]])
  :show-inheritance:
.. autoclass:: odmpy.opm.DataBlockSpacecraftParameters(mass, solar_rad_area, solar_rad_coeff, drag_area, drag_coeff[, comment])
  :show-inheritance:
.. autoclass:: odmpy.opm.DataBlockCovarianceMatrix([comment[, cov_ref_frame[, **cargs]]])
  :show-inheritance:
.. autoclass:: odmpy.opm.DataBlockManeuverParameters(man_epoch_ignition, man_duration, man_delta_mass, man_ref_frame, man_dv_1, man_dv_2, man_dv_3[, comment])
  :show-inheritance:
.. autoclass:: odmpy.opm.Data(state_vector[, spacecraft_parameters[, keplerian_elements[, covariance_matrix[, maneuver_parameters]]]])
  :members:
.. autoclass:: odmpy.opm.Opm(header, metadata, data[, user_defined])
  :members:

Enums
-----

.. autoclass:: odmpy.opm.RefFrame
.. autoclass:: odmpy.opm.TimeSystem