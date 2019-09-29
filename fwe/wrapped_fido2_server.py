# This file is part of sner4 project governed by MIT license, see the LICENSE.txt file.
"""
yubico fido2 server wrapped for flask factory pattern delayed configuration
"""

from socket import getfqdn

from fido2.server import Fido2Server, RelyingParty


class WrappedFido2Server(Fido2Server):
    """yubico fido2 server wrapped for flask factory pattern delayed configuration"""

    def __init__(self):
        """initialize with default rp name"""
        super().__init__(RelyingParty(getfqdn()))

    def init_app(self, app):
        """reinitialize on factory pattern config request"""
        super().__init__(RelyingParty(app.config['SERVER_NAME'] or getfqdn()))
