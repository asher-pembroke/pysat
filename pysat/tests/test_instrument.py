# -*- coding: utf-8 -*-
# Test some of the basic _core functions
import numpy as np
import sys

from nose.tools import raises
import pandas as pds

import pysat
import pysat.instruments.pysat_testing

if sys.version_info[0] >= 3:
    from importlib import reload as re_load
else:
    re_load = reload


class TestBasics():
    def setup(self):
        re_load(pysat.instruments.pysat_testing)
        """Runs before every method to create a clean testing setup."""
        self.testInst = pysat.Instrument('pysat', 'testing', '10',
                                         clean_level='clean',
                                         update_files=True)

    def teardown(self):
        """Runs after every method to clean up previous testing."""
        del self.testInst

###########################
    # basic loading tests, by date, filename, file id
    # and checks for .next and .prev data loading
    def test_basic_instrument_load(self):
        """Test if the correct day is being loaded (checking object date and
        data)."""
        self.testInst.load(2009, 1)
        test_date = self.testInst.index[0]
        test_date = pysat.datetime(test_date.year, test_date.month,
                                   test_date.day)
        assert (test_date == pds.datetime(2009, 1, 1)) & \
            (test_date == self.testInst.date)

    def test_basic_instrument_load_data(self):
        """Test if the correct day is being loaded (checking data down to the
        second)."""
        self.testInst.load(2009, 1)
        assert self.testInst.index[0] == pds.datetime(2009, 1, 1, 0, 0, 0)

    def test_basic_instrument_load_leap_year(self):
        """Test if the correct day is being loaded (Leap-Year)."""
        self.testInst.load(2008, 366)
        test_date = self.testInst.index[0]
        test_date = pysat.datetime(test_date.year, test_date.month,
                                   test_date.day)
        assert (test_date == pds.datetime(2008, 12, 31)) & \
            (test_date == self.testInst.date)

    def test_next_load_default(self):
        """Test if first day is loaded by default when first invoking .next."""
        self.testInst.next()
        test_date = self.testInst.index[0]
        test_date = pysat.datetime(test_date.year, test_date.month,
                                   test_date.day)
        assert test_date == pds.datetime(2008, 1, 1)

    def test_prev_load_default(self):
        """Test if last day is loaded by default when first invoking .prev."""
        self.testInst.prev()
        test_date = self.testInst.index[0]
        test_date = pysat.datetime(test_date.year, test_date.month,
                                   test_date.day)
        assert test_date == pds.datetime(2010, 12, 31)

    def test_basic_fid_instrument_load(self):
        """Test if first day is loaded by default when first invoking .next."""
        self.testInst.load(fid=0)
        test_date = self.testInst.index[0]
        test_date = pysat.datetime(test_date.year, test_date.month,
                                   test_date.day)
        assert (test_date == pds.datetime(2008, 1, 1)) & \
            (test_date == self.testInst.date)

    def test_next_fid_load_default(self):
        """Test next day is being loaded (checking object date)."""
        self.testInst.load(fid=0)
        self.testInst.next()
        test_date = self.testInst.index[0]
        test_date = pysat.datetime(test_date.year, test_date.month,
                                   test_date.day)
        assert (test_date == pds.datetime(2008, 1, 2)) & \
            (test_date == self.testInst.date)

    def test_prev_fid_load_default(self):
        """Test prev day is loaded when invoking .prev."""
        self.testInst.load(fid=3)
        self.testInst.prev()
        test_date = self.testInst.index[0]
        test_date = pysat.datetime(test_date.year, test_date.month,
                                   test_date.day)
        assert (test_date == pds.datetime(2008, 1, 3)) & \
            (test_date == self.testInst.date)

    def test_filename_load(self):
        """Test if file is loadable by filename, relative to
        top_data_dir/platform/name/tag"""
        self.testInst.load(fname='2010-12-31.nofile')
        assert self.testInst.index[0] == pds.datetime(2010, 12, 31)

    def test_next_filename_load_default(self):
        """Test next day is being loaded (checking object date)."""
        self.testInst.load(fname='2010-12-30.nofile')
        self.testInst.next()
        test_date = self.testInst.index[0]
        test_date = pysat.datetime(test_date.year, test_date.month,
                                   test_date.day)
        assert (test_date == pds.datetime(2010, 12, 31)) & \
            (test_date == self.testInst.date)

    def test_prev_filename_load_default(self):
        """Test prev day is loaded when invoking .prev."""
        self.testInst.load(fname='2009-01-04.nofile')
        # print(self.testInst.date)
        self.testInst.prev()
        test_date = self.testInst.index[0]
        test_date = pysat.datetime(test_date.year, test_date.month,
                                   test_date.day)
        assert (test_date == pds.datetime(2009, 1, 3)) & \
            (test_date == self.testInst.date)

    ############################
    # test basic date helpers
    def test_today_yesterday_and_tomorrow(self):
        now = pysat.datetime.now()
        today = pysat.datetime(now.year, now.month, now.day)
        assert today == self.testInst.today()
        assert today - pds.DateOffset(days=1) == self.testInst.yesterday()
        assert today + pds.DateOffset(days=1) == self.testInst.tomorrow()

    def test_filter_datetime(self):
        now = pysat.datetime.now()
        today = pysat.datetime(now.year, now.month, now.day)
        assert today == self.testInst._filter_datetime_input(now)

    ###########################
    # test flags
    def test_empty_flag_data_empty(self):
        assert self.testInst.empty

    def test_empty_flag_data_not_empty(self):
        self.testInst.load(2009, 1)
        assert not self.testInst.empty

    ############################
    # test the textual representation
    def test_basic_repr(self):
        print(self.testInst)
        assert True

    def test_repr_w_orbit(self):
        self.testInst.orbit_info = {'index': 'mlt',
                                    'kind': 'local time',
                                    'period': np.timedelta64(97, 'm')}
        self.testInst.orbits.num = 10
        print(self.testInst)
        assert True

    def test_repr_w_padding(self):
        self.testInst.pad = pds.DateOffset(minutes=5)
        print(self.testInst)
        assert True

    def test_repr_w_custom_func(self):
        def testfunc(self):
            pass
        self.testInst.custom.add(testfunc, 'modify')
        print(self.testInst)
        assert True

    def test_repr_w_load_data(self):
        self.testInst.load(2009, 1)
        print(self.testInst)
        assert True

