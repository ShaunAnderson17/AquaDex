from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout  
from django.http import JsonResponse
from .forms import CreateUserForm, CustomPasswordChangeForm
from .datapopulation import SpeciesEndangeredStatusScraper, SpeciesImageScraper, FetchSpeciesData, SpeciesConMeaScraper
from .models import Species, Images, EndangeredStatus,ConservationMeasures
from django.db.models import Q
from .utils import GenerateHeatMap
from django.template.loader import render_to_string
from django.contrib.sites.shortcuts import get_current_site
from django.contrib.auth import get_user_model
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.utils.encoding import force_bytes, force_str
from django.core.mail import EmailMessage
from .tokens import accountActivationToken
from django.contrib.auth import update_session_auth_hash
from django.contrib.auth.forms import SetPasswordForm
import os   
import time
 
from django.shortcuts import render
from .models import Species, Images

def Home(request):
    sortOrder = request.GET.get('sort', 'asc')
    if sortOrder == 'asc':
        speciesList = Species.objects.all().order_by('taxonomy__scientific_name')
        nextSortOrder = 'desc'
    else:
        speciesList = Species.objects.all().order_by('-taxonomy__scientific_name')
        nextSortOrder = 'asc'
    
    status_classes = {
        'Critically Endangered': 'ce',
        'Data Deficient': 'dd',
        'Endangered': 'en',
        'Least Concern': 'lc',
        'Near Threatened': 'nt',
        'Vulnerable': 'vu'
    }

    status_labels = {
        'Critically Endangered': 'CE',
        'Data Deficient': 'DD',
        'Endangered': 'EN',
        'Least Concern': 'LC',
        'Near Threatened': 'NT',
        'Vulnerable': 'VU'
    }

    speciesImages = []

    for species in speciesList:
        scientificName = species.taxonomy.get('scientific_name')
        commonName = species.name   

        try:
            status = EndangeredStatus.objects.get(name=scientificName)
            endangeredStatus = status.status
            status_class = status_classes.get(endangeredStatus, 'Unknown')
            status_label = status_labels.get(endangeredStatus, 'Unknown')
        except EndangeredStatus.DoesNotExist:
            endangeredStatus = 'Unknown'
            status_class = 'Unknown'
            status_label = 'Unknown'
            status_label = 'Unknown'

        if scientificName:
            image = Images.objects.filter(name=scientificName).first()
        else:
            image = None

        habitat_list = species.characteristics.get('habitat', '').split(',') if species.characteristics.get('habitat') else []

        speciesImages.append({
            'id': species.id,
            'common_name': commonName,
            'scientific_name': scientificName if scientificName else 'Unknown',
            'image': image,
            'endangeredStatus': endangeredStatus,
            'status_class': status_class,
            'status_label': status_label,
            'habitat_list': habitat_list,
        })

    return render(request, 'aquadex/home.html', {'speciesImages': speciesImages, 'sortOrder': sortOrder, 'nextSortOrder': nextSortOrder})

 
def Browse(request):
    return render(request, 'aquadex/browse.html')
 
def BrowseBySpecies(request): 
    return render(request, 'aquadex/browsebyspecies.html')

def FishAndSharks(request):
    fishNSharks = [
        "Cetorhinus Maximus","Prionace glauca", "Sphyrna tiburo", "Carcharhinus Leucas", "Isistius brasiliensis", "Chlamydoselachus anguineus", "Mitsukurina owstoni", 
        "Carcharodon carcharias", "Somniosus microcephalus", "Carcharhinus Amblyrhynchos", "Sphyrnidae", "Heterodontus francisci", "Megachasma pelagios", "Ginglymostoma cirratum", 
        "Lamna nasus", "Carcharhinus perezii", "Lamna ditropis", "Carcharias taurus", "Selachimorpha", "Hexanchus griseus", "Somniosidae", "Carcharhinus brevipinna", 
        "Galeocerdo Cuvier", "Trigonognathus kabeyai", "Rhincodon Typus", "Stegostoma Fasciatum", "Coryphaena hippurus", "Pterophyllum", 
        "Lophiiformes", "Lates calcarifer", "Sphyraena", "Psychrolutes marcidus", "Sarda", "Ostracion cubicus", "Chaetodontidae", "Amphiprioninae", 
        "Rachycentron canadum", "Gadus morhua", "Stomiidae", "Sciaenidae", "Paralichthys dentatus", "Exocoetidae", "Himantolophidae", "Antennariidae", 
        "Myxini", "Ariopsis felis", "Pterois volitans", "Synodus lucioceps", "Cyclopterus lumpus", 
        "Chanos chanos", "Mola mola", "Lophius", "Platybelone argalus", "Opsanus tau", "scaridae", "Syngnathinae", "Tetraodontidae", 
        "Ogcocephalus darwini", "Sebastes", "Pristidae", "Scorpaenidae", "Rajidae", "Squalus acanthias", "Holocentrus adscensionis", "Asteroidea", "Uranoscopus scaber", 
        "Acanthuridae", "Gigantura", "Tetractenos hamiltoni", "Acanthocybium solandri", "Wolffish", "Anarhichadidae", "Thunnus thynnus", "Katsuwonus pelamis", "Thunnini", 
        "Thunnus albacares", "Istiompax Indica", "Megalops", "Epinephelinae", "Labridae", "Coelacanthiformes", 
        ] 
    speciesList = Species.objects.filter(taxonomy__scientific_name__in=fishNSharks)

    status_classes = {
        'Critically Endangered': 'ce',
        'Data Deficient': 'dd',
        'Endangered': 'en',
        'Least Concern': 'lc',
        'Near Threatened': 'nt',
        'Vulnerable': 'vu'
    }

    status_labels = {
        'Critically Endangered': 'CE',
        'Data Deficient': 'DD',
        'Endangered': 'EN',
        'Least Concern': 'LC',
        'Near Threatened': 'NT',
        'Vulnerable': 'VU'
    }
    speciesImages = []

    for species in speciesList:
        scientificName = species.taxonomy.get('scientific_name')
        commonName = species.name   

        try:
            status = EndangeredStatus.objects.get(name=scientificName)
            endangeredStatus = status.status
            status_class = status_classes.get(endangeredStatus, 'Unknown')
            status_label = status_labels.get(endangeredStatus, 'Unknown')
        except EndangeredStatus.DoesNotExist:
            endangeredStatus = 'Unknown'
            status_class = 'Unknown'
            status_label = 'Unknown'
            status_label = 'Unknown'

        if scientificName:
            image = Images.objects.filter(name=scientificName).first()
        else:
            image = None

        speciesImages.append({
            'id': species.id,
            'common_name': commonName,
            'scientific_name': scientificName if scientificName else 'Unknown',
            'image': image,
            'status_class': status_class,
            'status_label': status_label,
        })

    return render(request, 'aquadex/fishnsharks.html', {'speciesImages': speciesImages})

def DolphinsAndPorpoises(request):
    dolphinsNPorpoises = [
        "Coryphaena hippurus", "Platanistoidea", "Tursiops Truncatus", "Delphinidae", "Lagenorhynchus obscurus", "Phocoenidae", "Phocoena sinus",
        ] 
    speciesList = Species.objects.filter(taxonomy__scientific_name__in=dolphinsNPorpoises)
    status_classes = {
        'Critically Endangered': 'ce',
        'Data Deficient': 'dd',
        'Endangered': 'en',
        'Least Concern': 'lc',
        'Near Threatened': 'nt',
        'Vulnerable': 'vu'
    }

    status_labels = {
        'Critically Endangered': 'CE',
        'Data Deficient': 'DD',
        'Endangered': 'EN',
        'Least Concern': 'LC',
        'Near Threatened': 'NT',
        'Vulnerable': 'VU'
    }
    speciesImages = []

    for species in speciesList:
        scientificName = species.taxonomy.get('scientific_name')
        commonName = species.name   

        try:
            status = EndangeredStatus.objects.get(name=scientificName)
            endangeredStatus = status.status
            status_class = status_classes.get(endangeredStatus, 'Unknown')
            status_label = status_labels.get(endangeredStatus, 'Unknown')
        except EndangeredStatus.DoesNotExist:
            endangeredStatus = 'Unknown'
            status_class = 'Unknown'
            status_label = 'Unknown'
            status_label = 'Unknown'

        if scientificName:
            image = Images.objects.filter(name=scientificName).first()
        else:
            image = None

        speciesImages.append({
            'id': species.id,
            'common_name': commonName,
            'scientific_name': scientificName if scientificName else 'Unknown',
            'image': image,
            'status_class': status_class,
            'status_label': status_label,
        })
    return render(request, 'aquadex/dolphinsnporpoises.html', {'speciesImages': speciesImages})

