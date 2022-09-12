from abc import ABC, abstractmethod

class Reason(ABC):

    @abstractmethod
    def __call__(self):
        pass

class BadRequestReason(Reason):

    def __call__(self):
        return 400

class ForbittenReason(Reason):

    def __call__(self):
        return 403

class NotFoundReason(Reason):

    def __call__(self):
        return 404

class NotAllowedReason(Reason):

    def __call__(self):
        return 405

class RequestTimeoutReason(Reason):

    def __call__(self):
        return 408