# testing init functions

# need to check with default1!!!!!
    def test_instrument_init(self):
        """Test if init function supplied by instrument can modify object"""
        assert self.testInst.new_thing is True

    def test_custom_instrument_load(self):
        """
        Test if the correct day is being loaded (End-to-End),
        with no instrument file but routines are passed.
        """
        import pysat.instruments.pysat_testing as test
        testInst = pysat.Instrument(inst_module=test, tag='',
                                    clean_level='clean')
        testInst.load(2009, 32)
        assert testInst.date == pds.datetime(2009, 2, 1)

    @raises(AttributeError)
    def test_custom_instrument_load_2(self):
        """
        Test if an exception is thrown correctly if there is no
        instrument file and supplied routines are incomplete.
        """
        import pysat.instruments.pysat_testing as test
        del test.list_files
        testIn = pysat.Instrument(inst_module=test, tag='',
                                  clean_level='clean')
        testIn.load(2009, 1)

    @raises(AttributeError)
    def test_custom_instrument_load_3(self):
        """
        Test if an exception is thrown correctly if there is no
        instrument file and supplied routines are incomplete.
        """
        import pysat.instruments.pysat_testing as test
        del test.load
        testIn = pysat.Instrument(inst_module=test, tag='',
                                  clean_level='clean')
        testIn.load(2009, 1)

