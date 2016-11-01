# hpimon

This is a realtime continuous HPI monitor for Elekta MEG systems (TRIUX/Neuromag). NOTE: still seriously work in progress.


## Installation

You can run the monitor either on the acquisition workstation (sinuhe), or on another computer. The simplest way is to run on sinuhe.

## Prerequisites

You need to install a Python environment on sinuhe. Anaconda is recommended and can be installed without root privileges.

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

Run `hpimon.py`. On the first run, it will create a new configuration file and abort. Edit the configuration file (`.hpimon.cfg` in your home directory). Edit `SERVER_PATH` so that points to the `neuromag2ft` binary.

## Running

hpimon needs to be started before you start acquiring data. Start it before starting acquisition or before you press 'GO!' on the acquisition control panel.











