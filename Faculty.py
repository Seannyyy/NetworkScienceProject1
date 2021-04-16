import collections
from operator import itemgetter
import json
#load library
import networkx as nx
import numpy as np
import matplotlib.pyplot
import matplotlib.pyplot as plt
from matplotlib.pyplot import figure
import pandas as pd
#load configs
#import configs as cfg

# Obtain data from JSON
def ParseJSONtoDict (filename):
    # Read JSON data into the datastore variable
    if filename:
        with open(filename, 'r') as f:
            datastore = json.load(f)
    return datastore


# Store data into JSON
def SaveNodesEdgesinJSON (nodes, edges, fileName):
    with open('json/'+fileName+'Nodes.json', 'w') as json_file:
        json.dump(nodes, json_file)

    with open('json/'+fileName+'Edges.json', 'w') as json_file:
        json.dump(edges, json_file)

class Networks:

    def __init__ (self):
        self.scseGraph = nx.Graph()
        self.scseMultiGraph = nx.MultiGraph()
        self.CoauthorGraph = self.CreateCoauthorNetwork()
        self.CreateScseNetwork()

    def CreateScseNetwork (self):
        nodes = ParseJSONtoDict('json/ScseStaffNodes.json')
        edges = ParseJSONtoDict('json/ScseStaffEdges.json')
        self.scseGraph.add_nodes_from(nodes)
        self.scseGraph.add_edges_from(edges)
        self.scseMultiGraph.add_nodes_from(nodes)
        self.scseMultiGraph.add_edges_from(edges)

    def CreateCoauthorNetwork (self):
        nodes = ParseJSONtoDict('json/CoauthorNodes.json')
        edges = ParseJSONtoDict('json/CoauthorEdges.json')
        dummy_graph = nx.Graph()
        dummy_graph.add_nodes_from(nodes)
        dummy_graph.add_edges_from(edges)
        mesh = sorted(dummy_graph.degree, key=lambda x: x[1], reverse=True)
        k = [i[0] for i in mesh]
        top_1000 = k[:1075]
        top_1000graph = dummy_graph.subgraph(top_1000).copy()
        return top_1000graph

    def GetScseNetwork(self):
        return self.scseGraph

    def GetScseMultiNetwork(self):
        return self.scseMultiGraph

    def GetCoauthorNetwork(self):
        return self.CoauthorGraph


"""
#Filter Graph
#For qn 3-5
#filterby: 'management','position','area'
#rank(management): "Y" , "N"
#position: "Professor" , "Associate Professor" , "Assistant Professor", "Lecturer"
"""
def filterGraphs(graph, filterby, rank1, rank2 = None):
    filteredNodes= []
    if rank2:
        for node in graph.nodes.data():
            if node[1][filterby] == rank1 or node[1][filterby]== rank2:
                filteredNodes.append(node[0])
    else:
        for node in graph.nodes.data():
            if node[1][filterby] == rank1:
                filteredNodes.append(node[0])

    subGraph = graph.subgraph(filteredNodes).copy()
    return subGraph

def compareFiltered(graph, filterby, rank1, rank2=None):
    subGraph = filterGraphs(graph, filterby, rank1, rank2)
    colormap = []
    if rank2:
        for node in subGraph.nodes.data():
            if node[1][filterby] == rank1:
                colormap.append('blue')
            else:
                colormap.append('green')
    else:
        for node in subGraph.nodes.data():
            if node[1][filterby] == rank1:
                colormap.append("blue")
    f = plt.figure(figsize=(10, 10), dpi=100)
    a = f.add_subplot(111)
    nx.draw_kamada_kawai(subGraph,with_labels=False, ax=a, node_color=colormap)
    return f


def FilterScseNodes(scseGraph, startyear, endyear):
    filteredNodes = []

    for node in scseGraph.nodes.data():
        if node[1]['start'] >= startyear or node[1]['end'] <= endyear :
            filteredNodes.append(node[0])

    scseSubGraph = scseGraph.subgraph(filteredNodes).copy()

    print(scseSubGraph)

    return scseSubGraph

"""
NetworkX Measures Algorithm
"""
# def GetBetweenness(graph):
#     #access specific node by using betweennessList[node]
#     betweennessList = nx.betweenness_centrality(graph)

#     for key, value in betweennessList.items():
#         if value > 0:
#             print(key, value)

# def GetEigenVector(graph):
#     #access specific node by using EigenMatrix[node]
#     eigenMatrix = nx.eigenvector_centrality(graph)
#     print(eigenMatrix)

# def GetCloseness(graph):
#     #acess specific node by using closeness[node]
#     closenessList = nx.closeness_centrality(graph)
#     print(closenessList)


"""
Graphs for questions
"""


def GetDegreeDistribution(graph):
    degree_sequence = sorted([d for n, d in graph.degree()], reverse=True)
    degreeCount = collections.Counter(degree_sequence)
    degList, degCountList = zip(*degreeCount.items())

    # print(degList, degCountList)

    return degList, degCountList