###################
    # test data setting features
    def test_basic_data_access_by_name(self):
        self.testInst.load(2009, 1)
        assert np.all(self.testInst['uts'] == self.testInst.data['uts'])

    def test_data_access_by_row_slicing_and_name(self):
        self.testInst.load(2009, 1)
        assert np.all(self.testInst[0:10, 'uts'] ==
                      self.testInst.data['uts'].values[0:10])

    def test_data_access_by_row_slicing_w_ndarray_and_name(self):
        self.testInst.load(2009, 1)
        assert np.all(self.testInst[np.arange(0, 10), 'uts'] ==
                      self.testInst.data['uts'].values[0:10])

    def test_data_access_by_row_and_name(self):
        self.testInst.load(2009, 1)
        assert np.all(self.testInst[0, 'uts'] ==
                      self.testInst.data['uts'].values[0])

    def test_data_access_by_row_index(self):
        self.testInst.load(2009, 1)
        idx = np.arange(10)
        assert np.all(self.testInst[idx]['uts'] ==
                      self.testInst.data['uts'].values[idx])

    def test_data_access_by_datetime_and_name(self):
        self.testInst.load(2009, 1)
        ind = pysat.datetime(2009, 1, 1, 0, 0, 0)
        assert np.all(self.testInst[ind, 'uts'] ==
                      self.testInst.data['uts'].values[0])

    def test_data_access_by_datetime_slicing_and_name(self):
        self.testInst.load(2009, 1)
        start = pysat.datetime(2009, 1, 1, 0, 0, 0)
        stop = pysat.datetime(2009, 1, 1, 0, 0, 10)
        assert np.all(self.testInst[start:stop, 'uts'] ==
                      self.testInst.data['uts'].values[0:11])

    def test_setting_data_by_name(self):
        self.testInst.load(2009, 1)
        self.testInst['doubleMLT'] = 2. * self.testInst['mlt']
        assert np.all(self.testInst['doubleMLT'] == 2. * self.testInst['mlt'])

    def test_setting_series_data_by_name(self):
        self.testInst.load(2009, 1)
        self.testInst['doubleMLT'] = 2.*pds.Series(self.testInst['mlt'].values,
                                                   index=self.testInst.index)
        assert np.all(self.testInst['doubleMLT'] == 2.*self.testInst['mlt'])

        self.testInst['blankMLT'] = pds.Series(None)
        assert np.all(np.isnan(self.testInst['blankMLT']))

    def test_setting_pandas_dataframe_by_names(self):
        self.testInst.load(2009, 1)
        self.testInst[['doubleMLT', 'tripleMLT']] = \
            pds.DataFrame({'doubleMLT': 2.*self.testInst['mlt'].values,
                           'tripleMLT': 3.*self.testInst['mlt'].values},
                          index=self.testInst.index)
        assert np.all(self.testInst['doubleMLT'] == 2.*self.testInst['mlt'])
        assert np.all(self.testInst['tripleMLT'] == 3.*self.testInst['mlt'])

    def test_setting_data_by_name_single_element(self):
        self.testInst.load(2009, 1)
        self.testInst['doubleMLT'] = 2.
        assert np.all(self.testInst['doubleMLT'] == 2.)

        self.testInst['nanMLT'] = np.nan
        assert np.all(np.isnan(self.testInst['nanMLT']))

    def test_setting_data_by_name_with_meta(self):
        self.testInst.load(2009, 1)
        self.testInst['doubleMLT'] = {'data': 2.*self.testInst['mlt'],
                                      'units': 'hours',
                                      'long_name': 'double trouble'}
        assert np.all(self.testInst['doubleMLT'] == 2.*self.testInst['mlt'])
        assert self.testInst.meta['doubleMLT'].units == 'hours'
        assert self.testInst.meta['doubleMLT'].long_name == 'double trouble'

    def test_setting_partial_data(self):
        self.testInst.load(2009, 1)
        cloneInst = self.testInst
        if self.testInst.pandas_format:
            self.testInst[0:3] = 0
            assert (np.all(self.testInst[3:] == cloneInst[3:]) &
                    np.all(self.testInst[0:3] == 0))
        else:
            # This command does not work for xarray
            assert True

    def test_setting_partial_data_by_name(self):
        self.testInst.load(2009, 1)
        self.testInst['doubleMLT'] = 2. * self.testInst['mlt']
        self.testInst[0, 'doubleMLT'] = 0
        assert np.all(self.testInst[1:, 'doubleMLT'] ==
                      2. * self.testInst[1:, 'mlt'])
        assert self.testInst[0, 'doubleMLT'] == 0

    def test_setting_partial_data_by_integer_and_name(self):
        self.testInst.load(2009, 1)
        self.testInst['doubleMLT'] = 2.*self.testInst['mlt']
        self.testInst[[0, 1, 2, 3], 'doubleMLT'] = 0
        assert np.all(self.testInst[4:, 'doubleMLT'] ==
                      2. * self.testInst[4:, 'mlt'])
        assert np.all(self.testInst[[0, 1, 2, 3], 'doubleMLT'] == 0)

    def test_setting_partial_data_by_slice_and_name(self):
        self.testInst.load(2009, 1)
        self.testInst['doubleMLT'] = 2. * self.testInst['mlt']
        self.testInst[0:10, 'doubleMLT'] = 0
        assert np.all(self.testInst[10:, 'doubleMLT'] ==
                      2. * self.testInst[10:, 'mlt'])
        assert np.all(self.testInst[0:10, 'doubleMLT'] == 0)

    def test_setting_partial_data_by_index_and_name(self):
        self.testInst.load(2009, 1)
        self.testInst['doubleMLT'] = 2. * self.testInst['mlt']
        self.testInst[self.testInst.index[0:10], 'doubleMLT'] = 0
        assert np.all(self.testInst[10:, 'doubleMLT'] ==
                      2. * self.testInst[10:, 'mlt'])
        assert np.all(self.testInst[0:10, 'doubleMLT'] == 0)

    def test_setting_partial_data_by_numpy_array_and_name(self):
        self.testInst.load(2009, 1)
        self.testInst['doubleMLT'] = 2. * self.testInst['mlt']
        self.testInst[np.array([0, 1, 2, 3]), 'doubleMLT'] = 0
        assert np.all(self.testInst[4:, 'doubleMLT'] ==
                      2. * self.testInst[4:, 'mlt'])
        assert np.all(self.testInst[0:4, 'doubleMLT'] == 0)

    def test_setting_partial_data_by_datetime_and_name(self):
        self.testInst.load(2009, 1)
        self.testInst['doubleMLT'] = 2. * self.testInst['mlt']
        self.testInst[pysat.datetime(2009, 1, 1, 0, 0, 0), 'doubleMLT'] = 0
        assert np.all(self.testInst[0, 'doubleMLT'] ==
                      2. * self.testInst[0, 'mlt'])
        assert np.all(self.testInst[0, 'doubleMLT'] == 0)

    def test_setting_partial_data_by_datetime_slicing_and_name(self):
        self.testInst.load(2009, 1)
        self.testInst['doubleMLT'] = 2. * self.testInst['mlt']
        self.testInst[pysat.datetime(2009, 1, 1, 0, 0, 0):
                      pysat.datetime(2009, 1, 1, 0, 0, 10),
                      'doubleMLT'] = 0
        assert np.all(self.testInst[11:, 'doubleMLT'] ==
                      2. * self.testInst[11:, 'mlt'])
        assert np.all(self.testInst[0:11, 'doubleMLT'] == 0)

    def test_modifying_data_inplace(self):
        self.testInst.load(2009, 1)
        self.testInst['doubleMLT'] = 2. * self.testInst['mlt']
        self.testInst['doubleMLT'] += 100
        assert np.all(self.testInst['doubleMLT'] ==
                      2.*self.testInst['mlt'] + 100)

    def test_getting_all_data_by_index(self):
        self.testInst.load(2009, 1)
        a = self.testInst[[0, 1, 2, 3, 4]]
        if self.testInst.pandas_format:
            assert len(a) == 5
        else:
            assert a.sizes['time'] == 5

    def test_getting_all_data_by_numpy_array_of_int(self):
        self.testInst.load(2009, 1)
        a = self.testInst[np.array([0, 1, 2, 3, 4])]
        if self.testInst.pandas_format:
            assert len(a) == 5
        else:
            assert a.sizes['time'] == 5

