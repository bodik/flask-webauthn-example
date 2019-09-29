"""fwe selenium tests module (and shared functions)"""

WEBDRIVER_WAIT = 10


class js_variable_ready():  # pylint: disable=invalid-name,too-few-public-methods
    """custom expected_condition, wait for variable/object"""

    def __init__(self, variable):
        self.variable = variable

    def __call__(self, driver):
        return driver.execute_script('return(%s !== undefined);' % self.variable)
