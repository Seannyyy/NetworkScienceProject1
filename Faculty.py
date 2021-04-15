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
import configs as cfg

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


    def CreateGraphForGUI(self):
        x,y = GetDegreeDistribution(self.scseGraph)


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
def GetBetweenness(graph):
    #access specific node by using betweennessList[node]
    betweennessList = nx.betweenness_centrality(graph)

    for key, value in betweennessList.items():
        if value > 0:
            print(key, value)

def GetEigenVector(graph):
    #access specific node by using EigenMatrix[node]
    eigenMatrix = nx.eigenvector_centrality(graph)
    print(eigenMatrix)

def GetCloseness(graph):
    #acess specific node by using closeness[node]
    closenessList = nx.closeness_centrality(graph)
    print(closenessList)

def DrawGraph(graph):
    nodessize = []
    edgecolors = []
    nodescolor = []

    edgeslist = graph.edges.data()

    for node in graph.nodes.data():
        nodessize.append(node[1]['size'])
        if node[1]['tier'] == 1:
            nodescolor.append([1,0,0])
        elif node[1]['tier'] == 2:
            nodescolor.append([1,0.2,0.2])
        elif node[1]['tier'] == 3:
            nodescolor.append([1,0.4,0.4])

    maxSize = max(nodessize)
    minSize = min(nodessize)
    maxNodeSize = 5000
    for size in nodessize:
        size = (size - minSize) / (maxSize -minSize) * maxNodeSize + 1000

    edgemax = max(edgeslist, key=lambda x: x[2]['weight'])[2]['weight']
    edgemin = min(edgeslist, key=lambda x: x[2]['weight'])[2]['weight']
    M = graph.number_of_edges()
    edgealphas = []
    for edge in edgeslist:
        weight = edge[2]['weight']
        color = (weight - edgemin) / (edgemax - edgemin)
        edgecolors.append(color)
        edgealphas.append(color)

    # plt.figure(figsize=(20,20))
    pos=nx.spring_layout(graph, k=5)

    nx.draw_networkx_nodes(
        graph,
        pos=pos,
        node_color=nodescolor,
        node_size=nodessize
    )

    edges = nx.draw_networkx_edges(
        graph,
        pos=pos,
        arrowstyle="->",
        arrowsize=5,
        edge_color=edgecolors,
        edge_cmap=plt.cm.Greys,
        width=1,
    )

    nx.draw_networkx_labels(
        graph, pos=pos, font_size=6,
        font_color='k', font_family='sans-serif',
        font_weight='normal', alpha=None,
        bbox=None, ax=None
    )

    # set alpha value for each edge
    for i in range(M):
        edges[i].set_alpha(edgealphas[i])

    plt.savefig("conferenceNW.png")