# check iteration behavior
    @raises(StopIteration)
    def test_left_bounds_with_prev(self):
        """Test if passing bounds raises StopIteration."""
        # load first data
        self.testInst.next()
        # go back to no data
        self.testInst.prev()
        # self.testInst.prev()

    @raises(StopIteration)
    def test_right_bounds_with_next(self):
        """Test if passing bounds raises StopIteration."""
        # load last data
        self.testInst.prev()
        # move on to future data that doesn't exist
        self.testInst.next()
        # self.testInst.next()

    def test_set_bounds_by_date(self):
        start = pysat.datetime(2009, 1, 1)
        stop = pysat.datetime(2009, 1, 15)
        self.testInst.bounds = (start, stop)
        assert np.all(self.testInst._iter_list ==
                      pds.date_range(start, stop).tolist())

    def test_iterate_over_bounds_set_by_date(self):
        start = pysat.datetime(2009, 1, 1)
        stop = pysat.datetime(2009, 1, 15)
        self.testInst.bounds = (start, stop)
        dates = []
        for inst in self.testInst:
            dates.append(inst.date)
        out = pds.date_range(start, stop).tolist()
        assert np.all(dates == out)

    def test_iterate_over_default_bounds(self):
        start = pysat.datetime(2008, 1, 1)
        stop = pysat.datetime(2010, 12, 31)
        self.testInst.bounds = (start, stop)
        dates = []
        for inst in self.testInst:
            dates.append(inst.date)
        out = pds.date_range(start, stop).tolist()
        assert np.all(dates == out)

    def test_set_bounds_by_date_season(self):
        start = [pysat.datetime(2009, 1, 1), pysat.datetime(2009, 2, 1)]
        stop = [pysat.datetime(2009, 1, 15), pysat.datetime(2009, 2, 15)]
        self.testInst.bounds = (start, stop)
        out = pds.date_range(start[0], stop[0]).tolist()
        out.extend(pds.date_range(start[1], stop[1]).tolist())
        assert np.all(self.testInst._iter_list == out)

    def test_iterate_over_bounds_set_by_date_season(self):
        start = [pysat.datetime(2009, 1, 1), pysat.datetime(2009, 2, 1)]
        stop = [pysat.datetime(2009, 1, 15), pysat.datetime(2009, 2, 15)]
        self.testInst.bounds = (start, stop)
        dates = []
        for inst in self.testInst:
            dates.append(inst.date)
        out = pds.date_range(start[0], stop[0]).tolist()
        out.extend(pds.date_range(start[1], stop[1]).tolist())
        assert np.all(dates == out)

    def test_set_bounds_by_fname(self):
        start = '2009-01-01.nofile'
        stop = '2009-01-03.nofile'
        self.testInst.bounds = (start, stop)
        assert np.all(self.testInst._iter_list ==
                      ['2009-01-01.nofile', '2009-01-02.nofile',
                       '2009-01-03.nofile'])

    def test_iterate_over_bounds_set_by_fname(self):
        start = '2009-01-01.nofile'
        stop = '2009-01-15.nofile'
        start_d = pysat.datetime(2009, 1, 1)
        stop_d = pysat.datetime(2009, 1, 15)
        self.testInst.bounds = (start, stop)
        dates = []
        for inst in self.testInst:
            dates.append(inst.date)
        out = pds.date_range(start_d, stop_d).tolist()
        assert np.all(dates == out)

    def test_iterate_over_bounds_set_by_fname_via_next(self):
        start = '2009-01-01.nofile'
        stop = '2009-01-15.nofile'
        start_d = pysat.datetime(2009, 1, 1)
        stop_d = pysat.datetime(2009, 1, 15)
        self.testInst.bounds = (start, stop)
        dates = []
        self.testInst.next()
        dates.append(self.testInst.date)
        while self.testInst.date < stop_d:
            self.testInst.next()
            dates.append(self.testInst.date)
        out = pds.date_range(start_d, stop_d).tolist()
        assert np.all(dates == out)

    def test_iterate_over_bounds_set_by_fname_via_prev(self):
        start = '2009-01-01.nofile'
        stop = '2009-01-15.nofile'
        start_d = pysat.datetime(2009, 1, 1)
        stop_d = pysat.datetime(2009, 1, 15)
        self.testInst.bounds = (start, stop)
        dates = []
        self.testInst.prev()
        dates.append(self.testInst.date)
        while self.testInst.date > start_d:
            self.testInst.prev()
            dates.append(self.testInst.date)
        out = pds.date_range(start_d, stop_d).tolist()
        assert np.all(dates == out[::-1])

    def test_set_bounds_by_fname_season(self):
        start = ['2009-01-01.nofile', '2009-02-01.nofile']
        stop = ['2009-01-03.nofile', '2009-02-03.nofile']
        self.testInst.bounds = (start, stop)
        assert np.all(self.testInst._iter_list ==
                      ['2009-01-01.nofile', '2009-01-02.nofile',
                       '2009-01-03.nofile', '2009-02-01.nofile',
                       '2009-02-02.nofile', '2009-02-03.nofile'])

    def test_iterate_over_bounds_set_by_fname_season(self):
        start = ['2009-01-01.nofile', '2009-02-01.nofile']
        stop = ['2009-01-15.nofile', '2009-02-15.nofile']
        start_d = [pysat.datetime(2009, 1, 1), pysat.datetime(2009, 2, 1)]
        stop_d = [pysat.datetime(2009, 1, 15), pysat.datetime(2009, 2, 15)]
        self.testInst.bounds = (start, stop)
        dates = []
        for inst in self.testInst:
            dates.append(inst.date)
        out = pds.date_range(start_d[0], stop_d[0]).tolist()
        out.extend(pds.date_range(start_d[1], stop_d[1]).tolist())
        assert np.all(dates == out)

    def test_creating_empty_instrument_object(self):
        null = pysat.Instrument()

        assert isinstance(null, pysat.Instrument)

    @raises(ValueError)
    def test_incorrect_creation_empty_instrument_object(self):
        # both name and platform should be empty
        null = pysat.Instrument(platform='cnofs')

    @raises(AttributeError)
    def test_supplying_instrument_module_requires_name_and_platform(self):
        class Dummy:
            pass
        Dummy.name = 'help'

        temp = pysat.Instrument(inst_module=Dummy)


