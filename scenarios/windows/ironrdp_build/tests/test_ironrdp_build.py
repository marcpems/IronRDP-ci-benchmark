# Copyright (c) Microsoft. All rights reserved.
# Licensed under the MIT license. See LICENSE file in the project root for full license information.

"""Isolated host tests: no HOBL dependencies, RPC, installers, or DUT access."""

import importlib.util
from pathlib import Path
import sys
import types
import unittest
from unittest.mock import Mock, patch


def load_scenario():
    core = types.ModuleType('core')
    app = types.ModuleType('core.app_scenario')
    app.Scenario = type('Scenario', (unittest.TestCase,), {
        'setUp': Mock(),
        'tearDown': Mock(),
    })
    core.app_scenario = app
    parameters = types.ModuleType('core.parameters')
    defaults = {}
    parameters.Params = type('Params', (), {
        'setDefault': staticmethod(lambda section, key, value: defaults.setdefault(key, value)),
        'get': Mock(side_effect=lambda section, key: defaults[key]),
    })
    path = Path(__file__).parents[1] / 'ironrdp_build.py'
    spec = importlib.util.spec_from_file_location('ironrdp_build', path)
    module = importlib.util.module_from_spec(spec)
    with patch.dict(sys.modules, {
        'core': core,
        'core.app_scenario': app,
        'core.parameters': parameters,
    }):
        spec.loader.exec_module(module)
    return module, defaults


