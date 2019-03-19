from dateutil.relativedelta import relativedelta as relativedelta
import numpy as np

from nose.tools import raises
import pandas as pds

import pysat


class TestSpecificUTOrbits():

    def setup(self):
        """Runs before every method to create a clean testing setup."""
        info = {'index': 'mlt'}
        self.testInst = pysat.Instrument('pysat', 'testing', '86400',
                                         clean_level='clean',
                                         orbit_info=info, update_files=True)

    def teardown(self):
        """Runs after every method to clean up previous testing."""
        del self.testInst

    def test_single_orbit_call_by_0_index(self):
        self.testInst.load(2009, 1)
        self.testInst.orbits[0]
        ans = (self.testInst.index[0] == pds.datetime(2009, 1, 1))
        ans2 = (self.testInst.index[-1] == pds.datetime(2009, 1, 1, 1, 36, 59))
        # print (ans,ans2)
        # print (self.testInst.index[0], self.testInst.index[-1])
        assert ans & ans2

    def test_single_orbit_call_by_1_index(self):
        self.testInst.load(2009, 1)
        self.testInst.orbits[1]
        ans = (self.testInst.index[0] == pds.datetime(2009, 1, 1, 1, 37))
        ans2 = (self.testInst.index[-1] == pds.datetime(2009, 1, 1, 3, 13, 59))
        # print (ans,ans2)
        # print (self.testInst.index[0], self.testInst.index[-1])
        assert ans & ans2

    def test_single_orbit_call_by_negative_1_index(self):
        self.testInst.load(2008, 366)
        self.testInst.orbits[-1]
        ans = (self.testInst.index[0] ==
               (pds.datetime(2009, 1, 1)-relativedelta(hours=1, minutes=37)))
        ans2 = (self.testInst.index[-1] ==
                (pds.datetime(2009, 1, 1)-relativedelta(seconds=1)))
        assert ans & ans2

    def test_single_orbit_call_by_last_index(self):
        self.testInst.load(2008, 366)
        self.testInst.orbits[14]
        assert (self.testInst.index[0] ==
                (pds.datetime(2009, 1, 1)-relativedelta(hours=1, minutes=37)))
        assert (self.testInst.index[-1] ==
                (pds.datetime(2009, 1, 1)-relativedelta(seconds=1)))

    def test_all_single_orbit_calls_in_day(self):
        self.testInst.load(2009, 1)
        ans = []
        ans2 = []
        self.testInst.bounds = (pysat.datetime(2009, 1, 1), None)
        for i, inst in enumerate(self.testInst.orbits):
            if i > 14:
                break

            ans.append(self.testInst.index[0] ==
                       (pds.datetime(2009, 1, 1) +
                       i*relativedelta(hours=1, minutes=37)))
            ans2.append(self.testInst.index[-1] ==
                        (pds.datetime(2009, 1, 1) +
                        (i + 1) * relativedelta(hours=1, minutes=37) -
                        relativedelta(seconds=1)))

        assert np.all(ans) & np.all(ans2)

    def test_orbit_next_call_no_loaded_data(self):
        self.testInst.orbits.next()
        assert (self.testInst.index[0] == pds.datetime(2008, 1, 1))
        assert (self.testInst.index[-1] == pds.datetime(2008, 1, 1, 0, 38, 59))

    def test_orbit_prev_call_no_loaded_data(self):
        self.testInst.orbits.prev()
        # this isn't a full orbit
        assert (self.testInst.index[-1] ==
                pds.datetime(2010, 12, 31, 23, 59, 59))
        assert (self.testInst.index[0] == pds.datetime(2010, 12, 31, 23, 49))

    def test_single_orbit_call_orbit_starts_0_UT_using_next(self):
        self.testInst.load(2009, 1)
        self.testInst.orbits.next()
        assert (self.testInst.index[0] == pds.datetime(2009, 1, 1))
        assert (self.testInst.index[-1] == pds.datetime(2009, 1, 1, 1, 36, 59))

    def test_single_orbit_call_orbit_starts_0_UT_using_prev(self):
        self.testInst.load(2009, 1)
        self.testInst.orbits.prev()
        assert (self.testInst.index[0] ==
                (pds.datetime(2009, 1, 1) +
                14 * relativedelta(hours=1, minutes=37)))
        assert (self.testInst.index[-1] ==
                (pds.datetime(2009, 1, 1) +
                15 * relativedelta(hours=1, minutes=37) -
                relativedelta(seconds=1)))

    def test_single_orbit_call_orbit_starts_off_0_UT_using_next(self):
        from dateutil.relativedelta import relativedelta as relativedelta
        self.testInst.load(2008, 366)
        self.testInst.orbits.next()
        # print self.testInst.index[0], pds.datetime(2008,12,30, 23, 45),
        # self.testInst.index[-1], (pds.datetime(2008,12,30, 23, 45)+
        # relativedelta(hours=1, minutes=36, seconds=59))
        assert (self.testInst.index[0] == pds.datetime(2008, 12, 30, 23, 45))
        assert (self.testInst.index[-1] ==
                (pds.datetime(2008, 12, 30, 23, 45) +
                relativedelta(hours=1, minutes=36, seconds=59)))

    def test_single_orbit_call_orbit_starts_off_0_UT_using_prev(self):
        self.testInst.load(2008, 366)
        self.testInst.orbits.prev()
        assert (self.testInst.index[0] ==
                (pds.datetime(2009, 1, 1)-relativedelta(hours=1, minutes=37)))
        assert (self.testInst.index[-1] ==
                (pds.datetime(2009, 1, 1)-relativedelta(seconds=1)))