def SealsAndSeaLions(request):
    sealsNSeaLions = [
        "Otariidae", "Lobodon carcinophaga", "Mirounga", "Arctocephalinae", "Halichoerus Grypus", "Phoca vitulina", "Pagophilus groenlandicus", 
        "Neomonachus schauinslandi", "Cystophora cristata", "Hydrurga Leptonyx", "Callorhinus ursinus", "Phoca vitulina",
        ]  
    speciesList = Species.objects.filter(taxonomy__scientific_name__in=sealsNSeaLions) 
    status_classes = {
        'Critically Endangered': 'ce',
        'Data Deficient': 'dd',
        'Endangered': 'en',
        'Least Concern': 'lc',
        'Near Threatened': 'nt',
        'Vulnerable': 'vu'
    }

    status_labels = {
        'Critically Endangered': 'CE',
        'Data Deficient': 'DD',
        'Endangered': 'EN',
        'Least Concern': 'LC',
        'Near Threatened': 'NT',
        'Vulnerable': 'VU'
    }
    speciesImages = []

    for species in speciesList:
        scientificName = species.taxonomy.get('scientific_name')
        commonName = species.name   

        try:
            status = EndangeredStatus.objects.get(name=scientificName)
            endangeredStatus = status.status
            status_class = status_classes.get(endangeredStatus, 'Unknown')
            status_label = status_labels.get(endangeredStatus, 'Unknown')
        except EndangeredStatus.DoesNotExist:
            endangeredStatus = 'Unknown'
            status_class = 'Unknown'
            status_label = 'Unknown'
            status_label = 'Unknown'

        if scientificName:
            image = Images.objects.filter(name=scientificName).first()
        else:
            image = None

        speciesImages.append({
            'id': species.id,
            'common_name': commonName,
            'scientific_name': scientificName if scientificName else 'Unknown',
            'image': image,
            'status_class': status_class,
            'status_label': status_label,
        })
    return render(request, 'aquadex/sealsnsealions.html', {'speciesImages': speciesImages})

def ViewAllSpecies(request):
    speciesList = Species.objects.all()
    status_classes = {
        'Critically Endangered': 'ce',
        'Data Deficient': 'dd',
        'Endangered': 'en',
        'Least Concern': 'lc',
        'Near Threatened': 'nt',
        'Vulnerable': 'vu'
    }

    status_labels = {
        'Critically Endangered': 'CE',
        'Data Deficient': 'DD',
        'Endangered': 'EN',
        'Least Concern': 'LC',
        'Near Threatened': 'NT',
        'Vulnerable': 'VU'
    }
    speciesImages = []

    for species in speciesList:
        scientificName = species.taxonomy.get('scientific_name')
        commonName = species.name   

        try:
            status = EndangeredStatus.objects.get(name=scientificName)
            endangeredStatus = status.status
            status_class = status_classes.get(endangeredStatus, 'Unknown')
            status_label = status_labels.get(endangeredStatus, 'Unknown')
        except EndangeredStatus.DoesNotExist:
            endangeredStatus = 'Unknown'
            status_class = 'Unknown'
            status_label = 'Unknown'
            status_label = 'Unknown'

        if scientificName:
            image = Images.objects.filter(name=scientificName).first()
        else:
            image = None

        speciesImages.append({
            'id': species.id,
            'common_name': commonName,
            'scientific_name': scientificName if scientificName else 'Unknown',
            'image': image,
            'status_class': status_class,
            'status_label': status_label,
        })
    return render(request, 'aquadex/viewallspecies.html', {'speciesImages': speciesImages})

def Whales(request):
    whales = [
        "Mysticeti", "Balsenoptera musculus", "Balaena mysticetus", "Pseudorca crassidens", "Balaenoptera Physalus", "Megaptera novaeangliae",
        "Orcinus orca", "Balaenoptera acutorostrata", "Balaenoptera borealis", "Physeter macrocephalus", "Monodon monoceros",
        ]
    speciesList = Species.objects.filter(taxonomy__scientific_name__in=whales)
    status_classes = {
        'Critically Endangered': 'ce',
        'Data Deficient': 'dd',
        'Endangered': 'en',
        'Least Concern': 'lc',
        'Near Threatened': 'nt',
        'Vulnerable': 'vu'
    }

    status_labels = {
        'Critically Endangered': 'CE',
        'Data Deficient': 'DD',
        'Endangered': 'EN',
        'Least Concern': 'LC',
        'Near Threatened': 'NT',
        'Vulnerable': 'VU'
    }
    speciesImages = []

    for species in speciesList:
        scientificName = species.taxonomy.get('scientific_name')
        commonName = species.name   

        try:
            status = EndangeredStatus.objects.get(name=scientificName)
            endangeredStatus = status.status
            status_class = status_classes.get(endangeredStatus, 'Unknown')
            status_label = status_labels.get(endangeredStatus, 'Unknown')
        except EndangeredStatus.DoesNotExist:
            endangeredStatus = 'Unknown'
            status_class = 'Unknown'
            status_label = 'Unknown'
            status_label = 'Unknown'

        if scientificName:
            image = Images.objects.filter(name=scientificName).first()
        else:
            image = None

        speciesImages.append({
            'id': species.id,
            'common_name': commonName,
            'scientific_name': scientificName if scientificName else 'Unknown',
            'image': image,
            'status_class': status_class,
            'status_label': status_label,
        })
    return render(request, 'aquadex/whales.html', {'speciesImages': speciesImages})

def SeaTurtles(request):
     seaTurtles = ["Dermochelys Coriacea", ]
     speciesList = Species.objects.filter(taxonomy__scientific_name__in=seaTurtles)
     status_classes = {
        'Critically Endangered': 'ce',
        'Data Deficient': 'dd',
        'Endangered': 'en',
        'Least Concern': 'lc',
        'Near Threatened': 'nt',
        'Vulnerable': 'vu'
    } 
     status_labels = {
        'Critically Endangered': 'CE',
        'Data Deficient': 'DD',
        'Endangered': 'EN',
        'Least Concern': 'LC',
        'Near Threatened': 'NT',
        'Vulnerable': 'VU'
    }
     speciesImages = []

     for species in speciesList:
        scientificName = species.taxonomy.get('scientific_name')
        commonName = species.name   

        try:
            status = EndangeredStatus.objects.get(name=scientificName)
            endangeredStatus = status.status
            status_class = status_classes.get(endangeredStatus, 'Unknown')
            status_label = status_labels.get(endangeredStatus, 'Unknown')
        except EndangeredStatus.DoesNotExist:
            endangeredStatus = 'Unknown'
            status_class = 'Unknown'
            status_label = 'Unknown'
            status_label = 'Unknown'

        if scientificName:
            image = Images.objects.filter(name=scientificName).first()
        else:
            image = None

        speciesImages.append({
            'id': species.id,
            'common_name': commonName,
            'scientific_name': scientificName if scientificName else 'Unknown',
            'image': image,
            'status_class': status_class,
            'status_label': status_label,
        })
     return render(request, 'aquadex/seaturtles.html', {'speciesImages': speciesImages})

def Coral(request):
     coral = ["Dendrogyra cylindricus", "Heliopora coerulea", "Acropora cervicornis", ]
     speciesList = Species.objects.filter(taxonomy__scientific_name__in=coral)
     status_classes = {
        'Critically Endangered': 'ce',
        'Data Deficient': 'dd',
        'Endangered': 'en',
        'Least Concern': 'lc',
        'Near Threatened': 'nt',
        'Vulnerable': 'vu'
    }

     status_labels = {
        'Critically Endangered': 'CE',
        'Data Deficient': 'DD',
        'Endangered': 'EN',
        'Least Concern': 'LC',
        'Near Threatened': 'NT',
        'Vulnerable': 'VU'
    }
     speciesImages = []

     for species in speciesList:
        scientificName = species.taxonomy.get('scientific_name')
        commonName = species.name   

        try:
            status = EndangeredStatus.objects.get(name=scientificName)
            endangeredStatus = status.status
            status_class = status_classes.get(endangeredStatus, 'Unknown')
            status_label = status_labels.get(endangeredStatus, 'Unknown')
        except EndangeredStatus.DoesNotExist:
            endangeredStatus = 'Unknown'
            status_class = 'Unknown'
            status_label = 'Unknown'
            status_label = 'Unknown'

        if scientificName:
            image = Images.objects.filter(name=scientificName).first()
        else:
            image = None

        speciesImages.append({
            'id': species.id,
            'common_name': commonName,
            'scientific_name': scientificName if scientificName else 'Unknown',
            'image': image,
            'status_class': status_class,
            'status_label': status_label,
        })
     return render(request, 'aquadex/coral.html', {'speciesImages': speciesImages})

