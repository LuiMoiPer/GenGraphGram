import typing
import networkx as nx

class Generator:

    def __init__(self, rules):
        self._rules = rules

    def generate(self):
        """start with a start symbol and then apply production rules
        """
        # make a graph
        # add start symbol to the graph
        # while production rules can be applied
        #   get all rules that can be applied
        #   pick a rule that can be applied at random
        #   return the graph
        pass

class Rule:
    """Representation of a production rule to be used in the generator, might be better as a 
    function instead of a class.  Responsible for holding the left hand side and right hand side of
    the production rule, might also store ways it changes generation parameters or how many times 
    it can be applied.
    """

    def __init__(self, lhs: str, rhs: str):
        self._lhs = lhs
        self._rhs = rhs


class Node:
    """Represents a node in the graph and has a type to help determine if they can be used in a 
    production rule.
    """

    def __init__(self, type: str, data):
        self._type = type
        self._data = data

    @property
    def typ(self):
        return self._type

    @property
    def data(self):
        return self._data