class TestGeneralOrbitsMLT():
    def setup(self):
        """Runs before every method to create a clean testing setup."""
        info = {'index': 'mlt'}
        self.testInst = pysat.Instrument('pysat', 'testing', '86400',
                                         clean_level='clean',
                                         orbit_info=info, update_files=True)

    def teardown(self):
        """Runs after every method to clean up previous testing."""
        del self.testInst

    def test_repeated_orbit_calls_symmetric_single_day_starting_with_last(self):
        self.testInst.load(2009, 1)
        # start on last orbit of last day
        self.testInst.orbits[0]
        self.testInst.orbits.prev()
        control = self.testInst.copy()
        for j in range(10):
            self.testInst.orbits.next()
        for j in range(10):
            self.testInst.orbits.prev()
        assert all(control.data == self.testInst.data)

    def test_repeated_orbit_calls_symmetric_single_day_0_UT(self):
        self.testInst.load(2009, 1)
        self.testInst.orbits.next()
        control = self.testInst.copy()
        for j in range(10):
            self.testInst.orbits.next()
        for j in range(10):
            self.testInst.orbits.prev()
        assert all(control.data == self.testInst.data)

    def test_repeated_orbit_calls_symmetric_multi_day_0_UT(self):
        self.testInst.load(2009, 1)
        self.testInst.orbits.next()
        control = self.testInst.copy()
        for j in range(20):
            self.testInst.orbits.next()
        for j in range(20):
            self.testInst.orbits.prev()
        assert all(control.data == self.testInst.data)

    def test_repeated_orbit_calls_symmetric_single_day_off_0_UT(self):
        self.testInst.load(2008, 366)
        self.testInst.orbits.next()
        control = self.testInst.copy()
        for j in range(10):
            self.testInst.orbits.next()
        for j in range(10):
            self.testInst.orbits.prev()
        assert all(control.data == self.testInst.data)

    def test_repeated_orbit_calls_symmetric_multi_day_off_0_UT(self):
        self.testInst.load(2008, 366)
        self.testInst.orbits.next()
        control = self.testInst.copy()
        for j in range(20):
            self.testInst.orbits.next()
        for j in range(20):
            self.testInst.orbits.prev()
        assert all(control.data == self.testInst.data)

    def test_repeated_orbit_calls_antisymmetric_multi_day_off_0_UT(self):
        self.testInst.load(2008, 366)
        self.testInst.orbits.next()
        control = self.testInst.copy()
        for j in range(10):
            self.testInst.orbits.next()
        for j in range(20):
            self.testInst.orbits.prev()
        for j in range(10):
            self.testInst.orbits.next()
        assert all(control.data == self.testInst.data)

    def test_repeated_orbit_calls_antisymmetric_multi_multi_day_off_0_UT(self):
        self.testInst.load(2008, 366)
        self.testInst.orbits.next()
        control = self.testInst.copy()
        for j in range(20):
            self.testInst.orbits.next()
        for j in range(40):
            self.testInst.orbits.prev()
        for j in range(20):
            self.testInst.orbits.next()
        assert all(control.data == self.testInst.data)

    def test_repeated_orbit_calls_antisymmetric_multi_day_0_UT(self):
        self.testInst.load(2009, 1)
        self.testInst.orbits.next()
        control = self.testInst.copy()
        for j in range(10):
            self.testInst.orbits.next()
        for j in range(20):
            self.testInst.orbits.prev()
        for j in range(10):
            self.testInst.orbits.next()
        assert all(control.data == self.testInst.data)

    def test_repeated_orbit_calls_antisymmetric_multi_multi_day_0_UT(self):
        self.testInst.load(2009, 1)
        self.testInst.orbits.next()
        control = self.testInst.copy()
        for j in range(20):
            self.testInst.orbits.next()
        for j in range(40):
            self.testInst.orbits.prev()
        for j in range(20):
            self.testInst.orbits.next()
        assert all(control.data == self.testInst.data)

    def test_repeated_orbit_calls_antisymmetric_multi_multi_day_0_UT_long_time_gap(self):
        self.testInst.load(2009, 12)
        self.testInst.orbits.next()
        control = self.testInst.copy()
        for j in range(20):
            self.testInst.orbits.next()
        for j in range(20):
            self.testInst.orbits.prev()
        assert all(control.data == self.testInst.data)

    def test_repeated_orbit_calls_antisymmetric_multi_multi_day_0_UT_really_long_time_gap(self):
        self.testInst.load(2009, 1)
        self.testInst.orbits.next()
        control = self.testInst.copy()
        for j in range(400):
            self.testInst.orbits.next()
        for j in range(400):
            self.testInst.orbits.prev()
        assert all(control.data == self.testInst.data)


    def test_repeated_orbit_calls_antisymmetric_multi_multi_day_0_UT_multiple_time_gaps(self):
        self.testInst.load(2009, 1)
        self.testInst.orbits.next()
        control = self.testInst.copy()
        n_time = []
        p_time = []
        for j in range(40):
            n_time.append(self.testInst.index[0])
            self.testInst.orbits.next()

        for j in range(40):
            self.testInst.orbits.prev()
            p_time.append(self.testInst.index[0])

        check = np.all(p_time == n_time[::-1])
        assert all(control.data == self.testInst.data) & check