"""
Used to solve questions
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

def GetAuthorReputationDegree(graph):
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

def GetAuthorPublicationDegree(graph):
    plt.close()
    authorDegree = list(graph.degree())
    authorPublication = list(graph.nodes(data='size'))

    authorDegree.sort(key=lambda tup: tup[0], reverse=True)
    authorPublication.sort(key=lambda tup: tup[0], reverse=True)

    # print(len(authorDegree))
    # print(len(authorReputation))

    data = []
    for i in range(len(authorDegree)):
        data.append((authorPublication[i][1], authorDegree[i][1]))

    data.sort(key=lambda tup: tup[0], reverse=True)

    # print(data)

    y_axis, x_axis = zip(*data)
    # ax = plt.gca()
    plt.scatter(y_axis, x_axis, c="r", s=1)
    plt.title("Author # Publications vs. Degree")
    plt.ylabel("# Publications")
    plt.xlabel("Degree")
    # ax.set(xscale="log")
    # ax.set(yscale="log")
    # plt.savefig("AuthorPublicationDegree.png")
    return plt

def GetConferenceInDegreeStrength(Graph):
    plt.close()
    d = {}
    for item in Graph.nodes.data():
        in_degree = Graph.in_degree(item[0], weight='weight')
        conftype = item[0][0:-4]
        if conftype not in d:
            d[conftype] = [in_degree, 1]
        else:
            d[conftype][0] += in_degree
            d[conftype][1] += 1

    data = []
    for k,v in d.items():
        data.append((k,v[0]))
    data.sort(key=lambda tup: tup[1], reverse=True)

    x_axis = [i[1] for i in data]
    y_axis = [i[0] for i in data]

    y_pos = np.arange(len(y_axis))

    plt.rcdefaults()
    fig, ax = plt.subplots()
    ax.barh(y_axis, x_axis, align='center')
    ax.set_yticks(y_pos)
    ax.set_yticklabels(y_axis)
    ax.invert_yaxis()  # labels read top-to-bottom
    ax.set_ylabel('Conference')
    ax.set_xlabel('in_degree')
    ax.set_title('Movement Between Conferences')

    # plt.savefig('ConferencesMovement1.png')

    return plt

def GetAuthorMaximumDegreeChange(graph):
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

def GetNetworkEffectOnReputation(graph, year1=1985, year2=2015):
    plt.close()
    subgraph = FilterAuthorNodes(graph,1975,year1)
    _, x1, y1 = GetAuthorReputationDistribution(subgraph, 1975,year1)
    _, x2, y2 = GetAuthorDegreeDistribution(subgraph)

    subgraph2 = FilterAuthorNodes(graph,1975,year2)
    _, x3, y3 = GetAuthorReputationDistribution(subgraph2, 1975,year2)
    _, x4, y4 = GetAuthorDegreeDistribution(subgraph2)

    #     print('''Degree of 1975-1985: {}, max: {}
    # Degree of 1975-2015: {}, max: {}
    # '''.format(max(x2), max(x1), max(x4), max(x3)))

    plt.figure()
    plt.title('Network Effect')

    plt.subplot(2, 2, 1)
    plt.yscale('log')
    plt.xscale('log')
    plt.scatter(x1, y1, c="r", s=5)
    plt.ylim((0.00001, 0.8))
    plt.xlim(0.9, 10**3)
    plt.ylabel('1975 - {}'.format(year1))
    plt.xlabel('Reputation')

    plt.subplot(2, 2, 2)
    plt.yscale('log')
    plt.xscale('log')
    plt.scatter(x2, y2, c="b", s=5)
    plt.ylim((0.00001, 0.8))
    plt.xlim(0.9, 10**2)
    plt.xlabel('Degree')

    plt.subplot(2, 2, 3)
    plt.yscale('log')
    plt.xscale('log')
    plt.scatter(x3, y3, c="r", s=5)
    plt.ylim((0.00001, 0.8))
    plt.xlim(0.9, 10**3)
    plt.ylabel('1975 - {}'.format(year2))
    plt.xlabel('Reputation')

    plt.subplot(2, 2, 4)
    plt.yscale('log')
    plt.xscale('log')
    plt.scatter(x4, y4, c="b", s=5)
    plt.ylim((0.00001, 0.8))
    plt.xlim(0.9, 10**2)
    plt.xlabel('Degree')

    # plt.savefig("test.png")

    return plt

def GetNetworkEffectOnSuccess(graph):
    plt.close()
    authorSuccess = list(graph.nodes(data='success'))
    authorSuccess.sort(key=lambda tup: tup[1], reverse=True)
    authorReputation = list(graph.nodes(data='reputation'))
    authorReputation.sort(key=lambda tup: tup[1], reverse=True)
    authorDegree = list(graph.degree())
    authorDegree.sort(key=lambda tup: tup[1], reverse=True)

    impact = []
    authorSuccess = authorSuccess[:20]
    authorReputation = authorReputation[:20]
    authorDegree = authorDegree[:20]
    for author1 in authorDegree:
        breaking = False
        for author2 in authorSuccess:
            if author1[0] == author2[0]:
                for author3 in authorReputation:
                    if author1[0] == author3[0]:
                        impact.append((author1[0],author1[1],author2[1], author3[1]))
                        breaking = True
                        break
            if breaking: break

    impact.sort(key=lambda tup: tup[1])
    # print(impact, len(impact))

    degree = list(map(lambda x: x[1], impact))
    success = list(map(lambda x: x[2], impact))
    reputation = list(map(lambda x: x[3], impact))
    authors = list(map(lambda x: x[0], impact))
    x = np.arange(len(authors))
    width = 0.2

    # normalization
    degree = [float(i)/max(degree) for i in degree]
    success = [float(i)/max(success) for i in success]
    reputation = [float(i)/max(reputation) for i in reputation]

    fig, ax = plt.subplots()
    ax.barh(x + width*2, degree, width, label='degree', color='#003f5c')
    ax.barh(x + width, success, width, label='success', color='#bc5090')
    ax.barh(x, reputation, width, label='reputation', color='#ffa600')
    ax.set(yticks=x + width, yticklabels=authors, ylim=[2*width - 1, len(authors)])
    ax.set_title('Authors with high Success, sorted by Degree')
    plt.tight_layout()
    ax.legend()
    # plt.savefig("test1.png")

    return plt


### ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ ###
###Question Based Functions
###
###
###########################################################################

def Q2_1():
    df = cfg.consolidated_df
    df["InstitutionRanks"] = "Unranked"

    tier_1_10 = df[(df["Institution Rank"] > 0) & (df["Institution Rank"] < 11)].index
    df.loc[tier_1_10, "InstitutionRanks"] = "001 - 010"

    tier_95_105 = df[(df["Institution Rank"] > 94) & (df["Institution Rank"] < 106)].index
    df.loc[tier_95_105, "InstitutionRanks"] = "095 - 104"

    tier_195_205 = df[(df["Institution Rank"] > 194) & (df["Institution Rank"] < 206)].index
    df.loc[tier_195_205, "InstitutionRanks"] = "105 - 204"

    tier_290_305 = df[(df["Institution Rank"] > 290) & (df["Institution Rank"] < 305)].index
    df.loc[tier_290_305, "InstitutionRanks"] = "295 - 304"

    tier_395_405 = df[(df["Institution Rank"] > 394) & (df["Institution Rank"] < 405)].index
    df.loc[tier_395_405, "InstitutionRanks"] = "395 - 404"

    tier_495_505 = df[(df["Institution Rank"] > 489) & (df["Institution Rank"] < 501)].index
    df.loc[tier_495_505, "InstitutionRanks"] = "490 - 500"

    df = df.groupby("InstitutionRanks").mean()[["Tier 1 Count"]]
    df.rename(columns = {"Tier 1 Count" : "Avg Tier 1 Publications Per Author"}, inplace = True)

    return df

def Q2_2():
    df = cfg.consolidated_df
    df = df.sort_values("Tier 1 Count", ascending = False)
    df["Root Institution"].fillna(df["Institution"], inplace = True)
    df.drop("Institution", axis = 1, inplace = True)
    df.rename(columns = {"Root Institution" : "Institution"}, inplace = True)

    df = df.head(30)[["Name", "Institution", "Institution Rank", "Tier 1 Count"]].reset_index(drop = True)
    df.index += 1

    return df

def Q4():
    df = cfg.consolidated_df

    df_count = df.groupby("Country").count()[["Name"]]
    df_count = df_count.rename(columns = {"Name" : "NumberOfAuthors"})

    temp = df.groupby("Country").mean()[["Success"]]
    temp = temp.rename(columns = {"Success" : "AvgSuccess"})

    temp2 = df.groupby("Country").sum()[["Success"]]
    temp2 = temp2.rename(columns = {"Success" : "TotalSuccess"})

    df_agg = pd.merge(temp, df_count, on = "Country")
    df_agg = pd.merge(df_agg, temp2, on = "Country")
    df_agg = df_agg.sort_values("AvgSuccess", ascending = False).reset_index()
    df_agg.index += 1

    return df_agg.head(20).round(3)

def Q6_retrieveInitialTier(author):
    X_CONFERENCES = 5 ##Denotes taking first/last X number of conferences to evaluate initial/final reputation of author
    FIRST_SLICE_INT = X_CONFERENCES
    LAST_SLICE_INT = X_CONFERENCES * -1 - 1

    if(author[1]["size"] < X_CONFERENCES*1):
        return

    ##Retrieve first / last X publications
    first = author[1]['publ'][0:FIRST_SLICE_INT:1]
    last = author[1]['publ'][-1:LAST_SLICE_INT:-1]

    initialTiers = sum(pub['tier'] for pub in first)
    finalTiers = sum(pub['tier'] for pub in last)

    data = {'Name' : author[0],
            ('initialRep' + "_" + str(X_CONFERENCES))  : X_CONFERENCES * 3 - initialTiers,
            ('FinalRep' + "_" + str(X_CONFERENCES)) : X_CONFERENCES * 3 - finalTiers,
            'Success' : author[1]['success'],
            'NumberOfPublications' : author[1]["size"],
            'Tier 1 Count' : author[1]["tier1cnt"],
            'Reputation' : author[1]["reputation"]
            }

    return data

def Q6():
    with open('json/authorNodes.json') as f:
        authorSet = json.load(f)

    qn6Parameters = []
    for author in authorSet:
        temp = Q6_retrieveInitialTier(author)
        if (temp):
            qn6Parameters.append(temp)

    df_Q6 = pd.DataFrame(qn6Parameters)

    df_Q6 = df_Q6[["Name", "initialRep_5", "Success", "NumberOfPublications", "Tier 1 Count"]]
    df_Q6.rename(columns = {"initialRep_5" : "initialRep(Max 10)"}, inplace = True)
    df_Q6 = df_Q6.sort_values("Success", ascending = False).reset_index(drop = True)
    df_Q6.index += 1

    return df_Q6.head(20)
