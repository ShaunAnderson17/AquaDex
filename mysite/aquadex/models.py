from django.db import models
class MarineModel(models.Model):
    createdAt = models.DateTimeField(auto_now_add=True)
    
class Images(models.Model):
    name = models.CharField(max_length = 100, null=True)
    img = models.ImageField(upload_to='images/', null=True)
    def __str__(self):
        return self.name
      
class ConservationMeasures(models.Model):
    name = models.CharField(max_length = 100, null = True)
    measures = models.TextField()
    def __str__(self):
        return self.measures

class EndangeredStatus(models.Model):
    name = models.CharField(max_length = 100, null = True)
    status = models.CharField(max_length = 100)
    def __str__(self):
        return self.status
     
class Species(models.Model):
    name = models.CharField(max_length = 255, unique = True)
    taxonomy = models.JSONField(null = True, blank = True)
    characteristics = models.JSONField(null = True, blank = True)
    locations = models.JSONField(null = True, blank = True)

    def __str__(self):
        return self.name
