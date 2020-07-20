import typing
import networkx as nx

class Generator:

    def __init__(self, rules):
        self._rules = rules
        self._type_buckets = {}
        # parse all the rules to populate the type buckets

    def _get_useable_rules(self, graph):
        # go through the lhs of the production rules and use that to determine if it can be applied
        # for rule in self._rules
        #   get how many of each type is needed for the rule
        #   use the type bucket to see there enough of ech type to apply the rules
        #   check connectivity stuff
        # return a list of applicable rules
        raise NotImplementedError

    def generate(self):
        """start with a start symbol and then apply production rules
        """
        graph = nx.Graph(Node('Start'))
        useable_rules = self._get_useable_rules(graph)
        while len(useable_rules) > 0:
            # pick one of the useable rules at random
            # apply the rule
            useable_rules = self._get_useable_rules(graph)
        # return the graph
        raise NotImplementedError

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

    def __init__(self, type: str, data = None):
        self._type = type
        self._data = data

    @property
    def typ(self):
        return self._type

    @property
    def data(self):
        return self._data
    
    @data.setter
    def data(self, data):
        self._data = data

if __name__ == "__main__":
    pass