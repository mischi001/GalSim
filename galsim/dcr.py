# Copyright 2012, 2013 The GalSim developers:
# https://github.com/GalSim-developers
#
# This file is part of GalSim: The modular galaxy image simulation toolkit.
#
# GalSim is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# GalSim is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with GalSim.  If not, see <http://www.gnu.org/licenses/>
#
"""@file dcr.py
Implementation of atmospheric differential chromatic refraction.

This file is used to implement atmospheric differential chromatic refraction.  Functions are defined
that return the refraction angle (the angle between the true and apparent zenith angles of an
object), as a function of zenith angle, wavelength, temperature, pressure, and water vapor content.
"""

import numpy

import galsim

def air_refractive_index(wave, pressure=69.328, temperature=293.15, H2O_pressure=1.067):
    """Return the refractive index of air as function of wavelength.

    Uses the formulae given in Filippenko (1982), which appears to come from Edlen (1953),
    and Coleman, Bozman, and Meggers (1960).  The units of the original formula are non-SI,
    being mmHg for pressure (and water vapor pressure), and degrees C for temperature.  This
    function accepts SI units however, and transforms them when plugging into the formula.

    @param wave           Wavelength in nanometers (Array)
    @param pressure       Air pressure in kiloPascals.  (Default of 69.328 kPa = 520 mmHg is default
                          value from PhoSim, and assumed typical for LSST / Cerro Pachon.)
    @param temperature    Temperature in Kelvins.  (Default of 293.15 K = 20 C is default value from
                          PhoSim, and assumed typical for LSST / Cerro Pachon.)
    @param H2O_pressure   Water vapor pressure in kiloPascals.  (Default of 1.067 kPa = 8 mmHg is
                          default value from PhoSim, and assumed typical for LSST / Cerro Pachon.
    @returns refractive index
    """
    P = pressure * 7.50061683 # kPa -> mmHg
    T = temperature - 273.15 # K -> C
    W = H2O_pressure * 7.50061683 # kPa -> mmHg

    sigma_squared = 1.0 / (wave * 1.e-3)**2.0 # inverse wavenumber squared in micron^-2
    n_minus_one = (64.328 + (29498.1 / (146.0 - sigma_squared))
                   + (255.4 / (41.0 - sigma_squared))) * 1.e-6
    n_minus_one *= P * (1.0 + (1.049 - 0.0157 * T) * 1.e-6 * P) / (720.883 * (1.0 + 0.003661 * T))
    n_minus_one -= (0.0624 - 0.000680 * sigma_squared)/(1.0 + 0.003661 * T) * W * 1.e-6
    return n_minus_one + 1.0

def atmosphere_refraction_angle(wave, zenith_angle, **kwargs):
    """Compute the angle of refraction for a photon entering the atmosphere.

    Photons refract when transitioning from space, where the refractive index n = 1.0 exactly, to
    air, where the refractive index is slightly greater than 1.0.  This function computes the
    change in zenith angle for a photon with a given wavelength.  Output is a positive number of
    radians, even though the apparent zenith angle technically decreases due to this effect.

    @param wave          Wavelength in nanometers (Array)
    @param zenith_angle  as a galsim.Angle
    @param kwargs        Keyword arguments to pass to air_refractive_index() to override default
                         pressure, temperature, and/or H2O_pressure.
    @returns             Absolute value of change in zenith angle as a galsim.Angle
    """
    n_squared = air_refractive_index(wave, **kwargs)**2
    r0 = (n_squared - 1.0) / (2.0 * n_squared)
    return r0 * numpy.tan(zenith_angle.rad()) * galsim.radians