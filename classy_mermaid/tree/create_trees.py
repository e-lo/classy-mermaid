import importlib
import inspect
from typing import Any, Collection, Mapping, Tuple, Union

from ..logger import get_logger

from .module_tree import (
    ModuleTree,
    NodeBase,
    ClassNode,
    ModuleNode,
    AttributeNode,
    FunctionNode,
)

log = get_logger(__name__)

def create_tree_from_module(
    module_name: Union[str,'Module'],
    tree: ModuleTree = None,
    ignore: Collection[str] = [],
    skip_private: bool = True,
    max_recursive: int = 2,
    num_recursive: int = 0,
    visited: Collection[str] = [],
) -> ModuleTree:
    """_summary_

    Args:
        module_name (str): _description_
        tree (ModuleTree, optional): _description_. Defaults to None.
        ignore (Collection[str], optional): _description_. Defaults to [].
        skip_private (bool, optional): _description_. Defaults to True.
        max_recursive (int, optional): _description_. Defaults to 2.
        num_recursive (int, optional): _description_. Defaults to 0.
        visited (Collection[str], optional): DO NOT INITIATE. Defaults to [].

    Returns:
        ModuleTree: _description_
    """
    
    if tree == None:
        tree = ModuleTree(module_name)

    if inspect.ismodule(module_name):
        _module = module_name
    else:
        _module = importlib.import_module(module_name)

    if num_recursive == 0:
        log.info(f"Creating tree from module {module_name}")
    else:
        log.debug(f"Creating tree from module {module_name}")
    
    num_recursive += 1

    _nodes, _submodules = get_members_from_module(
        _module,
        ignore=ignore,
        skip_private=skip_private,
    )

    log.debug(f"""In {_module.__name__} found:
          {len(_nodes)} Nodes
          {len(_submodules)} Submodules: {",".join([s.__name__ for s in _submodules])}""")

    tree.add_nodes(_nodes)

    if num_recursive == max_recursive or not _submodules:
        log.debug(f"Returning Tree: num_recursive={num_recursive}, _submodules={_submodules}")
        log.debug(f"   TREE: {tree._nodes_str()}")
        return tree

    for submodule in _submodules:
        if submodule in visited: continue
        visited.append(submodule)
        log.debug(f"Recursing into: {submodule.__name__}")
        branch = create_tree_from_module(
            submodule,
            tree=tree,
            ignore=ignore,
            skip_private=skip_private,
            max_recursive=max_recursive,
            num_recursive=num_recursive,
            visited = visited,
        )
        #tree.add_branch(branch,branch_name=submodule.__name__)
        log.debug(f"Exiting recursion from: {submodule.__name__}")
    return tree

def _is_private(
    obj_name:str
)->bool:
    private = obj_name.startswith("_")
    return private

def _is_outside_module(
    member, 
    module_name:str,
) -> bool:
    """_summary_

    Args:
        member (_type_): _description_
        module_name (str): _description_

    Returns:
        bool: _description_
    """

    if inspect.isbuiltin(member) or member.__name__ == "builtin":
        return True

    if inspect.ismodule(member):
        _path =  member.__package__
    else:
        _path =  member.__module__

    return module_name not in _path

def get_members_from_module(
    module,
    ignore: Collection[str] = [],
    skip_private: bool = True,
    skip_outside_module: bool = True,
) -> Tuple[Collection, Collection]:
    """_summary_

    Args:
        module (_type_): _description_
        ignore (Collection[str], optional): _description_. Defaults to [].
        skip_private (bool, optional): _description_. Defaults to True.

    Returns:
        Tuple[Collection[NodeBase],Collection[ModuleNode]]: _description_
    """
    _submodule_members = inspect.getmembers(module, predicate=inspect.ismodule)
    _class_members = inspect.getmembers(module, predicate=inspect.isclass)
    _function_members = inspect.getmembers(module, predicate=inspect.isfunction)
    _all_members =  _submodule_members+_class_members+_function_members
    
    if skip_private:
        ignore += [n for n,m in _all_members if _is_private(n)]
        log.debug(f"Skipping private members.")

    if skip_outside_module:
        ignore += [n for n,m in _all_members if _is_outside_module(m, module.__name__)]
        log.debug(f"Skipping members outside {module.__name__}.")

    _module_members = [m for n, m in inspect.getmembers(module) if n not in ignore]

    #log.debug(f"Module Members: {_module_members}")

    submodules =  [m for n,m in _submodule_members if n not in ignore]
    classes =  [m for n,m in _class_members if n not in ignore]
    # should hopefully only be getting lone functions (notclass methods) bc in module, not class
    functions = [m for n,m in _function_members if n not in ignore]

    log.debug(f"""Found members to document in module {module.__name__}:
        - Submodules: {len(submodules)}
        - Classes: {len(classes)}
        - Functions: {len(functions)}"""
    )

    nodes = submodules+classes+functions
    
    return nodes, submodules
