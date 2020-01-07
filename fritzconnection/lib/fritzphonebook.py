"""
Module for read-only access to the contents of the Fritz!Box phonebooks.
"""
# This module is part of the FritzConnection package.
# https://github.com/kbr/fritzconnection
# License: MIT (https://opensource.org/licenses/MIT)
# Authors: Klaus Bremer, David M. Straub


from ..core.processor import (
    processor,
    process_node,
    InstanceAttributeFactory,
    Storage,
    ValueSequencer,
)
from ..core.utils import get_xml_root
from .fritzbase import AbstractLibraryBase


__all__ = ['FritzPhonebook']


SERVICE = 'X_AVM-DE_OnTel1'


class FritzPhonebook(AbstractLibraryBase):
    """
    Interface to access the Fritz!Box phonebooks. All parameters are
    optional. If given, they have the following meaning: `fc` is an
    instance of FritzConnection, `address` the ip of the Fritz!Box,
    `port` the port to connect to, `user` the username, `password` the
    password, `timeout` a timeout as floating point number in seconds,
    `use_tls` a boolean indicating to use TLS (default False).
    """
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.phonebook = None

    def _action(self, actionname, **kwargs):
        return self.fc.call_action(SERVICE, actionname, **kwargs)

    @property
    def phonebook_ids(self):
        """
        List of integers identifying the phonebooks. This property is
        defined as `phonebook_ids` and as `list_phonebooks` for backward
        compatibility. The property `list_phonebooks` is deprecated and
        may get removed in the future.
        """
        result = self._action('GetPhonebookList')
        try:
            res = result['NewPhonebookList'].split(',')
            res = [int(x) for x in res]
        except KeyError:
            return []
        return res

    # legathy api name for backward compatibility
    list_phonebooks = phonebook_ids

    def phonebook_info(self, id):
        """
        Get the `name`, `url` and an optional `extra id` of the
        phonebook with integer `id`. Returns a dictionary with the keys
        `name`, `url` and `xid`.
        """
        result = self._action('GetPhonebook', NewPhonebookId=id)
        return {
            'name': result.get('NewPhonebookName'),
            'url': result.get('NewPhonebookURL'),
            'xid': result.get('NewPhonebookExtraID')
        }

    def get_all_names(self, id):
        """
        Get a dictionary with all names and their phone numbers for the
        phonebook with `id`.
        """
        url = self.phonebook_info(id)['url']
        self._read_phonebook(url)
        return {
            contact.name: contact.numbers
            for contact in self.phonebook.contacts
        }

    def get_all_numbers(self, id):
        """
        Get a dictionary with all phone numbers and the according names
        for the phonebook with `id`.
        """
        reverse_contacts = dict()
        for name, numbers in self.get_all_names(id).items():
            for number in numbers:
                reverse_contacts[number] = name
        return reverse_contacts

    def lookup_numbers(self, id, name):
        """
        Look up the phone numbers of contact `name` in the phonebook
        with `id`. Returns a list of numbers. Will raise a KeyError if
        the name is unknown.
        """
        return self.get_all_names(id)[name]

    def lookup_names(self, id, number):
        """
        Look up the names of the contacts with phone number `number` in
        the phonebook with `id`. Will raise a KeyError if the number is
        unknown.
        """
        return self.get_all_numbers(id)[number]

    def _read_phonebook(self, url):
        """
        Read the content of the phonebook with the given `url`. This
        method sets the phone book instance attribute and has no return
        value.
        """
        root = get_xml_root(url, session=self.fc.session)
        self.phonebook = Phonebook()
        process_node(self, root)


@processor
class Services:
    """
    Services container. So far just for an associated email-address.
    """
    def __init__(self):
        self.email = None


@processor
class Person:
    """
    Data storage for a contact name and an image.
    """
    def __init__(self):
        self.realName = None
        self.imageURL = None


@processor
class Telephony:
    """
    Data storage for the phone numbers of the contact and services.
    """
    number = ValueSequencer('numbers')

    def __init__(self):
        self.numbers = list()
        self.services = Services()


@processor
class Contact:
    """
    Represents a contact with `catecory`- and `uniqueid`-attributes as
    well as `person`- and telephony-subnodes.
    """

    def __init__(self):
        self.category = None
        self.uniqueid = None
        self.person = Person()
        self.telephony = Telephony()

    @property
    def name(self):
        return self.person.realName

    @property
    def numbers(self):
        return self.telephony.numbers


@processor
class Phonebook(Storage):
    """
    Represents a phonebook with a timestamp indicating the last
    modification and a list of Contact instances.
    """
    contact = InstanceAttributeFactory(Contact)

    def __init__(self):
        self.timestamp = None
        self.contacts = list()
        super().__init__(self.contacts)
