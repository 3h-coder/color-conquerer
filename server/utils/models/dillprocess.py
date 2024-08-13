from multiprocessing import Process  # Use the standard library only
from multiprocessing.process import AuthenticationString

import dill


class DillProcess(Process):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._target = dill.dumps(
            self._target
        )  # Save the target function as bytes, using dill

    def run(self):
        if self._target:
            self._target = dill.loads(
                self._target
            )  # Unpickle the target function before executing
            self._target(*self._args, **self._kwargs)  # Execute the target function
