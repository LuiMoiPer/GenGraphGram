from typing import List, Type
from collections import defaultdict
import random

import networkx as nx
from lark import Lark


class Generator:
    def __init__(self, rules: List["Rule"]) -> "Generator":
        # make sure every item is a rule
        if any(not isinstance(rule, Rule) for rule in rules):
            raise ValueError
        self._rules = rules
        self._type_buckets = defaultdict(lambda: 0)
        # parse all the rules to populate the type buckets

    def _get_useable_rules(self, graph) -> List["Rule"]:
        # go through the lhs of the production rules and use that to determine if it can be applied
        useable_rules = []
        for rule in self._rules:
            # use the type bucket to see there enough of each type to apply the rules
            for typ, count in rule.required_types.items():
                if self._type_buckets[typ] < count:
                    continue
            # check connectivity stuff
        return useable_rules
        raise NotImplementedError

    def generate(self):
        """start with a start symbol and then apply production rules until some condition is hit, 
        at the moment we just continue until we cant apply rules anymore.
        """
        graph = nx.Graph(Node("start"))
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
    lhs: product
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

    def _process_lhs(self, lhs):       
        """From the lhs of the rule we want to store the types used, and adjacency list and 
        store them
        """
        if lhs.data != "lhs":
            raise ValueError

        self._lhs = self._process_product(lhs.children[0])

    def _process_rhs(self, rhs):
        """From the rhs of the rule we want to store the each possible transfromstions and their 
        types used, and adjacentcies and store them
        """
        if rhs.data != "rhs":
            raise ValueError

        products = []
        for product in rhs.children:
            products.append(self._process_product(product))
        self._rhs = products

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

    @property
    def lhs(self):
        return self._lhs

    @property
    def rhs(self):
        return self._rhs

    @property
    def required_types(self):
        return self._lhs["types"]

    def get_random_product(self):
        if len(self._rhs) == 1:
            return self._rhs[0]
        else:
            return random.choice(self._rhs)


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
