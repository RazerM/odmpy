"""
Module for creating valid OPM files as specified in the Orbit Data Message
Recommended Standard CCSDS 502.0-B-2

Recommended import syntax:
import orbitdatamessages.opm as opm
"""
import re
import textwrap
from datetime import datetime
from enum import Enum
from math import floor, log10
from numbers import Number

# from orbitdatamessages.opm import * considered harmful
# Even so, make sure only core functionality gets imported
__all__ = [
    'DataBlockCovarianceMatrix',
    'DataBlockKeplerianElements',
    'DataBlockManeuverParameters',
    'DataBlockSpacecraftParameters',
    'DataBlockStateVector',
    'Header',
    'Metadata',
    'Opm',
    'RefFrame',
    'TimeSystem',
]


def prefix(prefix, iterable):
    """Add prefix to each item of an iterable."""
    for x in iterable:
        yield '{prefix}{x!s}'.format(prefix=prefix, x=x)


def suffix(suffix, iterable):
    """Add suffix to each item of an iterable."""
    for x in iterable:
        yield '{x!s}{suffix!s}'.format(suffix=suffix, x=x)


def _mant_exp(num):
    """
    Return the mantissa and (base 10) exponent of num.

    num -- float or int.
    """
    try:
        exponent = floor(log10(abs(num)))
    except ValueError:  # Case of log10(0)
        return (0, 0)  # Convention: 0 = 0*10^0
    mantissa = num / 10**exponent
    return (mantissa, int(exponent))


def format_number(number):
    """Format number for ODM output.

    Number is truncated to MAX_DIGITS if required. Numbers are given leading
    space such that any number passed in will have its decimal point in the
    same character position.
    """
    MAX_DIGITS = 16  # From ODM spec

    _, exponent = _mant_exp(number)

    if exponent > MAX_DIGITS - 2:
        return ' ' * (MAX_DIGITS - 1) + '{: .15e}'.format(number)
    elif exponent < -4:
        return ' ' * (MAX_DIGITS - 1) + '{: .15e}'.format(number)
    else:
        if exponent > 0:
            prec = '{: {padding}.{precision}f}'.format(
                number, precision=MAX_DIGITS - 1 - exponent,
                padding=MAX_DIGITS * 2)
            ind = exponent - 1
            prec = prec[ind:]
        elif exponent <= 0:
            prec = '{: {padding}.{precision}f}'.format(
                number, precision=MAX_DIGITS - 2, padding=MAX_DIGITS * 2)
        return prec


def validate_string(string):
    """Check string is non-empty."""
    return True if string else False


def validate_date(date):
    return date.utcoffset() is None


def validate_object_id(object_id):
    match = re.match('^[0-9]{4}\-[0-9]{3}[A-Z]{1,3}$', object_id)
    return True if match else False


class TimeSystem(Enum):
    GMST = 'GMST'
    GPS  = 'GPS'
    MET  = 'MET'
    MRT  = 'MRT'
    SCLK = 'SCLK'
    TAI  = 'TAI'
    TCB  = 'TCB'
    TDB  = 'TDB'
    TCG  = 'TCG'
    TT   = 'TT'
    UT1  = 'UT1'
    UTC  = 'UTC'


class RefFrame(Enum):
    EME2000  = 'EME2000'
    GCRF     = 'GCRF'
    GRC      = 'GRC'
    ICRF     = 'ICRF'
    ITRF2000 = 'ITRF2000'
    ITRF_93  = 'ITRF_93'
    ITRF_97  = 'ITRF_97'
    MCI      = 'MCI'
    TDR      = 'TDR'
    TEME     = 'TEME'
    TOD      = 'TOD'
    RSW      = 'RSW'
    RTN      = 'RTN'
    TNW      = 'TNW'


class MissingKeywordError(Exception):
    pass


class MissingBlockError(Exception):
    pass


class DuplicateKeywordError(Exception):
    pass


class Keyword:

    """ODM keyword object.

    Apart from the keyword name and value, the 'mandatory',
    'formatter', and 'validator' properties ensure that only a valid Keyword
    can be written to file, formatted appropriately.
    """

    def __init__(self, keyword, value=None, mandatory=True,
                 formatter=lambda x: x, validator=lambda x: True):
        """Initialise keyword with sane defaults.

        Note that keywords are mandatory by default, i.e. optional keywords
        are opt-out.

        formatter and validator are instance variables so that this information
        is associated directly with the keyword. This also allows individual
        keywords to have either method overriden for special cases.
        """
        self.keyword = keyword
        self.mandatory = mandatory
        self.value = value
        self.formatter = formatter
        self.validator = validator

    def __repr__(self):
        return ('{name}('
                'keyword={keyword!r}, '
                'value={value!r}, '
                'mandatory={mandatory!r})'
               ).format(
                    name=self.__class__.__name__,
                    keyword=self.keyword,
                    value=self.value,
                    mandatory=self.mandatory)

    @property
    def formatted_value(self):
        """Format keyword value for writing to file."""
        return self.formatter(self.value)

    def is_valid(self):
        """Check if keyword is valid."""
        return self.validator(self.value)