def SeaBirbs(request):
     seaBirbs = [
         "Sula nebouxii", "Pelecanus", "Pygoscelis Antarcticus", "Spheniscus demersus", "Fratercula arctica", "Pygoscelis adeliae", "Eudyptes robustus",
         "Aptenodytes forsteri", "Spheniscus Mendiculus", "Pygoscelis papua", "Spheniscus humboldti", "Aptenodytes patagonicus", "Eudyptula Minor", 
         "Eudyptes Chrysolophus", "Spheniscus magellanicus", "Aptenodytes Forsteri", "Eudyptes chrysocome", "Eudyptes schlegeli", "Megadyptes antipodes",
        ]
     speciesList = Species.objects.filter(taxonomy__scientific_name__in=seaBirbs)
     status_classes = {
        'Critically Endangered': 'ce',
        'Data Deficient': 'dd',
        'Endangered': 'en',
        'Least Concern': 'lc',
        'Near Threatened': 'nt',
        'Vulnerable': 'vu'
    }

     status_labels = {
        'Critically Endangered': 'CE',
        'Data Deficient': 'DD',
        'Endangered': 'EN',
        'Least Concern': 'LC',
        'Near Threatened': 'NT',
        'Vulnerable': 'VU'
    }
     speciesImages = []

     for species in speciesList:
        scientificName = species.taxonomy.get('scientific_name')
        commonName = species.name   

        try:
            status = EndangeredStatus.objects.get(name=scientificName)
            endangeredStatus = status.status
            status_class = status_classes.get(endangeredStatus, 'Unknown')
            status_label = status_labels.get(endangeredStatus, 'Unknown')
        except EndangeredStatus.DoesNotExist:
            endangeredStatus = 'Unknown'
            status_class = 'Unknown'
            status_label = 'Unknown'
            status_label = 'Unknown'

        if scientificName:
            image = Images.objects.filter(name=scientificName).first()
        else:
            image = None

        speciesImages.append({
            'id': species.id,
            'common_name': commonName,
            'scientific_name': scientificName if scientificName else 'Unknown',
            'image': image,
            'status_class': status_class,
            'status_label': status_label,
        })
     return render(request, 'aquadex/seabirds.html', {'speciesImages': speciesImages})

def Invertebrates(request):
     inverts = [
         "Sepiida", "Tremoctopus", "Hapalochlaena", "Octopus Vulgaris", "Mesonychoteuthis hamiltoni", "Dosidicus gigas", "Teuthida",
         "Vampyroteuthis infernalis", "Turritopsis dohrnii", "Scyphozoa", "Cyanea capillata", "Aurelia aurita", "Asteroidea", 
         "Echinoidea", "Actiniaria", "Euphausiacea", "Caridea", "Janthina janthina", "Glaucus-atlanticus", "Amphinomidae",
         "Dendrogyra cylindrus", "Heliopora coerulea", "Acropora cervicornis",
        ]
     speciesList = Species.objects.filter(taxonomy__scientific_name__in=inverts)
     status_classes = {
        'Critically Endangered': 'ce',
        'Data Deficient': 'dd',
        'Endangered': 'en',
        'Least Concern': 'lc',
        'Near Threatened': 'nt',
        'Vulnerable': 'vu'
    }

     status_labels = {
        'Critically Endangered': 'CE',
        'Data Deficient': 'DD',
        'Endangered': 'EN',
        'Least Concern': 'LC',
        'Near Threatened': 'NT',
        'Vulnerable': 'VU'
    }
     speciesImages = []

     for species in speciesList:
        scientificName = species.taxonomy.get('scientific_name')
        commonName = species.name   

        try:
            status = EndangeredStatus.objects.get(name=scientificName)
            endangeredStatus = status.status
            status_class = status_classes.get(endangeredStatus, 'Unknown')
            status_label = status_labels.get(endangeredStatus, 'Unknown')
        except EndangeredStatus.DoesNotExist:
            endangeredStatus = 'Unknown'
            status_class = 'Unknown'
            status_label = 'Unknown'
            status_label = 'Unknown'

        if scientificName:
            image = Images.objects.filter(name=scientificName).first()
        else:
            image = None

        speciesImages.append({
            'id': species.id,
            'common_name': commonName,
            'scientific_name': scientificName if scientificName else 'Unknown',
            'image': image,
            'status_class': status_class,
            'status_label': status_label,
        })
     return render(request, 'aquadex/invertebrates.html', {'speciesImages': speciesImages})

def HighlyMigratorySpecies(request):
     highlyMigratory = [
         "Cetorhinus maximus", "Prionace glauca", "Carcharodon carcharias", "Rhincodon typus", "Stegostoma fasciatum", "Dermochelys coriacea", "Mirounga",
         "Pagophilus groenlandicus", "Spheniscus Mendiculus", "Monachus schauinslandi", "Cystophora cristata", "Callorhinus ursinus", "Delphinidae", 
         "Mysticeti", "Balaenoptera musculus", "Balaena mysticetus", "Balaenoptera physalus", "Megaptera novaeangliae", "Orcinus orca", "Balaenoptera acutorostrata",
         "Balaenoptera borealis", "Physeter macrocephalus", "Gadus morhua", "Exocoetidae", "Thunnus alalunga", "Thunnus thynnus", "Katsuwonus pelamis",
         "Thunnini", "Thunnus albacares", "Istiompax indica", "Trichechus", "Monodon monoceros", "Ursus maritimus", "Sula nebouxii", "Glaucus atlanticus",
        ]
     speciesList = Species.objects.filter(taxonomy__scientific_name__in=highlyMigratory)
     status_classes = {
        'Critically Endangered': 'ce',
        'Data Deficient': 'dd',
        'Endangered': 'en',
        'Least Concern': 'lc',
        'Near Threatened': 'nt',
        'Vulnerable': 'vu'
    }

     status_labels = {
        'Critically Endangered': 'CE',
        'Data Deficient': 'DD',
        'Endangered': 'EN',
        'Least Concern': 'LC',
        'Near Threatened': 'NT',
        'Vulnerable': 'VU'
    }
     speciesImages = []

     for species in speciesList:
        scientificName = species.taxonomy.get('scientific_name')
        commonName = species.name   

        try:
            status = EndangeredStatus.objects.get(name=scientificName)
            endangeredStatus = status.status
            status_class = status_classes.get(endangeredStatus, 'Unknown')
            status_label = status_labels.get(endangeredStatus, 'Unknown')
        except EndangeredStatus.DoesNotExist:
            endangeredStatus = 'Unknown'
            status_class = 'Unknown'
            status_label = 'Unknown'
            status_label = 'Unknown'

        if scientificName:
            image = Images.objects.filter(name=scientificName).first()
        else:
            image = None

        speciesImages.append({
            'id': species.id,
            'common_name': commonName,
            'scientific_name': scientificName if scientificName else 'Unknown',
            'image': image,
            'status_class': status_class,
            'status_label': status_label,
        })
     return render(request, 'aquadex/highlymigratoryspecies.html', {'speciesImages': speciesImages})

def BrowseByRegion(request):
    return render(request, 'aquadex/browsebyregion.html')

def Alaska(request):
     alaska = [
         "Fratercula arctica", "Somniosus microcephalus", "Lamna ditropis", "Callorhinus ursinus", "Phoca vitulina", "Pagophilus groenlandicus", "Cystophora cristata",
         "Mirounga", "Halichoerus Grypus", "Balaenoptera acutorostrata", "Balaena mysticetus", "Orcinus orca", "Balsenoptera musculus", 
         "Balaenoptera Physalus", "Megaptera novaeangliae", "Balaenoptera borealis", "Coryphaena hippurus", "Gadus morhua", "Aptenodytes forsteri", "Sula nebouxii",
         "Enhydra Lutris", "Ursus maritimus", "Monodon monoceros", "Euphausiacea", "Cancer borealis", "C. opilio", "Labridae", 
        ]
     speciesList = Species.objects.filter(taxonomy__scientific_name__in=alaska)
     status_classes = {
        'Critically Endangered': 'ce',
        'Data Deficient': 'dd',
        'Endangered': 'en',
        'Least Concern': 'lc',
        'Near Threatened': 'nt',
        'Vulnerable': 'vu'
    }

     status_labels = {
        'Critically Endangered': 'CE',
        'Data Deficient': 'DD',
        'Endangered': 'EN',
        'Least Concern': 'LC',
        'Near Threatened': 'NT',
        'Vulnerable': 'VU'
    }
     speciesImages = []

     for species in speciesList:
        scientificName = species.taxonomy.get('scientific_name')
        commonName = species.name   

        try:
            status = EndangeredStatus.objects.get(name=scientificName)
            endangeredStatus = status.status
            status_class = status_classes.get(endangeredStatus, 'Unknown')
            status_label = status_labels.get(endangeredStatus, 'Unknown')
        except EndangeredStatus.DoesNotExist:
            endangeredStatus = 'Unknown'
            status_class = 'Unknown'
            status_label = 'Unknown'
            status_label = 'Unknown'

        if scientificName:
            image = Images.objects.filter(name=scientificName).first()
        else:
            image = None

        speciesImages.append({
            'id': species.id,
            'common_name': commonName,
            'scientific_name': scientificName if scientificName else 'Unknown',
            'image': image,
            'status_class': status_class,
            'status_label': status_label,
        })
     return render(request, 'aquadex/alaska.html', {'speciesImages': speciesImages})

