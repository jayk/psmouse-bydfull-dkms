# SPDX-License-Identifier: GPL-2.0-only
import importlib.util
from pathlib import Path
import tempfile
import unittest

spec = importlib.util.spec_from_file_location('build', Path(__file__).resolve().parents[1] / 'build.py')
build = importlib.util.module_from_spec(spec)
spec.loader.exec_module(build)


class SourceGuardTests(unittest.TestCase):
    def test_unknown_driver_source_is_rejected_without_touching_source_or_output(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            source = root / 'vendor'
            mouse = source / 'drivers/input/mouse'
            mouse.mkdir(parents=True)
            driver = mouse / 'byd.c'
            driver.write_text('unreviewed vendor driver\n')
            output = root / 'build'
            with self.assertRaisesRegex(ValueError, 'unreviewed BYD source'):
                build.prepare(source, output)
            self.assertEqual(driver.read_text(), 'unreviewed vendor driver\n')
            self.assertFalse(output.exists())

    def test_missing_vendor_tree_is_rejected_without_creating_output(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            with self.assertRaisesRegex(ValueError, 'kernel source must contain'):
                build.prepare(root / 'missing', root / 'build')
            self.assertFalse((root / 'build').exists())


if __name__ == '__main__':
    unittest.main()