def GetScsePublicationDistribution(Graph):
    # maxDegree = max(authorGraph.degree, key=lambda x: x[1])[1]
    # minDegree = min(authorGraph.degree, key=lambda x: x[1])[1]

    publication_seq = []
    for node in Graph.nodes.data():
        publication_seq.append(node[1]['size'])
    publication_seq = sorted(publication_seq, reverse=True)
    publicationCount = collections.Counter(publication_seq)

    publ, cnt = zip(*publicationCount.items())
    N = len(Graph.nodes)
    pk = []
    for publNum, cnt in publicationCount.items():
        pk.append(cnt/N)
    pk = sorted(pk)

    plt.figure()
    plt.scatter(publ, pk, c="r", s=10)

    plt.yscale('log')
    plt.xscale('log')

    # axes = plt.gca()
    # axes.set_xlim([0.9,max(publ)])
    # axes.set_ylim([min(pk)*0.1, 1])

    plt.scatter(publ, pk, c="r", s=10)

    plt.title("Author Publications Distribution")
    plt.ylabel("P(# Publications)")
    plt.xlabel("# Publications")
    # plt.savefig("AuthorPublicationsDistribution.png")
    # graph too large to be drawn, but algorithms based on degree etc, can be done
    return plt
def GetScseDegreeDistribution(graph):
    degree_sequence = sorted([d for n, d in graph.degree()], reverse=True)
    degreeCount = collections.Counter(degree_sequence)
    degList, degCountList = zip(*degreeCount.items())

    N = len(graph.nodes)
    pk = []
    for cnt in degCountList:
        pk.append(cnt/N)

    degList = sorted(degList)
    pk = sorted(pk, reverse=True)

    plt.figure()
    plt.scatter(degList, pk, c="r", s=10)

    plt.yscale('log')
    plt.xscale('log')

    axes = plt.gca()
    axes.set_xlim([0.9,max(degList)])
    axes.set_ylim([min(pk)*0.5, 1])

    plt.title("Author Degree Distribution")
    plt.ylabel("Pk")
    plt.xlabel("Degree")
    # plt.savefig("AuthorDegreeDistribution.png")
    # graph too large to be drawn, but algorithms based on degree etc, can be done
    return plt, degList, pk

def GetScseReputationDistribution(graph, start_year=2000, end_year=2019):
    plt.close()
    authorReputation = []
    count = 0
    for author, data in graph.nodes.data():
        reputation = 0
        publications = data['publ']
        count+=1
        print(count)
        publications.sort(key=itemgetter('year'))

        for publ in publications:
            if int(publ['year']) in list(range(start_year, end_year+1)):
                if publ['tier'] == 1:
                    reputation += 3
                elif publ['tier'] == 2:
                    reputation += 2
                elif publ['tier'] == 3:
                    reputation += 1
        if reputation > 0:
            authorReputation.append((author, reputation))


    authorReputation.sort(key=lambda tup: tup[0], reverse=True)
    author, reputation = zip(*authorReputation)

    reputationCount = collections.Counter(reputation)
    reputationList, repCountList = zip(*reputationCount.items())

    pk = []
    N = len(authorReputation)
    for cnt in repCountList:
        pk.append(cnt/N)

    plt.figure()
    plt.scatter(reputationList, pk, c="r", s=10)

    plt.yscale('log')
    plt.xscale('log')

    # axes = plt.gca()
    # axes.set_xlim([0.9,max(degList)])
    # axes.set_ylim([min(pk)*0.1, 1])

    plt.scatter(reputationList, pk, c="r", s=10)

    plt.title("Author Reputation Distribution")
    plt.ylabel("P(Reputation)")
    plt.xlabel("Reputation")
    # plt.savefig("AuthorReputationDistribution.png")
    # graph too large to be drawn, but algorithms based on degree etc, can be done
    # plt.show()
    return plt, reputationList, pk

def GetCoauthorReputationDegree(graph):
    plt.close()
    authorDegree = list(graph.degree())
    authorReputation = list(graph.nodes(data='reputation'))

    authorDegree.sort(key=lambda tup: tup[0], reverse=True)
    authorReputation.sort(key=lambda tup: tup[0], reverse=True)

    # print(len(authorDegree))
    # print(len(authorReputation))

    data = []
    for i in range(len(authorDegree)):
        data.append((authorReputation[i][1], authorDegree[i][1]))

    data.sort(key=lambda tup: tup[0], reverse=True)

    # print(data)

    y_axis, x_axis = zip(*data)

    # ax = plt.gca()
    plt.scatter(y_axis, x_axis, c="r", s=1)
    plt.title("Author Reputation vs. Degree")
    plt.ylabel("Reputation")
    plt.xlabel("Degree")
    # ax.set(xscale="log")
    # ax.set(yscale="log")
    # plt.savefig("AuthorReputationDegree.png")
    return plt


def GetCoauthorMaximumDegreeChange(graph):
    plt.close()
    x_axis1 = []
    y_axis1 = []
    x_axis2 = []
    y_axis2= []
    for year in list(range(2000, 2021)):
        subgraph = FilterScseNodes(graph,2000,year+1)

        degList, degCountList = GetDegreeDistribution(subgraph)
        y_axis1.append(max(degList))
        x_axis1.append(year)

        _, reputationList, _ = GetScseReputationDistribution(subgraph, 2000,year+1)
        y_axis2.append(max(reputationList))
        x_axis2.append(year)

    plt.close()
    plt.figure()
    # plotting the line 1 points
    plt.plot(x_axis1, y_axis1, label = "Maximum Degree")
    plt.plot(x_axis2, y_axis2, label = "Maximum Reputation")
    plt.title("Change in Maximum Degree")
    plt.ylabel("Maximum Degree")
    plt.xlabel("Year")
    plt.legend()
    return plt