def SouthEast(request):
     southEast = [
         "Pelecanus", "Sphyrna tiburo", "Carcharhinus Leucas", "Carcharodon carcharias", "Ginglymostoma cirratum", "Galeocerdo Cuvier", "Rhincodon Typus",
         "Muraenidae", "Myliobatoidei", "Dermochelys coriacea", "Chelonioidea", "Coryphaena hippurus", "Tursiops Truncatus", 
         "Delphinidae", "Phocoenidae", "Paralichthys dentatus", "Ariopsis felis", "Opsanus tau", "Scorpaenidae", "Menippe mercenaria",
         "Trichechus", "Uca", "Ocypodinae",  
         ]
     speciesList = Species.objects.filter(taxonomy__scientific_name__in=southEast)
     status_classes = {
        'Critically Endangered': 'ce',
        'Data Deficient': 'dd',
        'Endangered': 'en',
        'Least Concern': 'lc',
        'Near Threatened': 'nt',
        'Vulnerable': 'vu'
    }

     status_labels = {
        'Critically Endangered': 'CE',
        'Data Deficient': 'DD',
        'Endangered': 'EN',
        'Least Concern': 'LC',
        'Near Threatened': 'NT',
        'Vulnerable': 'VU'
    }
     speciesImages = []

     for species in speciesList:
        scientificName = species.taxonomy.get('scientific_name')
        commonName = species.name   

        try:
            status = EndangeredStatus.objects.get(name=scientificName)
            endangeredStatus = status.status
            status_class = status_classes.get(endangeredStatus, 'Unknown')
            status_label = status_labels.get(endangeredStatus, 'Unknown')
        except EndangeredStatus.DoesNotExist:
            endangeredStatus = 'Unknown'
            status_class = 'Unknown'
            status_label = 'Unknown'
            status_label = 'Unknown'

        if scientificName:
            image = Images.objects.filter(name=scientificName).first()
        else:
            image = None

        speciesImages.append({
            'id': species.id,
            'common_name': commonName,
            'scientific_name': scientificName if scientificName else 'Unknown',
            'image': image,
            'status_class': status_class,
            'status_label': status_label,
        })
     return render(request, 'aquadex/southeast.html', {'speciesImages': speciesImages})

def NewEnglandMidAtlantic(request):
     midAtlantic = [
         "Pelecanus", "Fratercula arctica", "Cetorhinus Maximus", "Prionace glauca", "Sphyrna tiburo", "Carcharodon carcharias", "Halichoerus Grypus",
         "Phoca vitulina", "Pagophilus groenlandicus", "Mysticeti", "Balsenoptera musculus", "Balaenoptera physalus", "Megaptera novaeangliae", 
         "Orcinus orca", "Balaenoptera acutorostrata", "Balaenoptera borealis", "Physeter macrocephalus", "Gadus morhua", "Paralichthys dentatus", "Opsanus tau",
         "Squalus acanthias", "Cancer borealis", "Cancer productus",
         ]
     speciesList = Species.objects.filter(taxonomy__scientific_name__in=midAtlantic)
     status_classes = {
        'Critically Endangered': 'ce',
        'Data Deficient': 'dd',
        'Endangered': 'en',
        'Least Concern': 'lc',
        'Near Threatened': 'nt',
        'Vulnerable': 'vu'
    }

     status_labels = {
        'Critically Endangered': 'CE',
        'Data Deficient': 'DD',
        'Endangered': 'EN',
        'Least Concern': 'LC',
        'Near Threatened': 'NT',
        'Vulnerable': 'VU'
    }
     speciesImages = []

     for species in speciesList:
        scientificName = species.taxonomy.get('scientific_name')
        commonName = species.name   

        try:
            status = EndangeredStatus.objects.get(name=scientificName)
            endangeredStatus = status.status
            status_class = status_classes.get(endangeredStatus, 'Unknown')
            status_label = status_labels.get(endangeredStatus, 'Unknown')
        except EndangeredStatus.DoesNotExist:
            endangeredStatus = 'Unknown'
            status_class = 'Unknown'
            status_label = 'Unknown'
            status_label = 'Unknown'

        if scientificName:
            image = Images.objects.filter(name=scientificName).first()
        else:
            image = None

        speciesImages.append({
            'id': species.id,
            'common_name': commonName,
            'scientific_name': scientificName if scientificName else 'Unknown',
            'image': image,
            'status_class': status_class,
            'status_label': status_label,
        })
     return render(request, 'aquadex/newenglandmidatlantic.html', {'speciesImages': speciesImages})

def WestCoast(request):
     westCoast = [
         "Pelecanus", "Carcharodon carcharias", "Lamna ditropis", "Heterodontus francisci", "Hexanchus griseus", "Galeocerdo Cuvier", "Rhincodon Typus",
         "Dermochelys coriacea", "Mirounga", "Phoca vitulina", "Neomonachus schauinslandi", "Callorhinus ursinus", "Tursiops Truncatus", 
         "Delphinidae", "Balsenoptera musculus", "Balaenoptera Physalus", "Megaptera novaeangliae", "Orcinus orca", "Balaenoptera acutorostrata", "Balaenoptera borealis",
         "Physeter macrocephalus", "Enhydra Lutris", "Phocoena sinus", "Sula nebouxii", "Cancer borealis", "Emerita analoga", "Enhydra lutris", "Mola mola", 
         "Sebastes",
         ]
     speciesList = Species.objects.filter(taxonomy__scientific_name__in=westCoast)
     status_classes = {
        'Critically Endangered': 'ce',
        'Data Deficient': 'dd',
        'Endangered': 'en',
        'Least Concern': 'lc',
        'Near Threatened': 'nt',
        'Vulnerable': 'vu'
    }

     status_labels = {
        'Critically Endangered': 'CE',
        'Data Deficient': 'DD',
        'Endangered': 'EN',
        'Least Concern': 'LC',
        'Near Threatened': 'NT',
        'Vulnerable': 'VU'
    }
     speciesImages = []

     for species in speciesList:
        scientificName = species.taxonomy.get('scientific_name')
        commonName = species.name   

        try:
            status = EndangeredStatus.objects.get(name=scientificName)
            endangeredStatus = status.status
            status_class = status_classes.get(endangeredStatus, 'Unknown')
            status_label = status_labels.get(endangeredStatus, 'Unknown')
        except EndangeredStatus.DoesNotExist:
            endangeredStatus = 'Unknown'
            status_class = 'Unknown'
            status_label = 'Unknown'
            status_label = 'Unknown'

        if scientificName:
            image = Images.objects.filter(name=scientificName).first()
        else:
            image = None

        speciesImages.append({
            'id': species.id,
            'common_name': commonName,
            'scientific_name': scientificName if scientificName else 'Unknown',
            'image': image,
            'status_class': status_class,
            'status_label': status_label,
        })
     return render(request, 'aquadex/westcoast.html', {'speciesImages': speciesImages})

def PacificIslands(request):
     pacificIslands = [
         "Neomonachus schauinslandi", "Mirounga", "Callorhinus ursinus", "Chelonioidea", "Dermochelys coriacea", "Carcharhinus Amblyrhynchos", "Carcharodon carcharias",
         "Prionace glauca", "Tursiops Truncatus", "Orcinus orca", "Myliobatoidei", "Rhincodon Typus", "Trigonognathus kabeyai", 
         "Manta", "Phoca vitulina", "Enhydra Lutris", "Galeocerdo Cuvier", "Sphyrna tiburo", "Sphyrnidae", "Muraenidae",
         "Exocoetidae", "Acanthuridae", "Labridae", "Hippocampus", "Brachyura", "Ocypodinae", "Acropora cervicornis", "Echinoidea", 
         "Actiniaria", "Asteroidea",
         ]
     speciesList = Species.objects.filter(taxonomy__scientific_name__in=pacificIslands)
     status_classes = {
        'Critically Endangered': 'ce',
        'Data Deficient': 'dd',
        'Endangered': 'en',
        'Least Concern': 'lc',
        'Near Threatened': 'nt',
        'Vulnerable': 'vu'
    }

     status_labels = {
        'Critically Endangered': 'CE',
        'Data Deficient': 'DD',
        'Endangered': 'EN',
        'Least Concern': 'LC',
        'Near Threatened': 'NT',
        'Vulnerable': 'VU'
    }
     speciesImages = []

     for species in speciesList:
        scientificName = species.taxonomy.get('scientific_name')
        commonName = species.name   

        try:
            status = EndangeredStatus.objects.get(name=scientificName)
            endangeredStatus = status.status
            status_class = status_classes.get(endangeredStatus, 'Unknown')
            status_label = status_labels.get(endangeredStatus, 'Unknown')
        except EndangeredStatus.DoesNotExist:
            endangeredStatus = 'Unknown'
            status_class = 'Unknown'
            status_label = 'Unknown'
            status_label = 'Unknown'

        if scientificName:
            image = Images.objects.filter(name=scientificName).first()
        else:
            image = None

        speciesImages.append({
            'id': species.id,
            'common_name': commonName,
            'scientific_name': scientificName if scientificName else 'Unknown',
            'image': image,
            'status_class': status_class,
            'status_label': status_label,
        })
     return render(request, 'aquadex/pacificislands.html', {'speciesImages': speciesImages})

