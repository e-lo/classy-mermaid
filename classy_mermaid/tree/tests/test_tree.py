import pytest


from classy_mermaid.tree import create_tree_from_module, tree_to_graph

TEST_MODULE = "pytest"


@pytest.mark.tree
def test_create_tree_from_module():
    t = create_tree_from_module("TEST_MODULE")


@pytest.mark.tree
def test_create_graph_from_tree():
    t = create_tree_from_module("TEST_MODULE")
    g = tree_to_graph(t)
