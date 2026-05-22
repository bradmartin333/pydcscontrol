class DCSControllerError(Exception):
    """Base exception for DCS controller failures."""


class DCSProtocolError(DCSControllerError):
    """Raised when a command or response violates DCS protocol expectations."""


class DCSNetworkError(DCSControllerError):
    """Raised when network communication with the controller fails."""
