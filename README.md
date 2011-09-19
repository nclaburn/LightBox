# LightBox

## Introduction
LightBox is a dirt simple project that was born out of frustration of waiting on long compiles.
Have you ever kicked off a long compile, or any other process really, and wanted a way to passively
monitor it's progress?  Well here's a solution. It's crude, but it worked for me.

## lightbox.pde
This is the [Arduino][1] source. It was tested against Arduino 19. It includes the capability to read temperature from an external sensor. 

### Randomize Mode
This is the default mode of LightBox. In this mode LightBox will cycle through random colors and listen for [Command Mode].

### Command Mode
While in this mode, LightBox can be issued commands that vary characteristics of the light.

#### Commands

* *Pz* - Poll the temperature at random interval and report it back serially.
* *Po* - Turn off temperature polling
* *P[0-3]* - Set the polling interval.  0 = ONE SECOND, 1 = FIFTEEN SECONDS, 2 = THIRTY SECONDS, 3 = SIXTY SECONDS
* *T* - Request the current temperature. Returned serially.
* *C* - This resets the device and settings and enables command mode.
* *D* - Turns off the light.
* *Z* - Randomizes the light colors. LightBox starts in this mode.
* *F* - Flashes the last color set.
* *R* - Set the LightBox color to red.
* *G* - Set the LightBox color to green.
* *B* - Set the LightBox color to blue.
* *Y* - Set the LightBox color to yellow.

While in command mode, if a command is not found LightBox will flash yellow.


## lightboxserver.py
The server application used to issue client commands to the LightBox circuit.

### serial
LightBox Server connects via a serial port to the LightBox circuit. The serial port can be an actual RS-232 port, or a virtualized port used in USB-to-Serial converters.

### server port
LightBox Server listens to a given ip:port combination for clients. The code is written to assume only one client per network, but could easily be modified to support more.

### Usage
    `LightBox Server
    Command line options:
    -h --help show this help screen
    -s --serialport= The serial port to use.  This parameter must be defined
    -c --command= The command to monitor.  If this parameter is not set then LightBox will operate in "server" mode
    --serverport=[%s] The port the LightBox server should listen on.  If this parameter is set "command" will be ignored'

## makeMonClient.py
This is a simple client used to monitor the build of a large project. It checks stdout and stderr for keywords, interprets those keywords, and then sends commands to LightBox Server. Because it issues the `make` command to a makefile is expected to be in the working directory. 

### Usage
    `LightBox Client
    Basic usage: lightboxMakeClient.py -m TARGET
    Command line options:
    -h --help show this help screen
    -m --maketarget= The make target to execute.  This parameter is required
    -a --address=[%s] The IP address of the sever.  Default is 127.0.0.1
    -p --port=[%s] The port the LightBox server is listening on. default is 3000`

# License
See license file



[1]:http://arduino.cc/ "Arduino" 

