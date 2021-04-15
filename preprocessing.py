from os import listdir, path
from os.path import join
import xml
from xml.dom.minidom import parse
from xml.sax.handler import ContentHandler
from xml.sax import make_parser
import io
import csv
import re
import json
from operator import itemgetter


MAX_COAUTHORS = 1000

CONFERENCE_AUTHOR_JSON = "json/conferencesAndAuthors.json"
AUTHOR_JSON = "json/authors.json"
INPROCEEDS_JSON = "json/inproceeds.json"
DBLP_FILENAME = "dblp.xml"

FACULTY_INPROCEEDS_JSON = "json/facultyInproceeds.json"
FACULTY_AUTHOR_JSON = "json/facultyAuthors.json"
FACULTY_CONFERENCE_AUTHOR_JSON = "json/facultyConferencesAndAuthors.json"
FACULTY_FILENAME ="faculty.xml" 

conferenceTier = {"sigmod": 1, "vldb": 1, "pvldb": 1, "kdd": 1,
                     "edbt": 2, "icde": 2, "icdm": 2, "sdm": 2, "cikm": 2,
                     "dasfaa": 3, "pakdd": 3, "pkdd": 3, "dexa": 3}
conferencesName = {"sigmod": "international conference on management of data",
                   "vldb": "very large data bases conference",
                   "pvldb": "proceedings of the vldb endowment",
                   "kdd": "knowledge discovery and data mining",
                   "edbt": "international conference on extending database technology",
                   "icde": "ieee international conference on data engineering",
                   "icdm": "ieee international conference on data mining",
                   "sdm": "siam international conference on data mining",
                   "cikm": "international conference on information and knowledge management",
                   "dasfaa": "international conference on database systems for advanced applications",
                   "pakdd": "pacific-asia conference on knowledge discovery and knowledge discovery",
                   "pkdd": "european conference on principles of data mining and knowledge discovery",
                   "dexa": "international conference on database and expert systems application"}

publicationsType = ["article", "inproceedings", "proceedings"]

publicationKeys = ["author", "title", "year", "volume",
                   "booktitle", "journal", "crossref", "school"]

dataHeader = ["publtype", "conftype", "confName", "key", "tier", "title", "year",
              "booktitle", "volume", "journal",
              "crossref"]

dictionary = {}
conferences = {}
inproceeds = {}
authorsList = {}
authorsFilter = set()


def processFaculty():
    getCoAuthor()
    data = parse(FACULTY_FILENAME)
    authors = data.getElementsByTagName("faculty")[0].getElementsByTagName("dblpperson")

    for author in authors:
        name = author.getAttribute("name")
        conf_list = []
        rs = author.getElementsByTagName("r")
        for r in rs:
            
     
            c = {} 
            c["key"] = r.firstChild.getAttribute("key")
            c["conftype"] = c["key"].split('/')[1]
            c["year"] = r.firstChild.getElementsByTagName("year")[0].firstChild.data
            c["conf"] = c["conftype"] + c["year"]
            c["tier"] = conferenceTier[c["conftype"]] if c["conftype"] in conferenceTier else 3
            c["authors"] = [f.firstChild.data for f in r.firstChild.getElementsByTagName("author") if f.firstChild.data in authorsFilter] 
            conf_list.append(c)

            if c["conf"] in conferences:
                temp = set(conferences[c["conf"]]["authors"])
                temp.add(name)
                conferences[c["conf"]]["authors"] = list(temp)
            else:
                item = {}
                item["key"] = c["conf"]
                item["conftype"] = c["conftype"]
                item["year"] = c["year"]
                item["tier"] = c["tier"]
                item["authors"] = [name]

                conferences[c["conf"]] = item

            
            if c["key"] not in inproceeds:
                item = {}
                item["key"] = c["key"]
                item["conf"] = c["conf"]
                item["conftype"] = c["conftype"]
                item["year"] = c["year"]
                item["tier"] = c["tier"]
                item["authors"] = c["authors"]

                inproceeds[c["key"]] = item
            


        authorsList[name] = conf_list
                

    with open(CONFERENCE_AUTHOR_JSON, 'w+') as json_file:
        json.dump(conferences, json_file)

    with open(AUTHOR_JSON, 'w+') as json_file:
        json.dump(authorsList, json_file)

    with open(INPROCEEDS_JSON, 'w+') as json_file:
        json.dump(inproceeds, json_file)



def getCoAuthor():
    filenames = [f for f in listdir(join(path.abspath(path.dirname(__file__)) ,"faculty"))]
    for filename in filenames:
        if (len(authorsFilter) >= MAX_COAUTHORS): break

        datas = parse("faculty/" + filename)

        # coauthors = datas.getElementsByTagName("coauthors")[0].getElementsByTagName("co")
        # for coauthor in coauthors:
        #     authorsFilter.add(coauthor.firstChild.firstChild.data)

        faculty_author = datas.getElementsByTagName("dblpperson")[0].getAttribute("name")
        authorsFilter.add(faculty_author)

