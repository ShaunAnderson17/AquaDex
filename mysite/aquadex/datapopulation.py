from tempfile import NamedTemporaryFile
from django.core.files import File
import requests
from .models import Species, EndangeredStatus, ConservationMeasures,Images
import time 
from selenium import webdriver
from selenium.webdriver.common.by import By  
import os
from bs4 import BeautifulSoup
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.action_chains import ActionChains
from django.core.exceptions import ValidationError
from selenium.common.exceptions import TimeoutException, NoSuchElementException

def PopulateSpeciesData(speciesData):
    try:
        for species in speciesData:
            name = species.get('name', '')
            taxonomy = species.get('taxonomy', {})
            characteristics = species.get('characteristics', {})
            locations = species.get('locations', [])

            speciesQuerySet = Species.objects.filter(name=name)

            if speciesQuerySet.exists():
                speciesQuerySet.update(
                    taxonomy = taxonomy,
                    characteristics = characteristics,
                    locations = locations
                )
            else:
                 Species.objects.create(
                     name=name,
                     taxonomy=taxonomy,
                     characteristics=characteristics,
                     locations=locations
                 )
                 print(f"Created data for {name}")
    except Exception as e:
        print(f"Error populating species data: {e}")

def FetchSpeciesData():
    speciesList = ["Pelican", "Chinstrap Penguin", "African Penguin", "Puffin", "Adelie Penguin", "Crested Penguin", "Emperor Penguin",
                  "Galapagos Penguin", "Gentoo Penguin", "Humboldt Penguin", "King Penguin", "Little Penguin", "Macaroni Penguin", 
                  "Magellanic Penguin", "Penguin", "Rockhopper Penguin", "Royal Penguin", "Yellow-Eyed Penguin", "Basking Shark", "Blue Shark",
                  "Bonnethead Shark", "Bull Shark", "Cookiecutter Shark", "Frilled Shark", "Goblin Shark", "Great White Shark", "Greenland Shark",
                  "Grey Reef Shark", "Hammerhead Shark", "Horn Shark", "Megamouth Shark", "Nurse Shark", "Porbeagle Shark", "Reef Shark", 
                  "Salmon Shark", "Sand Tiger Shark", "Shark", "Sixgill shark", "Sleeper Shark", "Spinner Shark", "Tiger Shark", "Viper shark (dogfish)", 
                  "Whale Shark", "Zebra Shark", "Manta Ray", "Moray Eel", "Stingray", "Leatherback Sea Turtle", "Sea Turtle", "Marine Iguana", "Sea Lion", 
                  "Crabeater Seal", "Elephant Seal", "Fur Seal", "Grey Seal", "Harbor Seal", "Harp Seal", "Hawaiian Monk Seal", "Hooded Seal", "Leopard Seal", 
                  "Northern Fur Seal", "Seal", "Cuttlefish", "Blanket Octopus", "Blue-Ringed Octopus", "Octopus", "Colossal Squid", "Humboldt Squid", "Squid", 
                  "Vampire Squid", "Amazon River Dolphin (Pink Dolphin)", "Bottlenose Dolphin", "Dolphin", "Dusky Dolphin", "Mahi Mahi (Dolphin Fish)", "Porpoise", 
                  "Baleen Whale", "Blue Whale", "Bowhead Whale", "False Killer Whale", "Fin Whale", "Humpback Whale", "Killer Whale", "Minke Whale", "Sei Whale", 
                  "Sperm Whale", "Angelfish", "Anglerfish", "Barramundi Fish", "Barracuda", "Blobfish", "Bonito Fish", "Boxfish", "Butterfly Fish", "Clownfish", 
                  "Cobia Fish", "Codfish", "Dragonfish", "Drum Fish", "Fluke Fish (summer flounder)", "Flying Fish", "Football Fish", "Frogfish", 
                  "Hagfish", "Hardhead Catfish", "Immortal Jellyfish", "Jellyfish", "Lion’s Mane Jellyfish", "Lionfish", "Lizardfish", "Lumpfish", "Man of War Jellyfish", 
                  "Milkfish", "Mola mola (Ocean Sunfish)", "Monkfish", "Moon Jellyfish", "Needlefish", "Oyster Toadfish", "Parrotfish", "Pipefish", "Pufferfish", 
                  "Red-Lipped Batfish", "Rockfish", "Sawfish", "Scorpion Fish", "Skate Fish", "Spiny Dogfish", "Squirrelfish", "Starfish", "Stargazer Fish", 
                  "Surgeonfish", "Telescope Fish", "Toadfish", "Wahoo Fish", "Wolffish", "Albacore Tuna", "Bluefin Tuna", "Skipjack Tuna", "Tuna", "Yellowfin Tuna", 
                  "Black Marlin", "Banana Eel", "Conger Eel", "Eel", "Electric Eel", "Fire Eel", "Garden Eel", "Ribbon Eel", "Wolf Eel", "Walrus", "Wrasse", 
                  "Sea Dragon", "Seahorse", "Tarpon", "Grouper", "Christmas Island Red Crab", "Crab", "Fiddler Crab", "Ghost Crab", "Hermit Crab", "Horseshoe Crab",
                  "Jonah Crab", "King Crab", "Rock Crab", "Sand Crab", "Snow Crab", "Stone Crab", "Yeti Crab", "Lobster", "Manatee", "Sea Urchin", "Sea Anemone", "Coelacanth", 
                  "Dugong", "Krill", "Shrimp", "Narwhal", "Polar Bear", "Sea Otter", "Vaquita", ]
    
    headers = {'X-Api-Key': os.environ.get('animalsAPIKey')}
    speciesData = []
    for speciesName in speciesList: 
        apiUrl = f'https://api.api-ninjas.com/v1/animals?name={speciesName}'
        response = requests.get(apiUrl, headers=headers)
        if response.status_code == 200:
            data = response.json()
            PopulateSpeciesData(data)
            speciesData.append({'speciesName': speciesName})
        else:
            print(f"Failed to fetch data for {speciesName}: {response.status_code}")
    return speciesData 
             
