"""
Module to access phonebooks and their content.
"""
# This module is part of the FritzConnection package.
# https://github.com/kbr/fritzconnection
# License: MIT (https://opensource.org/licenses/MIT)
# Authors: Klaus Bremer, David M. Straub


from ..core.fritzconnection import FritzConnection
from ..core.processor import (
    processor,
    process_node,
    InstanceAttributeFactory,
    Storage,
    ValueSequencer,
)
from ..core.utils import get_xml_root


SERVICE = 'X_AVM-DE_OnTel'


class FritzPhonebook(object):
    """
    Interface to access the Fritz!Box phonebooks. All parameters are
    optional. If given, they have the following meaning: *fc* is an
    instance of FritzConnection, *address* the ip of the Fritz!Box,
    *port* the port to connect to, *user* the username, *password* the
    password.
    """
    def __init__(self, fc=None, address=None, port=None,
                       user=None, password=None):
        if fc is None:
            fc = FritzConnection(address, port, user, password)
        self.fc = fc
        self.phonebook = None

    def _action(self, actionname, **kwargs):
        return self.fc.call_action(SERVICE, actionname, **kwargs)

    @property
    def modelname(self):
        return self.fc.modelname

    @property
    def list_phonebooks(self):
        """
        List of integers identifying the phonebooks.
        """
        result = self._action('GetPhonebookList')
        try:
            res = result['NewPhonebookList'].split(',')
            res = [int(x) for x in res]
        except KeyError:
            return []
        return res

    def phonebook_info(self, id):
        """
        Get the name, URL and an optional extra id of the phone book
        with integer `id`.
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
        phone book with `id`.
        """
        url = self.phonebook_info(id)['url']
        self.read_phonebook(url)
        return {
            contact.name: contact.numbers
            for contact in self.phonebook.contacts
        }

    def lookup_numbers(self, id, name):
        """
        Look up the phone numbers of contact `name` in the phone book with
        `id`. Returns a list of numbers. Raise a KeyError if the name is unknown.
        """
        return self.get_all_names(id)[name]

    def lookup_names(self, id, number):
        """
        Look up the names of the contacts with phone number `number`
        in the phone book with `id`.
        """
        nd = {}
        for name, numbers in self.get_all_names(id).items():
            for phonenumber in numbers:
                nd[phonenumber] = name
        return nd[number]

    def read_phonebook(self, url):
        """
        Read the content of the phonebook with the given `url`.
        """
        root = get_xml_root(url)
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
        imageURL = None


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