class DataKeyword(Keyword):

    """Subclass of Keyword for keywords with units."""

    def __init__(self, keyword, value=None, units=None, mandatory=True,
                 formatter=lambda x: x, validator=lambda x: True):
        """Initialise super & set instance variables unique to DataKeyword."""
        super().__init__(keyword=keyword, value=value, mandatory=mandatory,
                         formatter=formatter, validator=validator)
        self.units = units

    def __repr__(self):
        return ('{name}('
                'keyword={keyword!r}, '
                'value={value!r}, '
                'mandatory={mandatory!r}, '
                'units={units!r})'
               ).format(
                    name=self.__class__.__name__,
                    keyword=self.keyword,
                    value=self.value,
                    mandatory=self.mandatory,
                    units=self.units)


class KeywordContainer:

    """Base class of OPM keyword sections.

    The standard splits an orbital parameter message file into different
    sections, which will subclass KeywordContainer.

    The main purpose of the base class is to implement the methods for
    validating and formatting the list of keywords provided by each sublcass.
    """

    def __init__(self):
        """Initialise with empty keyword list.

        Initialise super() for co-operative subclassing.
        """
        super().__init__()
        self.keywords = list()

    def validate_keywords(self):
        """Ensure keywords are valid and set (if mandatory).

        This method should be called internally before data meant for output
        is produced.
        """
        for keyword in self.keywords:
            if keyword.mandatory and keyword.value is None:
                raise MissingKeywordError(keyword.keyword)
            if keyword.value is not None:
                if not keyword.is_valid():
                    raise ValueError('%s failed validation.' % keyword.keyword)

    def create_output_align_equals(self):
        """Align keywords by equal sign."""
        self.validate_keywords()
        longest_keyword_len = len(max(self.keywords,
                                      key=lambda x: len(x.keyword)).keyword)
        output = list()
        for keyword in (key for key in self.keywords if key.value is not None):
            keyword_name = keyword.keyword
            aligned_keyword = keyword_name.ljust(longest_keyword_len)
            value = keyword.formatted_value
            if keyword.keyword == 'COMMENT':
                for comment_line in prefix('COMMENT ', value.splitlines()):
                    yield comment_line
            else:
                yield '{keyword} = {value}'.format(keyword=aligned_keyword,
                                                   value=value)

    def create_output_align_decimal(self):
        """.

        Adapted from a StackOverflow answer by Alex Martelli,
        http://stackoverflow.com/a/1025528
        """
        self.validate_keywords()

        ut0 = re.compile(r'(\d)0+$')

        # Get all numerical keyword values for formatting.
        numbers = (keyword.value for keyword in self.keywords
                   if isinstance(keyword.value, Number))

        # Remove leading space
        aligned_numbers = iter(textwrap.dedent(
            '\n'.join(
                ut0.sub(r'\1', format_number(x)) for x in numbers
            )).splitlines())

        longest_keyword_len = len(
            max(self.keywords, key=lambda x: len(x.keyword)).keyword)
        output = list()

        # Already validated, so ignore unset keywords.
        for keyword in (key for key in self.keywords if key.value is not None):
            keyword_name = keyword.keyword

            if keyword_name == 'COMMENT':
                value = keyword.formatted_value
                for comment_line in prefix('COMMENT ', value.splitlines()):
                    yield comment_line
            else:
                aligned_keyword = keyword_name.ljust(longest_keyword_len)

                # Loop through all keywords, consuming the decimal-aligned number
                # from the iterator we made earlier.
                if isinstance(keyword.value, Number):
                    # If number has not been formatted manually, use
                    # decimal-aligned number. In this case, formatted means that
                    # the formatted value is a string.
                    if keyword.value == keyword.formatted_value:
                        value = next(aligned_numbers)
                    else:
                        # Consume next value from iterator, but use formatted value
                        _ = next(aligned_numbers)
                        value = keyword.formatted_value
                else:
                    value = keyword.formatted_value

                yield '{keyword} = {value}'.format(keyword=aligned_keyword,
                                                   value=value)