class TestBasicsXarray(TestBasics):
    def setup(self):
        re_load(pysat.instruments.pysat_testing)
        """Runs before every method to create a clean testing setup."""
        self.testInst = pysat.Instrument('pysat', 'testing_xarray', '10',
                                         clean_level='clean',
                                         update_files=True)

    def teardown(self):
        """Runs after every method to clean up previous testing."""
        del self.testInst


class TestDataPaddingbyFile():
    def setup(self):
        re_load(pysat.instruments.pysat_testing)
        """Runs before every method to create a clean testing setup."""
        self.testInst = pysat.Instrument('pysat', 'testing', '',
                                         clean_level='clean',
                                         pad={'minutes': 5},
                                         update_files=True)
        self.testInst.bounds = ('2008-01-01.nofile', '2010-12-31.nofile')

        self.rawInst = pysat.Instrument('pysat', 'testing', '',
                                        clean_level='clean',
                                        update_files=True)
        self.rawInst.bounds = self.testInst.bounds

    def teardown(self):
        """Runs after every method to clean up previous testing."""
        del self.testInst
        del self.rawInst

    def test_fid_data_padding(self):
        self.testInst.load(fid=1, verifyPad=True)
        self.rawInst.load(fid=1)
        assert ((self.testInst.index[0] ==
                 self.rawInst.index[0] - pds.DateOffset(minutes=5)) &
                (self.testInst.index[-1] ==
                 self.rawInst.index[-1] + pds.DateOffset(minutes=5)))

    def test_fid_data_padding_next(self):
        self.testInst.load(fid=1, verifyPad=True)
        self.testInst.next(verifyPad=True)
        self.rawInst.load(fid=2)
        assert ((self.testInst.index[0] ==
                 self.rawInst.index[0] - pds.DateOffset(minutes=5)) &
                (self.testInst.index[-1] ==
                 self.rawInst.index[-1] + pds.DateOffset(minutes=5)))

    def test_fid_data_padding_multi_next(self):
        """This also tests that _prev_data and _next_data cacheing"""
        self.testInst.load(fid=1)
        self.testInst.next()
        self.testInst.next(verifyPad=True)
        self.rawInst.load(fid=3)
        assert ((self.testInst.index[0] ==
                 self.rawInst.index[0] - pds.DateOffset(minutes=5)) &
                (self.testInst.index[-1] ==
                 self.rawInst.index[-1] + pds.DateOffset(minutes=5)))

    def test_fid_data_padding_prev(self):
        self.testInst.load(fid=2, verifyPad=True)
        self.testInst.prev(verifyPad=True)
        # print(self.testInst.index)
        self.rawInst.load(fid=1)
        # print(self.rawInst.index)
        # print(self.testInst.index[0], self.rawInst.index[0] -
        #   pds.DateOffset(minutes=5), self.testInst.index[-1],
        #   self.rawInst.index[-1] + pds.DateOffset(minutes=5))
        assert ((self.testInst.index[0] ==
                 self.rawInst.index[0] - pds.DateOffset(minutes=5)) &
                (self.testInst.index[-1] ==
                 self.rawInst.index[-1] + pds.DateOffset(minutes=5)))

    def test_fid_data_padding_multi_prev(self):
        """This also tests that _prev_data and _next_data cacheing"""
        self.testInst.load(fid=10)
        self.testInst.prev()
        self.testInst.prev(verifyPad=True)
        self.rawInst.load(fid=8)
        assert ((self.testInst.index[0] ==
                 self.rawInst.index[0] - pds.DateOffset(minutes=5)) &
                (self.testInst.index[-1] ==
                 self.rawInst.index[-1] + pds.DateOffset(minutes=5)))

    def test_fid_data_padding_jump(self):
        self.testInst.load(fid=1, verifyPad=True)
        self.testInst.load(fid=10, verifyPad=True)
        self.rawInst.load(fid=10)
        assert ((self.testInst.index[0] ==
                 self.rawInst.index[0] - pds.DateOffset(minutes=5)) &
                (self.testInst.index[-1] ==
                 self.rawInst.index[-1] + pds.DateOffset(minutes=5)))

    def test_fid_data_padding_uniqueness(self):
        self.testInst.load(fid=1, verifyPad=True)
        assert (self.testInst.index.is_unique)

    def test_fid_data_padding_all_samples_present(self):
        self.testInst.load(fid=1, verifyPad=True)
        test_index = pds.date_range(self.testInst.index[0],
                                    self.testInst.index[-1], freq='S')
        # print (test_index[0], test_index[-1], len(test_index))
        # print(self.testInst.index[0], self.testInst.index[-1],
        #       len(self.testInst.data))
        assert (np.all(self.testInst.index == test_index))

    def test_fid_data_padding_removal(self):
        self.testInst.load(fid=1)
        self.rawInst.load(fid=1)
        # print(self.testInst.index)
        # print(new_inst.data.index)
        assert self.testInst.index[0] == self.rawInst.index[0]
        assert self.testInst.index[-1] == self.rawInst.index[-1]
        assert len(self.rawInst.data) == len(self.testInst.data)


