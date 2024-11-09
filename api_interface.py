from abc import ABC, abstractmethod


class FunctionApiInterface(ABC):

    @abstractmethod
    def name(self):
        # Here how the function will be shown
        pass

    @abstractmethod
    def function(self):
        pass