def Foreign(request):
     pacificIslands = [
         "Pygoscelis Antarcticus", "Spheniscus demersus", "Pygoscelis adeliae", "Eudyptes robustus", "Aptenodytes forsteri", "Spheniscus Mendiculus", "Pygoscelis papua",
         "Spheniscus humboldti", "Aptenodytes patagonicus", "Eudyptula Minor", "Eudyptes Chrysolophus", "Spheniscus magellanicus", "Eudyptes chrysocome", 
         "Eudyptes schlegeli", "Megadyptes antipodes", "Cetorhinus Maximus", "Isistius brasiliensis", "Chlamydoselachus anguineus", "Mitsukurina owstoni", "Somniosus microcephalus",
         "Carcharhinus Amblyrhynchos", "Carcharhinus perezii", "Lamna ditropis", "Ginglymostoma cirratum", "Rhincodon Typus", "Stegostoma Fasciatum", "Muraenidae", 
         "Myliobatoidei", "Amblyrhynchus cristatus", "Lobodon carcinophaga", "Pagophilus groenlandicus", "Neomonachus schauinslandi", "Cystophora cristata",
         "Hydrurga Leptonyx", "Mirounga", "Callorhinus ursinus", "Sepiida", "Tremoctopus", "Hapalochlaena", "Mesonychoteuthis hamiltoni",
         "Dosidicus gigas", "Vampyroteuthis infernalis", "Lagenorhynchus obscurus", "Balaena mysticetus", "Pseudorca crassidens", "Balaenoptera acutorostrata",
         "Balaenoptera borealis", "Physeter macrocephalus", "Pterophyllum", "Lophiiformes", "Lates calcarifer", "Psychrolutes marcidus", "Sarda", 
         "Exocoetidae", "Stomiidae", "Himantolophidae", "Antennariidae", "Myxini", "Scyphozoa", "Cyanea capillata", "Chanos chanos", "Mola mola",
         "Aurelia aurita", "Opsanus tau", "Syngnathinae", "Tetraodontidae", "Ogcocephalus darwini", "Pristidae", "Rajidae", "Gigantura",
         "Tetractenos hamiltoni", "Anarhichadidae", "Istiompax Indica", "Gymnothorax miliaris", "Electrophorus Electricus", "Mastacembelus erythrotaenia",
         "Rhinomuraena quaesita", "Anarrhichthys ocellatus", "Gecarcoidea natalis", "Kiwa hirsuta", "Dugong Dugon ", "Euphausiacea", "Monodon monoceros",
         "Ursus maritimus", "Enhydra Lutris", "Phocoena sinus", "Sula nebouxii", "Janthina janthina", "Glaucus atlanticus", "Dendrogyra cylindrus", 
         "Heliopora coerulea", "Acropora cervicornis"
         ]
     speciesList = Species.objects.filter(taxonomy__scientific_name__in=pacificIslands)
     status_classes = {
        'Critically Endangered': 'ce',
        'Data Deficient': 'dd',
        'Endangered': 'en',
        'Least Concern': 'lc',
        'Near Threatened': 'nt',
        'Vulnerable': 'vu'
    }

     status_labels = {
        'Critically Endangered': 'CE',
        'Data Deficient': 'DD',
        'Endangered': 'EN',
        'Least Concern': 'LC',
        'Near Threatened': 'NT',
        'Vulnerable': 'VU'
    }
     speciesImages = []

     for species in speciesList:
        scientificName = species.taxonomy.get('scientific_name')
        commonName = species.name   

        try:
            status = EndangeredStatus.objects.get(name=scientificName)
            endangeredStatus = status.status
            status_class = status_classes.get(endangeredStatus, 'Unknown')
            status_label = status_labels.get(endangeredStatus, 'Unknown')
        except EndangeredStatus.DoesNotExist:
            endangeredStatus = 'Unknown'
            status_class = 'Unknown'
            status_label = 'Unknown'
            status_label = 'Unknown'

        if scientificName:
            image = Images.objects.filter(name=scientificName).first()
        else:
            image = None

        speciesImages.append({
            'id': species.id,
            'common_name': commonName,
            'scientific_name': scientificName if scientificName else 'Unknown',
            'image': image,
            'status_class': status_class,
            'status_label': status_label,
        })
     return render(request, 'aquadex/foreign.html', {'speciesImages': speciesImages})

def BrowseByEndangeredStatus(request):
    return render(request, 'aquadex/browsebyendangeredstatus.html')

def LeastConcern(request):
     leastConcern = [
         "Pygoscelis antarcticus", "Pygoscelis adeliae", "Pygoscelis papua", "Aptenodytes patagonicus", "Eudyptula Minor", "Spheniscus magellanicus",
         "Eudyptes schlegeli", "Isistius brasiliensis", "Chlamydoselachus anguineus", "Mitsukurina owstoni", "Megachasma pelagios",
         "Lamna ditropis", "Trigonognathus kabeyai", "Lobodon carcinophaga", "Mirounga", "Halichoerus Grypus", "Phoca vitulina",
         "Pagophilus groenlandicus", "Hydrurga Leptonyx", "Tremoctopus violaceus", "Mesonychoteuthis hamiltoni", "Tursiops Truncatus",
         "Lagenorhynchus obscurus", "Coryphaena hippurus", "Balaena mysticetus", "Megaptera novaeangliae", "Balaenoptera acutorostrata",
         "Lates calcarifer", "Sphyraena", "Ostracion cubicus", "Rachycentron canadum", "Paralichthys dentatus", "Ariopsis felis", 
         "Pterois volitans", "Chanos chanos", "Platybelone argalus", "Opsanus tau", "Scaridae", "Ogcocephalus darwini",
         "Holocentrus adscensionis", "Uranoscopus scaber", "Tetractenos hamiltoni", "Thunnus alalunga", "Thunnus thynnus",
         "Katsuwonus pelamis", "Thunnus albacares", "Conger conger", "Electrophorus Electricus", "Mastacembelus erythrotaenia",
         "Anarrhichthys ocellatus", "Phycodurus eques", "Echinoidea", "Monodon monoceros", "Sula nebouxii", 
         ]
     speciesList = Species.objects.filter(taxonomy__scientific_name__in=leastConcern)
     status_classes = {
        'Critically Endangered': 'ce',
        'Data Deficient': 'dd',
        'Endangered': 'en',
        'Least Concern': 'lc',
        'Near Threatened': 'nt',
        'Vulnerable': 'vu'
    }

     status_labels = {
        'Critically Endangered': 'CE',
        'Data Deficient': 'DD',
        'Endangered': 'EN',
        'Least Concern': 'LC',
        'Near Threatened': 'NT',
        'Vulnerable': 'VU'
    }
     speciesImages = []

     for species in speciesList:
        scientificName = species.taxonomy.get('scientific_name')
        commonName = species.name   

        try:
            status = EndangeredStatus.objects.get(name=scientificName)
            endangeredStatus = status.status
            status_class = status_classes.get(endangeredStatus, 'Unknown')
            status_label = status_labels.get(endangeredStatus, 'Unknown')
        except EndangeredStatus.DoesNotExist:
            endangeredStatus = 'Unknown'
            status_class = 'Unknown'
            status_label = 'Unknown'
            status_label = 'Unknown'

        if scientificName:
            image = Images.objects.filter(name=scientificName).first()
        else:
            image = None

        speciesImages.append({
            'id': species.id,
            'common_name': commonName,
            'scientific_name': scientificName if scientificName else 'Unknown',
            'image': image,
            'status_class': status_class,
            'status_label': status_label,
        })
     return render(request, 'aquadex/leastconcern.html', {'speciesImages': speciesImages})

def Endangered(request):
     endangered = [
         "Spheniscus demersus", "Spheniscus Mendiculus", "Megadyptes antipodes", "Cetorhinus Maximus", "Sphyrna tiburo", "Carcharhinus Amblyrhynchos",
         "Carcharhinus perezii", "Stegostoma Fasciatum", "Neomonachus schauinslandi", "Balaenoptera musculus", "Balaenoptera borealis",
         "Sarda", "Enhydra lutris",
         ]
     speciesList = Species.objects.filter(taxonomy__scientific_name__in=endangered)
     status_classes = {
        'Critically Endangered': 'ce',
        'Data Deficient': 'dd',
        'Endangered': 'en',
        'Least Concern': 'lc',
        'Near Threatened': 'nt',
        'Vulnerable': 'vu'
    }

     status_labels = {
        'Critically Endangered': 'CE',
        'Data Deficient': 'DD',
        'Endangered': 'EN',
        'Least Concern': 'LC',
        'Near Threatened': 'NT',
        'Vulnerable': 'VU'
    }
     speciesImages = []

     for species in speciesList:
        scientificName = species.taxonomy.get('scientific_name')
        commonName = species.name   

        try:
            status = EndangeredStatus.objects.get(name=scientificName)
            endangeredStatus = status.status
            status_class = status_classes.get(endangeredStatus, 'Unknown')
            status_label = status_labels.get(endangeredStatus, 'Unknown')
        except EndangeredStatus.DoesNotExist:
            endangeredStatus = 'Unknown'
            status_class = 'Unknown'
            status_label = 'Unknown'
            status_label = 'Unknown'

        if scientificName:
            image = Images.objects.filter(name=scientificName).first()
        else:
            image = None

        speciesImages.append({
            'id': species.id,
            'common_name': commonName,
            'scientific_name': scientificName if scientificName else 'Unknown',
            'image': image,
            'status_class': status_class,
            'status_label': status_label,
        })
     return render(request, 'aquadex/endangered.html', {'speciesImages': speciesImages})
  