class TestDataPaddingbyFileXarray():
    def setup(self):
        re_load(pysat.instruments.pysat_testing)
        """Runs before every method to create a clean testing setup."""
        self.testInst = pysat.Instrument('pysat', 'testing_xarray', '',
                                         clean_level='clean',
                                         pad={'minutes': 5},
                                         update_files=True)
        self.testInst.bounds = ('2008-01-01.nofile', '2010-12-31.nofile')

        self.rawInst = pysat.Instrument('pysat', 'testing_xarray', '',
                                        clean_level='clean',
                                        update_files=True)
        self.rawInst.bounds = self.testInst.bounds

    def teardown(self):
        """Runs after every method to clean up previous testing."""
        del self.testInst
        del self.rawInst


class TestOffsetRightFileDataPaddingBasics(TestDataPaddingbyFile):
    def setup(self):
        re_load(pysat.instruments.pysat_testing)
        """Runs before every method to create a clean testing setup."""
        self.testInst = pysat.Instrument('pysat', 'testing', '',
                                         clean_level='clean',
                                         update_files=True,
                                         sim_multi_file_right=True,
                                         pad={'minutes': 5})
        self.rawInst = pysat.Instrument('pysat', 'testing', '',
                                        clean_level='clean',
                                        update_files=True,
                                        sim_multi_file_right=True)
        self.testInst.bounds = ('2008-01-01.nofile', '2010-12-31.nofile')
        self.rawInst.bounds = self.testInst.bounds