class IronRdpBuildTests(unittest.TestCase):
    def setUp(self):
        self.module, self.values = load_scenario()
        self.values['platform'] = 'Windows'
        self.scenario = self.module.IronRdpBuild()
        self.scenario.dut_exec_path = r'D:\HOBL work\bin'
        self.scenario.result_dir = r'D:\HOBL results'
        self.scenario.checkPrepStatus = Mock(return_value='missing')
        self.events = []
        for name in ('_upload', '_call', '_copy_data_from_remote',
                     'createPrepStatusControlFile', '_kill'):
            setattr(self.scenario, name, Mock())
        self.scenario._call.side_effect = self.record_call
        self.module.core.app_scenario.Scenario.setUp.side_effect = (
            lambda scenario: self.events.append('measurement_start'))
        self.module.core.app_scenario.Scenario.tearDown.side_effect = (
            lambda scenario: self.events.append('measurement_stop'))

    def record_call(self, command, **kwargs):
        for phase in ('prep', 'run', 'kill', 'teardown'):
            if f'_{phase}.ps1' in command[1]:
                self.events.append(phase)
                break

    def execute(self):
        result = unittest.TestResult()
        self.scenario.run(result)
        return result

    def test_default_lifecycle_and_quoted_commands(self):
        result = self.execute()
        self.assertTrue(result.wasSuccessful(), result.errors)
        self.assertEqual(self.events, [
            'prep', 'measurement_start', 'run', 'measurement_stop', 'kill', 'teardown',
        ])
        self.scenario.checkPrepStatus.assert_called_once_with(['ironrdp_build1'])
        self.scenario._upload.assert_called_once_with(
            r'scenarios\windows\ironrdp_build\ironrdp_build_resources',
            self.scenario.dut_exec_path,
        )
        self.scenario.createPrepStatusControlFile.assert_called_once_with('1')
        for call in self.scenario._call.call_args_list:
            command = call.args[0]
            self.assertEqual(command[0], 'pwsh')
            self.assertTrue(command[1].startswith(
                '-NoProfile -NonInteractive -File '
                '"D:\\HOBL work\\bin\\ironrdp_build_resources\\'
            ))
            self.assertIn('.ps1"', command[1])
        run = self.scenario._call.call_args_list[1]
        self.assertIn(' -jobs 0', run.args[0][1])
        self.assertGreater(run.kwargs['timeout'], 2400)
        self.scenario._kill.assert_not_called()

    def test_invalid_parameters_fail_before_remote_work(self):
        for name, invalid in (
            ('loops', ('0', '-1', '1.5', '', None, True, 1.5)),
            ('jobs', ('-1', 'two', '0.5', None, False, 0.5, '4097', 4097)),
        ):
            for value in invalid:
                with self.subTest(name=name, value=value):
                    original = self.values[name]
                    self.values[name] = value
                    with self.assertRaisesRegex(ValueError, name):
                        self.scenario.setUp()
                    self.values[name] = original
                    self.scenario.checkPrepStatus.assert_not_called()
                    self.scenario._upload.assert_not_called()
                    self.scenario._call.assert_not_called()

    def test_maximum_jobs_is_passed_to_run(self):
        self.values['jobs'] = '4096'
        result = self.execute()
        self.assertTrue(result.wasSuccessful(), result.errors)
        runs = [call for call in self.scenario._call.call_args_list
                if '_run.ps1' in call.args[0][1]]
        self.assertEqual(len(runs), 1)
        self.assertIn(' -jobs 4096', runs[0].args[0][1])

    def test_prep_failure_has_no_marker_or_measurement_and_cleans_up(self):
        def fail_prep(command, **kwargs):
            self.record_call(command, **kwargs)
            if '_prep.ps1' in command[1]:
                raise RuntimeError('prep failed')
        self.scenario._call.side_effect = fail_prep
        result = self.execute()
        self.assertEqual(len(result.errors), 1)
        self.assertIn('prep failed', result.errors[0][1])
        self.assertEqual(self.events, ['prep', 'kill', 'teardown'])
        self.scenario.createPrepStatusControlFile.assert_not_called()
        self.assertEqual(self.scenario._copy_data_from_remote.call_count, 2)

    def test_diagnostics_failure_does_not_mask_prep_failure(self):
        self.scenario._call.side_effect = RuntimeError('original prep failure')
        self.scenario._copy_data_from_remote.side_effect = OSError('copy failure')
        with self.assertLogs(level='ERROR') as logs:
            result = self.execute()
        self.assertEqual(len(result.errors), 1)
        self.assertIn('original prep failure', result.errors[0][1])
        self.assertTrue(any('copy failure' in entry for entry in logs.output))
        self.scenario.createPrepStatusControlFile.assert_not_called()
        self.module.core.app_scenario.Scenario.setUp.assert_not_called()

    def test_prep_diagnostics_failure_prevents_marker(self):
        self.scenario._copy_data_from_remote.side_effect = [OSError('copy failed'), None]
        result = self.execute()
        self.assertIn('copy failed', result.errors[0][1])
        self.scenario.createPrepStatusControlFile.assert_not_called()
        self.module.core.app_scenario.Scenario.setUp.assert_not_called()

    def test_cached_prep_and_repeated_runs_share_timestamp_and_jobs(self):
        self.values.update(loops='3', jobs='4')
        self.scenario.checkPrepStatus.return_value = ''
        result = self.execute()
        self.assertTrue(result.wasSuccessful(), result.errors)
        self.scenario._upload.assert_not_called()
        self.scenario.createPrepStatusControlFile.assert_not_called()
        runs = [call for call in self.scenario._call.call_args_list
                if '_run.ps1' in call.args[0][1]]
        self.assertEqual(len(runs), 3)
        self.assertEqual(len({call.args[0][1] for call in runs}), 1)
        self.assertIn(' -jobs 4', runs[0].args[0][1])
        timestamp = runs[0].args[0][1].split(' -startTime "')[1].split('"')[0]
        self.assertIsNotNone(self.module.datetime.fromisoformat(timestamp).tzinfo)

    def test_run_failure_stops_measurement_before_cleanup_and_keeps_original(self):
        self.values['loops'] = '3'
        def fail_run_and_cleanup(command, **kwargs):
            self.record_call(command, **kwargs)
            if '_run.ps1' in command[1]:
                raise RuntimeError('original run failure')
            if '_teardown.ps1' in command[1]:
                raise OSError('cleanup failed')
        self.scenario._call.side_effect = fail_run_and_cleanup
        with self.assertLogs(level='ERROR') as logs:
            result = self.execute()
        self.assertEqual(len(result.errors), 1)
        self.assertIn('original run failure', result.errors[0][1])
        self.assertTrue(any('cleanup failed' in entry for entry in logs.output))
        self.assertEqual(self.events[-4:], ['run', 'measurement_stop', 'kill', 'teardown'])

    def test_base_setup_failure_still_stops_measurement_and_cleans_up(self):
        self.module.core.app_scenario.Scenario.setUp.side_effect = RuntimeError('setup failed')
        result = self.execute()
        self.assertIn('setup failed', result.errors[0][1])
        self.assertEqual(self.events, ['prep', 'measurement_stop', 'kill', 'teardown'])

    def test_base_teardown_failure_preserved_and_cleanup_still_runs(self):
        self.module.core.app_scenario.Scenario.tearDown.side_effect = RuntimeError('stop failed')
        with self.assertLogs(level='ERROR'):
            result = self.execute()
        self.assertEqual(len(result.errors), 1)
        self.assertIn('stop failed', result.errors[0][1])
        self.assertEqual(self.events[-2:], ['kill', 'teardown'])
        self.assertEqual(self.scenario._copy_data_from_remote.call_count, 2)

    def test_cleanup_failure_fails_otherwise_successful_run(self):
        def fail_cleanup(command, **kwargs):
            self.record_call(command, **kwargs)
            if '_teardown.ps1' in command[1]:
                raise OSError('cleanup failed')
        self.scenario._call.side_effect = fail_cleanup
        with self.assertLogs(level='ERROR'):
            result = self.execute()
        self.assertEqual(len(result.errors), 1)
        self.assertIn('cleanup failed', result.errors[0][1])
        self.assertEqual(self.scenario._copy_data_from_remote.call_count, 2)

    def test_kill_before_setup_uses_dedicated_script_and_never_raises(self):
        self.scenario._call.side_effect = OSError('RPC unavailable')
        with self.assertLogs(level='ERROR'):
            self.assertEqual(self.scenario.kill(), 0)
        self.scenario._call.assert_called_once_with([
            'pwsh',
            r'-NoProfile -NonInteractive -File "D:\HOBL work\bin\ironrdp_build_resources\ironrdp_build_kill.ps1"',
        ], timeout=60)
        self.scenario._kill.assert_not_called()


if __name__ == '__main__':
    unittest.main()
