class TestException(Exception):
    """Signals an error in the test"""
    def __init__(self, message="An unexpected error occured in a test (possibly a mistake in test case?)"):
        self.message = message
        super().__init__(self.message)
    pass