def PreprocessConferencesAuthors (dblpFileName, JSONList):
    getCoAuthor()
    parser = make_parser()
    parser.setFeature(xml.sax.handler.feature_namespaces, 0)
    Handler = DBLPHandler()
    parser.setContentHandler(Handler)
    print("PARSE1")
    parser.parse(io.open(dblpFileName))

    with open(JSONList[0], 'w+') as json_file:
        json.dump(conferences, json_file)

    with open(JSONList[1], 'w+') as json_file:
        json.dump(authorsList, json_file)

    with open(JSONList[2], 'w+') as json_file:
        json.dump(inproceeds, json_file)

    print("done parsing")
    return conferences


def CreateNetworks():
    conferenceInfo = ParseJSONtoDict("json/conferencesAndAuthors.json")
    authorInfo = ParseJSONtoDict("json/authors.json")
    inproceedsInfo = ParseJSONtoDict('json/inproceeds.json')
    print(len(conferenceInfo))
    print(len(authorInfo))
    print(len(inproceedsInfo))

    CreateConferenceNetwork(conferenceInfo)
    print('done conf')
    CreateAuthorNetwork(authorInfo, inproceedsInfo)
    print('done auth')


def CreateConferenceNetwork (conferenceInfo):
    conferenceNodes = []
    confNodeAttr = []
    confEdges = []
    for key, value in conferenceInfo.items():
        conferenceNodes.append((key, int(value['year']), value['conftype'],
                                int(value['tier']), len(value['authors'])))

    for key1 in conferenceNodes:
        conf1 = key1[0]
        conf1year = key1[1]
        if conf1[:-4] == 'pvldb':
            conf1 = 'vldb' + conf1[-4:]

        confNodeAttr.append((conf1, {'size': key1[4], 'tier': key1[3], 'year': key1[1],
                                     'authors': conferenceInfo[key1[0]]['authors']}))


        for key2 in conferenceNodes:
            conf2 = key2[0]
            conf2year = key2[1]
            if conf2[:-4] == 'pvldb':
                conf2 = 'vldb' + conf2[-4:]

            weight = 0
            if conf1 != conf2  and conf1year < conf2year:
                # can use set and intersect
                z = set(conferenceInfo[key1[0]]['authors']).intersection(set(conferenceInfo[key2[0]]['authors']))
                if key1[3] == 1:
                    weight = len(z) * 3
                elif key[3] == 2:
                    weight = len(z) * 2
                elif key[3] == 3:
                    weight = len(z) * 1
                confEdges.append((conf1, conf2, weight))

    SaveNodesEdgesinJSON(confNodeAttr, confEdges,'conference')



def CreateAuthorNetwork (authorsInfo, inproceedsInfo):
    authNodes = []
    authEdges = []

    for author, publications in authorsInfo.items():
        reputation = 0
        prevTier1Year = 2100
        tier1cnt = 0
        publications.sort(key=itemgetter('year'))
        prevPubl = None
        success = 0
        maxSuccess = 0
        for publ in publications:
            if publ['tier'] == 1:
                reputation += 3
            elif publ['tier'] == 2:
                reputation += 2
            elif publ['tier'] == 3:
                reputation += 1


            if publ['tier'] == 1:
                if prevPubl is not None:
                    if int(publ['year']) - prevTier1Year <= 1:
                        success += 1
                    elif int(publ['year']) - prevTier1Year > 1:
                        if success > maxSuccess:
                            maxSuccess = success
                        success = 0
                
                tier1cnt += 1
                prevPubl = publ
                prevTier1Year = int(publ['year'])

        if success > maxSuccess:
            maxSuccess = success
        authNodes.append((author, {'size': len(publications), 'success': maxSuccess, 'tier1cnt': tier1cnt,
                            'reputation': reputation,
                            'start': int(publications[0]['year']),
                            'end': int(publications[len(publications)-1]['year']),
                            'publ': publications}))

    for key, publ in inproceedsInfo.items():
        authors = publ['authors']
        authorcheck = set()
        for author1 in authors:
            authorcheck.add(author1)
            for author2 in authors:
                if author1 != author2 and author2 not in authorcheck:
                    authEdges.append((author1, author2, {'tier': int(publ['tier']), 'year':int(publ['year'])}))
            authorcheck.clear()

    SaveNodesEdgesinJSON(authNodes, authEdges,'author')


# Store data into JSON
def SaveNodesEdgesinJSON (nodes, edges, fileName):
    with open('json/'+fileName+'Nodes.json', 'w') as json_file:
        json.dump(nodes, json_file)

    with open('json/'+fileName+'Edges.json', 'w') as json_file:
        json.dump(edges, json_file)

# Get data from JSON
def ParseJSONtoDict (filename):
    # Read JSON data into the datastore variable
    if filename:
        with open(filename, 'r') as f:
            datastore = json.load(f)
    return datastore


