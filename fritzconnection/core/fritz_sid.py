"""
fritzsid.py

Defines the FritzSID class to get valid session ids, verify session ids
and logout (invalidate) session ids.
"""

from __future__ import annotations


import hashlib
import re
from dataclasses import field
from http import HTTPStatus

from fritzconnection.core.description import SessionInfo
from fritzconnection.core.utils import get_xml_root


BASE_LOGIN_URL = "/login_sid.lua"
MD5_LOGIN_URL = BASE_LOGIN_URL
PBKDF2_LOGIN_URL = f"{BASE_LOGIN_URL}?version=2"

MD5_CHALLENGE = "md5"
PBKDF2_CHALLENGE = "pbkdf2"
PBKDF2_CHALLENGE_INDICATOR = "2$"
MD5_CHALLENGE_OS_VERSION = 7.24


class FritzSID:
    """
    Provides access to an AVM-SID for using the REST-API
    """
    def __init__(self, fc: FritzConnection):
        self.fc = fc
        self.session_id = None
        self.challenge_method = self.get_challenge_method()
    
    @property
    def is_PBKDF2_challenge(self) -> bool:
        return self.challenge_method == PBKDF2_CHALLENGE
    
    @property
    def login_url(self) -> str:
        """
        Return sid login-url depending on the system software version.
        PBKDF2 for >= 7.24 else MD5
        """
        if self.is_PBKDF2_challenge:
            path = PBKDF2_LOGIN_URL
        else:
            path = MD5_LOGIN_URL
        return f"{self.fc.protocol}{self.fc.ip_address}{path}"
    
    def get_session_id(self) -> str:
        """
        Return a valid session id
        """
        if not self.is_valid_session_id(self.session_id):
            si = self.get_session_info()
            challenge = si.Challenge
            if challenge.startswith(PBKDF2_CHALLENGE_INDICATOR):
                challenge_hash = self.get_hash_from_PBKDF2_challenge(challenge)
            else:
                challenge_hash = self.get_hash_from_MD5_challenge(challenge)
            self.session_id = self.get_sid_from_challenge_hash(challenge_hash)
        return self.session_id
        
    def logout_session_id(self, session_id: str) -> None:
        """
        Makes the given session_id invalid.
        """
        data = {
            "logout": session_id,
            "sid": session_id
        }
        self._do_post_request(data)
        
    def check_session_id(self, session_id: str) -> str:
        """
        Checks whether the given sessioon id is still valid.
        On a valid id the id itself is returned,
        otherwise a series of 16 zeros is returned (0000000000000000)
        """
        data = {
            "sid": session_id
        }
        session_info = self._do_post_request(data)
        return session_info.SID
        
    def is_valid_session_id(self, session_id: str|None) -> bool:
        """
        Return a boolean whether the given session is is valid.
        """
        if not session_id:
            # None or empty
            return False
        sid = self.check_session_id(session_id)
        mo = re.match(r"0*$", sid)  
        return not bool(mo)
        
    def get_session_info(self) -> SessionInfo:
        """
        Return a SessionInfo instance with all information about SID,
        Users, BlockTime etc. as defined by the SessionInfo class.
        """
        with self.fc.session.get(self.login_url) as response:
            if response.status_code == HTTPStatus.OK:
                session_info = SessionInfo()
                session_info.load(get_xml_root(response.text))
            else:
                session_info = None
        return session_info
        
        
    # -- internal methods -----------------------------------------
    
    def get_challenge_method(self) -> str:
        try:
            os_version_state = float(self.fc.system_version) - MD5_CHALLENGE_OS_VERSION
        except (ValueError, TypeError):
            # use PBKDF2 schema by default
            os_version_state = 1
        if os_version_state > 0:
            return PBKDF2_CHALLENGE
        return MD5_CHALLENGE
        
    def get_hash_from_PBKDF2_challenge(self, challenge: str) -> str:
        _, iterations_1, salt_1, iterations_2, salt_2 = challenge.split('$')
        static_hash = hashlib.pbkdf2_hmac(
            "sha256",
            self.fc.soaper.password.encode(),
            bytes.fromhex(salt_1),
            int(iterations_1)
        )
        dynamic_hash = hashlib.pbkdf2_hmac(
            "sha256",
            static_hash,
            bytes.fromhex(salt_2),
            int(iterations_2)
        )
        return f"{salt_2}${dynamic_hash.hex()}"

    def get_hash_from_MD5_challenge(self, challenge: str) -> str:
        """Returns the legathy md5 challenge hash."""
        hash = hashlib.md5(
            f"{challenge}-{self.fc.soaper.password}".encode("utf-16-le")
        )
        return f"{challenge}-{hash.hexdigest()}"

    def get_sid_from_challenge_hash(self, challenge_hash: str) -> str:
        """
        Return a new sid based on the given challenge hash.
        """
        data = {
            "username": self.fc.soaper.user,
            "response": challenge_hash
        }
        session_info = self._do_post_request(data)
        return session_info.SID

    def _do_post_request(self, data: dict) -> SessionInfo:
        """
        Makes a post-request with the given data and returns a
        SessionInfo instance.
        """
        headers = {
            "Content-Type": "application/x-www-form-urlencoded"
        }
        with self.fc.session.post(
            self.login_url, headers=headers, data=data
        ) as response:
            # TODO: error handling necessary here?
            session_info = SessionInfo()
            session_info.load(get_xml_root(response.text))
        return session_info
