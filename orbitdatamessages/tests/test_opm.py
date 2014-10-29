import unittest
from datetime import datetime

import orbitdatamessages.orbital_parameter_message as opm


class TestOpmHeader(unittest.TestCase):
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

        self.assertRaises(
            ValueError,
            lambda: opm.Opm(header=header,
                            metadata=self.valid_metadata,
                            data=self.valid_data)
        )

    def test_empty_originator(self):
        header = opm.Header(originator='')

        # Check that validation fails

        self.assertRaises(ValueError, header.validate_keywords)

        # Check that OPM cannot be constructed from invalid header

        self.assertRaises(
            ValueError,
            lambda: opm.Opm(header=header,
                            metadata=self.valid_metadata,
                            data=self.valid_data)
        )
