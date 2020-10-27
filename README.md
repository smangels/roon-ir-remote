
# The Project

The goal is to provide a hardware controller based on a Raspberry PI (either Zero, 3, 4) that utilizes
a display, rotary encoder, some status LED and 4 buttons in order to control a Roon Core
installation in the network.

## Requirements

* ability to switch between Roon zones
* ability to display status for chosen zone
	- status
	- volume
	- total length
	- current position
* ability to pause all zones
* ability to change status of a zone
	- change volume
	- skip track
	- pause
	- mute
* auto-detect the zone
* let user chose the zone from a list
* when restarting, last known zone is used
* timeout for display backlight
* display backlight will be enabled when touching the rotary encoder

## Development Language

* development language will be Python
* documentation language will be English

## Hardware Devices

- proximity sensor, TMD2772, SMD, 8 pins, proximity and backlight sensor
	* controls backlight intensity
	* switches the LED backlight on when someone is in front of the sensor
	* I2C bus, interrupt, LOW active