class TestOffsetRightFileDataPaddingBasicsXarray(TestDataPaddingbyFile):
    def setup(self):
        re_load(pysat.instruments.pysat_testing)
        """Runs before every method to create a clean testing setup."""
        self.testInst = pysat.Instrument('pysat', 'testing_xarray', '',
                                         clean_level='clean',
                                         update_files=True,
                                         sim_multi_file_right=True,
                                         pad={'minutes': 5})
        self.rawInst = pysat.Instrument('pysat', 'testing_xarray', '',
                                        clean_level='clean',
                                        update_files=True,
                                        sim_multi_file_right=True)
        self.testInst.bounds = ('2008-01-01.nofile', '2010-12-31.nofile')
        self.rawInst.bounds = self.testInst.bounds


class TestOffsetLeftFileDataPaddingBasics(TestDataPaddingbyFile):
    def setup(self):
        re_load(pysat.instruments.pysat_testing)
        """Runs before every method to create a clean testing setup."""
        self.testInst = pysat.Instrument('pysat', 'testing', '',
                                         clean_level='clean',
                                         update_files=True,
                                         sim_multi_file_left=True,
                                         pad={'minutes': 5})
        self.rawInst = pysat.Instrument('pysat', 'testing', '',
                                        clean_level='clean',
                                        update_files=True,
                                        sim_multi_file_left=True)
        self.testInst.bounds = ('2008-01-01.nofile', '2010-12-31.nofile')
        self.rawInst.bounds = self.testInst.bounds


class TestDataPadding():
    def setup(self):
        re_load(pysat.instruments.pysat_testing)
        """Runs before every method to create a clean testing setup."""
        self.testInst = pysat.Instrument('pysat', 'testing', '',
                                         clean_level='clean',
                                         pad={'minutes': 5},
                                         update_files=True)

    def teardown(self):
        """Runs after every method to clean up previous testing."""
        del self.testInst

    def test_data_padding(self):
        self.testInst.load(2009, 2, verifyPad=True)
        assert ((self.testInst.index[0] ==
                 self.testInst.date - pds.DateOffset(minutes=5)) &
                (self.testInst.index[-1] == self.testInst.date +
                 pds.DateOffset(hours=23, minutes=59, seconds=59) +
                 pds.DateOffset(minutes=5)))

    def test_yrdoy_data_padding_missing_days(self):
        self.testInst.load(2008, 1)
        # test load
        self.testInst.load(2008, 0)
        # reset buffer data
        self.testInst.load(2008, -5)
        # test load, prev day empty, current and next has data
        self.testInst.load(2008, 1)
        # reset
        self.testInst.load(2008, -4)
        # etc
        self.testInst.load(2008, 2)
        self.testInst.load(2008, -3)
        self.testInst.load(2008, 3)
        # switch to missing data on the right
        self.testInst.load(2010, 365)
        self.testInst.load(2010, 360)
        self.testInst.load(2010, 366)
        self.testInst.load(2010, 360)
        self.testInst.load(2010, 367)
        assert True

    def test_data_padding_next(self):
        self.testInst.load(2009, 2, verifyPad=True)
        self.testInst.next(verifyPad=True)
        assert ((self.testInst.index[0] == self.testInst.date -
                 pds.DateOffset(minutes=5)) &
                (self.testInst.index[-1] == self.testInst.date +
                 pds.DateOffset(hours=23, minutes=59, seconds=59) +
                 pds.DateOffset(minutes=5)))

    def test_data_padding_multi_next(self):
        """This also tests that _prev_data and _next_data cacheing"""
        self.testInst.load(2009, 2)
        self.testInst.next()
        self.testInst.next(verifyPad=True)
        assert ((self.testInst.index[0] == self.testInst.date -
                 pds.DateOffset(minutes=5)) &
                (self.testInst.index[-1] == self.testInst.date +
                 pds.DateOffset(hours=23, minutes=59, seconds=59) +
                 pds.DateOffset(minutes=5)))

    def test_data_padding_prev(self):
        self.testInst.load(2009, 2, verifyPad=True)
        self.testInst.prev(verifyPad=True)
        print(self.testInst.index)
        assert ((self.testInst.index[0] == self.testInst.date -
                 pds.DateOffset(minutes=5)) &
                (self.testInst.index[-1] == self.testInst.date +
                 pds.DateOffset(hours=23, minutes=59, seconds=59) +
                 pds.DateOffset(minutes=5)))

    def test_data_padding_multi_prev(self):
        """This also tests that _prev_data and _next_data cacheing"""
        self.testInst.load(2009, 10)
        self.testInst.prev()
        self.testInst.prev(verifyPad=True)
        assert ((self.testInst.index[0] == self.testInst.date -
                 pds.DateOffset(minutes=5)) &
                (self.testInst.index[-1] == self.testInst.date +
                 pds.DateOffset(hours=23, minutes=59, seconds=59) +
                 pds.DateOffset(minutes=5)))

    def test_data_padding_jump(self):
        self.testInst.load(2009, 2, verifyPad=True)
        self.testInst.load(2009, 11, verifyPad=True)
        assert ((self.testInst.index[0] ==
                 self.testInst.date - pds.DateOffset(minutes=5)) &
                (self.testInst.index[-1] ==
                 self.testInst.date
                 + pds.DateOffset(hours=23, minutes=59, seconds=59)
                 + pds.DateOffset(minutes=5)))

    def test_data_padding_uniqueness(self):
        self.testInst.load(2009, 1, verifyPad=True)
        assert (self.testInst.index.is_unique)

    def test_data_padding_all_samples_present(self):
        self.testInst.load(2009, 1, verifyPad=True)
        test_index = pds.date_range(self.testInst.index[0],
                                    self.testInst.index[-1], freq='S')
        assert (np.all(self.testInst.index == test_index))

    def test_data_padding_removal(self):
        self.testInst.load(2009, 1)
        # print(self.testInst.index)
        assert (self.testInst.index[0] == self.testInst.date) & \
               (self.testInst.index[-1] == self.testInst.date +
                pds.DateOffset(hour=23, minutes=59, seconds=59))


