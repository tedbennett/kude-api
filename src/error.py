# API Error

class ApiError(Exception):
    """Exception raised to send a non-2xx response.

    Attributes:
        status_code -- error status code
        message     -- explanation of the error
    """

    def __init__(self, message, status_code=400):
        self.status_code = status_code
        self.message = message
        super().__init__(self.message)
