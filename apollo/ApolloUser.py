#!/usr/bin/python

import os

class ApolloUser(object):
    def __init__(self, user_email, firstname, lastname, password):
        self.user_email = user_email
        self.firstname = firstname
        self.lastname = lastname
        self.password = password
