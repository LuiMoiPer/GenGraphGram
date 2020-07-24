import typing
from collections import defaultdict

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
    lhs: path ("," path)*
    rhs: product ("|" product)*
    product: path ("," path)*
    path: id ("->" id)*
    id: WORD [INT]

    %import common.INT
    %import common.WORD
    %import common.WS
    %ignore WS
    """
    parser = Lark(grammar, lexer="auto", propagate_positions=True)

    def __init__(self, rule: str):
        parse_tree = Rule.parser.parse(rule).children[0]
        # store left and right hand side
        self._process_lhs(parse_tree.children[0])
        self._process_rhs(parse_tree.children[1])
        raise NotImplementedError

    def _process_lhs(self, lhs):
        """From the lhs of the rule we want to store the types used, and adjacency list and 
        store them
        """
        if lhs.data != "lhs":
            raise ValueError

        types = defaultdict(lambda: 0)
        edges = defaultdict(lambda: set())

        # get info from path and add it to the dicts
        for path in lhs.children:
            path_types, path_edges = self._process_path(path)
            # add path types
            for typ, count in path_types.items():
                types[typ] += count
            # add path edges
            for source, neighbors in path_edges.items():
                edges[source] = edges[source].union(neighbors)

        self._lhs = {"types": types, "edges": edges}

    def _process_rhs(self, rhs):
        """From the rhs of the rule we want to store the each possible transfromstions and their 
        types used, and adjacentcies and store them
        """
        if rhs.data != "rhs":
            raise ValueError

        products = []
        raise NotImplementedError

    def _process_product(self, product):
        "Given a product return a dict that stores the types used and the edges between nodes"
        if product.data != "product":
            raise ValueError

        types = defaultdict(lambda: 0)
        edges = defaultdict(lambda: set())

        # get info from path and add it to the dicts
        for path in product.children:
            path_types, path_edges = self._process_path(path)
            # add path types together
            for typ, count in path_types.items():
                types[typ] += count
            # add path edges
            for source, neighbors in path_edges.items():
                edges[source] = edges[source].union(neighbors)

        return {"types": types, "edges": edges}

    def _process_path(self, path):
        """From a path get back return a adjacency dict of all the nodes used and types
        """
        if path.data != "path":
            raise ValueError

        types = defaultdict(lambda: 0)
        edges = defaultdict(lambda: set())

        for i in range(len(path.children) - 1):
            # add an edge from parse_tree.children[i] to parse_tree.children[i + 1]
            source = self._process_id(path.children[i])
            dest = self._process_id(path.children[i + 1])
            edges[source[0]].add(dest[0])
            # add to type counts
            types[source[0]] += 1

        # add the last one that got missed by the loop
        source = self._process_id(path.children[-1])
        types[source[0]] += 1
        return types, edges

    def _process_id(self, ident):
        """Takes in a id tree and returns a tuple that stores the type of the id in the first
        position and the label in the second position.  If there is no label then None is stored
        in the second position.
        """
        if ident.data != "id":
            raise ValueError

        if len(ident.children) == 1:
            return ident.children[0].value, None
        elif len(ident.children) == 2:
            return ident.children[0].value, ident.children[1].value


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
