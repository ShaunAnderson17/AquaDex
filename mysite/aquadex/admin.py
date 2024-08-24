from django.contrib import admin
from .models import Species
from .models import Images 
from .models import EndangeredStatus
from .models import ConservationMeasures

admin.site.register(Species)
admin.site.register(Images) 
admin.site.register(EndangeredStatus)
admin.site.register(ConservationMeasures)
