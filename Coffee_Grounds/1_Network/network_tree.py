"""
Try to visualize swim lanes for parallel tasks
"""

import pandas as pd
import networkx as nx
import matplotlib.pyplot as plt

from collections import defaultdict

def find_sources_and_sinks(graph):
    sources = list()
    sinks = list()
    neither = list()

    for node in graph.nodes():
        if graph.in_degree(node) == 0:
            sources.append(node)
        elif graph.out_degree(node) == 0: # If both in_degrees = 0 & out = 0, free-floating task, pin to left anyway
            sinks.append(node)
        else:
            neither.append(node) # just for debugging purposes

    return sources, sinks

def create_graph(filename):
    with open(filename, 'r') as spreadsheet:
        pdframe = pd.read_csv(spreadsheet)

    dir_graph = nx.DiGraph()

    for index, row in pdframe.iterrows():
        root_node = row["Step Name"] # how to use the subsequent step?? Merge somehow
        dependent_node = row["Prerequisite Step"] if pd.notna(row["Prerequisite Step"]) else ""
        early_finish = row["Duration ( lower bound in minutes )"] if pd.notna(row["Duration ( lower bound in minutes )"]) else ""
        late_finish = early_finish = row["Duration ( upper bound in minutes )"] if pd.notna(row["Duration ( upper bound in minutes )"]) else ""
        edge_name = f"{early_finish} - {late_finish} minutes"

        dir_graph.add_edge(root_node, dependent_node, label=edge_name)

    return dir_graph

def invert_dict(og_dict):
    inverted_dict = defaultdict(list)
    for key, value in og_dict.items():
        inverted_dict[value].append(key)
    return inverted_dict

def main():
    orientation = "top"
    # filename = "prerequisites.csv"
    # filename = "Steak_2 copy.csv"
    filename = "outputs.txt"

    dir_graph = create_graph(filename)

    sources, sinks = find_sources_and_sinks(dir_graph)
    degree_lvls = {}

    for src_node in sources:
        for target in dir_graph.nodes():
            try:
                length = nx.shortest_path_length(dir_graph, source=src_node, target=target)

                if target not in degree_lvls or length < degree_lvls[target]:
                    degree_lvls[target] = length
            except nx.NetworkXNoPath:
                continue


    inv_degree_lvls = invert_dict(degree_lvls)

    max_span = max(degree_lvls.values()) if degree_lvls else 0
    plot_width = max_span
    plot_height = max_span

    pos = {}

    for node, level in degree_lvls.items():
        if orientation == "top" or orientation == "t":
            # x, y
            # pos[node] = (level, max_span - level)

            for src_node in sources:
                pos[src_node] = (0.5, plot_height)

            # src node = degree 0
            for nonsrc_lvl in range(1, max_span + 1):
                for index, sibling in enumerate(inv_degree_lvls[nonsrc_lvl]):
                    # pos[sibling] = (    round(  (index/plot_width) * plot_width, 0), plot_height - nonsrc_lvl )
                    pos[sibling] = (index, plot_height - nonsrc_lvl)


        elif orientation == "left" or orientation == "l":
            pass  # not implemented
    plt.figure(figsize=(50, 50))

    nx.draw(dir_graph, pos, with_labels=True, node_size=3000, node_color='orange', font_size=10, font_weight='bold',
            arrows=True)

    edge_labels = nx.get_edge_attributes(dir_graph, "label")
    nx.draw_networkx_edge_labels(dir_graph, pos, edge_labels=edge_labels, font_size=8)

    plt.title('Prerequisite Flowchart')
    plt.show()

if __name__ == "__main__":
    main()