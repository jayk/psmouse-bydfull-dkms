# Validation report: Banghó Zero G05

Evaluation date: 2026-10-09. No machine serial number or private logs are included.

| Item | Result and evidence |
| --- | --- |
| Distribution kernel | Ubuntu `7.0.0-38-generic`, source package `7.0.0-38.38` |
| Compiler | GCC `15.2.0-16ubuntu1`, matching the kernel compiler version |
| Source provenance | Ubuntu `linux-source-7.0.0_7.0.0-38.38_all.deb` |
| Source package SHA256 | `997a13a0c7fd0172a93b0c1ae9a4ffc7d3cbbf91d2fdd91d85334193580687de` |
| Ubuntu BYD base | Byte-identical to Linux v7.0 `drivers/input/mouse/byd.c` |
| Module build | Full psmouse compile, MODPOST and link completed successfully; vermagic matched stock module |
| Debug information | BTF generation skipped because vmlinux/pahole was unavailable; module link succeeded |
| Detection | Explicit BYD selection accepted the stricter vendor signature |
| Motion and clicks | Confirmed by the user during the hardware trial |
| Two-finger vertical scrolling | Confirmed by the user; 54 recorded wheel events with values `+1` and `-1` in one capture window |
| Recovery regression | Old teardown restored stock module but left the cursor erratic; reboot restored baseline |
| Corrected recovery | Confirmed normal movement and clicks after returning to stock module without reboot |
| Motion after corrected recovery | 345 X and 332 Y events in the observed window; X deltas `-9..9`, Y deltas `-5..7` |
| Reboot | User reported working correctly after installing the corrected module with a local activation service |
| Suspend/resume | User reported working correctly after suspend/resume in that installation |

The reboot/suspend observations validate the tested local installation, which
used a separate systemd activation service, not the legacy DKMS package. No
claim is made that the old DKMS bundle was compiled or tested on Linux 7.0.
Horizontal wheel mapping passes simulated tests but horizontal hardware scrolling
was not separately confirmed. Other machines, kernels, prolonged use, power-cycle
edge cases and all possible command failures have not been validated.

The C regression harness executes the actual packet, firmware configuration, restore and
disconnect functions. Kernel event output, PS/2 commands and timer/free APIs
are replaced at the boundary. It checks direction/signs, button frames, ignored
absolute packets, unknown packets, default versus experimental initialization,
signature failure, reset on failed initialization, teardown settings, failure
cleanup and preservation of the default teardown. These are userspace behavioral
tests, not kernel timing/concurrency tests. The teardown assertion failed against
the previous implementation and passed after correction.

Additional initialization/teardown command-failure cleanup was verified with
simulated PS/2 failures only; it was not loaded on the machine. The allocation
failure restoration in byd_init was reviewed but is not exercised by the harness.
