import collections
import importlib
import numpy as np
import pandas as pds
from pysat.ssnl.avg import _calc_2d_median
import numpy as np
import pandas as pds

class Constellation(object):
    """Manage and analyze data from multiple pysat Instruments.
        print(repr(med1)) #FIXME

    FIXME document this.
    Created as part of a Spring 2018 UTDesign project.
    """
    def __init__(self, instruments=None, name=None):
        if instruments and name:
            raise ValueError('When creating a constellation, please specify '
                             'a list of instruments or a name, not both.')
        elif instruments and not hasattr(instruments, '__getitem__'):
            raise ValueError('Constellation: Instruments must be list-like.')
        elif not (name or instruments):
            raise ValueError('Constellation: Cannot create empty '
                             'constellation.')

        if instruments:
            self.instruments = instruments
        else:
            const = importlib.import_module('pysat.constellations.'+name)
            self.instruments = const.instruments

    def __getitem__(self, *args, **kwargs):
        return self.instruments.__getitem__(*args, **kwargs)

    def __str__(self):
        """
        Print names of instruments within constellation
        """
        output_str = '\npysat Constellation object:\n'

        for instr in self.instruments:
            output_str += instr.name + '\n'

        return output_str

    def set_bounds(self, start, stop):
        """
        Sets boundaries for all instruments in constellation
        """
        for instrument in self.instruments:
            instrument.bounds = (start, stop)

    def data_mod(self, function, *args, kind='add', at_pos='end', **kwargs):
        for instrument in self.instruments:
            instrument.custom.add(function, *args, kind, at_pos, **kwargs)

    def load(self, *args, **kwargs):
        for instrument in self.instruments:
            instrument.load(*args, **kwargs)

    def add(self, bounds1, label1, bounds2, label2, bin3, label3,
            data_label):
        """
        Combines signals from multiple instruments within
        given bounds.

        Parameters
        ----------
        bounds1 : (min, max)
            Bounds for selecting data on the axis of label1
            Data points with label1 in [min, max) will be considered.
        label1 : string
            Data label for bounds1 to act on.
        bounds2 : (min, max)
            Bounds for selecting data on the axis of label2
            Data points with label1 in [min, max) will be considered.
        label2 : string
            Data label for bounds2 to act on.
        bin3 : (min, max, #bins)
            Min and max bounds and number of bins for third axis.
        label3 : string
            Data label for third axis.
        data_label : array of strings
            Data label(s) for data product(s) to be averaged.

        Returns
        -------
        median : dictionary

        """
        # TODO document return more
        # TODO insert type checks

        if isinstance(data_label, str):
            data_label = [data_label,]
        elif not isinstance(data_label, collections.Sequence):
            raise ValueError("Please pass data_label as a string or "
                             "collection of strings.")

        # Modeled after pysat.ssnl.median2D

        # Make bin boundaries.
        # y: values at label3
        # z: *data_labels
        biny = np.linspace(bin3[0], bin3[1], bin3[2]+1)

        numy = len(biny)-1
        numz = len(data_label)

        # Ranges
        yarr, zarr = map(np.arange, (numy, numz))

        # Store data here.
        ans = [[[collections.deque()] for j in yarr] for k in zarr]

        # Filter data by bounds and bin it.
        # Idiom for loading all of the data in an instrument's bounds.
        for inst in self:
            for inst in inst:
                if len(inst.data) != 0:
                    # Select indicies for each piece of data we're interest in.
                    # Not all of this data is in bounds on label3 but we'll
                    #  sort this later.
                    min1, max1 = bounds1
                    min2, max2 = bounds2
                    data1 = inst.data[label1]
                    data2 = inst.data[label2]
                    in_bounds, = np.where((min1 <= data1) & (data1 < max1) &
                                          (min2 <= data2) & (data2 < max2))
                    # Grab the data in bounds on data1, data2.
                    data_considered = inst.data.iloc[in_bounds]

                    y_indexes = np.digitize(data_considered[label3], biny) -1

                    # Iterate over the bins along y
                    for yj in yarr:
                        # Indicies of data in this bin
                        yindex, = np.where(y_indexes == yj)

                        # If there's data in this bin
                        if len(yindex) > 0:

                            # For each data label, add the points.
                            for zk in zarr:
                                ans[zk][yj][0].extend(
                                    data_considered.ix[yindex, data_label[zk]].tolist())

        # Now for the averaging.
        # Let's, try .. packing the answers for the 2d function.
        numx = 1
        xarr = np.arange(numx)
        binx = None

        # TODO modify output
        out_2d = _calc_2d_median(ans, data_label, binx, biny, xarr, yarr, zarr, numx, numy, numz)

        # Transform output
        output = {}
        for i, label in enumerate(data_label):
            median = [r[0] for r in out_2d[label]['median']]
            count  = [r[0] for r in out_2d[label]['count']]
            dev     = [r[0] for r in out_2d[label]['avg_abs_dev']]
            output[label] = {'median':  median,
                             'count':   count,
                             'avg_abs_dev': dev,
                             'bin':     out_2d[label]['bin_y']}
        return output

    def difference(self, instrument1, instrument2, bounds, data_labels, 
                cost_function):
        """
        Calculates the difference in signals from multiple
        instruments within the given bounds.

        TODO more doc

        Parameters
        ----------
        s1 : Instrument
            Information must already be loaded into the 
            instrument.
        
        s2 : Instrument
            Information must already be loaded into the 
            instrument.

        data_labels : list of tuples of data labels
            The first key is used to access data in s1 
            and the second data in s2.

        bounds : list of tuples in the form (inst1_label, inst2_label,
            min, max, max_difference)
            inst1_label are inst2_label are labels for the data in
            instrument1 and instrument2
            min and max are bounds on the data considered
            max_difference is the maximum difference between two points
            for the difference to be calculated
        
        translate : dict
            User provides dict translate maps
            ("time", "lat", "long", "alt", "time2", "lat2",
            "long2", "alt2") to their respective data labels
            on their respectives s1, s2. # XXX rewrite

        Returns
        -------
        data_df: pandas DataFrame
            Each row has a point from instrument1, with the keys
            preceded by '1_',
        
        Pseudocode
        ----------
        Check integrity of inputs.

        Let STD_LABELS be the constant tuple:
        ("time", "lat", "long", "alt")
        
        Note: modify so that user can override labels for time,
        lat, long, data for each satelite.
        
        // We only care about the data currently loaded
           into each object.
        
        Let start be the later of the datetime of the
         first piece of data loaded into s1, the first
         piece of data loaded into s2, and the user
         supplied start bound.
        
        Let end be the later of the datetime of the first
         piece of data loaded into s1, the first piece
         of data loaded into s2, and the user supplied
         end bound.

        If start is after end, raise an error.
        
        // Let data be the 2D array of deques holding each piece
        //  of data, sorted into bins by lat/long/alt.
        
        Let s1_data (resp s2_dat) be data from s1.data, s2.data
        filtered by user-provided lat/long/alt bounds, time bounds
        calculated.

        Let data be a dictionary of lists with the keys
        [ dl1 for dl1, dl2 in data_labels ] +
        STD_LABELS + 
        [ lb+"2" for lb in STD_LABELS ]
        
        For each piece of data s1_point in s1_data:
        
            # Hopefully np.where is very good, because this
            #  runs O(n) times.
            # We could try reusing selections, maybe, if needed.
            #  This would probably involve binning.
            Let s2_near be the data from s2.data within certain
             bounds on lat/long/alt/time using 8 statements to
             numpy.where. We can probably get those defaults from
             the user or handy constants / config?
        
            # XXX we could always try a different closest 
            #  pairs algo
        
            Let distance be the numpy array representing the
             distance between s1_point and each point in s2_near.
        
            # S: Difference for others: change this line.
            For each of those, calculate the spatial difference 
             from the s1 using lat/long/alt. If s2_near is 
             empty; break loop.
        
            Let s2_nearest be the point in s2_near corresponding
             to the lowest distance.
        
            Append to data: a point, indexed by the time from
             s1_point, containing the following data:
        
            # note
            Let n be the length of data["time"].
            For each key in data:
                Assert len(data[key]) == n
            End for.
        
            # Create data row to pass to pandas.
            Let row be an empty dict.
            For dl1, dl2 in data_labels:
                Append s1_point[dl1] - s2_nearest[dl2] to data[dl1].
        
            For key in STD_LABELS:
                Append s1_point[translate[key]] to data[key]
                key = key+"2"
                Append s2_nearest[translate[key]] to data[key]
        
        Let data_df be a pandas dataframe created from the data
        in data.
        
        return { 'data': data_df, 'start':start, 'end':end }

        Created as part of a Spring 2018 UTDesign project.
        """

        #translate = {"time":"mlt", "time2":"mlt", 
        #            "long":"longitude", "long2":"longitude",
        #            "lat":"latitude", "lat2":"latitude"}
                    #"alt":"altitude", "alt2":"altitude"}

        #bounds = [("longitude", "longitude", .5),
        #        ("latitude", "latitude", .5),
        #        ("mlt", "mlt", .1)]
        
        #STD_LABELS = ("time", "lat", "long")#, "alt")
        labels = [dl1 for dl1, dl2 in data_labels] + ['1_'+b[0] for b in bounds] + ['2_'+b[1] for b in bounds] + ['dist']
        data = {label:[] for label in labels}

        #apply bounds
        inst1 = instrument1.data
        inst2 = instrument2.data
        for b in bounds:
            label1 = b[0]
            label2 = b[1]
            low = b[2]
            high = b[3]

            data1 = inst1[label1]
            ind1 = np.where((data1 >= low) & (data1 < high))
            inst1 = inst1.iloc[ind1]

            data2 = inst2[label2]
            ind2 = np.where((data2 >= low) & (data2 < high))
            inst2 = inst2.iloc[ind2]

        for i, s1_point in inst1.iterrows():
            #print(i)

            #gets points in instrument2 within the given bounds
            #b = (label1, label2, min, max, max_distance)
            s2_near = instrument2.data
            for b in bounds:
                label1 = b[0]
                label2 = b[1]
                s1_val = s1_point[label1]
                max_dist = b[4]
                minbound = s1_val - max_dist
                maxbound = s1_val + max_dist

                data2 = s2_near[label2]
                indices = np.where((data2 >= minbound) & (data2 < maxbound))
                s2_near = s2_near.iloc[indices]

            #finds nearest point to s1_point in s2_near
            s2_nearest = None
            min_dist = float('NaN')
            for j, s2_point in s2_near.iterrows():
                dist = cost_function(s1_point, s2_point)
                if dist < min_dist or min_dist != min_dist:
                    min_dist = dist
                    s2_nearest = s2_point
            
            data['dist'].append(min_dist)

            #append difference to data dict
            for dl1, dl2 in data_labels:
                if s2_nearest is not None:
                    data[dl1].append(s1_point[dl1] - s2_nearest[dl2])
                else:
                    data[dl1].append(float('NaN'))

            #append the rest of the row
            for b in bounds:
                label1 = b[0]
                label2 = b[1]
                data['1_'+label1].append(s1_point[label1])
                if s2_nearest is not None:
                    data['2_'+label2].append(s2_nearest[label2])
                else:
                    data['2_'+label2].append(float('NaN'))

        data_df = pds.DataFrame(data=data)
        #return {'data':data_df, start: , end: }
        return data_df

"""
def cost_function(point1, point2):
    #TODO: actually do lat/long difference correctly.
    #alternatively, let the user supply a cost function.
    lat_diff = point1['latitude'] - point2['latitude']
    long_diff = point1['longitude'] - point2['longitude']
    return lat_diff*lat_diff + long_diff*long_diff
"""
