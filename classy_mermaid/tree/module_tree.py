"""Parse a python module into a ModuleTree.
"""
import inspect
import pprint

from dataclasses import dataclass, field
from typing import Any, Collection, Mapping, Optional, Union

from ..logger import get_logger

log = get_logger(__name__)


@dataclass
class NodeBase:
    name: str
    path: str
    parents: list[str]
    children: Optional[list[str]] = field(default_factory=list[str])
    tree: "ModuleTree" = None

    @property
    def id(self):
        return self.node_id(self)

    @staticmethod
    def node_id(node):
        if isinstance(node, NodeBase):
            return node.name
            #return node.path + "." + node.name
        else:
            return node.__name__

    def __str__(self):
        return f"{self.__class__.__name__}({self.id})"

    @classmethod
    def create_from_inspect_member(CLS, member, **kwargs):
        """Create a NodeBase from an inspect.Member."""

        _name = member.__name__

        log.debug(f"Creating {CLS.__name__} from {_name}")

        if inspect.ismodule(member):
            _path = member.__package__
            _parents = []
            return ModuleNode(_name, _path, _parents)
        elif inspect.isclass(member):
            _path = member.__module__
            _parents = [CLS.node_id(_p) for _p in member.__bases__]
            return ClassNode(_name, _path, _parents)
        elif inspect.isfunction(member):
            _path = member.__module__
            _parents = [member.__module__]
            return FunctionNode(_name, _path, _parents)
        else:
            raise NotImplementedError(f"Unsupported member type {type(member)}")

    @property
    def functions(self):
        return {
            child.id: child
            for child in self.children
            if isinstance(child, FunctionNode)
        }

    @property
    def classes(self):
        return {
            child.id: child for child in self.children if isinstance(child, ClassNode)
        }

    @property
    def submodules(self):
        return {
            child.id: child for child in self.children if isinstance(child, ModuleNode)
        }


@dataclass
class AttributeNode(NodeBase):
    pass


@dataclass
class FunctionNode(NodeBase):
    parameters: Mapping = field(default_factory=dict)


@dataclass
class ClassNode(NodeBase):
    pass
    # functions: Mapping[str,AttributeNode]= field(default_factory=dict)
    # attributes: Mapping[str,AttributeNode]= field(default_factory=dict)


@dataclass
class ModuleNode(NodeBase):
    attributes: Mapping[str, AttributeNode] = field(default_factory=dict)


@dataclass
class ModuleTree:
    """A tree of modules and classes."""

    name: str
    nodes: Mapping[str, ClassNode] = field(default_factory=dict)
    private: bool = False

    @property
    def classes(self):
        _classes = {k: v for k, v in self.nodes.items() if isinstance(v, ClassNode)}
        return _classes

    @property
    def modules(self):
        _modules = {k: v for k, v in self.nodes.items() if isinstance(v, ModuleNode)}
        return _modules

    @property
    def functions(self):
        _functions = {
            k: v for k, v in self.nodes.items() if isinstance(v, FunctionNode)
        }
        return _functions

    @property
    def node_list(self):
        return list(self.nodes.values())

    @property
    def children(self):
        _children = {k: n for k, n in self.nodes.iteritems() if n.parents}
        return _children

    @property
    def child_list(self):
        return list(self.children.values())

    @property
    def parents(self):
        _parents = {k: n for k, n in self.nodes.iteritems() if n.children}
        return _parents

    @property
    def parent_list(self):
        return list(self.parents.values())

    def __repr__(self):
        return str(self)

    def __str__(self):
        return f"""ModuleTree(
                name={self.name}, 
                modules=\n - {self._modules_str()}
                classes=\n - {self._classes_str()}
                """

    def _nodes_str(self, nodes: Collection[NodeBase] = None):
        if nodes == None:
            nodes = self.node_list
        return "\n     - "+"\n     - ".join([f"{str(n)}" for n in nodes])

    def _modules_str(self, modules: Collection[ModuleNode] = None):
        if modules == None:
            modules = self.modules
        return "\n     - "+"\n     - ".join([f"{str(m)}" for m in modules])

    def _classes_str(self, classes: Collection[ClassNode] = None):
        if classes == None:
            classes = self.classes
        return "\n     - "+"\n     - ".join([f"{str(c)}" for c in classes])

    def add_node(self, member: Union[NodeBase, Any], **kwargs):
        """Add a member to this tree as a node or update an existing node.

        Args:
            member: The member to add
        """

        if isinstance(member, NodeBase):
            _n = member
        else:
            _n = NodeBase.create_from_inspect_member(member, **kwargs)

        # Currently not doing anything if node already exists.
        if _n.id in self.nodes:
            return

        log.debug(f"Adding node {_n.id} to tree")
        _n.tree = self
        self.nodes[_n.id] = _n
        self.add_parent_refs(_n)

    def add_parent_refs(self, child_node: NodeBase):
        """Add a parent reference to child in tree.

        Args:
            child_node(NodeBase): The child member to add a parent reference to.
        """

        for p_id in child_node.parents:
            if p_id not in self.node_list:
                # need to fix to update this later if it is added.
                log.debug(f"Parent module {p_id} not in tree")
            elif child_node.id not in self.nodes[p_id].children:
                self.nodes[p_id].children.append(child_node.id)

    def add_nodes(self, nodes: Collection[NodeBase]):
        """Add a list of nodes to this tree.

        Args:
            nodes (Mapping[str, NodeBase]): The nodes to add.
        """

        for node in nodes:
            self.add_node(node)

    def add_branch(self, branch: "ModuleTree",branch_name: str= None):
        """Add a branch to this tree.

        Args:
            branch (ModuleTree): The branch to add.
        """
        if branch_name:
            log.debug(f"Adding branch {branch_name} to tree")
        for _node in branch.nodes.values():
            self.add_node(node)