class Header(KeywordContainer):

    """OPM Header object (mandatory).

    Properties are used so that instance variables can be set with assignment,
    but the full keyword object is returned when read.
    """

    def __init__(self, originator, opm_version='2.0',
                 creation_date=datetime.utcnow(), comment=None):
        """Initialise OPM Header.

        Required keywords:
        - opm_version
        - creation_date
        - originator

        Optional keywords:
        - comment
        """
        super().__init__()
        self._opm_version = Keyword('CCSDS_OPM_VERS', opm_version,
                                    validator=validate_string)
        self._comment = Keyword('COMMENT', comment, mandatory=False)
        self._creation_date = Keyword(
            'CREATION_DATE', creation_date,
            formatter=lambda x: x.isoformat(sep='T'),
            validator=validate_date)
        self._originator = Keyword('ORIGINATOR', originator,
                                   validator=validate_string)

        self.keywords = [
            self._opm_version,
            self._comment,
            self._creation_date,
            self._originator
        ]

    @property
    def opm_version(self):
        return self._opm_version

    @opm_version.setter
    def opm_version(self, value):
        self._opm_version.value = value

    @property
    def comment(self):
        return self._comment

    @comment.setter
    def comment(self, value):
        self._comment.value = value

    @property
    def creation_date(self):
        return self._creation_date

    @creation_date.setter
    def creation_date(self, value):
        self._creation_date.value = value

    @property
    def originator(self):
        return self._originator

    @originator.setter
    def originator(self, value):
        self._originator.value = value


class Metadata(KeywordContainer):

    """OPM Metadata object (mandatory)."""

    def __init__(self, object_name=None, object_id=None, center_name=None,
                 ref_frame=None, ref_frame_epoch=None, time_system=None,
                 comment=None):
        """Initialise OPM Metadata section.

        Required keywords:
        - object_name
        - object_id
        - center_name
        - ref_frame
        - time_system

        Optional keywords:
        - comment
        - ref_frame_epoch
        """
        super().__init__()
        self._comment         = Keyword('COMMENT', comment, mandatory=False)
        self._object_name     = Keyword('OBJECT_NAME', object_name,
                                        validator=validate_string)
        self._object_id       = Keyword('OBJECT_ID', object_id,
                                        validator=validate_object_id)
        self._center_name     = Keyword('CENTER_NAME', center_name,
                                        validator=validate_string)
        self._ref_frame       = Keyword('REF_FRAME', ref_frame,
                                        formatter=lambda x: x.value)
        self._ref_frame_epoch = Keyword(
            'REF_FRAME_EPOCH', ref_frame_epoch, mandatory=False,
            formatter=lambda x: x.isoformat(sep='T'),
            validator=validate_date)
        self._time_system     = Keyword('TIME_SYSTEM', time_system,
                                        formatter=lambda x: x.value)

        self.keywords = [
            self._comment,
            self._object_name,
            self._object_id,
            self._center_name,
            self._ref_frame,
            self._ref_frame_epoch,
            self._time_system
        ]

    @property
    def comment(self):
        return self._comment

    @comment.setter
    def comment(self, value):
        self._comment.value = value

    @property
    def object_name(self):
        return self._object_name

    @object_name.setter
    def object_name(self, value):
        self._object_name.value = value

    @property
    def object_id(self):
        return self._object_id

    @object_id.setter
    def object_id(self, value):
        self._object_id.value = value

    @property
    def center_name(self):
        return self._center_name

    @center_name.setter
    def center_name(self, value):
        self._center_name.value = value

    @property
    def ref_frame(self):
        return self._ref_frame

    @ref_frame.setter
    def ref_frame(self, value):
        self._ref_frame.value = value

    @property
    def ref_frame_epoch(self):
        return self._ref_frame_epoch

    @ref_frame_epoch.setter
    def ref_frame_epoch(self, value):
        self._ref_frame_epoch.value = value

    @property
    def time_system(self):
        return self._time_system

    @time_system.setter
    def time_system(self, value):
        self._time_system.value = value


class DataBlock:

    """Named block for part of OPM data section."""

    def __init__(self, name=None):
        """name parameter can be set by user, otherwise
        default set at write time.
        """
        super().__init__()
        self.name = name


class DataBlockStateVector(DataBlock, KeywordContainer):

    """State vector block for OPM data section."""

    def __init__(self, comment=None, epoch=None, x=None, y=None, z=None,
                 x_dot=None, y_dot=None, z_dot=None):
        """Initialise state vector data block.

        Required keywords:
        - epoch
        - x
        - y
        - z
        - x_dot
        - y_dot
        - z_dot

        Optional keywords:
        - comment
        """
        super().__init__()
        self._comment = DataKeyword('COMMENT', comment, mandatory=False)
        self._epoch   = DataKeyword(
            'EPOCH', epoch, formatter=lambda x: x.isoformat(sep='T'),
            validator=validate_date)
        self._x       = DataKeyword('X', x, units='km')
        self._y       = DataKeyword('Y', y, units='km')
        self._z       = DataKeyword('Z', z, units='km')
        self._x_dot   = DataKeyword('X_DOT', x_dot, units='km/s')
        self._y_dot   = DataKeyword('Y_DOT', y_dot, units='km/s')
        self._z_dot   = DataKeyword('Z_DOT', z_dot, units='km/s')

        self.keywords = [
            self._comment,
            self._epoch,
            self._x,
            self._y,
            self._z,
            self._x_dot,
            self._y_dot,
            self._z_dot
        ]

    @property
    def comment(self):
        return self._comment

    @comment.setter
    def comment(self, value):
        self._comment.value = value

    @property
    def epoch(self):
        return self._epoch

    @epoch.setter
    def epoch(self, value):
        self._epoch.value = value

    @property
    def x(self):
        return self._x

    @x.setter
    def x(self, value):
        self._x.value = value

    @property
    def y(self):
        return self._y

    @y.setter
    def y(self, value):
        self._y.value = value

    @property
    def z(self):
        return self._z

    @z.setter
    def z(self, value):
        self._z.value = value

    @property
    def x_dot(self):
        return self._x_dot

    @x_dot.setter
    def x_dot(self, value):
        self._x_dot.value = value

    @property
    def y_dot(self):
        return self._y_dot

    @y_dot.setter
    def y_dot(self, value):
        self._y_dot.value = value

    @property
    def z_dot(self):
        return self._z_dot

    @z_dot.setter
    def z_dot(self, value):
        self._z_dot.value = value