class TestGeneralOrbitsMLTxarray(TestGeneralOrbitsMLT):
    def setup(self):
        """Runs before every method to create a clean testing setup."""
        info = {'index': 'mlt'}
        self.testInst = pysat.Instrument('pysat', 'testing_xarray', '86400',
                                         clean_level='clean',
                                         orbit_info=info, update_files=True)

    def teardown(self):
        """Runs after every method to clean up previous testing."""
        del self.testInst


class TestGeneralOrbitsLong(TestGeneralOrbitsMLT):

    def setup(self):
        """Runs before every method to create a clean testing setup."""
        info = {'index': 'longitude', 'kind': 'longitude'}
        self.testInst = pysat.Instrument('pysat', 'testing', '86400',
                                         clean_level='clean',
                                         orbit_info=info, update_files=True)

    def teardown(self):
        """Runs after every method to clean up previous testing."""
        del self.testInst


class TestGeneralOrbitsLongxarray(TestGeneralOrbitsMLT):

    def setup(self):
        """Runs before every method to create a clean testing setup."""
        info = {'index': 'longitude', 'kind': 'longitude'}
        self.testInst = pysat.Instrument('pysat', 'testing_xarray', '86400',
                                         clean_level='clean',
                                         orbit_info=info, update_files=True)

    def teardown(self):
        """Runs after every method to clean up previous testing."""
        del self.testInst


class TestGeneralOrbitsOrbitNumber(TestGeneralOrbitsMLT):

    def setup(self):
        """Runs before every method to create a clean testing setup."""
        info = {'index': 'orbit_num', 'kind': 'orbit'}
        self.testInst = pysat.Instrument('pysat', 'testing', '86400',
                                         clean_level='clean',
                                         orbit_info=info, update_files=True)

    def teardown(self):
        """Runs after every method to clean up previous testing."""
        del self.testInst


class TestGeneralOrbitsOrbitNumberXarray(TestGeneralOrbitsMLT):

    def setup(self):
        """Runs before every method to create a clean testing setup."""
        info = {'index': 'orbit_num', 'kind': 'orbit'}
        self.testInst = pysat.Instrument('pysat', 'testing_xarray', '86400',
                                         clean_level='clean',
                                         orbit_info=info, update_files=True)

    def teardown(self):
        """Runs after every method to clean up previous testing."""
        del self.testInst


