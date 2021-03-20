
import requests
import re
import json
from bs4 import BeautifulSoup

# regionData("US-WA-061")

def regionData(regionCode):
    regexParseCommaNumbers = r'(\d+,\d+,\d+,\d+|\d+,\d+,\d+|\d+,\d+|\d+)'
    BASE_URL = f"https://ebird.org/region/"

    allYearsURL = BASE_URL + regionCode + "?yr=all" + "&hs_sortBy=taxon_order&hs_o=asc"  # Consider adding option to sort by first seen: "&rank=lrec&hs_sortBy=date&hs_o=asc"
    currentYearURL = BASE_URL + regionCode + "?yr=cur"
    
    print("Retrieving URL: " + allYearsURL)
    r = requests.get(allYearsURL)
    #   r1 = requests.get(currentYearURL)
    print(r)

    soup = BeautifulSoup(r.text, 'html.parser')

    totalSpecies = int(soup.find("span", id="speciesStat").string) # Get species number and convert store as integer. 

    # Initialize below variables to null so that they don't recall old data when testing:
    regionHTML, regionSpecific, regionsTemp, regionSubregion, regionRegion, regionString, totalChecklists, totalEbirders, hotspots = (None,)*9

    # Parse out region variables: 
    regionHTML      = soup.find("div", class_="GridFlex-cell u-sizeFill")
    regionList = []
    regionList.append(regionHTML.find("span", class_="Heading-main").string)
    for region in (regionHTML.find_all("a", href=re.compile("/region/"))):
        regionList.append(region.string.strip())

    regionString = ""
    for region in regionList:
        regionString += region + ", "
    regionString = re.sub(", $", "", regionString)


    # Parse 'Complete Checklists' number
    recentVisitsTitle = soup.find_all(title=re.compile("Complete checklists", re.IGNORECASE), limit=1)[0]['title'] # Strips out the contents of the title string out of the tag above. 
    totalChecklists = int((re.findall(r'(\d+,\d+,\d+,\d+|\d+,\d+,\d+|\d+,\d+|\d+)', recentVisitsTitle))[0].replace(',',''))

    # Parse 'Total eBirders' number
    topEbirdersTitle = soup.find("a", title=re.compile("eBirders:"))['title']
    totalEbirders = int((re.findall(regexParseCommaNumbers, topEbirdersTitle))[0].replace(',',''))

    # Parse 'Hotspots' Number
    hotspotsTitle = soup.find("a", title=re.compile("Hotspots", re.IGNORECASE))['title']
    hotspots = int((re.findall(r'(\d+,\d+,\d+,\d+|\d+,\d+,\d+|\d+,\d+|\d+)', hotspotsTitle))[0].replace(',',''))

    # Parse out a list of species:  
    # speciesList = [] # Deprecated? 
    speciesNames = []
    speciesLinks = soup.find_all("a", href=re.compile("/species/"))
    
    for speciesLink in speciesLinks: 
        speciesNames.append(speciesLink.find("span", class_="Heading-main").string.strip())

    # Parse out a list of non-species (ex. 'Empidonax sp.')
    nonSpeciesHTML = soup.find_all("span", style="font-weight: normal;")

    nonSpeciesList = []
    nonSpeciesNames = []
    for nonSpecies in nonSpeciesHTML:
        nonSpeciesNames.append(nonSpecies.getText().strip())     


    # checklistLinks = soup.find_all("a", class_="Observation-meta-date-label", href=re.compile("/checklist/"))

    print("Total Checklists for " + regionString + ": " + str(totalChecklists))
    print("Total eBirders:", totalEbirders)
    print("Number of Hotspots:", hotspots)

  
    if(totalSpecies != len(speciesNames)):
        print(f"Warning: The number of species listed by the webpage ({totalSpecies}) does not match the number of species parsed from the species list ({len(speciesNames)})...")


    outputData = {
        'regionCode'        : regionCode,
        'regionString'      : regionString,
        'totalSpecies'      : totalSpecies,
        'totalChecklists'   : totalChecklists, 
        'totalEbirders'     : totalEbirders,
        'hotspots'          : hotspots,
        'speciesCount'      : len(speciesNames),
        'speciesNames'      : speciesNames,
        'nonSpeciesNames'   : nonSpeciesNames,
    }
    return outputData