def NearThreatened(request):
     nearThreatened = [
         "Pelecanus", "Aptenodytes forsteri", "Prionace glauca", "Hexanchus griseus", "Galeocerdo Cuvier", "Pseudorca crassidens",
         ]
     speciesList = Species.objects.filter(taxonomy__scientific_name__in=nearThreatened)
     status_classes = {
        'Critically Endangered': 'ce',
        'Data Deficient': 'dd',
        'Endangered': 'en',
        'Least Concern': 'lc',
        'Near Threatened': 'nt',
        'Vulnerable': 'vu'
    }

     status_labels = {
        'Critically Endangered': 'CE',
        'Data Deficient': 'DD',
        'Endangered': 'EN',
        'Least Concern': 'LC',
        'Near Threatened': 'NT',
        'Vulnerable': 'VU'
    }
     speciesImages = []

     for species in speciesList:
        scientificName = species.taxonomy.get('scientific_name')
        commonName = species.name   

        try:
            status = EndangeredStatus.objects.get(name=scientificName)
            endangeredStatus = status.status
            status_class = status_classes.get(endangeredStatus, 'Unknown')
            status_label = status_labels.get(endangeredStatus, 'Unknown')
        except EndangeredStatus.DoesNotExist:
            endangeredStatus = 'Unknown'
            status_class = 'Unknown'
            status_label = 'Unknown'
            status_label = 'Unknown'

        if scientificName:
            image = Images.objects.filter(name=scientificName).first()
        else:
            image = None

        speciesImages.append({
            'id': species.id,
            'common_name': commonName,
            'scientific_name': scientificName if scientificName else 'Unknown',
            'image': image,
            'status_class': status_class,
            'status_label': status_label,
        })
     return render(request, 'aquadex/nearthreatened.html', {'speciesImages': speciesImages})

def CriticallyEndangered(request):
     criticallyEndangered = [
         "Carcharias taurus", "Phocoena sinus", "Dendrogyra cylindrus", "Acropora cervicornis", 
         ]
     speciesList = Species.objects.filter(taxonomy__scientific_name__in=criticallyEndangered)
     status_classes = {
        'Critically Endangered': 'ce',
        'Data Deficient': 'dd',
        'Endangered': 'en',
        'Least Concern': 'lc',
        'Near Threatened': 'nt',
        'Vulnerable': 'vu'
    }

     status_labels = {
        'Critically Endangered': 'CE',
        'Data Deficient': 'DD',
        'Endangered': 'EN',
        'Least Concern': 'LC',
        'Near Threatened': 'NT',
        'Vulnerable': 'VU'
    }
     speciesImages = []

     for species in speciesList:
        scientificName = species.taxonomy.get('scientific_name')
        commonName = species.name   

        try:
            status = EndangeredStatus.objects.get(name=scientificName)
            endangeredStatus = status.status
            status_class = status_classes.get(endangeredStatus, 'Unknown')
            status_label = status_labels.get(endangeredStatus, 'Unknown')
        except EndangeredStatus.DoesNotExist:
            endangeredStatus = 'Unknown'
            status_class = 'Unknown'
            status_label = 'Unknown'
            status_label = 'Unknown'

        if scientificName:
            image = Images.objects.filter(name=scientificName).first()
        else:
            image = None

        speciesImages.append({
            'id': species.id,
            'common_name': commonName,
            'scientific_name': scientificName if scientificName else 'Unknown',
            'image': image,
            'status_class': status_class,
            'status_label': status_label,
        })
     return render(request, 'aquadex/criticallyendangered.html', {'speciesImages': speciesImages})
  
def DataDeficient(request):
     dataDeficient = [
         "Heterodontus francisci", "Dosidicus gigas", "Orcinus orca", "Istiompax Indica", "Trichechus", "Antennarius striatus", "Actiniaria",
         "Anarhichadidae", "Arctocephalinae", "Aurelia aurita", "Cancer borealis", "Cancer productus", "Chaetodontidae", "Chionoecetes opilio",
         "Coelacanthiformes", "Conger conger", "Cyclopterus lumpus", "Cyanea capillata", "Dugong Dugon", "Emerita analoga",
         "Enhydra Lutris", "Exocoetidae", "Gecarcoidea natalis", "Glaucus atlanticus", "Hermodice carunculata", "Janthina janthina",
         "Kiwa hirsuta", "Litopenaeus vannamei", "Menippe mercenaria", "Myxini", "Ogcocephalus darwini", "Phocoenidae", 
         "Physalia physalis", "Pterophyllum", "Pygoscelis Antarcticus", "Sepiida", "Sebastes", "Strongylocentrotus purpuratus",
         "Tetraodontidae", "Turritopsis dohrnii", "Vampyroteuthis infernalis", "Lopholithodes Mandtii", "Pagurus bernhardus"
         ]
     speciesList = Species.objects.filter(taxonomy__scientific_name__in=dataDeficient)
     status_classes = {
        'Critically Endangered': 'ce',
        'Data Deficient': 'dd',
        'Endangered': 'en',
        'Least Concern': 'lc',
        'Near Threatened': 'nt',
        'Vulnerable': 'vu'
    }

     status_labels = {
        'Critically Endangered': 'CE',
        'Data Deficient': 'DD',
        'Endangered': 'EN',
        'Least Concern': 'LC',
        'Near Threatened': 'NT',
        'Vulnerable': 'VU'
    }
     speciesImages = []

     for species in speciesList:
        scientificName = species.taxonomy.get('scientific_name')
        commonName = species.name   

        try:
            status = EndangeredStatus.objects.get(name=scientificName)
            endangeredStatus = status.status
            status_class = status_classes.get(endangeredStatus, 'Unknown')
            status_label = status_labels.get(endangeredStatus, 'Unknown')
        except EndangeredStatus.DoesNotExist:
            endangeredStatus = 'Unknown'
            status_class = 'Unknown'
            status_label = 'Unknown'
            status_label = 'Unknown'

        if scientificName:
            image = Images.objects.filter(name=scientificName).first()
        else:
            image = None

        speciesImages.append({
            'id': species.id,
            'common_name': commonName,
            'scientific_name': scientificName if scientificName else 'Unknown',
            'image': image,
            'status_class': status_class,
            'status_label': status_label,
        })
     return render(request, 'aquadex/datadeficient.html', {'speciesImages': speciesImages})

def Vulnerable(request):
     vulnerable = [
         "Fratercula arctica", "Eudyptes robustus", "Spheniscus humboldti", "Eudyptes Chrysolophus", "Eudyptes chrysocome", "Carcharhinus Leucas",
         "Carcharodon carcharias", "Somniosus microcephalus", "Ginglymostoma cirratum", "Lamna nasus", "Carcharhinus brevipinna",
         "Dermochelys coriacea", "Amblyrhynchus cristatus", "Cystophora cristata", "Callorhinus ursinus", "Balaenoptera Physalus",
         "Physeter macrocephalus", "Gadus morhua", "Mola mola", "Squalus acanthias", "Odobenus rosmarus", 
         "Dugong dugon", "Ursus maritimus", "Heliopora coerulea",
         ]
     speciesList = Species.objects.filter(taxonomy__scientific_name__in=vulnerable)
     status_classes = {
        'Critically Endangered': 'ce',
        'Data Deficient': 'dd',
        'Endangered': 'en',
        'Least Concern': 'lc',
        'Near Threatened': 'nt',
        'Vulnerable': 'vu'
    }

     status_labels = {
        'Critically Endangered': 'CE',
        'Data Deficient': 'DD',
        'Endangered': 'EN',
        'Least Concern': 'LC',
        'Near Threatened': 'NT',
        'Vulnerable': 'VU'
    }
     speciesImages = []

     for species in speciesList:
        scientificName = species.taxonomy.get('scientific_name')
        commonName = species.name   

        try:
            status = EndangeredStatus.objects.get(name=scientificName)
            endangeredStatus = status.status
            status_class = status_classes.get(endangeredStatus, 'Unknown')
            status_label = status_labels.get(endangeredStatus, 'Unknown')
        except EndangeredStatus.DoesNotExist:
            endangeredStatus = 'Unknown'
            status_class = 'Unknown'
            status_label = 'Unknown'
            status_label = 'Unknown'

        if scientificName:
            image = Images.objects.filter(name=scientificName).first()
        else:
            image = None

        speciesImages.append({
            'id': species.id,
            'common_name': commonName,
            'scientific_name': scientificName if scientificName else 'Unknown',
            'image': image,
            'status_class': status_class,
            'status_label': status_label,
        })
     return render(request, 'aquadex/vulnerable.html', {'speciesImages': speciesImages})
  
def ConMea(request):
    speciesList = Species.objects.all()
    speciesWithConmea = []

    for species in speciesList:
        scientificName = species.taxonomy.get('scientific_name')
        
        if scientificName:
            conmeas = ConservationMeasures.objects.filter(name=scientificName)
            
            if conmeas.exists():
                speciesWithConmea.append({'species': species, 'conmeas': conmeas})
            else:
                speciesWithConmea.append({'species': species, 'conmeas': None})
        else:
            speciesWithConmea.append({'species': species, 'conmeas': None})

    return render(request, 'aquadex/conmea.html', {'speciesWithConmea': speciesWithConmea})

