import preprocessing as ps
import Faculty as sc
import gui
import json

conferenceAuthorJSON = "json/ScseStaff.json"
#authorJSON = "json/authors.json"
#inproceedsJSON = 'json/inproceeds.json'
#dblpFilename = "dblp.xml"
#listOfJSON = [conferenceAuthorJSON, authorJSON, inproceedsJSON]


def main ():
    # uncomment line below to preprocess dblp.xml again
    # ps.PreprocessConferencesAuthors(dblpFilename, listOfJSON)
    # uncomment line below to create new nodes and edges
    # ps.CreateNetworks()

    # inititalize networks class to create networkx graphs
    networks = sc.Networks()
    gui.openGUI()

if __name__ == "__main__":
    main()