class DataBlockKeplerianElements(DataBlock, KeywordContainer):

    """Keplerian elements block for OPM data section."""

    def __init__(self, comment=None, semi_major_axis=None, eccentricity=None,
                 inclination=None, ra_of_asc_node=None, arg_of_pericenter=None,
                 true_anomaly=None, mean_anomaly=None, gm=None):
        """Initialise keplerian elements data block.

        Required keywords:
        - semi_major_axis
        - eccentricity
        - inclination
        - ra_of_asc_node
        - arg_of_pericenter
        - true_anomaly or mean_anomaly
        - gm

        Optional keywords:
        - comment
        """
        super().__init__()
        self._comment           = DataKeyword('COMMENT', comment,
                                              mandatory=False)
        self._semi_major_axis   = DataKeyword('SEMI_MAJOR_AXIS',
                                              semi_major_axis, units='km')
        self._eccentricity      = DataKeyword('ECCENTRICITY', eccentricity)
        self._inclination       = DataKeyword('INCLINATION', inclination,
                                              units='deg')
        self._ra_of_asc_node    = DataKeyword('RA_OF_ASC_NODE', ra_of_asc_node,
                                              units='deg')
        self._arg_of_pericenter = DataKeyword('ARG_OF_PERICENTER',
                                              arg_of_pericenter, units='deg')

        if true_anomaly is not None and mean_anomaly is not None:
            raise DuplicateKeywordError(
                'mean_anomaly and true_anomaly cannot both be set')

        self._true_anomaly      = DataKeyword('TRUE_ANOMALY', true_anomaly,
                                              units='deg')
        self._mean_anomaly      = DataKeyword('MEAN_ANOMALY', mean_anomaly,
                                              units='deg')
        self._gm                = DataKeyword('GM', gm, units='km**3/s**2')

        self.keywords = [
            self._comment,
            self._semi_major_axis,
            self._eccentricity,
            self._inclination,
            self._ra_of_asc_node,
            self._arg_of_pericenter,
            self._true_anomaly,
            self._mean_anomaly,
            self._gm
        ]

    @property
    def true_anomaly(self):
        return self._true_anomaly

    @true_anomaly.setter
    def true_anomaly(self, value):
        if self._mean_anomaly.value is not None:
            raise DuplicateKeywordError('mean_anomaly already set')
        self._true_anomaly.value = value

    @property
    def mean_anomaly(self):
        return self._mean_anomaly

    @mean_anomaly.setter
    def mean_anomaly(self, value):
        if self._true_anomaly.value is not None:
            raise DuplicateKeywordError('true_anomaly already set')
        self._mean_anomaly.value = value

    @property
    def comment(self):
        return self._comment

    @comment.setter
    def comment(self, value):
        self._comment.value = value

    @property
    def semi_major_axis(self):
        return self._semi_major_axis

    @semi_major_axis.setter
    def semi_major_axis(self, value):
        self._semi_major_axis.value = value

    @property
    def eccentricity(self):
        return self._eccentricity

    @eccentricity.setter
    def eccentricity(self, value):
        self._eccentricity.value = value

    @property
    def inclination(self):
        return self._inclination

    @inclination.setter
    def inclination(self, value):
        self._inclination.value = value

    @property
    def ra_of_asc_node(self):
        return self._ra_of_asc_node

    @ra_of_asc_node.setter
    def ra_of_asc_node(self, value):
        self._ra_of_asc_node.value = value

    @property
    def arg_of_pericenter(self):
        return self._arg_of_pericenter

    @arg_of_pericenter.setter
    def arg_of_pericenter(self, value):
        self._arg_of_pericenter.value = value

    @property
    def gm(self):
        return self._gm

    @gm.setter
    def gm(self, value):
        self._gm.value = value