def Monsters(request):
     モンスター = [
         "Nessititan crypticus",
        ]
     speciesList = Species.objects.filter(taxonomy__scientific_name__in=モンスター)
     status_classes = {
        'Critically Endangered': 'ce',
        'Data Deficient': 'dd',
        'Endangered': 'en',
        'Least Concern': 'lc',
        'Near Threatened': 'nt',
        'Vulnerable': 'vu'
     }

     status_labels = {
        'Critically Endangered': 'CE',
        'Data Deficient': 'DD',
        'Endangered': 'EN',
        'Least Concern': 'LC',
        'Near Threatened': 'NT',
        'Vulnerable': 'VU'
     }
     speciesImages = []

     for species in speciesList:
        scientificName = species.taxonomy.get('scientific_name')
        commonName = species.name   

        try:
            status = EndangeredStatus.objects.get(name=scientificName)
            endangeredStatus = status.status
            status_class = status_classes.get(endangeredStatus, 'Unknown')
            status_label = status_labels.get(endangeredStatus, 'Unknown')
        except EndangeredStatus.DoesNotExist:
            endangeredStatus = 'Unknown'
            status_class = 'Unknown'
            status_label = 'Unknown'
            status_label = 'Unknown'

        if scientificName:
            image = Images.objects.filter(name=scientificName).first()
        else:
            image = None

        speciesImages.append({
            'id': species.id,
            'common_name': commonName,
            'scientific_name': scientificName if scientificName else 'Unknown',
            'image': image,
            'status_class': status_class,
            'status_label': status_label,
        })
     return render(request, 'aquadex/monsters.html', {'speciesImages': speciesImages})

def ProfilePage(request):
    return render(request, 'aquadex/profile.html')

def Activate(request, uidb64, token):
    User = get_user_model()
    try:
        uid = force_str(urlsafe_base64_decode(uidb64))  
        user = User.objects.get(pk=uid)  
    except (TypeError, ValueError, OverflowError, User.DoesNotExist):
        user = None
         
    if user is not None and accountActivationToken.check_token(user, token):
        user.is_active = True  
        user.save()  
         
        messages.success(request, "Your email has been confirmed. Please choose a new password.")
        update_session_auth_hash(request, user)  
         
        password_change_form = SetPasswordForm(user)
        return render(request, 'aquadex/password_change.html', {'form': password_change_form})

    else: 
        messages.error(request, "Activation link is invalid.")
        return redirect('signin')

def ActivateEmail(request, user, toEmail):
    mailSubject = "Activate your user account."
    message = render_to_string("aquadex/activateaccount.html",{
                              'user': user.username, 
                              'domain': get_current_site(request).domain, 
                              'uid': urlsafe_base64_encode(force_bytes(user.pk)),  
                              'token': accountActivationToken.make_token(user),  
                              "protocol": 'https' if request.is_secure() else 'http'  
                              })
    email = EmailMessage(mailSubject, message, to=(toEmail))  
    if email.send():   
        messages.success(request, f'Dear <b>{user}</b>, please go to your email <b>{toEmail}</b> inbox and click on \
                 recieved activation link to confirm and complete the registration. <b>Note:</b> Check your spam folder.')
    else:
        message.error(request, f'Problem sending email to {toEmail}, make sure you entered in the email correctly.') 

def SignUp(request): 
   form = CreateUserForm()  
   
   if request.method == "POST":  
       form = CreateUserForm(request.POST)  
       if form.is_valid():  
           user = form.save(commit=False)  
           user.is_active = False  
           user.save()  
           ActivateEmail(request, user, form.cleaned_data.get('email'))  
           messages.success(request, 'Account created successfully. Please check your email to activate your account.')
           return redirect('signin')   
   context = {'form': form}  
   return render(request, 'aquadex/signup.html', context)

@login_required
def ChangePassword(request):
    if request.method == 'POST':  
        form = CustomPasswordChangeForm(request.user, request.POST) 
        if form.is_valid(): 
            user = form.save()  
            update_session_auth_hash(request, user)  
            messages.success(request, 'Your password was successfully updated!')
            return redirect('home')
        else:
            messages.error(request, 'Please correct the error below.')  
    else:
        form = CustomPasswordChangeForm(request.user) 
    return render(request, 'aquadex/changepassword.html', {'form': form}) 

def SignIn(request):  
    if request.method == "POST":
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            return redirect('home')
        else:
            messages.info(request, "Username or Password is incorrect." ) 
    context = {}
    return render(request, 'aquadex/signin.html', context)
 
@login_required
def Logout(request):     
         logout(request)
         return redirect('signin')

def Search(request):
    query = request.GET.get('query', '').strip()
    print(f'Search query: {query}')
    
    if query:
        species_list = Species.objects.filter(
            Q(name__icontains=query) | Q(taxonomy__scientific_name__icontains=query)
        )
    else:
        species_list = Species.objects.none()
    
    print(f'Search results: {species_list}')

    status_classes = {
        'Critically Endangered': 'ce',
        'Data Deficient': 'dd',
        'Endangered': 'en',
        'Least Concern': 'lc',
        'Near Threatened': 'nt',
        'Vulnerable': 'vu'
    }

    status_labels = {
        'Critically Endangered': 'CE',
        'Data Deficient': 'DD',
        'Endangered': 'EN',
        'Least Concern': 'LC',
        'Near Threatened': 'NT',
        'Vulnerable': 'VU'
    }

    species_images = []

    for species in species_list:
        scientific_name = species.taxonomy.get('scientific_name')
        common_name = species.name   

        try:
            status = EndangeredStatus.objects.get(name=scientific_name)
            endangered_status = status.status
            status_class = status_classes.get(endangered_status, 'Unknown')
            status_label = status_labels.get(endangered_status, 'Unknown')
        except EndangeredStatus.DoesNotExist:
            endangered_status = 'Unknown'
            status_class = 'Unknown'
            status_label = 'Unknown'

        image = Images.objects.filter(name=scientific_name).first()

        species_images.append({
            'id': species.id,
            'common_name': common_name,
            'scientific_name': scientific_name if scientific_name else 'Unknown',
            'image': image,
            'status_class': status_class,
            'status_label': status_label,
        })

    return render(request, 'aquadex/searchresults.html', {'speciesImages': species_images})
def SpeciesCard(request, speciesId):
    try:
        species = Species.objects.get(id=speciesId)
        try:
            image = Images.objects.get(name=species.taxonomy['scientific_name'])
        except Images.DoesNotExist:
            image = None  
        try:
            status = EndangeredStatus.objects.get(name=species.taxonomy['scientific_name'])
        except EndangeredStatus.DoesNotExist:
            status = None
        try:
            conmea = ConservationMeasures.objects.get(name=species.taxonomy['scientific_name'])
        except ConservationMeasures.DoesNotExist:
            conmea = None  

        statusImages = {
           'Critically Endangered': 'aquadex/Critically Endangered.png',
           'Data Deficient': 'aquadex/Data Deficient.png',
           'Endangered': 'aquadex/Endangered.png',
           'Least Concern': 'aquadex/Least Concern.png',
           'Near Threatened': 'aquadex/Near Threatened.png',
           'Vulnerable': 'aquadex/Vulnerable.png', 
        }

        formattedStatusImages = {key.replace('_', ' '): value for key, value in statusImages.items()}

        return render(request, 'aquadex/speciescard.html', 
        {
            'species': species,
            'image': image,
            'status': status,
            'conmea': conmea,
            'statusImages': formattedStatusImages
        })
    except Species.DoesNotExist:
        return JsonResponse({'error': 'Species not found'}, status=404)

