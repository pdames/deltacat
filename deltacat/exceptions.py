class RetryableError(Exception):
    pass


class NonRetryableError(Exception):
    pass


class ConcurrentModificationError(Exception):
    pass


class ValidationError(NonRetryableError):
    pass


class NamespaceNotFoundError(NonRetryableError):
    pass


class TableNotFoundError(NonRetryableError):
    pass


class TableVersionNotFoundError(NonRetryableError):
    pass


class StreamNotFoundError(NonRetryableError):
    pass


class DeltaNotFoundError(NonRetryableError):
    pass


class TableAlreadyExistsError(NonRetryableError):
    pass
