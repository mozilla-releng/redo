# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at http://mozilla.org/MPL/2.0/.
"""
Create a task per python-version
"""

from copy import deepcopy

from taskgraph.transforms.base import TransformSequence

transforms = TransformSequence()


def _replace_string(obj, subs):
    if isinstance(obj, dict):
        return {k: v.format(**subs) for k, v in obj.items()}
    elif isinstance(obj, list):
        for c in range(0, len(obj)):
            obj[c] = obj[c].format(**subs)
    else:
        obj = obj.format(**subs)
    return obj


def _resolve_replace_string(item, field, subs):
    # largely from resolve_keyed_by
    container, subfield = item, field
    while "." in subfield:
        f, subfield = subfield.split(".", 1)
        if f not in container:
            return item
        container = container[f]
        if not isinstance(container, dict):
            return item

    if subfield not in container:
        return item

    container[subfield] = _replace_string(container[subfield], subs)
    return item


@transforms.add
def set_script_name(config, tasks):
    for task in tasks:
        task.setdefault("attributes", {}).update(
            {
                "script-name": task["name"],
            }
        )
        yield task


@transforms.add
def tasks_per_python_version(config, tasks):
    fields = [
        "description",
        "docker-repo",
        "run.command",
        "worker.command",
        "worker.docker-image",
    ]
    for task_raw in tasks:
        for python_version in task_raw.pop("python-versions"):
            task = deepcopy(task_raw)
            subs = {"name": task["name"], "python_version": python_version}
            for field in fields:
                _resolve_replace_string(task, field, subs)
            task["attributes"]["python-version"] = python_version
            yield task


@transforms.add
def update_name_with_python_version(config, tasks):
    for task in tasks:
        task["name"] = "{}-python{}".format(task["name"], task["attributes"]["python-version"])
        yield task