def SpeciesHeatMap(request): 
    taxonKeys ={ "2480353": "Pelecanus crispus          ",
                 "2481664": "Pygoscelis antarcticus     ",
                 "5229384": "Spheniscus demersus        ",
                 "2481352": "Fratercula arctica         ",
                 "2481663": "Pygoscelis adeliae         ",
                 "2481633": "Eudyptes robustus          ",
                 "2481661": "Aptenodytes forsteri       ",
                 "5229383": "Spheniscus Mendiculus      ",
                 "2481666": "Pygoscelis papua           ",
                 "5229386": "Spheniscus humboldti       ",
                 "2481660": "Aptenodytes patagonicus    ",
                 "2481646": "Eudyptula Minor            ",
                 "2481643": "Eudyptes Chrysolophus      ",
                 "5229385": "Spheniscus magellanicus    ",
                 "2481635": "Eudyptes chrysocome        ",
                 "2481641": "Eudyptes schlegeli         ",
                 "2481632": "Megadyptes antipodes       ",
                 "2420726": "Cetorhinus Maximus         ",
                 "2417940": "Prionace glauca            ",
                 "2418800": "Sphyrna tiburo             ",
                 "2418036": "Carcharhinus Leucas        ",
                 "2420875": "Isistius brasiliensis      ",
                 "2420627": "Chlamydoselachus anguineus ",
                 "2420637": "Mitsukurina owstoni        ",
                 "2420694": "Carcharodon carcharias     ",
                 "2421162": "Somniosus microcephalus    ",
                 "2418064": "Carcharhinus Amblyrhynchos ",
                 "2207"   : "Sphyrna tiburo             ",
                 "5215678": "Heterodontus francisci     ",
                 "2420718": "Megachasma pelagios        ",
                 "2417495": "Ginglymostoma cirratum     ",
                 "5216239": "Lamna nasus                ",
                 "2418059": "Carcharhinus perezi        ",
                 "5216246": "Lamna ditropis             ",
                 "2420766": "Carcharias taurus          ",
                 "2420569": "Hexanchus griseus          ",
                 "2417983": "Carcharhinus brevipinna    ",
                 "2418234": "Galeocerdo Cuvier          ",
                 "2421011": "Trigonognathus kabeyai     ",
                 "2417450": "Stegostoma Fasciatum       ",
                 "2419160": "Manta alfredi              ",
                 "2441866": "Dermochelys coriacea       ",
                 "5224602": "Amblyrhynchus cristatus    ",
                 "2433486": "Arctocephalinae            ",
                 "2434762": "Lobodon carcinophaga       ",
                 "2434812": "Mirounga                   ",
                 "2434806": "Halichoerus Grypus         ",
                 "2434793": "Phoca vitulina             ",
                 "2434801": "Pagophilus groenlandicus   ",
                 "5219376": "Neomonachus schauinslandi  ",
                 "5219378": "Cystophora cristata        ",
                 "2434790": "Hydrurga Leptonyx          ",
                 "2433487": "Callorhinus ursinus        ",
                 "989"    : "Sepiida                    ",
                 "2289334": "Tremoctopus                ",
                 "2289323": "Hapalochlaena              ",
                 "459"    : "Octopus Vulgaris           ",
                 "2289991": "Mesonychoteuthis hamiltoni ",
                 "9205532": "Dosidicus gigas            ",
                 "2290924": "Vampyroteuthis infernalis  ",
                 "6165034": "Platanistoidea             ",
                 "2440446": "Tursiops Truncatus         ",
                 "5314"   : "Delphinidae                ",
                 "5220077": "Lagenorhynchus obscurus    ",
                 "2381939": "Coryphaena hippurus        ",
                 "9361"   : "Phocoenidae                ",
                 "2440735": "Balaenoptera musculus      ",
                 "2440330": "Balaena mysticetus         ",
                 "2440440": "Pseudorca crassidens       ",
                 "2440718": "Balaenoptera Physalus      ",
                 "5220086": "Megaptera novaeangliae     ",
                 "2440483": "Orcinus orca               ",
                 "2440728": "Balaenoptera acutorostrata ",
                 "7194024": "Balaenoptera borealis      ",
                 "8123917": "Physeter macrocephalus     ",
                 "2414318": "Melanocetus johnsonii      ",
                 "2393172": "Lates calcarifer           ",
                 "2369201": "Sphyraena                  ",
                 "5208593": "Sarda sarda                ",
                 "5213766": "Ostracion cubicus          ",
                 "8517"   : "Chaetodontidae             ",
                 "2391729": "Rachycentron canadum       ",
                 "8084280": "Gadus morhua               ", 
                 "2408866": "Paralichthys dentatus      ",
                 "2968"   : "Exocoetidae                ",
                 "2415104": "Himantolophus sagamius     ",
                 "7677"   : "Antennariidae              ",
                 "5870"   : "Myxini                     ",
                 "5202927": "Ariopsis felis             ",
                 "2266021": "Turritopsis dohrnii        ",
                 "352"    : "Scyphozoa                  ",
                 "2264478": "Cyanea capillata           ",
                 "2334432": "Pterois volitans           ",
                 "5962255": "Cyclopterus lumpus         ",
                 "2381886": "Physalia physalis          ",
                 "2406374": "Chanos chanos              ",   
                 "5213725": "Mola mola                  ",
                 "2415075": "Lophius piscatorius        ",
                 "2264442": "Aurelia aurita             ",
                 "7190"   : "Platybelone argalus        ",
                 "2350910": "Opsanus tau                ",
                 "4504"   : "Scaridae                   ",
                 "2219"   : "Tetraodontidae             ",
                 "5214838": "Ogcocephalus darwini       ",
                 "5216276": "Pristis pristis            ",
                 "4508"   : "Scorpaenidae               ",
                 "2420234": "Dipturus batis             ",
                 "5216368": "Squalus acanthias          ",
                 "5204777": "Holocentrus adscensionis   ",
                 "214"    : "Asteroidea                 ",
                 "2394370": "Uranoscopus scaber         ",
                 "2379647": "Acanthuridae               ",
                 "2401650": "Gigantura chuni            ",
                 "2407624": "Tetractenos hamiltoni      ",
                 "8006460": "Anarhichadidae             ",
                 "9694948": "Thunnus alalunga           ",
                 "2373980": "Thunnus thynnus            ",
                 "2374191": "Katsuwonus pelamis         ",
                 "2374013": "Thunnus albacares          ",
                 "4285896": "Istiompax Indica           ",
                 "2403964": "Gymnothorax funebris       ",
                 "2403522": "Conger Conger              ",
                 "495"    : "Anguilliformes             ",
                 "2401958": "Electrophorus Electricus   ",
                 "2351804": "Mastacembelus erythrotaenia",
                 "2403157": "Heteroconger hassi         ",
                 "2392219": "Anarrhichthys ocellatus    ",
                 "5218819": "Odobenus rosmarus          ", 
                 "2332986": "Phycodurus eques           ",
                 "5201029": "Hippocampus                ",
                 "2346650": "Megalops                   ",
                 "4645892": "Gecarcoidea natalis        ", 
                 "11132538":"Brachyura                  ",
                 "6586700": "Uca                        ",
                 "1010610": "Limulus polyphemus         ",
                 "2222084": "Cancer borealis            ",
                 "8146"   : "Lopholithodes Mandtii      ",
                 "2222075": "Cancer productus           ",
                 "2225698": "Emerita analoga            ",
                 "2226639": "Chionoecetes opilio        ",
                 "5178757": "Menippe mercenaria         ",
                 "2222780": "Kiwa hirsuta               ",
                 "5972004": "Homarus americanus         ",
                 "2435291": "Trichechus                 ", 
                 "705"    : "Actiniaria                 ",
                 "765"    : "Coelacanthiformes          ",
                 "9729967": "Dugong dugon               ",
                 "2228010": "Euphausia superba          ",
                 "5220008": "Monodon monoceros          ",
                 "2433451": "Ursus maritimus            ",
                 "2433670": "Enhydra lutris             ",
                 "2440665": "Phocoena sinus             ", 
                 "6178176": "Sula nebouxii              ", 
                 "2299286": "Janthina janthina          ", 
                 "5190072": "Glaucus atlanticus         ",
                 "2317552": "Hermodice carunculata      ",  
                 "4944083": "Dendrogyra cylindrus       ",
                 "2264328": "Heliopora coerulea         ", 
                 "5184681": "Acropora cervicornis       ",
                 "2374069": "Acanthocybium solandri     ",   
                 "5212106": "Amphiprion ocellaris       ",   
                 "2223871": "Litopenaeus vannamei       ", 
                 "2388456": "Epinephelus itajara        ", 
                 "2403816": "Gymnothorax miliaris       ",     
                 "2384533": "Thalassoma bifasciatum     ",      
                 "2278852": "Strongylocentrotus purpuratus",
                 "9775198": "Himantura uarnak           ",
                 "2433462": "Eumetopias jubatus         ",
                 "2224231": "Pagurus bernhardus         ", 
                 "3230433": "Pterophyllum               ",
                 "2400222": "Sciaenops ocellatus        ",
                 "2333712": "Sebastes                   ",
                 "2347378": "Malacosteus niger          ", 
                 "2332775": "Doryrhamphus dactylophorus ",   
                }

    projection = '3857'
    speciesMaps = {}
    for taxonKey, speciesName in taxonKeys.items():
        fmap = GenerateHeatMap(taxonKey=taxonKey, projection=projection)
        filename = os.path.join('C:\\Users\\shaun\\Desktop\\AquaDex\\mysite\\aquadex\\templates\\aquadex', f'heatmap_{speciesName}.html')
        fmap.save(filename)
        speciesMaps[speciesName] = filename
        time.sleep(1)

    print("Number of maps generated:", len(speciesMaps))
    return render(request, 'speciescard.html', {'speciesMaps': speciesMaps})

def SpeciesApiData(request): 
    FetchSpeciesData()
    return JsonResponse({'message': 'Data saved successfully'}) 
 
def EndangeredStatusScraper(request): 
    SpeciesEndangeredStatusScraper()
    return JsonResponse({'message': 'Data saved successfully'})

def ConservationMeasuresScraper(request):
    SpeciesConMeaScraper()
    return JsonResponse({'message': 'Data saved successfully'})

def ImageScraper(request):
     SpeciesImageScraper()
     return JsonResponse({'message': 'Images scraped and saved successfully'})
