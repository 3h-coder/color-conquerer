from multiprocessing import Lock, Manager


class MultiProcessingManager:
    _manager = None
    _lock = Lock()
    _shared_dict = None

    @classmethod
    def get_instance(cls):
        if cls._manager is None:
            cls._manager = Manager()
        return cls._manager

    @classmethod
    def get_lock(cls):
        return cls._lock

    @classmethod
    def get_shared_dict(cls):
        if cls._shared_dict is None:
            cls._shared_dict = cls.get_instance().dict()
        return cls._shared_dict

    @classmethod
    def get_shared_dict_and_lock(cls):
        return (cls.get_shared_dict(), cls.get_lock())

    @classmethod
    def get_bundle(cls):
        return (cls.get_instance(), cls.get_shared_dict(), cls.get_lock())
