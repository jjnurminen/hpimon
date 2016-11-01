# hpimon

This is a realtime monitor of continuous HPI for Elekta MEG systems (TRIUX/Neuromag). NOTE: still seriously work in progress.

## Installation

You can run the monitor either on the acquisition workstation (sinuhe), or on another computer. The simplest way is to run on sinuhe.

## Prerequisites

You need to install a Python environment on sinuhe. Anaconda satisfies all requirements and can be installed without root privileges.

You also need to install a realtime server (`neuromag2ft`) that streams data from Elekta data acquisition to a FieldTrip buffer. This comes with the standard FieldTrip package. Unpack FieldTrip into your desired location. After unpacking, you probably need to recompile neuromag2ft on sinuhe, which can be done as follows:

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

Run `hpimon.py`. On the first run, it will create a new configuration file and abort. Edit the configuration file (`~/.hpimon.cfg`). Edit `SERVER_PATH` so that points to the `neuromag2ft` binary.  By default, hpimon manages starting and stopping the realtime server by itself.

## Running

hpimon (actually the realtime server) needs to be started before you start acquiring data (before you press 'GO' on the acquisition control panel).

## Interpreting the output


## Warning about shutting dowm the realtime server

It is necessary to cleanly shut down `neuromag2ft` (Ctrl-C or SIGTERM). If this does not happen (e.g. power failure, or process terminated with SIGKILL), `neuromag2ft` will not have a chance to restore the buffer settings of the data acquisition to their original values. This can manifest as trouble with processing the subsequently recorded files (e.g. MaxFilter does not like fiff files with a non-standard buffer length). If in doubt, run `neuromag2ft` manually with the `--fixchunksize` option. Also, restarting the acquisition programs from the maintenance menu will always restore the settings.

## Configuration

The line frequency and HPI frequencies are automatically read from the data acquisition config files. You can override them in the config file, like so:

```
LINE_FREQ = 50
HPI_FREQS = [293.0, 307.0, 314.0, 321.0, 328.0]
```













