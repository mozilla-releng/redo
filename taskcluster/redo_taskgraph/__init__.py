# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at http://mozilla.org/MPL/2.0/.

from __future__ import absolute_import, print_function, unicode_literals

from pipes import quote as shell_quote

from taskgraph.transforms.base import TransformSequence
from taskgraph.util.templates import merge


transforms = TransformSequence()


@transforms.add
def fill_template(config, tasks):

    for task in tasks:
        python_version = task.pop('python-version')
        if 'tox-environment' in task:
            job_type = tox_environment = task.pop('tox-environment')
        else:
            job_type = 'tests'
            tox_environment = "py{}".format(python_version.replace('.', ''))

        taskdesc = {
            'description': "Python {} {}".format(python_version, job_type),
            'worker': {
                'docker-image': {"in-tree": "python{}".format(python_version)}
            },
            'run': {
                'using': 'run-task',
                'cwd': '{checkout}',
                'use-caches': False,
                "command": 'pip install --user tox && tox -e {}'.format(shell_quote(tox_environment)),
            }
        }
        taskdesc = merge(task, taskdesc)

        yield taskdesc
