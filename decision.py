from decisionlib.decisionlib import Scheduler, ShellTask, TaskclusterQueue, Checkout, Trigger


def task(tox_command, docker_image):
    return ShellTask(
        'Redo Pull Request {}'.format(tox_command),
        'aws-provisioner-v1',
        'github-worker',
        docker_image,
        '''
        pip install tox
        tox -e {}
        '''.format(tox_command)
    )


def main():
    scheduler = Scheduler()
    for python_config in (
            ('pypy', 'pypy:2'),
            ('py27', 'python:2.7'),
            ('py34', 'python:3.4'),
            ('py35', 'python:3.5'),
            ('py36', 'python:3.6'),
            ('py37', 'python:3.7'),
            ('py37-black', 'python:3.7'),
    ):
        task(python_config[0], python_config[1]).schedule(scheduler)

    scheduler.schedule_tasks(
        TaskclusterQueue.from_environment(),
        Checkout.from_environment(),
        Trigger.from_environment()
    )


if __name__ == '__main__':
    main()