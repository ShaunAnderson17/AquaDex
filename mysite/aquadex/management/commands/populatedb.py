from django.core.management.base import BaseCommand
from ...datapopulation import SpeciesConMeaScraper
class Command(BaseCommand):
    help = 'Populates the database with API data'

    def handle(self, *args, **options):
        SpeciesConMeaScraper() 
        #SpeciesEndangeredStatusScraper()
        #FetchSpeciesData()
        #SpeciesImageScraper()
