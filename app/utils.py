from threading import Lock

class SingletonMeta(type):
    """Singleton metaclass.

    Args:
        type (type): Metaclass type.

    Returns:
        type: Metaclass type.
    """
    _instances = {}
    _lock = Lock()

    def __call__(self, *args, **kwargs):
        with self._lock:
            if self not in self._instances:
                instance = super().__call__(*args, **kwargs)
                self._instances[self] = instance
        return self._instances[self]