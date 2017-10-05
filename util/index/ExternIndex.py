#!/usr/bin/python
import collections
import abc
from abc import ABCMeta

class ExternIndex(object):
    __metaclass__ = ABCMeta

    @abc.abstractmethod
    def __init__(self):
        """init"""
    
    @abc.abstractmethod
    def setExtLink(self):
        """set external link"""
        