class DataBlockSpacecraftParameters(DataBlock, KeywordContainer):

    """Spacecraft parameters block for OPM data section."""

    def __init__(self, comment=None, mass=None, solar_rad_area=None,
                 solar_rad_coeff=None, drag_area=None, drag_coeff=None):
        """Initialise spacecraft parameters data block.

        Required keywords:
        - mass
        - solar_rad_area
        - solar_rad_coeff
        - drag_area
        - drag_coeff

        Optional keywords:
        - comment
        """
        super().__init__()
        self._comment         = DataKeyword('COMMENT', comment,
                                            mandatory=False)
        self._mass            = DataKeyword('MASS', mass, units='kg',
                                            mandatory=False)
        self._solar_rad_area  = DataKeyword('SOLAR_RAD_AREA', solar_rad_area,
                                            units='m**2', mandatory=False)
        self._solar_rad_coeff = DataKeyword('SOLAR_RAD_COEFF', solar_rad_coeff,
                                            mandatory=False)
        self._drag_area       = DataKeyword('DRAG_AREA', drag_area,
                                            units='m**2', mandatory=False)
        self._drag_coeff      = DataKeyword('DRAG_COEFF', drag_coeff,
                                            mandatory=False)

        self.keywords = [
            self._comment,
            self._mass,
            self._solar_rad_area,
            self._solar_rad_coeff,
            self._drag_area,
            self._drag_coeff
        ]

    @property
    def comment(self):
        return self._comment

    @comment.setter
    def comment(self, value):
        self._comment.value = value

    @property
    def mass(self):
        return self._mass

    @mass.setter
    def mass(self, value):
        self._mass.value = value

    @property
    def solar_rad_area(self):
        return self._solar_rad_area

    @solar_rad_area.setter
    def solar_rad_area(self, value):
        self._solar_rad_area.value = value

    @property
    def y(self):
        return self._y

    @y.setter
    def y(self, value):
        self._y.value = value

    @property
    def solar_rad_coeff(self):
        return self._solar_rad_coeff

    @solar_rad_coeff.setter
    def solar_rad_coeff(self, value):
        self._solar_rad_coeff.value = value

    @property
    def drag_area(self):
        return self._drag_area

    @drag_area.setter
    def drag_area(self, value):
        self._drag_area.value = value

    @property
    def drag_coeff(self):
        return self._drag_coeff

    @drag_coeff.setter
    def drag_coeff(self, value):
        self._drag_coeff.value = value