class TestGeneralOrbitsLatitude(TestGeneralOrbitsMLT):

    def setup(self):
        """Runs before every method to create a clean testing setup."""
        info = {'index': 'latitude', 'kind': 'polar'}
        self.testInst = pysat.Instrument('pysat', 'testing', '86400',
                                         clean_level='clean',
                                         orbit_info=info, update_files=True)

    def teardown(self):
        """Runs after every method to clean up previous testing."""
        del self.testInst


class TestGeneralOrbitsLatitudeXarray(TestGeneralOrbitsMLT):

    def setup(self):
        """Runs before every method to create a clean testing setup."""
        info = {'index': 'latitude', 'kind': 'polar'}
        self.testInst = pysat.Instrument('pysat', 'testing_xarray', '86400',
                                         clean_level='clean',
                                         orbit_info=info, update_files=True)

    def teardown(self):
        """Runs after every method to clean up previous testing."""
        del self.testInst


def filter_data(inst):
    """Remove data from instrument, simulating gaps"""

    times = [[pysat.datetime(2009, 1, 1, 10),
              pysat.datetime(2009, 1, 1, 12)],
             [pysat.datetime(2009, 1, 1, 4),
              pysat.datetime(2009, 1, 2, 5, 37)],
             [pysat.datetime(2009, 1, 1, 1, 37),
              pysat.datetime(2009, 1, 1, 3, 14)],
             [pysat.datetime(2009, 1, 1, 15),
              pysat.datetime(2009, 1, 1, 16)],
             [pysat.datetime(2009, 1, 1, 22),
              pysat.datetime(2009, 1, 2, 2)],
             [pysat.datetime(2009, 1, 13),
              pysat.datetime(2009, 1, 15)],
             [pysat.datetime(2009, 1, 20, 1),
              pysat.datetime(2009, 1, 25, 23)],
             [pysat.datetime(2009, 1, 25, 23, 30),
              pysat.datetime(2009, 1, 26, 3)]
             ]
    for time in times:
        idx, = np.where((inst.index > time[1]) | (inst.index < time[0]))
        inst.data = inst[idx]


def filter_data2(inst, times=None):
    """Remove data from instrument, simulating gaps"""

    for time in times:
        idx, = np.where((inst.index > time[1]) | (inst.index < time[0]))
        inst.data = inst[idx]


class TestOrbitsGappyData(TestGeneralOrbitsMLT):
    def setup(self):
        """Runs before every method to create a clean testing setup."""
        info = {'index': 'mlt'}
        self.testInst = pysat.Instrument('pysat', 'testing', '86400',
                                         clean_level='clean',
                                         orbit_info=info, update_files=True)
        self.testInst.custom.add(filter_data, 'modify')

    def teardown(self):
        """Runs after every method to clean up previous testing."""
        del self.testInst


class TestOrbitsGappyDataXarray(TestGeneralOrbitsMLT):
    def setup(self):
        """Runs before every method to create a clean testing setup."""
        info = {'index': 'mlt'}
        self.testInst = pysat.Instrument('pysat', 'testing_xarray', '86400',
                                         clean_level='clean',
                                         orbit_info=info, update_files=True)
        self.testInst.custom.add(filter_data, 'modify')

    def teardown(self):
        """Runs after every method to clean up previous testing."""


class TestOrbitsGappyData2(TestGeneralOrbitsMLT):
    def setup(self):
        """Runs before every method to create a clean testing setup."""
        info = {'index': 'mlt'}
        self.testInst = pysat.Instrument('pysat', 'testing', '86400',
                                         clean_level='clean',
                                         orbit_info=info)
        times = [[pysat.datetime(2008, 12, 31, 4),
                  pysat.datetime(2008, 12, 31, 5, 37)],
                 [pysat.datetime(2009, 1, 1),
                  pysat.datetime(2009, 1, 1, 1, 37)]
                 ]
        for seconds in np.arange(38):
            day = pysat.datetime(2009, 1, 2) + \
                pds.DateOffset(days=int(seconds))
            times.append([day, day +
                          pds.DateOffset(hours=1, minutes=37,
                                         seconds=int(seconds)) -
                          pds.DateOffset(seconds=20)])

        self.testInst.custom.add(filter_data2, 'modify', times=times)

    def teardown(self):
        """Runs after every method to clean up previous testing."""
        del self.testInst


