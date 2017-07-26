'''
Happy numbers
'''
import numpy as np
import igraph as ig
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D
import matplotlib as mpl


mpl.rcParams['toolbar'] = 'toolbar2'


def generate(n, visualise=True, as_3D=False, layout='tree'):
    '''Generate happy numbers from a seed upper bound of n'''
    def get_next(x):
        return sum(map(lambda y: int(y)**2, list(str(x))))

    nodes = ['1']
    edges = []
    for ix, num in enumerate(range(n+1, 1, -1)):
        k = num
        while str(k) not in nodes:
            nodes.append(str(k))
            next_k = get_next(k)
            edges.append((str(k), str(next_k), ix))
            k = next_k

    G = generate_graph(edges, nodes, '1', n)
    if visualise:
        draw_graph(G, as_3D, layout)
    return G


def generate_graph(edges, nodes, root, n_iterations):
    cmap = plt.cm.tab20b(np.linspace(0.0, 1.0, n_iterations))
    G = ig.Graph(directed=False)

    largest = max(map(int, nodes))
    sizes = []
    node_cols = []
    edge_cols = []
    edge_gens = []

    for n in nodes:
        G.add_vertex(n)
        if n == root:
            sizes.append(100)
            node_cols.append('b')
        else:
            sizes.append(200 * int(n) / largest)
            node_cols.append('r')

    for e in edges:
        G.add_edge(e[0], e[1])
        edge_gens.append(e[2])
        edge_cols.append(cmap[e[2]])

    G.sizes = sizes
    G.nodes = nodes
    G.edges = edges
    G.node_cols = node_cols
    G.edge_cols = edge_cols
    G.edge_gens = edge_gens
    G.root = root

    return G


def draw_graph(G, as_3D=False, layout='kk'):
    '''Visualise how strings generate one another'''
    fig = plt.figure(figsize=(24, 10))
    N = len(G.nodes)

    if as_3D:
        layout = G.layout('fr3d', dim=3)
        # layout = G.layout('kk3d', dim=3)

        xs = [layout[k][0] for k in range(N)]  # x-coordinates of nodes
        ys = [layout[k][1] for k in range(N)]  # y-coordinates
        zs = [layout[k][2] for k in range(N)]  # z-coordinates
        Xe, Ye, Ze = [], [], []

        # edge endpoint coordinates
        for e in G.edges:
            source = G.nodes.index(e[0])
            target = G.nodes.index(e[1])
            Xe.append((layout[source][0], layout[target][0], None))
            Ye.append((layout[source][1], layout[target][1], None))
            Ze.append((layout[source][2], layout[target][2], None))

        ax = fig.add_subplot(111, projection='3d', facecolor='w')
        # ax.axis('tight')
        fig.subplots_adjust(left=0, right=1, bottom=0, top=1)

        for i in range(len(G.es)):
            ax.plot(
                (Xe[i][0], Xe[i][1]),
                (Ye[i][0], Ye[i][1]),
                zs=(Ze[i][0], Ze[i][1]), c=G.edge_cols[i],
                linewidth=1.6, zorder=1)

        ax.scatter(xs, ys, zs, c=G.node_cols, s=G.sizes, zorder=2)

    else:
        # layout = G.layout('kk', dim=2)
        layout = G.layout(layout)

        xs = [layout[k][0] for k in range(N)]  # x-coordinates of nodes
        ys = [layout[k][1] for k in range(N)]  # y-coordinates
        Xe, Ye = [], []

        # edge endpoint coordinates
        for e in G.edges:
            source = G.nodes.index(e[0])
            target = G.nodes.index(e[1])
            Xe.append((layout[source][0], layout[target][0], None))
            Ye.append((layout[source][1], layout[target][1], None))

        ax = fig.add_subplot(111, facecolor='w')

        for i in range(len(G.edges)):
            ax.plot(
                (Xe[i][0], Xe[i][1]),
                (Ye[i][0], Ye[i][1]),
                c=G.edge_cols[i], linewidth=1.2,
                zorder=1)

        ax.scatter(xs, ys, c=G.node_cols, s=G.sizes, zorder=2)
        for i, n in enumerate(G.nodes):
            ax.text(xs[i]+0.02, ys[i], n, fontsize=20)

    plt.ion()
    plt.axis('off')
    plt.tight_layout()
    plt.show()
