""" TC001_VALID_LOGIN
Checks the login of the application running on 10.10.192.120.

Steps:
1. Send login request with the correct username and password -> expect success (HTTP 200)
2. Send login request with a wrong password -> expect failure (HTTP 401/403/400)

Structure (GetRegal, logger, execute()) follows the example in the Regal User Guide.
"""
import json
import traceback
import urllib.request
import urllib.error

from test_executor.test_executor.utility import GetRegal


class TCConstants:
    """ Change these values to match your application """
    BASE_URL = "http://10.10.192.120:8085"
    LOGIN_PATH = "/login"
    VALID_USERNAME = "testuser"
    VALID_PASSWORD = "test@123"
    INVALID_PASSWORD = "wrong_password"
    TIMEOUT = 10
    SUCCESS_CODES = (200,)
    FAILURE_CODES = (400, 401, 403)


class ValidLoginTest(object):
    """ Test case for application login """

    def __init__(self):
        self.regal_api = GetRegal()
        log_mgr_obj = self.regal_api.get_log_mgr_obj()
        self._log = log_mgr_obj.get_logger("ValidLoginTest")

    def send_login(self, username, password):
        """ Sends a login request and returns (status_code, response_body) """
        url = TCConstants.BASE_URL + TCConstants.LOGIN_PATH
        # JSON login. If your app uses an HTML form, use instead:
        #   data = urllib.parse.urlencode({...}).encode()
        #   and Content-Type: application/x-www-form-urlencoded
        data = json.dumps({"username": username,
                           "password": password}).encode("utf-8")
        request = urllib.request.Request(
            url, data=data, method="POST",
            headers={"Content-Type": "application/json"})
        self._log.info("POST %s (user=%s)", url, username)
        try:
            with urllib.request.urlopen(request,
                                        timeout=TCConstants.TIMEOUT) as resp:
                return resp.getcode(), resp.read().decode("utf-8", "ignore")
        except urllib.error.HTTPError as error:
            return error.code, error.read().decode("utf-8", "ignore")

    def execute_test(self):
        """ Logic to execute the test case """
        self._log.info("Starting TC001_VALID_LOGIN")
        try:
            # Step 1: correct credentials must succeed
            code, body = self.send_login(TCConstants.VALID_USERNAME,
                                         TCConstants.VALID_PASSWORD)
            self._log.info("Valid login -> HTTP %s, body: %s", code, body[:200])
            if code not in TCConstants.SUCCESS_CODES:
                raise Exception("Valid login failed: HTTP %s" % code)

            # Step 2: wrong password must be rejected
            code, body = self.send_login(TCConstants.VALID_USERNAME,
                                         TCConstants.INVALID_PASSWORD)
            self._log.info("Invalid login -> HTTP %s", code)
            if code not in TCConstants.FAILURE_CODES:
                raise Exception("Wrong password was not rejected: HTTP %s"
                                % code)

            self._log.info("TC001_VALID_LOGIN passed")
        except Exception as error:
            self._log.error(error)
            self._log.error(traceback.format_exc())
            raise


def execute():
    """ Execution starts from this method (called by Regal) """
    test = ValidLoginTest()
    test.execute_test()
    test = None
