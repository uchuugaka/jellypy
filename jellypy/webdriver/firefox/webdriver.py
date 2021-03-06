import base64
import httplib
from selenium.common.exceptions import ErrorInResponseException
from selenium.webdriver.remote.command import Command
from selenium.webdriver.remote.webdriver import WebDriver as RemoteWebDriver
from selenium.webdriver.remote.webelement import WebElement
from firefox_binary import FirefoxBinary
from selenium.webdriver.firefox.firefox_profile import FirefoxProfile
from selenium.webdriver.firefox.extension_connection import ExtensionConnection
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities 
import urllib2
import socket

class WebDriver(RemoteWebDriver):

    def __init__(self, fx_profile=None, firefox_binary=None, timeout=30):

        self.binary = firefox_binary
        self.profile = fx_profile

        if self.profile is None:
            self.profile = FirefoxProfile()
        
        if self.binary is None:
            self.binary = FirefoxBinary()

        RemoteWebDriver.__init__(self,
            command_executor=ExtensionConnection("127.0.0.1", self.profile,
            self.binary, timeout),
            desired_capabilities=DesiredCapabilities.FIREFOX)

    def create_web_element(self, element_id):
        """Override from RemoteWebDriver to use firefox.WebElement."""
        return WebElement(self, element_id)

    def quit(self):
        """Quits the driver and close every associated window."""
        try:
            RemoteWebDriver.quit(self)
        except httplib.BadStatusLine:
            # Happens if Firefox shutsdown before we've read the response from
            # the socket.
            pass
        self.binary.kill()

    @property
    def firefox_profile(self):
        return self.profile

    def save_screenshot(self, filename):
        """
        Gets the screenshot of the current window. Returns False if there is
        any IOError, else returns True. Use full paths in your filename.
        """
        png = self._execute(Command.SCREENSHOT)['value']
        try:
            f = open(filename, 'wb')
            f.write(base64.decodestring(png))
            f.close()
        except IOError:
            return False
        finally:
            del png
        return True

    def _execute(self, command, params=None):
        try:
            return RemoteWebDriver.execute(self, command, params)
        except ErrorInResponseException, e:
            # Legacy behavior: calling close() multiple times should not raise
            # an error
            if command != Command.CLOSE and command != Command.QUIT:
                raise e
        except urllib2.URLError, e:
            # Legacy behavior: calling quit() multiple times should not raise
            # an error
            if command != Command.QUIT:
                raise e
