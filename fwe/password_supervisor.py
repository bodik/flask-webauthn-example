"""fwe password supervisor"""

from crypt import crypt, mksalt, METHOD_SHA512  # pylint: disable=no-name-in-module
from hmac import compare_digest


class PasswordSupervisor():
    """password supervisor"""

    @staticmethod
    def hash(value, salt=None):
        """encoder; hash password with algo"""
        return crypt(value, salt if salt else mksalt(METHOD_SHA512))

    @staticmethod
    def get_salt(value):
        """encoder; demerge salt from value"""
        return value[:value.rfind('$')] if value else None

    @staticmethod
    def compare(value1, value2):
        """encoder; compare hashes"""
        return compare_digest(value1, value2) if isinstance(value1, str) and isinstance(value2, str) else False