def Login(driver, email, password):
    driver.get('https://www.iucnredlist.org/users/sign_in')   
    WebDriverWait(driver, 20).until(EC.visibility_of_element_located((By.ID, 'user_email')))
    WebDriverWait(driver, 20).until(EC.visibility_of_element_located((By.ID, 'user_password')))
     
    driver.find_element(By.ID, 'user_email').send_keys(email)
    driver.find_element(By.ID, 'user_password').send_keys(password)
     
    driver.find_element(By.XPATH, '//input[@value="Log in"]').click()
     
    WebDriverWait(driver, 20).until(EC.presence_of_element_located((By.XPATH, '//a[contains(text(), "Log out")]')))


def SpeciesEndangeredStatusScraper():
    speciesList = ["Pelecanus crispus          ",
                   "Pygoscelis antarcticus     ",
                   "Spheniscus demersus        ",
                   "Fratercula arctica         ",
                   "Pygoscelis adeliae         ",
                   "Eudyptes robustus          ",
                   "Aptenodytes forsteri       ",
                   "Spheniscus Mendiculus      ",
                   "Pygoscelis papua           ",
                   "Spheniscus humboldti       ",
                   "Aptenodytes patagonicus    ",
                   "Eudyptula Minor            ",
                   "Eudyptes Chrysolophus      ",
                   "Spheniscus magellanicus    ",
                   "Eudyptes chrysocome        ",
                   "Eudyptes schlegeli         ",
                   "Megadyptes antipodes       ",
                   "Cetorhinus Maximus         ",
                   "Prionace glauca            ",
                   "Sphyrna tiburo             ",
                   "Carcharhinus Leucas        ",
                   "Isistius brasiliensis      ",
                   "Chlamydoselachus anguineus ",
                   "Mitsukurina owstoni        ",
                   "Carcharodon carcharias     ",
                   "Somniosus microcephalus    ",
                   "Carcharhinus Amblyrhynchos ", 
                   "Heterodontus francisci     ",
                   "Megachasma pelagios        ",
                   "Ginglymostoma cirratum     ",
                   "Lamna nasus                ",
                   "Carcharhinus perezi        ",
                   "Lamna ditropis             ",
                   "Carcharias taurus          ",
                   "Hexanchus griseus          ",
                   "Carcharhinus brevipinna    ",
                   "Galeocerdo Cuvier          ",
                   "Trigonognathus kabeyai     ",
                   "Stegostoma Fasciatum       ",
                   "Manta alfredi              ",
                   "Dermochelys coriacea       ",
                   "Amblyrhynchus cristatus    ", 
                   "Lobodon carcinophaga       ",
                   "Mirounga                   ",
                   "Halichoerus Grypus         ",
                   "Phoca vitulina             ",
                   "Pagophilus groenlandicus   ",
                   "Neomonachus schauinslandi  ",
                   "Cystophora cristata        ",
                   "Hydrurga Leptonyx          ",
                   "Callorhinus ursinus        ", 
                   "Tremoctopus                ",
                   "Hapalochlaena              ",
                   "Octopus Vulgaris           ",
                   "Mesonychoteuthis hamiltoni ",
                   "Dosidicus gigas            ",  
                   "Tursiops Truncatus         ", 
                   "Lagenorhynchus obscurus    ",
                   "Coryphaena hippurus        ", 
                   "Balaenoptera musculus      ",
                   "Balaena mysticetus         ",
                   "Pseudorca crassidens       ",
                   "Balaenoptera Physalus      ",
                   "Megaptera novaeangliae     ",
                   "Orcinus orca               ",
                   "Balaenoptera acutorostrata ",
                   "Balaenoptera borealis      ",
                   "Physeter macrocephalus     ",
                   "Melanocetus johnsonii      ",
                   "Lates calcarifer           ",
                   "Sphyraena                  ",
                   "Sarda sarda                ",
                   "Ostracion cubicus          ", 
                   "Rachycentron canadum       ",
                   "Gadus morhua               ", 
                   "Paralichthys dentatus      ", 
                   "Himantolophus sagamius     ", 
                   "Ariopsis felis             ",  
                   "Pterois volitans           ",  
                   "Chanos chanos              ",   
                   "Mola mola                  ",
                   "Lophius piscatorius        ", 
                   "Platybelone argalus        ",
                   "Opsanus tau                ",
                   "Scaridae                   ",  
                   "Pristis pristis            ", 
                   "Dipturus batis             ",
                   "Squalus acanthias          ",
                   "Holocentrus adscensionis   ", 
                   "Uranoscopus scaber         ", 
                   "Gigantura chuni            ",
                   "Tetractenos hamiltoni      ", 
                   "Thunnus alalunga           ",
                   "Thunnus thynnus            ",
                   "Katsuwonus pelamis         ",
                   "Thunnus albacares          ",
                   "Istiompax Indica           ",
                   "Gymnothorax funebris       ",
                   "Conger Conger              ", 
                   "Electrophorus Electricus   ",
                   "Mastacembelus erythrotaenia",
                   "Heteroconger hassi         ",
                   "Anarrhichthys ocellatus    ",
                   "Odobenus rosmarus          ", 
                   "Phycodurus eques           ",
                   "Hippocampus                ",
                   "Megalops                   ", 
                   "Brachyura                  ",
                   "Uca                        ",
                   "Limulus polyphemus         ",  
                   "Homarus americanus         ",   
                   "Dugong dugon               ",
                   "Euphausia superba          ",
                   "Monodon monoceros          ",
                   "Ursus maritimus            ",
                   "Enhydra lutris             ",
                   "Phocoena sinus             ", 
                   "Sula nebouxii              ",   
                   "Dendrogyra cylindrus       ",
                   "Heliopora coerulea         ", 
                   "Acropora cervicornis       ",
                   "Acanthocybium solandri     ",   
                   "Amphiprion ocellaris       ",   
                   "Epinephelus itajara        ", 
                   "Gymnothorax miliaris       ",     
                   "Thalassoma bifasciatum     ",     
                   "Himantura uarnak           ",
                   "Eumetopias jubatus         ",   
                   "Sciaenops ocellatus        ", 
                   "Malacosteus niger          ",    
                    ]
    driver = webdriver.Chrome() 
    Login(driver, os.environ.get('IUCNEMAIL'), os.environ.get('IUCNPASSWORD'))   

    for species in speciesList:
        url = f'https://www.iucnredlist.org/search?query={species}&searchType=species'
        driver.get(url) 
        WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.CLASS_NAME, "species-category")))
         
        soup = BeautifulSoup(driver.page_source, 'html.parser') 
        endangeredStatus = soup.find('a', {'class': 'species-category'}).get('title')
        scientificName = species
         
        status = EndangeredStatus(status=endangeredStatus, name=scientificName)
        status.save()
         
        time.sleep(5)

    driver.quit()

