'''
The MIU system (λ = any string):
    I)   λI   -> λIU
    II)  Mλ   -> Mλλ
    III) λIII -> λU
    IV)  UU   -> ''

.: Starting from MI can you make MU? :.
=======================================

No. It is impossible to the given rules of the system.

To see why, look at the number of Is in a string and the rules that change
this total - the second and third.
    II)  Double the number of Is
    III) Reduce the number of Is by three

Now, the invariant property is that "the number of I is not divisible by 3":
    In the beginning, the number of Is is 1:   1 % 3 != 0.
    If n % 3 != 0...
        2n % 3  != 0
        n-3 % 3 != 0
    --> MU (n=0) can't be reached because 0 % 3 == 0.

NOTE: this uses igraph for visualisation (http://igraph.org)
'''
import numpy as np
import igraph as ig
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D
import matplotlib as mpl


mpl.rcParams['toolbar'] = 'toolbar2'


class Rule:
    def __init__(self, pattern, action):
        self.pattern = pattern
        self.action = action

    def can_apply(self, string):
        return self.pattern(string)

    def apply(self, string):
        return self.action(string)


def substitute(s, old, new):
    def sub(k):
        head, III, tail = k.partition(old)
        if III != '':
            return (head, tail)
        else:
            return (None, None)
    strs = []
    # replace the first instance of old with new
    head, III, tail = s.partition(old)
    strs.append(head + new + tail)
    head += old

    mid, tail = sub(tail)
    while mid is not None:
        strs.append(head + mid + new + tail)
        head = head + mid + old
        mid, tail = sub(tail)

    return strs


# rule1 = Rule(lambda s: s.endswith('I'), lambda s: [s + 'U'])
# rule2 = Rule(lambda s: s.startswith('M'), lambda s: [s + s[1:]])
# rule3 = Rule(lambda s: s.endswith('III'), lambda s: s[:-3] + 'U')
# rules = [rule1, rule2, rule3]

rule1 = Rule(lambda s: s.endswith('I'), lambda s: [s + 'U'])
rule2 = Rule(lambda s: s.startswith('M'), lambda s: [s + s[1:]])
rule3 = Rule(lambda s: 'III' in s, lambda s: substitute(s, 'III', 'U'))
rule4 = Rule(lambda s: 'UU' in s, lambda s: substitute(s, 'UU', ''))
rules = [rule1, rule2, rule3, rule4]


def apply_rules(s, iterations=10, rules=rules, return_graph=False,
                show_MUI_n=False, visualise=False, as_3D=False, layout='kk'):
    '''
    Try to get from s to t using the rules provided
    '''
    if isinstance(s, str):
        root = [s]
        strings = [s]
    else:
        root = list(s)
        strings = list(s)
    current_level = set(strings)
    edges = set()
    new_strings = set()
    MUI_n = [1]
    generation_new = [1]
    total_generated = [1]

    for n in range(iterations):
        for string in current_level:
            for ix, rule in enumerate(rules):
                if rule.can_apply(string):
                    strs = rule.apply(string)
                    for new_string in strs:
                        new_strings.add(new_string)
                        edges.add((string, new_string, n))
        generation_new.append(len(new_strings))
        total_generated.append(total_generated[-1] + len(new_strings))
        current_level = new_strings.difference(strings)
        strings.extend(current_level)
        new_strings = set()
        MUI_n.append(len(strings))

    G = generate_graph(list(edges), strings, root, iterations)

    if show_MUI_n:
        print('mu_n ', MUI_n)
        print('new per generation ', generation_new)
        print('total ', total_generated)

    if visualise:
        draw_graph(G, as_3D, layout)

    if return_graph:
        return G
    else:
        return strings


def search(s, target, iterations=10, rules=rules):
    return target in apply_rules(s, iterations, rules, as_list=False)


def generate_graph(edges, nodes, root, n_iterations):
    # igraph version
    # http://igraph.org/python/doc/tutorial/tutorial.html
    cmap = plt.cm.tab20b(np.linspace(0.0, 1.0, n_iterations))
    G = ig.Graph(directed=False)

    longest = max(map(len, nodes))
    sizes = []
    node_cols = []
    edge_cols = []
    edge_gens = []

    for n in nodes:
        G.add_vertex(n)
        sizes.append(400 * len(n) / longest)
        if n in root:
            node_cols.append('b')
        else:
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
        plt.title(G.root)

    plt.ion()
    plt.axis('off')
    plt.tight_layout()
    plt.show()