class DataBlockCovarianceMatrix(DataBlock, KeywordContainer):

    """Covariance matrix block for data section."""

    def __init__(
        self, comment=None, cov_ref_frame=None,
        cx_x=None,
        cy_x=None,     cy_y=None,
        cz_x=None,     cz_y=None,     cz_z=None,
        cx_dot_x=None, cx_dot_y=None, cx_dot_z=None, cx_dot_x_dot=None,
        cy_dot_x=None, cy_dot_y=None, cy_dot_z=None, cy_dot_x_dot=None, cy_dot_y_dot=None,
        cz_dot_x=None, cz_dot_y=None, cz_dot_z=None, cz_dot_x_dot=None, cz_dot_y_dot=None, cz_dot_z_dot=None):
        """Initialise covariance matrix data block.

        Required keywords:
        - cx_x
        - cy_x
        - cy_y
        - cz_x
        - cz_y
        - cz_z
        - cx_dot_x
        - cx_dot_y
        - cx_dot_z
        - cx_dot_x_dot
        - cy_dot_x
        - cy_dot_y
        - cy_dot_z
        - cy_dot_x_dot
        - cy_dot_y_dot
        - cz_dot_x
        - cz_dot_y
        - cz_dot_z
        - cz_dot_x_dot
        - cz_dot_y_dot
        - cz_dot_z_dot

        Optional keywords:
        - comment
        - cov_ref_frame
        """
        super().__init__()
        self._comment       = DataKeyword('COMMENT', comment, mandatory=False)
        self._cov_ref_frame = DataKeyword('COV_REF_FRAME', cov_ref_frame,
                                          mandatory=False, formatter=lambda x: x.value)
        self._cx_x          = DataKeyword('CX_X', cx_x, units='km**2')
        self._cy_x          = DataKeyword('CY_X', cy_x, units='km**2')
        self._cy_y          = DataKeyword('CY_Y', cy_y, units='km**2')
        self._cz_x          = DataKeyword('CZ_X', cz_x, units='km**2')
        self._cz_y          = DataKeyword('CZ_Y', cz_y, units='km**2')
        self._cz_z          = DataKeyword('CZ_Z', cz_z, units='km**2')
        self._cx_dot_x      = DataKeyword('CX_DOT_X', cx_dot_x,
                                          units='km**2/s')
        self._cx_dot_y      = DataKeyword('CX_DOT_Y', cx_dot_y,
                                          units='km**2/s')
        self._cx_dot_z      = DataKeyword('CX_DOT_Z', cx_dot_z,
                                          units='km**2/s')
        self._cx_dot_x_dot  = DataKeyword('CX_DOT_X_DOT', cx_dot_x_dot,
                                          units='km**2/s**2')
        self._cy_dot_x      = DataKeyword('CY_DOT_X', cy_dot_x,
                                          units='km**2/s')
        self._cy_dot_y      = DataKeyword('CY_DOT_Y', cy_dot_y,
                                          units='km**2/s')
        self._cy_dot_z      = DataKeyword('CY_DOT_Z', cy_dot_z,
                                          units='km**2/s')
        self._cy_dot_x_dot  = DataKeyword('CY_DOT_X_DOT', cy_dot_x_dot,
                                          units='km**2/s**2')
        self._cy_dot_y_dot  = DataKeyword('CY_DOT_Y_DOT', cy_dot_y_dot,
                                          units='km**2/s**2')
        self._cz_dot_x      = DataKeyword('CZ_DOT_X', cz_dot_x,
                                          units='km**2/s')
        self._cz_dot_y      = DataKeyword('CZ_DOT_Y', cz_dot_y,
                                          units='km**2/s')
        self._cz_dot_z      = DataKeyword('CZ_DOT_Z', cz_dot_z,
                                          units='km**2/s')
        self._cz_dot_x_dot  = DataKeyword('CZ_DOT_X_DOT', cz_dot_x_dot,
                                          units='km**2/s**2')
        self._cz_dot_y_dot  = DataKeyword('CZ_DOT_Y_DOT', cz_dot_y_dot,
                                          units='km**2/s**2')
        self._cz_dot_z_dot  = DataKeyword('CZ_DOT_Z_DOT', cz_dot_z_dot,
                                          units='km**2/s**2')

        self.keywords = [
            self._comment,
            self._cov_ref_frame,
            self._cx_x,
            self._cy_x,
            self._cy_y,
            self._cz_x,
            self._cz_y,
            self._cz_z,
            self._cx_dot_x,
            self._cx_dot_y,
            self._cx_dot_z,
            self._cx_dot_x_dot,
            self._cy_dot_x,
            self._cy_dot_y,
            self._cy_dot_z,
            self._cy_dot_x_dot,
            self._cy_dot_y_dot,
            self._cz_dot_x,
            self._cz_dot_y,
            self._cz_dot_z,
            self._cz_dot_x_dot,
            self._cz_dot_y_dot,
            self._cz_dot_z_dot
        ]

    @property
    def comment(self):
        return self._comment

    @comment.setter
    def comment(self, value):
        self._comment.value = value

    @property
    def cov_ref_frame(self):
        return self._cov_ref_frame

    @cov_ref_frame.setter
    def cov_ref_frame(self, value):
        self._cov_ref_frame.value = value

    @property
    def cx_x(self):
        return self._cx_x

    @cx_x.setter
    def cx_x(self, value):
        self._cx_x.value = value

    @property
    def cy_x(self):
        return self._cy_x

    @cy_x.setter
    def cy_x(self, value):
        self._cy_x.value = value

    @property
    def cy_y(self):
        return self._cy_y

    @cy_y.setter
    def cy_y(self, value):
        self._cy_y.value = value

    @property
    def cz_x(self):
        return self._cz_x

    @cz_x.setter
    def cz_x(self, value):
        self._cz_x.value = value

    @property
    def cz_y(self):
        return self._cz_y

    @cz_y.setter
    def cz_y(self, value):
        self._cz_y.value = value

    @property
    def cz_z(self):
        return self._cz_z

    @cz_z.setter
    def cz_z(self, value):
        self._cz_z.value = value

    @property
    def cx_dot_x(self):
        return self._cx_dot_x

    @cx_dot_x.setter
    def cx_dot_x(self, value):
        self._cx_dot_x.value = value

    @property
    def cx_dot_y(self):
        return self._cx_dot_y

    @cx_dot_y.setter
    def cx_dot_y(self, value):
        self._cx_dot_y.value = value

    @property
    def cx_dot_z(self):
        return self._cx_dot_z

    @cx_dot_z.setter
    def cx_dot_z(self, value):
        self._cx_dot_z.value = value

    @property
    def cx_dot_x_dot(self):
        return self._cx_dot_x_dot

    @cx_dot_x_dot.setter
    def cx_dot_x_dot(self, value):
        self._cx_dot_x_dot.value = value

    @property
    def cy_dot_x(self):
        return self._cy_dot_x

    @cy_dot_x.setter
    def cy_dot_x(self, value):
        self._cy_dot_x.value = value

    @property
    def cy_dot_y(self):
        return self._cy_dot_y

    @cy_dot_y.setter
    def cy_dot_y(self, value):
        self._cy_dot_y.value = value

    @property
    def cy_dot_z(self):
        return self._cy_dot_z

    @cy_dot_z.setter
    def cy_dot_z(self, value):
        self._cy_dot_z.value = value

    @property
    def cy_dot_x_dot(self):
        return self._cy_dot_x_dot

    @cy_dot_x_dot.setter
    def cy_dot_x_dot(self, value):
        self._cy_dot_x_dot.value = value

    @property
    def cy_dot_y_dot(self):
        return self._cy_dot_y_dot

    @cy_dot_y_dot.setter
    def cy_dot_y_dot(self, value):
        self._cy_dot_y_dot.value = value

    @property
    def cz_dot_x(self):
        return self._cz_dot_x

    @cz_dot_x.setter
    def cz_dot_x(self, value):
        self._cz_dot_x.value = value

    @property
    def cz_dot_y(self):
        return self._cz_dot_y

    @cz_dot_y.setter
    def cz_dot_y(self, value):
        self._cz_dot_y.value = value

    @property
    def cz_dot_z(self):
        return self._cz_dot_z

    @cz_dot_z.setter
    def cz_dot_z(self, value):
        self._cz_dot_z.value = value

    @property
    def cz_dot_x_dot(self):
        return self._cz_dot_x_dot

    @cz_dot_x_dot.setter
    def cz_dot_x_dot(self, value):
        self._cz_dot_x_dot.value = value

    @property
    def cz_dot_y_dot(self):
        return self._cz_dot_y_dot

    @cz_dot_y_dot.setter
    def cz_dot_y_dot(self, value):
        self._cz_dot_y_dot.value = value

    @property
    def cz_dot_z_dot(self):
        return self._cz_dot_z_dot

    @cz_dot_z_dot.setter
    def cz_dot_z_dot(self, value):
        self._cz_dot_z_dot.value = value


