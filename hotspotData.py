import requests
import re
import json
from bs4 import BeautifulSoup

def hotspotData(hotspotCode, yr="all"):
    
    if(yr == "cur"):
        print("Getting hotspot data for current year...")
        yearString = "?yr=cur"
    elif(yr == "all"):
        print("Getting hotspot data for all years...")
        yearString = "?yr=all"    
    else:
        print("Requested 'yr' variable " + yr + "is not supported by this function...")
        return None # Need to research and improve this. 
    
    BASE_URL = f"https://ebird.org/hotspot/"
    hotspotURL = BASE_URL + hotspotCode + yearString

    print("Retrieving URL: " + hotspotURL)
    r = requests.get(hotspotURL)

    if(r.status_code != 200): # Check to see if eBird gave you some valid data.
        print("Error: Response " + str(r.status_code))
        return None # Need to research and improve this. 

    # All good? Let's parse some data!
    soup = BeautifulSoup(r.text, 'html.parser')

    # The code to retrieve species, location data, etc. is similar/identical between regions and hotspots. Consider either merging the functions or making a seperate function to parse this data for both regionData and hotspotData functions.     
    totalSpecies = int(soup.find("span", id="speciesStat").string) # Get species number and convert store as integer. 

    # Initialize below variables to null so that they don't recall old data when testing:
    hotspotHTML, hotspotSpecific, hotspotsTemp, hotspotSubhotspot, hotspothotspot, hotspotString, totalChecklists, totalEbirders, hotspots = (None,)*9

    # Parse out hotspot variables: 
    hotspotHTML      = soup.find("div", class_="GridFlex-cell u-sizeFill")
    hotspotList = []
    hotspotList.append(hotspotHTML.find("span", class_="Heading-main").string)
    for hotspot in (hotspotHTML.find_all("a", href=re.compile("/region/"))):
        hotspotList.append(hotspot.string.strip())

    hotspotString = ""
    for hotspot in hotspotList:
        hotspotString += hotspot + ", "
    hotspotString = re.sub(", $", "", hotspotString)

    # Parse 'Complete Checklists' number
    recentVisitsTitle = soup.find_all(title=re.compile("Complete checklists", re.IGNORECASE), limit=1)[0]['title'] # Strips out the contents of the title string out of the tag above. 
    totalChecklists = int((re.findall(r'(\d+,\d+,\d+,\d+|\d+,\d+,\d+|\d+,\d+|\d+)', recentVisitsTitle))[0].replace(',',''))

    # Total eBirders is not data displayed for hotspot

    # Hotspots is not data applicable to a hotspot, obviously. 

    # Parse out a list of species:  
    speciesList = []
    speciesNames = []
    speciesLinks = soup.find_all("a", href=re.compile("/species/"))
  
    for speciesLink in speciesLinks: 
        speciesNames.append(speciesLink.getText().strip()) #getText seems superior to .string? 

    # Parse out a list of non-species (ex. 'Empidonax sp.')
    nonSpeciesHTML = soup.find_all("span", style="font-weight: normal;")

    nonSpeciesList = []
    nonSpeciesNames = []
    for nonSpecies in nonSpeciesHTML:
        nonSpeciesNames.append(nonSpecies.getText().strip()) 
    

    if(totalSpecies != len(speciesNames)):
        print(f"Warning: The number of species listed by the webpage ({totalSpecies}) does not match the number of species parsed from the species list ({len(speciesNames)})...")

    outputData = {
        'hotspotCode'       : hotspotCode,
        'hotspotString'     : hotspotString,
        'totalSpecies'      : totalSpecies,
        'totalChecklists'   : totalChecklists,
        'speciesCount'      : len(speciesNames),
        'speciesNames'      : speciesNames,
        'nonSpeciesNames'   : nonSpeciesNames,
    }
    return outputData