def SpeciesConMeaScraper():
    speciesList = ["Pelecanus crispus          ",
                   "Pygoscelis antarcticus     ",
                   "Spheniscus demersus        ",
                   "Fratercula arctica         ",
                   "Pygoscelis adeliae         ",
                   "Eudyptes robustus          ",
                   "Aptenodytes forsteri       ",
                   "Spheniscus Mendiculus      ",
                   "Pygoscelis papua           ",
                   "Spheniscus humboldti       ",
                   "Aptenodytes patagonicus    ",
                   "Eudyptula Minor            ",
                   "Eudyptes Chrysolophus      ",
                   "Spheniscus magellanicus    ",
                   "Eudyptes chrysocome        ",
                   "Eudyptes schlegeli         ",
                   "Megadyptes antipodes       ",
                   "Cetorhinus Maximus         ",
                   "Prionace glauca            ",
                   "Sphyrna tiburo             ",
                   "Carcharhinus Leucas        ",
                   "Isistius brasiliensis      ",
                   "Chlamydoselachus anguineus ",
                   "Mitsukurina owstoni        ",
                   "Carcharodon carcharias     ",
                   "Somniosus microcephalus    ",
                   "Carcharhinus Amblyrhynchos ", 
                   "Heterodontus francisci     ",
                   "Megachasma pelagios        ",
                   "Ginglymostoma cirratum     ",
                   "Lamna nasus                ",
                   "Carcharhinus perezi        ",
                   "Lamna ditropis             ",
                   "Carcharias taurus          ",
                   "Hexanchus griseus          ",
                   "Carcharhinus brevipinna    ",
                   "Galeocerdo Cuvier          ",
                   "Trigonognathus kabeyai     ",
                   "Stegostoma Fasciatum       ",
                   "Manta alfredi              ",
                   "Dermochelys coriacea       ",
                   "Amblyrhynchus cristatus    ", 
                   "Lobodon carcinophaga       ",
                   "Mirounga                   ",
                   "Halichoerus Grypus         ",
                   "Phoca vitulina             ",
                   "Pagophilus groenlandicus   ",
                   "Neomonachus schauinslandi  ",
                   "Cystophora cristata        ",
                   "Hydrurga Leptonyx          ",
                   "Callorhinus ursinus        ", 
                   "Tremoctopus                ",
                   "Hapalochlaena              ",
                   "Octopus Vulgaris           ",
                   "Mesonychoteuthis hamiltoni ",
                   "Dosidicus gigas            ",  
                   "Tursiops Truncatus         ", 
                   "Lagenorhynchus obscurus    ",
                   "Coryphaena hippurus        ", 
                   "Balaenoptera musculus      ",
                   "Balaena mysticetus         ",
                   "Pseudorca crassidens       ",
                   "Balaenoptera Physalus      ",
                   "Megaptera novaeangliae     ",
                   "Orcinus orca               ",
                   "Balaenoptera acutorostrata ",
                   "Balaenoptera borealis      ",
                   "Physeter macrocephalus     ",
                   "Melanocetus johnsonii      ",
                   "Lates calcarifer           ",
                   "Sphyraena                  ",
                   "Sarda sarda                ",
                   "Ostracion cubicus          ", 
                   "Rachycentron canadum       ",
                   "Gadus morhua               ", 
                   "Paralichthys dentatus      ", 
                   "Himantolophus sagamius     ", 
                   "Ariopsis felis             ",  
                   "Pterois volitans           ",  
                   "Chanos chanos              ",   
                   "Mola mola                  ",
                   "Lophius piscatorius        ", 
                   "Platybelone argalus        ",
                   "Opsanus tau                ",
                   "Scaridae                   ",  
                   "Pristis pristis            ", 
                   "Dipturus batis             ",
                   "Squalus acanthias          ",
                   "Holocentrus adscensionis   ", 
                   "Uranoscopus scaber         ", 
                   "Gigantura chuni            ",
                   "Tetractenos hamiltoni      ", 
                   "Thunnus alalunga           ",
                   "Thunnus thynnus            ",
                   "Katsuwonus pelamis         ",
                   "Thunnus albacares          ",
                   "Istiompax Indica           ",
                   "Gymnothorax funebris       ",
                   "Conger Conger              ", 
                   "Electrophorus Electricus   ",
                   "Mastacembelus erythrotaenia",
                   "Heteroconger hassi         ",
                   "Anarrhichthys ocellatus    ",
                   "Odobenus rosmarus          ", 
                   "Phycodurus eques           ",
                   "Hippocampus                ",
                   "Megalops                   ", 
                   "Brachyura                  ",
                   "Uca                        ",
                   "Limulus polyphemus         ",  
                   "Homarus americanus         ",   
                   "Dugong dugon               ",
                   "Euphausia superba          ",
                   "Monodon monoceros          ",
                   "Ursus maritimus            ",
                   "Enhydra lutris             ",
                   "Phocoena sinus             ", 
                   "Sula nebouxii              ",   
                   "Dendrogyra cylindrus       ",
                   "Heliopora coerulea         ", 
                   "Acropora cervicornis       ",
                   "Acanthocybium solandri     ",   
                   "Amphiprion ocellaris       ",   
                   "Epinephelus itajara        ", 
                   "Gymnothorax miliaris       ",     
                   "Thalassoma bifasciatum     ",     
                   "Himantura uarnak           ",
                   "Eumetopias jubatus         ",   
                   "Sciaenops ocellatus        ", 
                   "Malacosteus niger          ",    
                    ]
    driver = webdriver.Chrome() 
    Login(driver, os.environ.get('IUCNEMAIL'), os.environ.get('IUCNPASSWORD'))   

    for species in speciesList:
        url = 'https://www.iucnredlist.org/search'
        driver.get(url)
        
        try:
            print(f"Processing species: {species}")
            
            searchField = WebDriverWait(driver, 15).until(
                EC.visibility_of_element_located((By.CSS_SELECTOR, '.search.search--site'))
            )
            searchField.clear()
            searchField.send_keys(species)
            print(f"Entered species: {species}")
            
            searchButton = driver.find_element(By.CSS_SELECTOR, '.search--site__button.search-form-button')
            ActionChains(driver).move_to_element(searchButton).click(searchButton).perform()
            print(f"Clicked search button for species: {species}")
            
            searchResults = WebDriverWait(driver, 15).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, '.cards.cards--narrow'))
            )
            print(f"Search results loaded for species: {species}")
            
            firstResult = WebDriverWait(driver, 15).until(
                EC.element_to_be_clickable((By.CSS_SELECTOR, '.cards.cards--narrow .card.card--column.card--shadowed.card--3n'))
            )
            ActionChains(driver).move_to_element(firstResult).click(firstResult).perform()
            print(f"Clicked first result for species: {species}")
            
            WebDriverWait(driver, 15).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, '#conservation-actions'))
            )
            print(f"Details page loaded for species: {species}")
            
            conMea = "No conservation measures found"
            conMeaList = []
             
            time.sleep(5)
             
            isPresent = driver.execute_script("return document.querySelector('#conservation-action-details .text-body') !== null;")
            if isPresent:
                print("Conservation actions element found in DOM.")
            else:
                print("Conservation actions element NOT found in DOM.")
             
            conservationSection = driver.find_element(By.CSS_SELECTOR, '#conservation-action-details')
            html_content = conservationSection.get_attribute('innerHTML')
            print("Conservation Actions HTML:\n", html_content)
             
            soup = BeautifulSoup(html_content, 'html.parser')
            conservationActions = soup.find_all(class_='text-body')
            
            for action in conservationActions:
                action_text = action.get_text(separator=' ', strip=True)
                if action_text:
                    conMeaList.append(action_text)
                    print(f"Found text: {action_text}")
        
            if conMeaList:
                conMea = " ".join(conMeaList)
            else:
                print(f"No text found in conservation measures for {species}")
                conMea = "No conservation measures found"
             
            measures = ConservationMeasures(measures=conMea, name=species)
            try:
                measures.full_clean()
            except ValidationError as e:
                print(f"Validation error while saving data for {species}: {e}")
            else:
                measures.save()
                print(f"Data saved for species: {species}")
            
            time.sleep(5)
        except (TimeoutException, NoSuchElementException) as e:
            print(f"Error processing {species}: {e}")
            print(f"Current URL: {driver.current_url}")
        
    driver.quit()


