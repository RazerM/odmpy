import unittest
from datetime import datetime

import orbitdatamessages.orbital_parameter_message as opm


class TestOpmSections(unittest.TestCase):
    def setUp(self):
        # Create dummy sections with valid data.

        self.valid_header = opm.Header(
            originator='ESA',
            opm_version='2.0',
            creation_date=datetime.utcnow()
        )

        self.valid_metadata = opm.Metadata(
            object_name='Dragon',
            object_id='2010-026A',
            center_name='EARTH',
            ref_frame=opm.RefFrame.GCRF,
            time_system=opm.TimeSystem.UTC
        )

        self.valid_data = opm.Data(
            state_vector=opm.DataBlockStateVector(
                epoch=datetime.utcnow(),
                x=0,
                y=0,
                z=0,
                x_dot=0,
                y_dot=0,
                z_dot=0
            )
        )

    def test_empty_opm_version(self):
        header = opm.Header(originator='ESA', opm_version='')

        # Check that validation fails

        self.assertRaises(ValueError, header.validate_keywords)

        # Check that OPM cannot be constructed from invalid header

        with self.assertRaises(ValueError):
            opm.Opm(header=header,
                    metadata=self.valid_metadata,
                    data=self.valid_data)

    def test_empty_originator(self):
        header = opm.Header(originator='')

        # Check that validation fails

        self.assertRaises(ValueError, header.validate_keywords)

        # Check that OPM cannot be constructed from invalid header

        with self.assertRaises(ValueError):
            opm.Opm(header=header,
                    metadata=self.valid_metadata,
                    data=self.valid_data)

    def test_empty_object_id(self):
        # Take valid metadata object, and set invalid object_id
        metadata = self.valid_metadata
        metadata.object_id = ''

        # Check that validation fails

        self.assertRaises(ValueError, metadata.validate_keywords)

        # Check that OPM cannot be constructed from invalid header

        with self.assertRaises(ValueError):
            opm.Opm(header=self.valid_header,
                    metadata=metadata,
                    data=self.valid_data)

    def test_invalid_object_id(self):
        # Take valid metadata object, and set invalid object_id
        # Note that the validator itself is tested in the TestValidators class
        metadata = self.valid_metadata
        metadata.object_id = '2010-062'

        # Check that validation fails

        self.assertRaises(ValueError, metadata.validate_keywords)

        # Check that OPM cannot be constructed from invalid header

        with self.assertRaises(ValueError):
            opm.Opm(header=self.valid_header,
                    metadata=metadata,
                    data=self.valid_data)

    def test_both_anomalies(self):
        # Check both cannot be set during initialisation
        with self.assertRaises(opm.DuplicateKeywordError):
            opm.DataBlockKeplerianElements(
                semi_major_axis=0,
                eccentricity=0,
                inclination=0,
                ra_of_asc_node=0,
                arg_of_pericenter=0,
                true_anomaly=0,
                mean_anomaly=0,
                gm=0,
            )

        # Check mean can't be set if true already has been
        with self.assertRaises(opm.DuplicateKeywordError):
            ke = opm.DataBlockKeplerianElements(
                semi_major_axis=0,
                eccentricity=0,
                inclination=0,
                ra_of_asc_node=0,
                arg_of_pericenter=0,
                true_anomaly=0,
                gm=0,
            )
            ke.mean_anomaly = 0

        # Check true can't be set if mean already has been
        with self.assertRaises(opm.DuplicateKeywordError):
            ke = opm.DataBlockKeplerianElements(
                semi_major_axis=0,
                eccentricity=0,
                inclination=0,
                ra_of_asc_node=0,
                arg_of_pericenter=0,
                mean_anomaly=0,
                gm=0,
            )
            ke.true_anomaly = 0

    def test_data_block_missing_spacecraft_parameters(self):
        """If maneuver parameters are used, spacecraft parameters block
        is mandatory.
        """
        mp = opm.DataBlockManeuverParameters(
            man_epoch_ignition=datetime.utcnow(),
            man_duration=1,
            man_delta_mass=1,
            man_ref_frame=opm.RefFrame.TNW,
            man_dv_1=1,
            man_dv_2=0,
            man_dv_3=0
        )

        data = self.valid_data
        data.maneuver_parameters = mp
        with self.assertRaises(ValueError):
            data.validate_blocks()

        with self.assertRaises(ValueError):
            opm.Opm(header=self.valid_header,
                    metadata=self.valid_metadata,
                    data=data)

    def test_multiple_maneuver_parameters(self):
        """There can be one or more maneuver parameters blocks"""
        mp1 = opm.DataBlockManeuverParameters(
            man_epoch_ignition=datetime.utcnow(),
            man_duration=1,
            man_delta_mass=1,
            man_ref_frame=opm.RefFrame.TNW,
            man_dv_1=1,
            man_dv_2=0,
            man_dv_3=0
        )

        mp2 = opm.DataBlockManeuverParameters(
            man_epoch_ignition=datetime.utcnow(),
            man_duration=2,
            man_delta_mass=1,
            man_ref_frame=opm.RefFrame.TNW,
            man_dv_1=1,
            man_dv_2=1,
            man_dv_3=1
        )

        sp = opm.DataBlockSpacecraftParameters(
            mass=0,
            solar_rad_area=0,
            solar_rad_coeff=0,
            drag_area=0,
            drag_coeff=0
        )

        data = self.valid_data
        data.maneuver_parameters = mp1
        data.spacecraft_parameters = sp

        data.validate_blocks()

        opm.Opm(header=self.valid_header,
                metadata=self.valid_metadata,
                data=data)

        data.maneuver_parameters = [mp1, mp2]
        data.validate_blocks()

        opm.Opm(header=self.valid_header,
                metadata=self.valid_metadata,
                data=data)

    def test_missing_state_vector(self):
        data = self.valid_data
        with self.assertRaises(ValueError):
            data.state_vector = None

        data = opm.Data(
            state_vector=None
        )
        with self.assertRaises(opm.MissingBlockError):
            data.validate_blocks()

class TestValidators(unittest.TestCase):
    def test_validate_object_id(self):
        self.assertTrue(opm.validate_object_id('2010-026A'))
        self.assertTrue(opm.validate_object_id('2010-026AB'))
        self.assertTrue(opm.validate_object_id('2010-026ABC'))
        self.assertFalse(opm.validate_object_id(''))
        self.assertFalse(opm.validate_object_id('201-026A'))
        self.assertFalse(opm.validate_object_id('2010-02A'))
        self.assertFalse(opm.validate_object_id('2010--026A'))
        self.assertFalse(opm.validate_object_id(' 2010-026A'))
        self.assertFalse(opm.validate_object_id('2010-026A '))
        self.assertFalse(opm.validate_object_id('2010 026A '))

    def test_validate_string(self):
        self.assertTrue(opm.validate_string('non-empty'))
        self.assertFalse(opm.validate_string(''))