class TestOrbitsGappyData2Xarray(TestGeneralOrbitsMLT):
    def setup(self):
        """Runs before every method to create a clean testing setup."""
        info = {'index': 'mlt'}
        self.testInst = pysat.Instrument('pysat', 'testing_xarray', '86400',
                                         clean_level='clean',
                                         orbit_info=info)
        times = [[pysat.datetime(2008, 12, 31, 4),
                  pysat.datetime(2008, 12, 31, 5, 37)],
                 [pysat.datetime(2009, 1, 1),
                  pysat.datetime(2009, 1, 1, 1, 37)]
                 ]
        for seconds in np.arange(38):
            day = pysat.datetime(2009, 1, 2) + \
                pds.DateOffset(days=int(seconds))
            times.append([day, day +
                          pds.DateOffset(hours=1, minutes=37,
                                         seconds=int(seconds)) -
                          pds.DateOffset(seconds=20)])

        self.testInst.custom.add(filter_data2, 'modify', times=times)

    def teardown(self):
        """Runs after every method to clean up previous testing."""
        del self.testInst


class TestOrbitsGappyLongData(TestGeneralOrbitsMLT):
    def setup(self):
        """Runs before every method to create a clean testing setup."""
        info = {'index': 'longitude', 'kind': 'longitude'}
        self.testInst = pysat.Instrument('pysat', 'testing', '86400',
                                         clean_level='clean',
                                         orbit_info=info)
        self.testInst.custom.add(filter_data, 'modify')

    def teardown(self):
        """Runs after every method to clean up previous testing."""
        del self.testInst


class TestOrbitsGappyLongDataXarray(TestGeneralOrbitsMLT):
    def setup(self):
        """Runs before every method to create a clean testing setup."""
        info = {'index': 'longitude', 'kind': 'longitude'}
        self.testInst = pysat.Instrument('pysat', 'testing_xarray', '86400',
                                         clean_level='clean',
                                         orbit_info=info)
        self.testInst.custom.add(filter_data, 'modify')

    def teardown(self):
        """Runs after every method to clean up previous testing."""
        del self.testInst


class TestOrbitsGappyOrbitNumData(TestGeneralOrbitsMLT):
    def setup(self):
        """Runs before every method to create a clean testing setup."""
        info = {'index': 'orbit_num', 'kind': 'orbit'}
        self.testInst = pysat.Instrument('pysat', 'testing', '86400',
                                         clean_level='clean',
                                         orbit_info=info)
        self.testInst.custom.add(filter_data, 'modify')

    def teardown(self):
        """Runs after every method to clean up previous testing."""
        del self.testInst


class TestOrbitsGappyOrbitNumDataXarray(TestGeneralOrbitsMLT):
    def setup(self):
        """Runs before every method to create a clean testing setup."""
        info = {'index': 'orbit_num', 'kind': 'orbit'}
        self.testInst = pysat.Instrument('pysat', 'testing_xarray', '86400',
                                         clean_level='clean',
                                         orbit_info=info)
        self.testInst.custom.add(filter_data, 'modify')

    def teardown(self):
        """Runs after every method to clean up previous testing."""
        del self.testInst


class TestOrbitsGappyOrbitLatData(TestGeneralOrbitsMLT):
    def setup(self):
        """Runs before every method to create a clean testing setup."""
        info = {'index': 'latitude', 'kind': 'polar'}
        self.testInst = pysat.Instrument('pysat', 'testing', '86400',
                                         clean_level='clean',
                                         orbit_info=info)
        self.testInst.custom.add(filter_data, 'modify')

    def teardown(self):
        """Runs after every method to clean up previous testing."""
        del self.testInst


class TestOrbitsGappyOrbitLatDataXarray(TestGeneralOrbitsMLT):
    def setup(self):
        """Runs before every method to create a clean testing setup."""
        info = {'index': 'latitude', 'kind': 'polar'}
        self.testInst = pysat.Instrument('pysat', 'testing_xarray', '86400',
                                         clean_level='clean',
                                         orbit_info=info)
        self.testInst.custom.add(filter_data, 'modify')

    def teardown(self):
        """Runs after every method to clean up previous testing."""
        del self.testInst
