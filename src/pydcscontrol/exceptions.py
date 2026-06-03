class DCSControllerError(Exception):
    """Base exception for DCS controller failures."""


class DCSProtocolError(DCSControllerError):
    """Raised when a command or response violates DCS protocol expectations."""


class DCSNetworkError(DCSControllerError):
    """Raised when network communication with the controller fails."""


class DCSControllerWarning(UserWarning):
    """Base warning for non-fatal DCS controller issues."""


class DCSSignalWarning(DCSControllerWarning):
    """Raised when the controller reports a signal-related warning."""
