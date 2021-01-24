from logging import getLogger, DEBUG

log = getLogger("nodes")
log.setLevel(DEBUG)

root_node = -1


def find_internal_nodes_num(tree: list) -> int:
    """ Returns the number of internal nodes (nodes with children) in the tree.

    :param list tree: A list representation of the tree.
    :return:          The number of nodes with children.
    :rtype:           int
    """
    tree_set = set(tree)
    try:
        tree_set.remove(root_node)  # Remove root node entry as it points to outside the tree.
    except KeyError:
        log.debug(
            f"Couldn't remove root node from tree as the node does not exist."
            f"root_node={root_node} tree={tree}"
        )
    return len(tree_set)