class DataBlockManeuverParameters(DataBlock, KeywordContainer):

    """Maneuver parameters block for data section."""

    def __init__(self, comment=None, man_epoch_ignition=None,
                 man_duration=None, man_delta_mass=None, man_ref_frame=None,
                 man_dv_1=None, man_dv_2=None, man_dv_3=None):
        """Initialise maneuver parameters data block.

        Required keywords:
        - man_epoch_ignition
        - man_duration
        - man_delta_mass
        - man_ref_frame
        - man_dv_1
        - man_dv_2
        - man_dv_3

        Optional keywords:
        - comment
        """
        super().__init__()
        self._comment = DataKeyword('COMMENT', comment, mandatory=False)
        self._man_epoch_ignition = DataKeyword(
            'MAN_EPOCH_IGNITION', man_epoch_ignition,
            formatter=lambda x: x.isoformat(sep='T'),
            validator=validate_date)
        self._man_duration = DataKeyword('MAN_DURATION', man_duration,
                                         units='s')
        self._man_delta_mass = DataKeyword('MAN_DELTA_MASS', man_delta_mass,
                                           units='kg')
        self._man_ref_frame = DataKeyword('MAN_REF_FRAME', man_ref_frame,
                                          formatter=lambda x: x.value)
        self._man_dv_1 = DataKeyword('MAN_DV_1', man_dv_1, units='km/s')
        self._man_dv_2 = DataKeyword('MAN_DV_2', man_dv_2, units='km/s')
        self._man_dv_3 = DataKeyword('MAN_DV_3', man_dv_3, units='km/s')

        self.keywords = [
            self._comment,
            self._man_epoch_ignition,
            self._man_duration,
            self._man_delta_mass,
            self._man_ref_frame,
            self._man_dv_1,
            self._man_dv_2,
            self._man_dv_3
        ]

    @property
    def comment(self):
        return self._comment

    @comment.setter
    def comment(self, value):
        self._comment.value = value

    @property
    def man_epoch_ignition(self):
        return self._man_epoch_ignition

    @man_epoch_ignition.setter
    def man_epoch_ignition(self, value):
        self._man_epoch_ignition.value = value

    @property
    def man_duration(self):
        return self._man_duration

    @man_duration.setter
    def man_duration(self, value):
        self._man_duration.value = value

    @property
    def man_delta_mass(self):
        return self._man_delta_mass

    @man_delta_mass.setter
    def man_delta_mass(self, value):
        self._man_delta_mass.value = value

    @property
    def man_ref_frame(self):
        return self._man_ref_frame

    @man_ref_frame.setter
    def man_ref_frame(self, value):
        self._man_ref_frame.value = value

    @property
    def man_dv_1(self):
        return self._man_dv_1

    @man_dv_1.setter
    def man_dv_1(self, value):
        self._man_dv_1.value = value

    @property
    def man_dv_2(self):
        return self._man_dv_2

    @man_dv_2.setter
    def man_dv_2(self, value):
        self._man_dv_2.value = value

    @property
    def man_dv_3(self):
        return self._man_dv_3

    @man_dv_3.setter
    def man_dv_3(self, value):
        self._man_dv_3.value = value


class DataBlockContainer:
    def __init__(self, name, block, allow_multiple=False, mandatory=True,
                 prerequisite=lambda: True, prerequisite_error=None):
        self.name = name
        self.block = block
        self.allow_multiple = allow_multiple
        self.mandatory = mandatory
        self.prerequisite = prerequisite
        self.prerequisite_error = prerequisite_error


