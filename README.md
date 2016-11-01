# hpimon

This is a realtime monitor of continuous HPI for Elekta MEG systems (TRIUX/Neuromag). NOTE: still seriously work in progress.

## Installation

You can run the monitor either on the acquisition workstation (sinuhe), or on another computer. The simplest way is to run on sinuhe.

## Prerequisites

You need to install a Python environment on sinuhe. Anaconda satisfies all requirements and can be installed without root privileges.

You also need to install a RT server that streams data from Elekta data acquisition to a FieldTrip buffer. This comes with the standard FieldTrip package. Unpack FieldTrip into your desired location. After unpacking, you probably need to recompile neuromag2ft on sinuhe, which can be done as follows:

```
cd fieldtrip/realtime/src/buffer/src
make clean
make
cd fieldtrip/realtime/src/acquisition/neuromag
make clean
make
```

If compilation succeeds, the neuromag2ft binary should now be available under `fieldtrip/realtime/src/acquisition/neuromag/bin/x86_64-pc-linux-gnu/neuromag2ft`.

## Initial configuration

Run `hpimon.py`. On the first run, it will create a new configuration file and abort. Edit the configuration file (`~/.hpimon.cfg`). Edit `SERVER_PATH` so that points to the `neuromag2ft` binary.

## Running

hpimon (actually the realtime server) needs to be started before you start acquiring data.

By default, hpimon manages the realtime server by itself. Shut down hpimon cleanly, so that it can shut down the server. Otherwise the buffer settings in the data acquisition might not be restored to default values, which can manifest as trouble with subsequently recorded files (MaxFilter does not like fiff files with a non-standard buffer length). If in doubt, restarting the acquisition programs from the maintenance menu will always restore the settings.

## Configuration

The line frequency and HPI frequencies are automatically read from the data acquisition config files. You can override them in the config file, like so:

```
LINE_FREQ = 50
HPI_FREQS = [293.0, 307.0, 314.0, 321.0, 328.0]
```













