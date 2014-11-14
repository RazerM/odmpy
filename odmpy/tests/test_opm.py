import hashlib
import random
import sys
import unittest
from datetime import datetime
from pathlib import Path
from tempfile import TemporaryFile

import odmpy.opm as opm


class TestOpmSections(unittest.TestCase):
    def setUp(self):
        # Create dummy sections with valid data.

        random.seed(1)

        randnum = lambda: random.uniform(-1, 1) ** random.randint(-20, 20)

        self.valid_header = opm.Header(
            originator='ESA',
            opm_version='2.0',
            creation_date=datetime(2011,3,1,1,2,3),
            comment='Test comment\nline 2'
        )

        self.valid_metadata = opm.Metadata(
            object_name='Dragon',
            object_id='2010-026A',
            center_name='EARTH',
            ref_frame=opm.RefFrame.GCRF,
            time_system=opm.TimeSystem.UTC
        )

        self.valid_state_vector = opm.DataBlockStateVector(
                epoch=datetime(2011,2,24,1,2,3),
                x=randnum(),
                y=randnum(),
                z=randnum(),
                x_dot=randnum(),
                y_dot=randnum(),
                z_dot=randnum()
            )

        self.valid_spacecraft_parameters = opm.DataBlockSpacecraftParameters(
            mass=randnum(),
            solar_rad_area=randnum(),
            solar_rad_coeff=randnum(),
            drag_area=randnum(),
            drag_coeff=randnum()
        )

        self.valid_keplerian_elements = opm.DataBlockKeplerianElements(
            semi_major_axis=randnum(),
            eccentricity=randnum(),
            inclination=randnum(),
            ra_of_asc_node=randnum(),
            arg_of_pericenter=randnum(),
            true_anomaly=randnum(),
            gm=randnum()
        )

        self.valid_covariance_matrix = opm.DataBlockCovarianceMatrix(
            cx_x=randnum(),
            cy_x=randnum(),
            cy_y=randnum(),
            cz_x=randnum(),
            cz_y=randnum(),
            cz_z=randnum(),
            cx_dot_x=randnum(),
            cx_dot_y=randnum(),
            cx_dot_z=randnum(),
            cx_dot_x_dot=randnum(),
            cy_dot_x=randnum(),
            cy_dot_y=randnum(),
            cy_dot_z=randnum(),
            cy_dot_x_dot=randnum(),
            cy_dot_y_dot=randnum(),
            cz_dot_x=randnum(),
            cz_dot_y=randnum(),
            cz_dot_z=randnum(),
            cz_dot_x_dot=randnum(),
            cz_dot_y_dot=randnum(),
            cz_dot_z_dot=randnum()
        )

        self.valid_maneuver_parameters = opm.DataBlockManeuverParameters(
            man_epoch_ignition=datetime(2014, 11, 12, 13, 14, 15, 999999),
            man_duration=randnum(),
            man_delta_mass=-randnum(),
            man_ref_frame=opm.RefFrame.RSW,
            man_dv_1=randnum(),
            man_dv_2=randnum(),
            man_dv_3=randnum())

        self.valid_data = opm.Data(
            state_vector=self.valid_state_vector
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

    def test_missing_keyword(self):
        header = self.valid_header
        header.originator = None

        with self.assertRaises(opm.MissingKeywordError):
            header.validate_keywords()

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
        randnum = lambda: random.uniform(-1, 1) ** random.randint(-20, 20)

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
                semi_major_axis=randnum(),
                eccentricity=randnum(),
                inclination=randnum(),
                ra_of_asc_node=randnum(),
                arg_of_pericenter=randnum(),
                mean_anomaly=randnum(),
                gm=randnum()
            )
            ke.true_anomaly = 0

    def test_data_block_missing_spacecraft_parameters(self):
        """If maneuver parameters are used, spacecraft parameters block
        is mandatory.
        """
        mp = self.valid_maneuver_parameters

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

        sp = self.valid_spacecraft_parameters

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

    def test_invalid_multiple_blocks(self):
        sv = self.valid_data.state_vector.block

        sp = self.valid_spacecraft_parameters

        ke = self.valid_keplerian_elements

        cm = self.valid_covariance_matrix

        data = opm.Data(
            state_vector=[sv, sv],
            spacecraft_parameters=sp,
            keplerian_elements=ke,
            covariance_matrix=cm,
        )
        with self.assertRaises(ValueError):
            data.validate_blocks()

        data = opm.Data(
            state_vector=sv,
            spacecraft_parameters=[sp, sp],
            keplerian_elements=ke,
            covariance_matrix=cm,
        )
        with self.assertRaises(ValueError):
            data.validate_blocks()

        data = opm.Data(
            state_vector=sv,
            spacecraft_parameters=sp,
            keplerian_elements=[ke, ke],
            covariance_matrix=cm,
        )
        with self.assertRaises(ValueError):
            data.validate_blocks()

        data = opm.Data(
            state_vector=sv,
            spacecraft_parameters=sp,
            keplerian_elements=ke,
            covariance_matrix=[cm, cm],
        )
        with self.assertRaises(ValueError):
            data.validate_blocks()

    def test_multiple_blocks_type(self):
        data = self.valid_data

        sp = self.valid_spacecraft_parameters

        data.spacecraft_parameters = sp
        data.maneuver_parameters = [1]

        with self.assertRaises(TypeError):
            data.validate_blocks()

    def test_block_type(self):
        data = self.valid_data
        data.keplerian_elements = 'a'

        with self.assertRaises(TypeError):
            data.validate_blocks()

    def test_output(self):
        """Fail test if output doesn't match previously created file."""
        randnum = lambda: random.uniform(-1, 1) ** random.randint(-20, 20)

        data = opm.Data(
            state_vector=self.valid_state_vector,
            spacecraft_parameters=self.valid_spacecraft_parameters,
            keplerian_elements=self.valid_keplerian_elements,
            covariance_matrix=self.valid_covariance_matrix,
            maneuver_parameters=self.valid_maneuver_parameters)

        user_defined = {'TEST': randnum(), 'TEST2': 'String'}

        opm_obj = opm.Opm(
            header=self.valid_header,
            metadata=self.valid_metadata,
            data=data,
            user_defined=user_defined)

        output_hash = hashlib.sha256()
        for line in opm_obj.output():
            output_hash.update(line.encode('utf-8'))

        valid_hash = hashlib.sha256()
        with open(str(Path('.', 'odmpy', 'tests', 'valid.opm.txt')), 'r') as f:
            for line in f.read().splitlines():
                valid_hash.update(line.encode('utf-8'))
        self.assertEqual(output_hash.hexdigest(), valid_hash.hexdigest())

    def test_write(self):
        randnum = lambda: random.uniform(-1, 1) ** random.randint(-20, 20)

        data = opm.Data(
            state_vector=self.valid_state_vector,
            spacecraft_parameters=self.valid_spacecraft_parameters,
            keplerian_elements=self.valid_keplerian_elements,
            covariance_matrix=self.valid_covariance_matrix,
            maneuver_parameters=self.valid_maneuver_parameters)

        user_defined = {'TEST': randnum(), 'TEST2': 'String'}

        opm_obj = opm.Opm(
            header=self.valid_header,
            metadata=self.valid_metadata,
            data=data,
            user_defined=user_defined)

        file_hash = hashlib.sha256()
        with TemporaryFile(mode='w+') as f:
            opm_obj.write(f)
            f.seek(0)
            for line in f.read().splitlines():
                file_hash.update(line.encode('utf-8'))

        valid_hash = hashlib.sha256()
        with open(str(Path('.', 'odmpy', 'tests', 'valid.opm.txt')), 'r') as f:
            for line in f.read().splitlines():
                valid_hash.update(line.encode('utf-8'))
        self.assertEqual(file_hash.hexdigest(), valid_hash.hexdigest())


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


class TestFormatters(unittest.TestCase):
    def test_format_date(self):
        self.assertEqual(opm.format_date(datetime(2014, 11, 12, 13, 14, 15, 999999)), '2014-11-12T13:14:15.999999')
        self.assertEqual(opm.format_date(datetime(2014, 11, 12, 13, 14, 15)), '2014-11-12T13:14:15')

    def test_format_date_yyyyddd(self):
        self.assertEqual(opm.format_date_yyyyddd(datetime(2014, 11, 12, 13, 14, 15, 999999)), '2014-316T13:14:15.999999')
        self.assertEqual(opm.format_date_yyyyddd(datetime(2014, 11, 12, 13, 14, 15)), '2014-316T13:14:15')