class Data:
    """OPM Data object (mandatory)."""
    def __init__(self, state_vector, spacecraft_parameters=None,
                 keplerian_elements=None, covariance_matrix=None,
                 maneuver_parameters=None):
        """Initialise data section from constituent blocks.

        Required blocks:
        - state_vector

        Optional blocks:
        - spacecraft_parameters
        - keplerian_elements
        - covariance_matrix
        - maneuver_parameters

        Note that maneuver_parameters can be an array of
        DataBlockManeuverParameters
        """
        self._state_vector = DataBlockContainer(
            name='State Vector Components',
            block=state_vector)
        self._spacecraft_parameters = DataBlockContainer(
            name='Spacecraft Parameters',
            block=spacecraft_parameters,
            mandatory=False)
        self._keplerian_elements = DataBlockContainer(
            name='Osculating Keplerian Elements',
            block=keplerian_elements,
            mandatory=False)
        self._covariance_matrix = DataBlockContainer(
            name='osition/Velocity Covariance Matrix',
            block=covariance_matrix,
            mandatory=False)
        self._maneuver_parameters = DataBlockContainer(
            name='Maneuver Parameters',
            block=maneuver_parameters,
            mandatory=False,
            allow_multiple=True,
            prerequisite=lambda: self._spacecraft_parameters.block is not None,
            prerequisite_error=('spacecraft parameters block mandatory if any '
                                'maneuver_parameters are given'))


        self.blocks = [
            self.state_vector,
            self.spacecraft_parameters,
            self.keplerian_elements,
            self.covariance_matrix,
            self.maneuver_parameters
        ]

    def validate_blocks(self):
        for bc in self.blocks:
            if bc.mandatory and bc.block is None:
                raise MissingBlockError(bc.name)
            if bc.block is not None:
                if not bc.prerequisite():
                    raise ValueError(bc.prerequisite_error)
                if not isinstance(bc.block, DataBlock):
                    if isinstance(bc.block, list):
                        if not bc.allow_multiple:
                            raise ValueError('the ''{name}'' block cannot be '
                                             'repeated.'.format(name=bc.name))
                        for block in bc.block:
                            if not isinstance(block, DataBlock):
                                raise TypeError('data blocks must subclass '
                                                '{}.DataBlock'.format(__name__))
                    else:
                        raise TypeError('data blocks must subclass {}.'
                                        'DataBlock, or be a list containing'
                                        ' them'.format(__name__))

    @property
    def state_vector(self):
        return self._state_vector

    @state_vector.setter
    def state_vector(self, value):
        if value is None:
            raise ValueError('state vector cannot be None.')
        self._state_vector.block = value

    @property
    def spacecraft_parameters(self):
        return self._spacecraft_parameters

    @spacecraft_parameters.setter
    def spacecraft_parameters(self, value):
        if self.maneuver_parameters is not None:
            if value is None:
                raise ValueError('spacecraft parameters mandatory if '
                                 'any maneuver parameters are set.')
        self._spacecraft_parameters.block = value

    @property
    def keplerian_elements(self):
        return self._keplerian_elements

    @keplerian_elements.setter
    def keplerian_elements(self, value):
        self._keplerian_elements.block = value

    @property
    def covariance_matrix(self):
        return self._covariance_matrix

    @covariance_matrix.setter
    def covariance_matrix(self, value):
        self._covariance_matrix.block = value

    @property
    def maneuver_parameters(self):
        return self._maneuver_parameters

    @maneuver_parameters.setter
    def maneuver_parameters(self, value):
        self._maneuver_parameters.block = value


class Opm:

    """Represent complete OPM.

    Also handles file writing.
    """

    def __init__(self, header, metadata, data, user_defined=None):
        """Initialise Opm

        header, metadata, and data are instances of Header, Metadata,
        and Data respectively.

        user_defined is a dictionary of parameters. The USER_DEFINED_ prefix
        is added automatically.
        """
        self.header = header
        self.metadata = metadata
        self.data = data
        self.user_defined = user_defined

        self.header.validate_keywords()
        self.metadata.validate_keywords()
        self.data.validate_blocks()

    def write(self, fp):
        fp.writelines(suffix('\n', self.output()))

    def output(self):
        for line in self.header.create_output_align_equals():
            yield line
        yield ''
        yield 'COMMENT Metadata'
        for line in self.metadata.create_output_align_equals():
            yield line
        yield ''
        for bc in self.data.blocks:
            if bc.block is not None:
                yield 'COMMENT %s' % (bc.name if bc.block.name is None else bc.block.name)
                for line in bc.block.create_output_align_decimal():
                    yield line
                yield ''
        if self.user_defined is not None:
            for key, value in self.user_defined.items():
                yield 'USER_DEFINED_{key} = {value}'.format(key=key,
                                                            value=value)
