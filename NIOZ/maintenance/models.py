from django.db import models


class MaintenanceSpeciesList(models.Model):
    nl_name = models.CharField(max_length=255)
    latin_name = models.CharField(max_length=255)
    species_id = models.IntegerField()
    WoRMS = models.CharField(max_length=255)
    var_x = models.TextField(null=True, blank=True)
    en_name = models.CharField(max_length=254)
    fishflag = models.BooleanField(default=False)
    oldnrmee = models.TextField(null=True, blank=True)
    active = models.BooleanField(default=True)
    pauly_trophic_level = models.CharField(max_length=51)
    extraction_date = models.CharField(max_length=50, null=True, blank=True)
    collecting_per_week = models.IntegerField()
    always_collecting = models.BooleanField(default=False)
    

    # Meta class for table settings (optional)
    class Meta:
        db_table = 'maintenance_species_list'
        verbose_name = 'Maintenance Species'
        verbose_name_plural = 'Maintenance Species List'

    def __str__(self):
        return self.nl_name  
    
        
class FykeLocation(models.Model):
    no = models.AutoField(primary_key=True)  # Auto-incrementing 'no'
    location = models.CharField(max_length=254)
    comment = models.TextField(blank=True, null=True)

    class Meta:
        db_table = 'maintenance_fyke_locations'
        verbose_name = "Fyke Location"
        verbose_name_plural = "Fyke Locations"

    def __str__(self):
        return f"{self.no} - {self.location}"

class FykeProgramme(models.Model):
    no = models.AutoField(primary_key=True)  # Auto-incrementing 'no'
    programme = models.CharField(max_length=255)
    comment = models.TextField(blank=True, null=True)

    class Meta:
        db_table = 'maintenance_fyke_programmes'
        verbose_name = "Fyke Programme"
        verbose_name_plural = "Fyke Programmes"

    def __str__(self):
        return f"{self.no} - {self.programme}"



