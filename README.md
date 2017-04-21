# DKMS module for BYD multitouch touchpads 

This repository provides a psmouse module that supports the full
functionality of the BYD multi-touch touchpad. These touchpads 
are found in, among other things, Purism's Librem line of laptops.

## What you get...

This module provides a significantly enhanced touchpad experience.
Tapping is disabled, and two-finger scrolling both vertically and
horizontally is enabled by default. The right-click zone is also
limited to the bottom-right corner of the pad, rather than the right
half of the lower quarter of the pad.

There is significant configurability in the touchpad. In future 
versions, I intend to expose these configuration options via 
sysfs.

## Build

To build or test the functionality of the module, simply cd into
the psmouse-bydfull directory and run `make`.  This will build 
the current version of the module. You can then test it by 
insmod'ing the module.  

### ** WARNING - It's a good idea to have an external mouse available for this process **

To test the module, you have to first remove the existing psmouse module:

    sudo rmmod psmouse

Then, you can install the module you just built:

    sudo insmod ./psmouse.ko

If you were successful, your trackpad should be working.  You can test
that the new module is working by checking that tapping is not registered
as a click, and two-finger scrolling works.

## DKMS Installation

To install this module into your auto-update DKMS process, copy
the psmouse-bydfull directory to /usr/src/psmouse-bydfull-1.0.

Once the file is copied, you can run the following commands to 
install the dkms.

    # build module
    sudo dkms build -m psmouse -v bydfull-1.0

    # install module
    sudo dkms install -m psmouse -v bydfull-1.0

To load the new module, run the following two commands:

    sudo rmmod psmouse
    sudo modprobe psmouse

*Note that this is only necessary the first time.  Subsequent
boots will load the updated module automatically*

