# -*- coding: utf-8 -*-
"""Provides default routines for projecting pyglow model values onto locations
from pysat instruments.

"""

import pyglow
from pyglow.pyglow import Point

def add_iri_thermal_plasma(inst, glat_label='glat', glong_label='glong',
                           alt_label='alt'):
    """
    Uses IRI (International Reference Ionosphere) model to simulate an
    ionosphere.

    Uses pyglow module to run IRI. Configured to use actual solar parameters
    to run model.

    Example
    -------
        # function added velow modifies the inst object upon every inst.load
        call inst.custom.add(add_iri_thermal_plasma, 'modify',
        glat_label='custom_label')

    Parameters
    ----------
    inst : pysat.Instrument
        Designed with pysat_sgp4 in mind
    glat_label : string
        label used in inst to identify WGS84 geodetic latitude (degrees)
    glong_label : string
        label used in inst to identify WGS84 geodetic longitude (degrees)
    alt_label : string
        label used in inst to identify WGS84 geodetic altitude (km, height
        above surface)

    Returns
    -------
    inst
        Input pysat.Instrument object modified to include thermal plasma
        parameters.
        'ion_temp' for ion temperature in Kelvin
        'e_temp' for electron temperature in Kelvin
        'ion_dens' for the total ion density (O+ and H+)
        'frac_dens_o' for the fraction of total density that is O+
        'frac_dens_h' for the fraction of total density that is H+

    """


    iri_params = []
    for time, lat, lon, alt in zip(inst.data.index, inst[glat_label],
                                   inst[glong_label], inst[alt_label]):
        # Point class is instantiated. Its parameters are a function of time
        # and spatial location
        pt = Point(time, lat, lon, alt)
        pt.run_iri()
        iri = {}
        # After the model is run, its members like Ti, ni[O+], etc. can be
        # accessed
        iri['ion_temp'] = pt.Ti
        iri['e_temp'] = pt.Te
        iri['ion_dens'] = pt.ni['O+'] + pt.ni['H+'] + pt.ni['HE+']
        # pt.ne - pt.ni['NO+'] - pt.ni['O2+'] - pt.ni['HE+']
        iri['frac_dens_o'] = pt.ni['O+']/iri['ion_dens']
        iri['frac_dens_h'] = pt.ni['H+']/iri['ion_dens']
        iri['frac_dens_he'] = pt.ni['HE+']/iri['ion_dens']
        iri_params.append(iri)
    iri = pds.DataFrame(iri_params)
    iri.index = inst.data.index
    inst[iri.keys()] = iri

    inst.meta['ion_temp'] = {'units': 'Kelvin', 'long_name': 'Ion Temperature'}
    inst.meta['ion_dens'] = {'units': 'N/cc', 'long_name': 'Ion Density',
                             'desc': 'Total ion density including O+ and H+ ' +
                             'from IRI model run.'}
    inst.meta['frac_dens_o'] = {'units': '',
                                'long_name': 'Fractional O+ Density'}
    inst.meta['frac_dens_h'] = {'units': '',
                                'long_name': 'Fractional H+ Density'}

def add_msis(inst, glat_label='glat', glong_label='glong', alt_label='alt'):
    """
    Uses MSIS model to obtain thermospheric values.

    Uses pyglow module to run MSIS. Configured to use actual solar parameters
    to run model.

    Example
    -------
        # function added velow modifies the inst object upon every inst.load
        call inst.custom.add(add_msis, 'modify', glat_label='custom_label')

    Parameters
    ----------
    inst : pysat.Instrument
        Designed with pysat_sgp4 in mind
    glat_label : string
        label used in inst to identify WGS84 geodetic latitude (degrees)
    glong_label : string
        label used in inst to identify WGS84 geodetic longitude (degrees)
    alt_label : string
        label used in inst to identify WGS84 geodetic altitude (km, height
        above surface)

    Returns
    -------
    inst
        Input pysat.Instrument object modified to include MSIS values winds.
        'Nn' total neutral density particles/cm^3
        'Nn_N' Nitrogen number density (particles/cm^3)
        'Nn_N2' N2 number density (particles/cm^3)
        'Nn_O' Oxygen number density (particles/cm^3)
        'Nn_O2' O2 number density (particles/cm^3)
        'Tn_msis' Temperature from MSIS (Kelvin)

    """

    msis_params = []
    for time, lat, lon, alt in zip(inst.data.index, inst[glat_label],
                                   inst[glong_label], inst[alt_label]):
        pt = Point(time, lat, lon, alt)
        pt.run_msis()
        msis = {}
        total = 0
        for key in pt.nn.keys():
            total += pt.nn[key]
        msis['Nn'] = total
        msis['Nn_N'] = pt.nn['N']
        msis['Nn_N2'] = pt.nn['N2']
        msis['Nn_O'] = pt.nn['O']
        msis['Nn_O2'] = pt.nn['O2']
        msis['Tn_msis'] = pt.Tn_msis
        msis_params.append(msis)
    msis = pds.DataFrame(msis_params)
    msis.index = inst.data.index
    inst[msis.keys()] = msis

    # metadata
    inst.meta['Nn'] = {'units': 'cm^-3',
                       'desc': 'Total neutral number particle density ' +
                       'from MSIS.'}
    inst.meta['Nn_N'] = {'units': 'cm^-3',
                         'desc': 'Total nitrogen number particle density ' +
                         'from MSIS.'}
    inst.meta['Nn_N2'] = {'units': 'cm^-3',
                          'desc': 'Total N2 number particle density ' +
                          'from MSIS.'}
    inst.meta['Nn_O'] = {'units': 'cm^-3',
                         'desc': 'Total oxygen number particle density ' +
                         'from MSIS.'}
    inst.meta['Nn_O2'] = {'units': 'cm^-3',
                          'desc': 'Total O2 number particle density ' +
                          'from MSIS.'}
    inst.meta['Tn_msis'] = {'units': 'K',
                            'desc': 'Neutral temperature from MSIS.'}

    return
