"""
Module to interact with the telephone answering machine (TAM).
"""
# This module is part of the FritzConnection package.
# https://github.com/kbr/fritzconnection

# License: MIT (https://opensource.org/licenses/MIT)
# Author: Mark Ullmann


from ..core.exceptions import FritzServiceError
from .fritzbase import AbstractLibraryBase
from xml.etree import ElementTree as etree


# important: don't set an extension number here:
SERVICE = 'X_AVM-DE_TAM'


class FritzTAM(AbstractLibraryBase):
    """
    Class to interact with the integrated telephone answering machine (TAM).  All
    parameters are optional.  If given, they have the following meaning: `fc`
    is an instance of FritzConnection, `address` the ip of the Fritz!Box,
    `port` the port to connect to, `user` the username, `password` the
    password, `timeout` a timeout as floating point number in seconds,
    `use_tls` a boolean indicating to use TLS (default False). It is
    recommended to use a dedicated user for security reasons.  Setup of the
    TAM is not supported, this needs to be done in the web interface.
    """
    # This class is adapted from the class FritzWLAN.
    def __init__(self, *args, service=1, **kwargs):
        super().__init__(*args, **kwargs)
        self.service = service
        self._sid_token = None

    def _action(self, actionname, **kwargs):
        service = f'{SERVICE}{self.service}'
        return self.fc.call_action(service, actionname, **kwargs)

    @property
    def _sid(self):
        """
        Authentication token for sid, to access certain urls. This is cached
        internally.
        """
        if self._sid_token is None:
            sidResponse = self.fc.call_action("DeviceConfig",
                                              "X_AVM-DE_CreateUrlSID")
            self._sid_token = sidResponse['NewX_AVM-DE_UrlSID'].split("=")[1]
        return self._sid_token

    def _get_tam_list_xml(self):
        """
        Information about the TAMs. Returns an XML with the data.
        """
        result = self._action('GetList')
        return result['NewTAMList']

    def _get_message_list_xml(self, tamIndex="0"):
        """
        Fetches an XML with the list of messages for the specified TAM.
        """
        result = self._action("GetMessageList", NewIndex=tamIndex)
        messageListRequest = self.fc.session.get(result['NewURL'])
        return messageListRequest.content

    @property
    def tam_options(self):
        """
        Return the general options of all TAM as a dictionary. These values are provided by Fritz!Box.

        Keys: TAMRunning, Stick, Status, Capacity.
        """
        root = etree.fromstring(self._get_tam_list_xml())
        tags = ['TAMRunning', 'Stick', 'Status', 'Capacity']
        result = {element.tag: element.text for element in root
                  if element.tag in tags}
        return result

    # @property
    def tam_list(self):
        """
        Returns a list of dictionaries, each representing one TAM. The values are provided by the Fritz!Box.

        Properties of the dictionary: Index, Display, Enable, Name.
        """
        root = etree.fromstring(self._get_tam_list_xml())
        result = []
        for item in root.iter("Item"):
            result.append({element.tag: element.text for element in item})
        return result

    def message_list(self, tamIndex="0"):
        """
        Returns the list of metadata of the messages for the TAM with given index.

        Each message is a dictionary with keys which are provided by the TAM.
        Currently, these include Index, Tam, Called, Date, Duration, Inbook, Name, New, Number, Path.
        """
        root = etree.fromstring(self._get_message_list_xml(tamIndex))
        result = []
        for item in root.iter("Message"):
            result.append({element.tag: element.text for element in item})
        return result

    def message_nr(self, tamIndex="0", messageIndex=None):
        """
        Fetches the metadata for the message with messageIndex for the TAM with tamIndex. By default, fetches the newest
        message (first in the result). This should be the one with the highest
        index. This is a convenience wrapper around the message_list function.
        """
        message_list = self.message_list(tamIndex)
        if messageIndex is None:
            message = message_list[0]
        else:
            message = [m for m in message_list if m["Index"] ==
                       str(messageIndex)][0]
        return message

    def message(self, tamIndex="0", messageIndex=None):
        """
        Returns the voice message for the tam tamIndex with given messageIndex.
        Result is a bytes objects containing the message in the wav-Format.
        """
        # Fetching the message requires a sid-Token for authentication.
        params = {"sid": self._sid}
        message_url = self.message_nr(tamIndex=tamIndex,
                                    messageIndex=messageIndex)["Path"]
        # TODO: Better construction of the URL, is there way analogous to path?
        answer_message_request = \
            self.fc.session.get(url=self.fc.address + ":" +
                                str(self.fc.port) + message_url, params=params)
        if answer_message_request.status_code != 200:
            raise FritzServiceError(f"Could not fetch voice message for TAM" +
                                    f"{tamIndex} and Message {messageIndex}")
        return answer_message_request.content

    def mark_message(self, tamIndex="0", messageIndex=None, markAsRead=1):
        """
        Mark the message with messageIndex on the TAM with tamIndex as
        read(default)/unread.
        """
        if messageIndex is None:
            raise TypeError("messageIndex must be provided")
        self._action("MarkMessage", NewIndex=tamIndex,
                     NewMessageIndex=messageIndex,
                     NewMarkedAsRead=markAsRead)
