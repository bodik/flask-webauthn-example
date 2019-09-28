# This file is part of sner4 project governed by MIT license, see the LICENSE.txt file.
"""
server side stored session implementation
"""

import json
import os
import re
from binascii import hexlify
from random import random
from time import time

from flask.sessions import SessionInterface, SessionMixin
from werkzeug.datastructures import CallbackDict


class Session(CallbackDict, SessionMixin):  # pylint: disable=too-many-ancestors
    """custom session object, modeled after original flask impl and flask_session"""

    sid = None

    def __init__(self, initial=None, sid=None, new=False):
        def on_update(self):
            self.modified = True

        super().__init__(initial, on_update)
        self.sid = sid
        self.new = new
        self.modified = False


class FilesystemSessionInterface(SessionInterface):
    """server side stored flask sessions implementation"""

    def __init__(self, storage, max_idle_time=3600, gc_probability=0.1):
        self.storage = storage
        self.max_idle_time = max_idle_time
        self.gc_probability = gc_probability

    @staticmethod
    def _generate_sid():
        """generate sid; implementation taken from py36 secrets for py35 compatibility"""
        return hexlify(os.urandom(32)).decode('ascii')

    @staticmethod
    def _validate_sid(sid):
        """validate sid value"""
        return bool(sid and re.match('^[a-f0-9]{64}$', sid))

    def _gc_sessions(self):
        """perform gc collection"""

        if (random() > self.gc_probability) or (not os.path.exists(self.storage)):
            return

        horizont = time() - self.max_idle_time
        for fpath in [os.path.join(self.storage, fn) for fn in os.listdir(self.storage)]:
            if os.path.getatime(fpath) < horizont:
                os.remove(fpath)

    def new_session(self):
        """create new session, used in open_session and during login"""
        return Session(sid=self._generate_sid(), new=True)

    def open_session(self, app, request):
        """open existing or create new session"""

        self._gc_sessions()

        sid = request.cookies.get(app.session_cookie_name)
        if self._validate_sid(sid):
            session_path = os.path.join(self.storage, sid)
            try:
                if os.path.getatime(session_path) > (time()-self.max_idle_time):
                    os.utime(session_path)
                    with open(session_path, 'r') as ftmp:
                        return Session(json.loads(ftmp.read()), sid=sid, new=False)
                os.remove(session_path)
            except (OSError, json.decoder.JSONDecodeError):
                pass

        return self.new_session()

    def save_session(self, app, session, response):
        """save session"""

        domain = self.get_cookie_domain(app)
        path = self.get_cookie_path(app)

        # https://github.com/pallets/flask/blob/master/src/flask/sessions.py
        # If the session is modified to be empty, remove the cookie. If the session is empty, return without setting the cookie.
        if not session:
            if session.modified:
                response.delete_cookie(app.session_cookie_name, domain=domain, path=path)
                self.delete_session(session)
            return

        if session.modified:
            if self._validate_sid(session.sid):
                session_path = os.path.join(self.storage, session.sid)
                os.makedirs(self.storage, exist_ok=True)  # due to pylint app fixture, cannot be in constructor
                with open(session_path, 'w', 0o600) as ftmp:
                    ftmp.write(json.dumps(session))

        if session.new:
            response.set_cookie(
                app.session_cookie_name,
                session.sid,
                expires=self.get_expiration_time(app, session),
                path=path,
                domain=domain,
                secure=self.get_cookie_secure(app),
                httponly=self.get_cookie_httponly(app),
                samesite=self.get_cookie_samesite(app))

    def delete_session(self, session):
        """delete session"""

        if self._validate_sid(session.sid):
            session_path = os.path.join(self.storage, session.sid)
            if os.path.exists(session_path):
                os.remove(session_path)
