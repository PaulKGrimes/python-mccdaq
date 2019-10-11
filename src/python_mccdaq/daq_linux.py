#! /usr/bin/env python
##################################################
#                                                #
# Driver for DAQ devices using the MCC UL        #
# for linux                                      #
#                                                #
# Import this via the daq.py wrapper that        #
# selects which of DAQ_windows and DAQ_linux to  #
# import.                                        #
#                                                #
# Larry Gardner, July 2018                       #
#                                                #
##################################################

from __future__ import print_function, division

import uldaq
from time import sleep
import numpy as np
import hjsonconfig

from . import _default_daq_config


class DAQ:
    def __init__(self, config=None, configfile=None, verbose=False, vverbose=True, autoconnect=True):
        """Create the DAQ device, and if autoconnect, automatically connect to
        board number 0"""
        self.verbose = verbose or vverbose
        self.vverbose = vverbose  # Set to true to set config object to be verbose

        # Load the default config
        self.configfile = None
        self.config = None
        self.set_config(_default_daq_config.default_config)

        self.devices = None
        self.daq_device = None
        self.boardnum = None

        self.interface_type = enums.InterfaceType.USB

        if configfile is not None:
            self.read_config(configfile)

        if config is not None:
            self.set_config(config)

        if autoconnect:
            self.connect(self.config["boardnum"])

    def read_config(self, filename):
        """Read the .hjson configuration file to set up the DAQ unit."""
        # Opens use file
        self.configfile = filename

        if self.verbose:
            print("Reading config file: ", self.configfile)
        try:
            new_config = hjsonconfig.Hjsonconfig(filename=filename, verbose=self.vverbose)
            self.set_config(new_config)
        except OSError:
            if self.verbose:
                print("No DAQ config file found, using existing DAQ config.")

    def set_config(self, config):
        """Merge a new config into the existing config.

        Called automatically from readFile()"""
        self.config = hjsonconfig.merge(self.config, config)
        self._apply_config()

    def _apply_config(self):
        """Apply the configuration to set up the object variables.  Will get
        called automatically from set_config

        This should be overridden to read any additional configuration values
        when subclassing daq.py"""
        self.ao_range = self.look_up_range(self.config["DACrange"], "unipolar")
        self.ai_mode = self.look_up_mode(self.config["ADCmode"])
        self.ai_range = self.look_up_range(self.config["ADCrange"], self.config["ADCpolarity"])
        self.do_port = self.look_up_dio_port(self.config["DOutPort"])
        self.di_port = self.look_up_dio_port(self.config["DInPort"])
        self.sleep_time = self.config("sleep_time")

    def look_up_mode(self, mode):
        """Look up an Analog Input Mode and return the enum value"""
        return enums.AnalogInputMode[mode.upper()]

    def look_up_range(self, rang, polarity):
        """Look up a range by maximum voltage and polarity and return the enum value"""
        ulout = None
        for ulr in list(enums.ULRange):
            if ulr.name.startswith(polarity.upper()[0:2]):
                if ulr.range_max == rang:
                    ulout = ulr
                    break
        return ulout

    def look_up_dio_port(self, port_name):
        """Look up the DioPort by port name and return the enum value"""
        return enums.DigitalPortType[port_name.upper()]

    def list_devices(self):
        """List DAQ devices connected to this machine"""
        try:
            self.devices = get_daq_device_inventory(self.interface_type)
            self.number_of_devices = len(self.devices)
            if self.number_of_devices == 0:
                raise Exception('Error: No DAQ devices found')
            if self.verbose:
                print("Found {:d} DAQ device(s): ".format(self.number_of_devices))
                for i in range(self.number_of_devices):
                    print("    {:s} ({:s})".format(self.devices[i].product_name, self.devices[i].unique_id))
        except (KeyboardInterrupt, ValueError):
            print("Could not find DAQ device(s).")

    def connect(self, boardnum=None):
        """Connects to DAQ device <boardnum>.  If device is already connected,
        this will access that device.

        Sets self.daq_device to the resulting uldaq object."""
        if boardnum is None:
            boardnum = self.config["boardnum"]

        try:
            if self.devices is None:
                self.list_devices()
            if self.daq_device is not None:
                del self.daq_device
            self.daq_device = uldaq.DaqDevice(self.devices[boardnum])
            self.boardnum = boardnum
            # Connect to DAQ device
            descriptor = self.daq_device.get_descriptor()
            if not self.daq_device.is_connected():
                self.daq_device.connect()
            if self.verbose:
                print("Connected to {:s} {:s}".format(descriptor.product_name, descriptor.unique_id))
        except (KeyboardInterrupt, ValueError):
            print("Could not connect to DAQ device.")

        # Get some basic info on the device
        self.ai_device = self.daq_device.get_ai_device()
        self.get_ai_info()
        self.ao_device = self.daq_device.get_ao_device()
        self.get_ao_info()
        self.dio_device = self.daq_device.get_dio_device()
        self.get_dio_info()

        # Set the Ai Input mode and range to that specified in __init__
        self.set_ai_mode(self.ai_mode)
        self.set_ai_range(self.ai_range)
        self.set_ao_range(self.ao_range)

        self.num_channels()
        self.get_ai_range()
        self.get_ao_range()

    def disconnect(self):
        """Disconnects DAQ device"""
        if self.daq_device is not None:
            del self.daq_device
            if self.verbose:
                print("DAQ device {:s} {:s} is disconnected.".format(self.devices[self.boardnum].product_name,
                                                                     self.devices[self.boardnum].unique_id))
        else:
            if self.verbose:
                print("DAQ device {:s} not connected".format(self.devices[self.boardnum].product_name))
        self.daq_device = None
        self.boardnum = None
        self.number_of_channels = None

    def name(self, index=0):
        if self.devices is not None:
            name = self.devices[index].product_name
        else:
            name = None
        return name

    def num_channels(self):
        """Get the number of channels in the current AI Mode"""
        self.number_of_channels = self.AiInfo.get_num_chans_by_mode(self.ai_mode)

    def get_ai_info(self):
        """Get the AI Info object"""
        if self.daq_device is None:
            raise RuntimeError("DAQ device is not connected")
        self.AiInfo = self.ai_device.get_info()

    def get_ao_info(self):
        """Get the AO Info object"""
        if self.daq_device is None:
            raise RuntimeError("DAQ device is not connected")
        self.AoInfo = self.ao_device.get_info()

    def get_dio_info(self):
        """Get the DIO Info object"""
        if self.daq_device is None:
            raise RuntimeError("DAQ device is not connected")
        self.DioInfo = self.dio_device.get_info()

    def set_ai_mode(self, mode):
        """Set the ai_mode to one of the modes in AnalogInputMode"""
        self.ai_mode = mode
        self.get_ai_info()
        self.num_channels()
        self.set_ai_range(self.AiInfo.get_ranges(self.ai_mode)[0])
        self.get_ai_range()

    def get_ai_mode(self):
        """Get the ai_mode"""
        return self.ai_mode

    def set_ai_range(self, r):
        """Set the AI Range to one of the members of Range class"""
        self.ai_range = r

    def get_ai_range(self):
        """Get the AI Range"""
        return self.ai_range

    def set_ai_range_index(self, r):
        """Sets the AI Range to the index r in the list of ranges returned by
        self.AiInfo.get_ranges(self.ai_mode)"""
        ranges = self.getAiRanges()
        if r < len(ranges):
            self.ai_range = ranges[r]
        else:
            raise ValueError("Specified range index not found")

    def getAiRangeIndex(self):
        """Returns the index of the current ai_range in the list of
        self.AiInfo.get_ranges(self.ai_mode)"""
        ranges = self.getAiRanges()
        return ranges.index(self.ai_range)

    def setAiRangeValue(self, v):
        """Set the ai_range by value"""
        self.set_ai_range(Range(v))

    def getAiRangeValue(self):
        """Set the value of the ai_range"""
        return self.get_ai_range().value

    def getAiRanges(self):
        """Returns the list of valid ranges for this DAQ"""
        return self.AiInfo.get_ranges(self.ai_mode)

    def set_ao_range(self, r):
        """Sets the AO Range to one of the members of the Range class"""
        self.ao_range = r

    def get_ao_range(self):
        """Returns the current AO Range"""
        return self.ao_range

    def setAiRangeIndec(self, r):
        """Sets the AO Range to one of the ranges returned by AoGetRanges()"""
        ranges = self.getAoInfoRanges()
        if r < len(ranges):
            self.ao_range = ranges[r]
        else:
            raise ValueError("Specified range index not found")

    def getAiRangeIndex(self):
        """Returns the index of the current ao_range in the list of ranges
        returned by self.getAoRanges()"""
        ranges = self.getAoRanges()
        return ranges.index(self.ao_range)

    def getAiRanges(self):
        """Returns the list of available AoRanges"""
        self.AoInfo.get_ranges()

    def AIn(self, channel=0):
        """Reads input analog data from specified channel"""
        if self.daq_device is None:
            raise RuntimeError("DAQ device is not connected")
        if channel > self.number_of_channels:
            raise ValueError("channel index requested is higher than number of channels")
        if channel < 0:
            raise ValueError("channel index must be 0 or positive")
        data = self.ai_device.a_in(channel, self.ai_mode, self.ai_range, AInFlag.DEFAULT)
        return data

    def AOut(self, data, channel=0):
        """Write output analog data to specified channel"""
        if self.daq_device is None:
            raise RuntimeError("DAQ device is not connected")
        if channel < 0:
            raise ValueError("channel index must be 0 or positive")
        self.ao_device.a_out(channel, self.ao_range, AOutFlag.DEFAULT, data)

    def DOut(self, data, channel=0, port=DigitalPortType.FIRSTPORTA):
        """Write output digital data to specified channel"""
        # Configure port
        self.dio_device.d_config_port(port, DigitalDirection.OUTPUT)

        # Writes output for bit
        self.dio_device.d_bit_out(port, channel, data)

    def AInScan(self, low_channel, high_channel, rate, samples_per_channel, scan_time=None):
        """Runs a scan across multiple channels, with multiple samples per channel.  Returns a numpy array of
        shape (samples_per_channel, channel_count)"""
        # Verify that the specified device supports hardware pacing for analog input.
        if not self.AiInfo.has_pacer():
            raise Exception('Error: The specified DAQ device does not support hardware paced analog input')

        # Verify the high channel does not exceed the number of channels, and
        # set the channel count.
        if high_channel >= self.number_of_channels:
            high_channel = self.number_of_channels - 1
        channel_count = high_channel - low_channel + 1

        # Allocate a buffer to receive the data.
        data = create_float_buffer(channel_count, samples_per_channel)

        try:
            # Start the acquisition.
            self.ai_device.a_in_scan(low_channel, high_channel, self.ai_mode, self.ai_range, samples_per_channel,
                                     rate, ScanOption.CONTINUOUS, AInScanFlag.DEFAULT, data)

            start_time = time.time()

            # Set scan time to a high number of seconds if it isn't set
            if scan_time is None:
                scan_time = 500000

            while (time.time() - start_time) <= scan_time:
                # Get the status of the background operation
                status, transfer_status = self.ai_device.get_scan_status()
                index = transfer_status.current_index

                # Check to see if we are done
                if transfer_status.current_scan_count >= samples_per_channel:
                    break

                sleep(self.sleep_time)
        finally:
            if self.daq_device:
                # Stop the acquisition if it is still running.
                if status == ScanStatus.RUNNING:
                    self.ai_device.scan_stop()

        d = np.array(data)
        d = d.reshape((samples_per_channel, channel_count))

        return d


if __name__ == "__main__":
    daq = DAQ()
    data = daq.AIn(0)
    print(data)
    data = daq.AInScan(0, 1, 10000, 1000, 1)
    print(data)
    daq.DOut(1)
    daq.disconnect()
