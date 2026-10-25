# Copyright (c) Microsoft. All rights reserved.
# Licensed under the MIT license. See LICENSE file in the project root for full license information.

"""Windows IronRDP build timing orchestration."""

from datetime import datetime
import logging
import sys

import core.app_scenario
from core.parameters import Params


class IronRdpBuild(core.app_scenario.Scenario):
    module = __module__.split('.')[-1]
    prep_version = "1"
    resources = module + "_resources"

    Params.setDefault(module, 'loops', '1')
    Params.setDefault(module, 'jobs', '0')

    def _integer_parameter(self, name, minimum):
        value = Params.get(self.module, name)
        try:
            if isinstance(value, bool) or not isinstance(value, (str, int)):
                raise ValueError
            result = int(value)
            if result < minimum:
                raise ValueError
        except (TypeError, ValueError):
            raise ValueError(f"{name} must be an integer >= {minimum}") from None
        return result

    def _script_command(self, phase):
        target = f"{self.dut_exec_path}\\{self.resources}"
        return [
            "pwsh",
            f'-NoProfile -NonInteractive -File "{target}\\{self.module}_{phase}.ps1"',
        ]

    def _copy_diagnostics(self, suppress_errors=False):
        try:
            self._copy_data_from_remote(self.result_dir)
        except Exception:
            if not suppress_errors:
                raise
            logging.exception("Failed to copy IronRDP diagnostics; preserving original failure.")

    def setUp(self):
        self.loops = self._integer_parameter('loops', 1)
        self.jobs = self._integer_parameter('jobs', 0)
        if self.jobs > 4096:
            raise ValueError("jobs must be an integer between 0 and 4096")
        self.platform = Params.get('global', 'platform')
        self.target = f"{self.dut_exec_path}\\{self.resources}"
        self._failed = False
        self._resources_ready = False
        self._measurement_attempted = False
        self._teardown_done = False
        # unittest skips tearDown on setUp failure, but always runs cleanups.
        self.addCleanup(self.tearDown)
        try:
            if self.checkPrepStatus([self.module + self.prep_version]):
                logging.info("Uploading IronRDP resources to %s", self.target)
                self._upload(
                    f"scenarios\\windows\\{self.module}\\{self.resources}",
                    self.dut_exec_path,
                )
                self._resources_ready = True
                try:
                    self._call(self._script_command('prep'), timeout=3600)
                finally:
                    self._copy_diagnostics(suppress_errors=sys.exc_info()[0] is not None)
                self.createPrepStatusControlFile(self.prep_version)
            else:
                self._resources_ready = True

            self._measurement_attempted = True
            core.app_scenario.Scenario.setUp(self)
        except BaseException:
            self._failed = True
            raise

    def runTest(self):
        start_time = datetime.now().astimezone().isoformat()
        try:
            for index in range(self.loops):
                logging.info("Running IronRDP loop %s", index + 1)
                command = self._script_command('run')
                command[1] += f' -startTime "{start_time}" -jobs {self.jobs}'
                self._call(command, timeout=2500)
        except BaseException:
            self._failed = True
            raise

    def tearDown(self):
        if self._teardown_done:
            return
        self._teardown_done = True
        errors = []
        try:
            if self._measurement_attempted:
                core.app_scenario.Scenario.tearDown(self)
        except Exception as error:
            logging.exception("Failed to stop IronRDP measurement.")
            errors.append(error)
        finally:
            if self._resources_ready:
                self.kill()
                try:
                    self._call(self._script_command('teardown'), timeout=300)
                except Exception as error:
                    logging.exception("Failed to clean IronRDP build outputs.")
                    errors.append(error)
                finally:
                    try:
                        self._copy_diagnostics()
                    except Exception as error:
                        logging.exception("Failed to collect IronRDP cleanup diagnostics.")
                        errors.append(error)
        if errors and not self._failed:
            raise errors[0]

    def kill(self):
        try:
            self._call(self._script_command('kill'), timeout=60)
        except Exception:
            logging.exception("Failed to clean up owned IronRDP processes.")
        # Also prevents the framework kill wrapper's broad process-name fallback.
        return 0
