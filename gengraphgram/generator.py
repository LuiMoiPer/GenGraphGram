import typing

import networkx as nx
from lark import Lark


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
        graph = nx.Graph(Node("Start"))
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

    grammar = """
    start: rule
    rule: lhs "==>" rhs ";"
    lhs: item ("," item)*
    rhs: product ("|" product)*
    product: item ("," item)*
    item: id ("->" id)*
    id: WORD [INT]

    %import common.INT
    %import common.WORD
    %import common.WS
    %ignore WS
    """
    parser = Lark(grammar, lexer="auto", propagate_positions=True)

    def __init__(self, rule: str):
        parse_tree = Rule.parser.parse(rule)
        # store left and right hand side
        self._process_lhs()
        self._process_rhs()
        raise NotImplementedError

    def _process_lhs(self, parse_tree):
        """From the lhs of the rule we want to store the labels used, types used, and adjacentcies
        and store them
        """
        raise NotImplementedError

    def _process_rhs(self, parse_tree):
        """From the rhs of the rule we want to store the each possible transfromstions and their 
        labels used, types used, and adjacentcies and store them
        """
        raise NotImplementedError


class Node:
    """Represents a node in the graph and has a type to help determine if they can be used in a 
    production rule.
    """

    def __init__(self, type: str, data=None):
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
