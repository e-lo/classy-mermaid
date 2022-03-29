from networkx import DiGraph

from .module_tree import ModuleTree


def tree_to_graph(tree: ModuleTree) -> DiGraph:
    """
    Convert a tree to a graph.
    """
    graph = DiGraph()

    for node_id, node in tree.nodes.items():
        graph.add_node(node_id)
        for child_id in node.children:
            graph.add_edge(node_id, child_id)
        for parent_id in node.parents:
            graph.add_edge(parent_id, node_id)
    return graph
