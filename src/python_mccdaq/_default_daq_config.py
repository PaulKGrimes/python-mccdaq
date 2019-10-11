# creates a default configuration for a DAQ object

import hjsonconfig
from pkg_resources import resource_filename
from pprint import pprint

verbose=False

filename = resource_filename("python_mccdaq", "config/daq-default.hjson")

if verbose:
    print("_default_DAQ_config: reading defaultConfig from {:s}".format(filename))
default_config = hjsonconfig.Hjsonconfig(filename=filename, verbose=verbose)

if verbose:
    print("_default_DAQ_config: Got defaultConfig:")
    pprint(default_config)
