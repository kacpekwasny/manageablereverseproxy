from multiprocessing import Manager, Lock, Value


class SharedStateBase:
    """
    Base class for SharedState objects used by all components and their controllers.  
    """

    def __init__(self) -> None:
        self._m = Manager()

    