class TestDataPaddingXarray(TestDataPadding):
    def setup(self):
        re_load(pysat.instruments.pysat_testing)
        """Runs before every method to create a clean testing setup."""
        self.testInst = pysat.Instrument('pysat', 'testing_xarray', '',
                                         clean_level='clean',
                                         pad={'minutes': 5},
                                         update_files=True)


class TestMultiFileRightDataPaddingBasics(TestDataPadding):
    def setup(self):
        re_load(pysat.instruments.pysat_testing)
        """Runs before every method to create a clean testing setup."""
        self.testInst = pysat.Instrument('pysat', 'testing', '',
                                         clean_level='clean',
                                         update_files=True,
                                         sim_multi_file_right=True,
                                         pad={'minutes': 5},
                                         multi_file_day=True)

    def teardown(self):
        """Runs after every method to clean up previous testing."""
        del self.testInst


class TestMultiFileRightDataPaddingBasicsXarray(TestDataPadding):
    def setup(self):
        re_load(pysat.instruments.pysat_testing)
        """Runs before every method to create a clean testing setup."""
        self.testInst = pysat.Instrument('pysat', 'testing_xarray', '',
                                         clean_level='clean',
                                         update_files=True,
                                         sim_multi_file_right=True,
                                         pad={'minutes': 5},
                                         multi_file_day=True)

    def teardown(self):
        """Runs after every method to clean up previous testing."""
        del self.testInst


class TestMultiFileLeftDataPaddingBasics(TestDataPadding):
    def setup(self):
        re_load(pysat.instruments.pysat_testing)
        """Runs before every method to create a clean testing setup."""
        self.testInst = pysat.Instrument('pysat', 'testing', '',
                                         clean_level='clean',
                                         update_files=True,
                                         sim_multi_file_left=True,
                                         pad={'minutes': 5},
                                         multi_file_day=True)

    def teardown(self):
        """Runs after every method to clean up previous testing."""
        del self.testInst


class TestMultiFileLeftDataPaddingBasicsXarray(TestDataPadding):
    def setup(self):
        re_load(pysat.instruments.pysat_testing)
        """Runs before every method to create a clean testing setup."""
        self.testInst = pysat.Instrument('pysat', 'testing_xarray', '',
                                         clean_level='clean',
                                         update_files=True,
                                         sim_multi_file_left=True,
                                         pad={'minutes': 5},
                                         multi_file_day=True)

    def teardown(self):
        """Runs after every method to clean up previous testing."""
        del self.testInst
