from django.db import models
from datetime import datetime
from django.contrib.auth.hashers import make_password
from django.contrib.auth.models import User

# Person model
class Person(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    realName = models.CharField(max_length=50)
    collectlocation = models.CharField(max_length=100, default="Texel (RW) Lauwersoog (RW)")
    yearFrom = models.CharField(max_length=10, default=str(datetime.now().year))
    yearUntil = models.CharField(max_length=4, default=9999)
    accessTexel = models.IntegerField(default=3)
    accessLauwersoog = models.IntegerField(default=3)
    fishdata = models.IntegerField(default=3)
    deleteRecords = models.IntegerField(default=3)
    fishdataExport = models.IntegerField(default=3)
    fishdataRecords = models.IntegerField(default=3)
    fishdataSource = models.IntegerField(default=3)
    fyke = models.IntegerField(default=3)
    fykeBioticdata = models.IntegerField(default=3)
    fykeDatacollection = models.IntegerField(default=3)
    fykeExportdata = models.IntegerField(default=3)
    fykeFishDetails = models.IntegerField(default=3)
    fykeLocations = models.IntegerField(default=3)
    help = models.IntegerField(default=3)
    maintenance = models.IntegerField(default=3)
    maintenanceFishprogrammes = models.IntegerField(default=3)
    maintenanceLocations = models.IntegerField(default=3)
    maintenanceSpecies = models.IntegerField(default=3)
    manager = models.IntegerField(default=3)
    managerUserAccess = models.IntegerField(default=3)
    options = models.IntegerField(default=3)
    optionsUserSettings = models.IntegerField(default=3)


    def __str__(self):
        return f"{self.user.username} Profile"

    class Meta:
        db_table = 'adminmenu_person'
        verbose_name = "Gebruiker"
        verbose_name_plural = "Gebruikers"