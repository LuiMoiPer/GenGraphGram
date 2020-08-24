from typing import List, Type, DefaultDict, Set
from collections import defaultdict
import random
import copy

import matplotlib.pyplot as plt
from networkx import Graph, draw
from networkx.algorithms.isomorphism import GraphMatcher
from lark import Lark


class Generator:
    def __init__(self, rules: List["Rule"]) -> "Generator":
        # make sure every item is a rule
        if any(not isinstance(rule, Rule) for rule in rules):
            raise ValueError
        self._rules = rules
        self._type_buckets = defaultdict(lambda: set())
        # parse all the rules to populate the type buckets

    def _add_to_type_buckets(self, node: "Node"):
        # get the node type and add the node to the bucket of its type
        self._type_buckets[node.typ].add(node)

    def _remove_from_type_buckets(self, node: "Node"):
        # get the node type and discard it from the bucket of its type
        self._type_buckets[node.typ].discard(node)

    def _get_useable_rules(self, graph: "Graph") -> List["Rule"]:
        # go through the lhs of the production rules and use that to determine if it can be applied
        useable_rules = []
        for rule in self._rules:
            # check if there are nodes of each type needed
            if not self._has_required_types(rule, graph.graph["types"]):
                continue
            # check if there are enough of each node type
            if not self._has_required_type_counts(rule, graph.graph["type_counts"]):
                continue
            # check if there is the required conectivity
            if not self._has_required_connections(rule, graph):
                continue
            # check other meta stuff
            useable_rules.append(rule)
        return useable_rules

    def _has_required_types(self, rule: "Rule", types: "Set") -> bool:
        # check if all elements in the lhs of the rule are in types
        return rule.lhs.graph["types"] <= types

    def _has_required_type_counts(
        self, rule: "Rule", type_counts: "DefaultDict"
    ) -> bool:
        # make sure there are enough of each node type in type_counts
        for typ, count in rule.required_type_counts.items():
            if type_counts[typ] < count:
                return False
        # there are enough of each node
        return True

    def _has_required_connections(self, rule: "Rule", graph: "Graph") -> bool:
        # check if the lhs of the rule is a subgraph of our current graph
        node_matcher = lambda node1, node2: node1["type"] == node2["type"]
        matcher = GraphMatcher(graph, rule.lhs, node_matcher)
        return matcher.subgraph_is_isomorphic()

    def _make_starting_graph(self) -> "Graph":
        # make the graph
        graph = copy.deepcopy(self._rules[0].lhs)
        return graph

    def _apply_rule(self, rule: "Rule", graph: "Graph") -> None:
        # apply rule
        #   find where we're applying the rule
        #   do the node replacement
        #   figure out how to reconnect any dangling edges

        # update type info
        self._update_type_info(graph)
        raise NotImplementedError

    def _update_type_info(self, graph: "Graph") -> None:
        # get current type info
        types = set()
        type_counts = defaultdict(int)
        for node_data in graph.nodes.values():
            typ = node_data["type"]
            types.add(typ)
            type_counts[typ] += 1
        # update type info
        graph.graph["types"] = types
        graph.graph["type_counts"] = type_counts

    @property
    def rules(self):
        return self._rules

    def generate(self) -> "Graph":
        """start with a start symbol and then apply production rules until some condition is hit, 
        at the moment we just continue until we cant apply rules anymore.
        """

        # make a graph like the first rule made when the gen was inited
        graph = self._make_starting_graph()

        useable_rules = self._get_useable_rules(graph)
        while len(useable_rules) > 0:
            # pick one of the useable rules at random and apply it
            self._apply_rule(random.choice(useable_rules), graph)
            # update the usable rules
            useable_rules = self._get_useable_rules(graph)
        raise NotImplementedError
        # return the graph
        return graph


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

        # get the networkx representation of the left hand side
        graph = self._process_product(lhs.children[0])
        self._lhs = graph

    def _process_rhs(self, rhs):
        """From the rhs of the rule we want to store each possible transfromstions and their 
        types used, and adjacentcies and store them
        """
        if rhs.data != "rhs":
            raise ValueError

        products = []
        for product in rhs.children:
            products.append(self._process_product(product))
        self._rhs = products

    def _process_product(self, product):
        "Given a product return a networkx graph that represents the product"
        if product.data != "product":
            raise ValueError

        graph = Graph(types=set(), type_counts=defaultdict(int))

        # process ids and edges, and update types, and type_counts for each path
        for path in product.children:
            self._process_path(path, graph)

        # make a networkx representation of the product
        # draw(graph, with_labels=True)
        # from time import time
        # plt.savefig(f"{time()}.png")
        # plt.close()

        return graph

    def _process_path(self, path, graph):
        """From a path add the edges between nodes to the graph
        """
        if path.data != "path":
            raise ValueError

        if len(path.children) == 1:
            # there are no edges in this path so we just need to process the id
            self._process_id(path.children[0], graph)
        else:
            for i in range(len(path.children) - 1):
                # add an edge from parse_tree.children[i] to parse_tree.children[i + 1]
                source = self._process_id(path.children[i], graph)
                dest = self._process_id(path.children[i + 1], graph)
                # add edge to graph
                graph.add_edge(source, dest)

    def _process_id(self, ident, graph):
        """Takes in a id tree and adds the id as a npde in the graph.  Also upates the type counts 
        dict of the graph.  Returns the name of the node.
        """
        if ident.data != "id":
            raise ValueError

        # get the type and add it to types and increase type_counts
        typ = ident.children[0].value

        # make the name
        if len(ident.children) == 1:
            name = typ
        elif len(ident.children) == 2:
            name = typ + ident.children[1].value

        if name not in graph:
            # add the node to the graph and update type info
            graph.add_node(name, type=typ)
            graph.graph["types"].add(typ)
            graph.graph["type_counts"][typ] += 1

        return name

    @property
    def lhs(self):
        return self._lhs

    @property
    def rhs(self):
        return self._rhs

    @property
    def required_types(self) -> "Set":
        return self._lhs.graph["types"]

    @property
    def required_type_counts(self) -> "DefaultDict":
        return self._lhs.graph["type_counts"]

    def get_random_product(self):
        if len(self._rhs) == 1:
            return self._rhs[0]
        else:
            return random.choice(self._rhs)


if __name__ == "__main__":
    pass