def AddToConference (key, conftype, year, tier, publauthors):
    authors = publauthors.copy()
    if key not in conferences and year != "NULL" and int(year) >= 1975:
        conferences[key] = {'key': key, 'conftype': conftype, 'year': year, 'tier': tier, 'authors': authors}
    elif key in conferences:
        conferences[key]['authors'].extend(authors)


def AddToInproceeds (key, crossref, conftype, year, tier, publauthors):
    authors = publauthors.copy()
    if key not in inproceeds:
        inproceeds[key] = {'key': key, 'conf':crossref, 'conftype':conftype, 'year':year, 'tier':tier, 'authors':authors}
        for author in authors:
            if author not in authorsList:
                authorsList[author] = [inproceeds[key]]
            else:
                authorsList[author].append(inproceeds[key])



def AddToData (publicationData, confType, publicationAuthors):
    conftype = confType
    tier = publicationData["tier"]
    year = publicationData["year"]
    confname = conferencesName[confType] + " " + year
    crossref = publicationData["crossref"].lower()
    key = publicationData["key"].lower()
    conferencekey = publicationData["conftype"] + publicationData["year"]
    writeBool = False

    if publicationData["publtype"] == "inproceedings":
        if re.search("^conf/[a-z]+/[0-9]{2,4}(-[1-3])?$", crossref):
            writeBool = True
    elif publicationData["publtype"] == "article":
        if re.search("^journals/pvldb/[a-zA-Z0-9]+$", key):
            writeBool = True

    if writeBool:
        publicationData.update({"confName": confname})
        AddToInproceeds(key, conferencekey, conftype, year, tier, publicationAuthors)
        AddToConference(conferencekey, conftype, year, tier, publicationAuthors)


class DBLPHandler(ContentHandler):
    # variables used to check publications
    currentTypeOfConf = ""
    currentPublicationType = ""
    currentTag = ""
    fullContent = ""
    listOfContent = ""
    isPublication = False

    # publication content, use for temporary storage per publication
    currPublicationAuthors = []
    currPublicationData = {"publtype": "NULL", "conftype": "NULL", "confName": "NULL", "key": "NULL", "tier": "NULL",
                           "title": "NULL", "year": "NULL",
                           "booktitle": "NULL", "volume": "NULL", "journal": "NULL",
                           "crossref": "NULL"}

    def __init__ (self):
        super().__init__()
        self.authorsFilter = authorsFilter

    # Call when an element starts
    def startElement (self, tag, attrs):
        if tag == "dblp":
            return
        if tag in publicationsType:
            self.isPublication = True

            self.currentPublicationType = tag

            if "key" in attrs:
                value = attrs.get("key")
                valueArray = value.split('/')
                self.currentTypeOfConf = valueArray[1].lower()
                if self.currentTypeOfConf in conferencesName:
                    self.currPublicationData.update({"tier": conferenceTier[self.currentTypeOfConf]})
                self.currPublicationData.update({"key": value})
                self.currPublicationData.update({"publtype": tag})
                self.currPublicationData.update({"conftype": valueArray[1].lower()})

        # if inside a publication
        elif self.isPublication:
            self.currentTag = tag

    # Call when a character is read
    def characters (self, content):
        if self.isPublication and self.currentTypeOfConf in conferencesName and self.currentTag in publicationKeys:
            self.listOfContent += content

    # Call when ending tag found </example>
    def endElement (self, tag):
        if self.listOfContent != "":
            self.fullContent = self.listOfContent.strip().replace("\n", "")

        if self.isPublication and self.currentTypeOfConf in conferencesName and tag in publicationKeys:
            if tag == "author" :
                self.currPublicationAuthors.append(self.fullContent)
            else:
                self.currPublicationData.update({tag: self.fullContent})

        self.fullContent = ""
        self.listOfContent = ""

        # end of publication, i.e. found </proceedings>
        if tag == self.currentPublicationType:
            if self.currentTypeOfConf in conferencesName:
                if self.currentPublicationType == "inproceedings" or self.currentPublicationType == "article":
                    AddToData(self.currPublicationData, self.currentTypeOfConf, self.currPublicationAuthors)
            self.resetTemporaryVariables()

    # reset variables after every end of publication
    def resetTemporaryVariables (self):
        self.currPublicationAuthors = []
        self.currPublicationData = {"publtype": "NULL", "confName": "NULL", "key": "NULL", "tier": "NULL",
                                    "title": "NULL", "year": "NULL",
                                    "booktitle": "NULL", "volume": "NULL", "journal": "NULL",
                                    "crossref": "NULL"}
        self.isPublication = False
        self.currentTypeOfConf = ""






if __name__ == "__main__":
    # SCSE member only
    processFaculty()

    # 1000 co-authors
    # PreprocessConferencesAuthors (DBLP_FILENAME, [CONFERENCE_AUTHOR_JSON, AUTHOR_JSON, INPROCEEDS_JSON])
    
    CreateNetworks()