def DownloadImage(imageUrl, speciesName):          
    response = requests.get(imageUrl, stream=True)
    if response.status_code == 200:
        imgTemp = NamedTemporaryFile(delete=True)
        imgTemp.write(response.content)
        imgTemp.flush()
        if not Images.objects.filter(name=speciesName).exists():
            imgObj = Images(name=speciesName)
            imgObj.img.save(f"{speciesName}.jpg", File(imgTemp))
            imgObj.save()
            print(f"Successfully downloaded image for {speciesName}") 

def SpeciesImageScraper():
    speciesList = ["Pelecanus crispus",
                   "Pygoscelis antarcticus",
                   "Spheniscus demersus",
                   "Fratercula arctica",
                   "Pygoscelis adeliae",
                   "Eudyptes robustus",
                   "Aptenodytes forsteri",
                   "Spheniscus Mendiculus",
                   "Pygoscelis papua",
                   "Spheniscus humboldti",
                   "Aptenodytes patagonicus",
                   "Eudyptula Minor",
                   "Eudyptes Chrysolophus",
                   "Spheniscus magellanicus",
                   "Eudyptes chrysocome",
                   "Eudyptes schlegeli",
                   "Megadyptes antipodes",
                   "Cetorhinus Maximus",
                   "Prionace glauca",
                   "Sphyrna tiburo",
                   "Carcharhinus Leucas",
                   "Isistius brasiliensis",
                   "Chlamydoselachus anguineus",
                   "Mitsukurina owstoni",
                   "Carcharodon carcharias",
                   "Somniosus microcephalus",
                   "Carcharhinus Amblyrhynchos", 
                   "Heterodontus francisci",
                   "Megachasma pelagios",
                   "Ginglymostoma cirratum",
                   "Lamna nasus",
                   "Carcharhinus perezi",
                   "Lamna ditropis",
                   "Carcharias taurus",
                   "Hexanchus griseus",
                   "Carcharhinus brevipinna",
                   "Galeocerdo Cuvier",
                   "Trigonognathus kabeyai",
                   "Stegostoma Fasciatum",
                   "Manta alfredi",
                   "Dermochelys coriacea",
                   "Amblyrhynchus cristatus", 
                   "Lobodon carcinophaga",
                   "Mirounga",
                   "Halichoerus Grypus",
                   "Phoca vitulina",
                   "Pagophilus groenlandicus",
                   "Neomonachus schauinslandi",
                   "Cystophora cristata",
                   "Hydrurga Leptonyx",
                   "Callorhinus ursinus", 
                   "Tremoctopus",
                   "Hapalochlaena",
                   "Octopus Vulgaris",
                   "Mesonychoteuthis hamiltoni",
                   "Dosidicus gigas",  
                   "Tursiops Truncatus", 
                   "Lagenorhynchus obscurus",
                   "Coryphaena hippurus", 
                   "Balaenoptera musculus",
                   "Balaena mysticetus",
                   "Pseudorca crassidens",
                   "Balaenoptera Physalus",
                   "Megaptera novaeangliae",
                   "Orcinus orca",
                   "Balaenoptera acutorostrata",
                   "Balaenoptera borealis",
                   "Physeter macrocephalus",
                   "Melanocetus johnsonii",
                   "Lates calcarifer",
                   "Sphyraena",
                   "Sarda sarda",
                   "Ostracion cubicus", 
                   "Rachycentron canadum",
                   "Gadus morhua", 
                   "Paralichthys dentatus", 
                   "Himantolophus sagamius", 
                   "Ariopsis felis",  
                   "Pterois volitans",  
                   "Chanos chanos",   
                   "Mola mola",
                   "Lophius piscatorius", 
                   "Platybelone argalus",
                   "Opsanus tau",
                   "Scaridae",  
                   "Pristis pristis", 
                   "Dipturus batis",
                   "Squalus acanthias",
                   "Holocentrus adscensionis", 
                   "Uranoscopus scaber", 
                   "Gigantura chuni",
                   "Tetractenos hamiltoni", 
                   "Thunnus alalunga",
                   "Thunnus thynnus",
                   "Katsuwonus pelamis",
                   "Thunnus albacares",
                   "Istiompax Indica",
                   "Gymnothorax funebris",
                   "Conger Conger", 
                   "Electrophorus Electricus",
                   "Mastacembelus erythrotaenia",
                   "Heteroconger hassi",
                   "Anarrhichthys ocellatus",
                   "Odobenus rosmarus", 
                   "Phycodurus eques",
                   "Hippocampus",
                   "Megalops", 
                   "Brachyura",
                   "Uca",
                   "Limulus polyphemus",  
                   "Homarus americanus",   
                   "Dugong dugon",
                   "Euphausia superba",
                   "Monodon monoceros",
                   "Ursus maritimus",
                   "Enhydra lutris",
                   "Phocoena sinus", 
                   "Sula nebouxii",   
                   "Dendrogyra cylindrus",
                   "Heliopora coerulea", 
                   "Acropora cervicornis",
                   "Acanthocybium solandri",   
                   "Amphiprion ocellaris",   
                   "Epinephelus itajara", 
                   "Gymnothorax miliaris",     
                   "Thalassoma bifasciatum",     
                   "Himantura uarnak",
                   "Eumetopias jubatus",   
                   "Sciaenops ocellatus", 
                   "Malacosteus niger",]  
    driver = webdriver.Chrome()

    for species in speciesList:
        query = species.replace(" ", "%20")  
        url = f'https://www.iucnredlist.org/search?query={query}&searchType=species'
        driver.get(url)
         
        WebDriverWait(driver, 15).until(EC.presence_of_element_located((By.CLASS_NAME, 'card__thumbnail--search')))
        imgTags = driver.find_elements(By.CLASS_NAME, 'card__thumbnail--search')
        
        for img in imgTags:
            imgUrl = img.get_attribute('src')
            if 'new_thumb' in imgUrl:  
                try:  
                    DownloadImage(imgUrl, species)
                except Exception as e:
                    print(f"Error downloading image for {species}: {str(e)}")
        
        time.sleep(5)
    
    driver.quit()
