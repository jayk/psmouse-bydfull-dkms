# Opt-in BYD firmware scrolling on a Linux 7.0 base

The original `psmouse-bydfull/` bundle remains available. This directory adds a
separate modern build path: compile the matching distribution's mouse sources
with the BYD overlay instead of compiling the entire 2017 mouse-driver snapshot.

`byd.c` is based on the GPL-2.0-only BYD driver from Linux v7.0, retaining its
original copyright credits. The firmware gesture mapping is also documented in
the existing community driver. Firmware supplies gesture codes, not independent
coordinates for every finger.

## Build and tests

Obtain **the kernel sources and headers matching the target distribution kernel**.
This overlay currently accepts only the original Linux 7.0 BYD source hash. It does
not claim support for other kernels. It never downloads sources, installs DKMS,
changes the boot configuration, or loads a module.

```sh
CC=gcc-15 python3 modern/tests/test_byd.py
python3 -m unittest discover -s modern/tests -p 'test_build.py'
python3 modern/build.py --kernel-source /path/to/matching/kernel/source --cc gcc-15
```

Use a fresh `--output` directory for a subsequent build. The output is
`modern/build/psmouse.ko` by default. Other `psmouse` components come from the
supplied vendor source tree, using its object list. The SHA gate checks the BYD
base; the caller must still supply matching vendor sources for the other components.

## Behavior and recovery

The `byd_firmware_scroll` module parameter is **off by default**. With it enabled,
the pad is presented as a relative pointer. Firmware scroll packets become
`REL_WHEEL` and `REL_HWHEEL`. Known pinch/swipe packets are ignored. Standard
pointer motion and physical buttons remain available; corner click packets use
separate press/release frames. Tap-to-click is disabled in the experimental mode.

The additional BYD signature check rejects a pad without the historical vendor
signature before enabling gestures. Existing automatic detection is not changed.
Loading the module does not automatically bind the BYD protocol: protocol selection
must be explicit for the correct serio device. On the tested machine the path was
`/sys/bus/serio/devices/serio1/protocol` (write `byd` **without a newline**).

Before unloading this profile, the disconnect handler stops streaming, disables
multitouch, scrolling and absolute packets, restores firmware tapping, leaves
vendor command mode and requests a PS/2 reset. Merely reloading stock `psmouse`
was insufficient on the tested pad: the cursor became erratic until reboot.
The corrected teardown restored normal stock-driver movement and clicks without
reboot. Errors during teardown produce a kernel warning; they cannot guarantee
recovery from firmware or controller faults.

For a manual hardware test, retain an independent USB mouse, wait until the serio
driver has finished attaching, and arrange recovery outside the test terminal.
Remove the test module before reloading stock `psmouse`, so the corrected teardown
can run. Do not install an unverified module persistently. Machine-specific systemd
installation scripts used during evaluation are intentionally not part of this PR.

Presenting the pad as a mouse trades away ordinary libinput touchpad settings and
advanced gestures. Only the Banghó system below has been validated; other BYD
hardware needs separate testing. See [the validation report](VALIDATION.md).
