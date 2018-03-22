import pathpy as pp
import pytest


@pytest.mark.parametrize('edge_list', (
        [(1, 2), (2, 3), (5, 2)],
        list(zip(range(9), range(2, 11))) + list(zip(range(10), range(2, 12))),  # redundant
        list(zip(range(8), range(2, 10))) + list(zip(range(8), range(8)))  # self-loops
))
def test_dag_init(edge_list):
    dag = pp.DAG(edges=edge_list)
    print(dag)


def test_dag_acyclic(dag_object):
    dag = dag_object
    dag.topsort()
    assert dag.is_acyclic is True

    # Add cycle to the graph
    dag.add_edge('b', 'c')
    dag.topsort()
    assert (dag.edge_classes[('b', 'c')] == 'back' or
            dag.edge_classes[('c', 'b')] == 'back')
    assert dag.is_acyclic is False

    dag.make_acyclic()
    assert ('b', 'c') not in dag.edges or ('c', 'b') not in dag.edges
    assert len(dag.edges) == 9


def test_dag_path_extraction(dag_object):
    dag = dag_object
    dag.topsort()

    # Extract paths between nodes in DAG
    paths = pp.path_extraction.paths_from_dag(dag)
    assert paths.observation_count == 7


def test_dag_path_extraction_cyclic(dag_object: pp.DAG):
    dag_object.add_edge('g', 'a')  # adds a cycle to the dag object
    with pytest.raises(ValueError):
        pp.path_extraction.paths_from_dag(dag_object)


def test_route_from_node(dag_object: pp.DAG):
    root = 'a'
    routes = list(sorted(dag_object.routes_from_node(root)))
    expected = [['a', 'b', 'e'], ['a', 'b', 'f', 'g'], ['a', 'c', 'b', 'e'],
                ['a', 'c', 'b', 'f', 'g'], ['a', 'c', 'g']]
    assert routes == expected


def test_route_to_node(dag_object: pp.DAG):
    route_i = dag_object.routes_to_node('i')
    assert route_i == [['h', 'i']]

    route_e = dag_object.routes_to_node('e')
    assert route_e == [['a', 'b', 'e'], ['a', 'c', 'b', 'e']]

    route_g = list(sorted(dag_object.routes_to_node('g')))
    assert len(route_g) == 3
    expected = list(sorted([['a', 'c', 'g'], ['a', 'b', 'f', 'g'], ['a', 'c', 'b', 'f', 'g']]))
    for rout, e_route in zip(route_g, expected):
        assert rout == e_route


def test_dag_path_mapping(dag_object):
    dag = dag_object
    dag.topsort()

    mapping = {'a': 'A', 'b': 'B', 'c': 'A', 'e': 'B', 'f': 'B', 'g': 'A', 'h': 'A',
               'i': 'B', 'j': 'A'}
    paths_mapped2 = pp.path_extraction.paths_from_dag(dag, node_mapping=mapping)
    assert paths_mapped2.paths[1][('A', 'B')][1] == 1
    assert paths_mapped2.paths[1][('A', 'A')][1] == 1
    assert paths_mapped2.paths[2][('A', 'B', 'B')][1] == 1
    assert paths_mapped2.paths[2][('A', 'A', 'A')][1] == 1
    assert paths_mapped2.paths[3][('A', 'B', 'B', 'A')][1] == 1
    assert paths_mapped2.paths[3][('A', 'A', 'B', 'B')][1] == 1
    assert paths_mapped2.paths[4][('A', 'A', 'B', 'B', 'A')][1] == 1
    assert paths_mapped2.observation_count == 7


def test_dag_path_mapping_to_many(dag_object):
    dag = dag_object
    dag.topsort()

    mapping = {
        'a': {1, 2}, 'b': {2, 5},
        'c': {5}, 'e': {1, 2},
        'f': {2, 3}, 'g': {2, 5},
        'h': {1}, 'i': {1, 5},
        'j': {4}
    }
    paths_mapped2 = pp.path_extraction.paths_from_dag(dag, node_mapping=mapping)

    assert paths_mapped2.observation_count == 55
    assert set(paths_mapped2.nodes) == {'1', '2', '3', '4', '5'}


edges1, types1 = [(1, 2), (1, 3), (2, 3)], ({1}, {2}, {3})
edges2 = [(1, 2), (1, 3), (2, 3), (3, 7), (4, 2), (4, 5), (4, 6), (5, 7), (6, 5)]
types2 = ({1, 4}, {2, 6, 3, 5}, {7})
edges3 = 2*[(1, 2), (1, 3), (2, 3), (3, 3)]  # self loop + redundant
types3 = ({1}, {2}, {3})


@pytest.mark.parametrize('edges, types', (
        (edges1, types1),
        (edges2, types2),
        (edges3, types3)
))
def test_add_edges(edges, types):
    roots, neither, leafs = types
    from pathpy import DAG

    D = DAG(edges=edges)
    assert D.leafs == leafs
    assert D.roots == roots
    assert neither not in leafs
    assert neither not in roots


def test_dag_io(dag_object, tmpdir):
    file_path = str(tmpdir.mkdir("sub").join("test.edges"))
    dag_orig = dag_object
    dag_orig.make_acyclic()

    dag_orig.write_file(file_path)
    dag_back = pp.DAG.read_file(file_path)
    assert set(dag_back.edges) == set(dag_orig.edges)

    # filter_nodes out nodes not in the mapping
    mapping = {'a': 'A', 'b': 'B', 'c': 'A'}
    dag_back_map = pp.DAG.read_file(file_path, mapping=mapping)
    assert set(dag_back_map.nodes.keys()) == {'a', 'b', 'c'}


def test_remove_edge(dag_object: pp.DAG):
    dag_object.remove_edge('b', 'f')
    dag_object.remove_edge('b', 'e')
    assert 'f' in dag_object.roots
    assert 'e' in dag_object.roots
    assert 'e' in dag_object.leafs
    assert 'e' in dag_object.isolate_nodes()





