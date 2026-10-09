#!/usr/bin/env python3
# SPDX-License-Identifier: GPL-2.0-only
"""Build psmouse from matching vendor sources with the opt-in BYD overlay."""
import argparse
import hashlib
import os
from pathlib import Path
import shutil
import subprocess

BASE_BYD_SHA256 = '98f327fb5e3eab8a3493b1c87ce7d212f3ce6737d1752735a525682593977177'


def prepare(source, output):
    mouse = source / 'drivers/input/mouse'
    if not (mouse / 'byd.c').is_file():
        raise ValueError('kernel source must contain drivers/input/mouse/byd.c')
    if hashlib.sha256((mouse / 'byd.c').read_bytes()).hexdigest() != BASE_BYD_SHA256:
        raise ValueError('unreviewed BYD source: this overlay is restricted to the Linux 7.0 base')
    if output.exists() and any(output.iterdir()):
        raise ValueError('output directory must be empty; use a fresh directory')
    # Never overwrite the source tree or this package with build products.
    if output == source or source in output.parents or output in source.parents:
        raise ValueError('output must be separate from the kernel source tree')
    output.mkdir(parents=True, exist_ok=True)
    for path in mouse.iterdir():
        if path.is_file() and path.suffix in ('.c', '.h'):
            shutil.copy2(path, output / path.name)
    shutil.copy2(Path(__file__).with_name('byd.c'), output / 'byd.c')
    lines = (mouse / 'Makefile').read_text().splitlines()
    objects = [line for line in lines if line.startswith(('psmouse-objs', 'psmouse-$'))]
    if not any(line.startswith('psmouse-objs') for line in objects):
        raise ValueError('psmouse object list not found in vendor Makefile')
    (output / 'Makefile').write_text('# SPDX-License-Identifier: GPL-2.0\nobj-m += psmouse.o\n' + '\n'.join(objects) + '\n')


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--kernel-source', type=Path, required=True)
    parser.add_argument('--kernel-release', default=os.uname().release)
    parser.add_argument('--output', type=Path, default=Path(__file__).with_name('build'))
    parser.add_argument('--cc', default=os.environ.get('CC', 'cc'))
    args = parser.parse_args()
    headers = Path('/lib/modules') / args.kernel_release / 'build'
    if not headers.is_dir():
        parser.error('matching kernel headers not found')
    if os.geteuid() == 0:
        parser.error('build as a regular user; this command never installs or loads modules')
    try:
        prepare(args.kernel_source.resolve(), args.output.resolve())
    except ValueError as error:
        parser.error(str(error))
    subprocess.run(['make', '-C', str(headers), 'M=' + str(args.output.resolve()),
                    'CC=' + args.cc, '-j2'], check=True)
    print('Built:', args.output.resolve() / 'psmouse.ko')


if __name__ == '__main__':
    main()
