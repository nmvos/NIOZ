from django.db import models
from django.contrib.auth.models import User

class DataCollection(models.Model):
    tidal_phase = models.CharField(max_length=255, blank=True, null=True)
    salinity = models.CharField(max_length=8, blank=True, null=True)
    temperature = models.CharField(max_length=8, blank=True, null=True)
    wind_direction = models.CharField(max_length=255, blank=True, null=True)
    wind_speed = models.CharField(max_length=8, blank=True, null=True)
    secchi_depth = models.CharField(max_length=8, blank=True, null=True)
    fu_scale = models.CharField(max_length=255, blank=True, null=True)
    remarks = models.TextField(blank=True, null=True)
    observer = models.CharField(max_length=255, blank=True, null=True)
    
    changed_by = models.ForeignKey(User, null=True, blank=True, on_delete=models.SET_NULL)
    last_change = models.DateTimeField(auto_now=True)

    date = models.DateField()
    time = models.TimeField()
    fishingday = models.CharField(max_length=8, blank=True, null=True)
    duration = models.CharField(max_length=8, blank=True, null=True)
    
    FYKE_CHOICES = [
        ('Stuifdijk', 'Stuifdijk'),
        ('Afsluitdijk', 'Afsluitdijk'),
        ('Schanserwaard', 'Schanserwaard'),
        ('Pakeerplaats NIOZ achter', 'Pakeerplaats NIOZ achter'),
        ('Parkeerplaats haven', 'Parkeerplaats haven'),
        ('Texelstroom', 'Texelstroom'),
        ('NIOZ dam', 'NIOZ dam'),
        ('Navicula', 'Navicula'),
        ('Wierbalg', 'Wierbalg'),
        ('WMR-NIOZ otoliths project', 'WMR-NIOZ otoliths project'),
        ('Gat v Stier', 'Gat v Stier'),
        ('HW-prog', 'HW-prog'),
        ('IJhaven Amsterdam', 'IJhaven Amsterdam'),
        ('NA', 'NA'),
        ('NIOZ_Harbour', 'NIOZ_Harbour'),
        ('North Sea', 'North Sea'),
        ('Terschelling', 'Terschelling'),
        ('Texelstroom', 'Texelstroom'),
        ('WaddenSea', 'WaddenSea'),
        ('Texel beach', 'Texel beach'),
        ('Fyke Sieme', 'Fyke Sieme'),
        ('Eems', 'Eems'),
        ('Dooie Hond', 'Dooie Hond'),
        ('Eerste hoofd', 'Eerste hoofd'),
        ('Veerhaven', 'Veerhaven'),
        ('Hors', 'Hors'),
        ('Schanderwaard', 'Schanderwaard'),
        ('Vlettenstelling', 'Vlettenstelling'),
        ('Hoek van de staak', 'Hoek van de staak'),
        ('Onbekend', 'Onbekend'),
        ('Schiermonnikoog', 'Schiermonnikoog'),
        ('Borkumse stenen', 'Borkumse stenen'),
    ]
    
    fyke = models.CharField(max_length=100, choices=FYKE_CHOICES)

    class Meta:
        db_table = 'fyke_datacollection'  # Set the name to your existing database table

    def __str__(self):
        return f"{self.date} by {self.observer}"
    
    def save(self, *args, **kwargs):
        # Normalize floating-point fields
        for field in self._meta.fields:
            value = getattr(self, field.name)

            # Convert empty strings to None
            if value == '':
                setattr(self, field.name, None)
            
            # Convert ',' to '.' for FloatField inputs
            if isinstance(value, str) and ',' in value:
                try:
                    setattr(self, field.name, float(value.replace('.', ',')))
                except ValueError:
                    setattr(self, field.name, None)
                    
        # Automatically set the changed_by and last_change fields
        if not self.changed_by and hasattr(self, 'user') and self.user:
            self.changed_by = self.user

        super().save(*args, **kwargs)

class FishDetails(models.Model):
    collectdate = models.DateField(auto_now=False, auto_now_add=False, blank=True, null=True)
    registrationtime = models.DateTimeField(auto_now=False, auto_now_add=True, blank=True, null=True)
    collectno = models.IntegerField()
    biotic = models.ForeignKey(
        'bioticData',
        on_delete=models.CASCADE,  # Use CASCADE or your preferred option
        related_name='fish_details',  # Optional: for reverse lookup
    )
    species = models.ForeignKey(
        'maintenance.MaintenanceSpeciesList',
        on_delete=models.CASCADE,  # Use CASCADE or your preferred option
        related_name='data_collections',  # Optional: for reverse lookup
    )
    condition = models.CharField(max_length=50, blank=True, null=True)
    total_length = models.CharField(max_length=50, blank=True, null=True)
    fork_length = models.CharField(max_length=50, blank=True, null=True)
    standard_length = models.CharField(max_length=50, blank=True, null=True)
    fresh_weight = models.CharField(max_length=50, blank=True, null=True)
    liver_weight = models.CharField(max_length=50, blank=True, null=True)
    total_wet_mass = models.CharField(max_length=50, blank=True, null=True)
    stomach_content = models.CharField(max_length=255, blank=True, null=True)
    gonad_mass = models.CharField(max_length=50, blank=True, null=True)
    sexe = models.CharField(max_length=50, blank=True, null=True)
    ripeness = models.CharField(max_length=50, blank=True, null=True)
    otolith = models.CharField(max_length=50, blank=True, null=True)
    isotopeflag = models.CharField(max_length=50, blank=True, null=True)
    total_length_frozen = models.CharField(max_length=50, blank=True, null=True)
    fork_length_frozen = models.CharField(max_length=50, blank=True, null=True)
    standard_length_frozen = models.CharField(max_length=50, blank=True, null=True)
    frozen_mass = models.CharField(max_length=50, blank=True, null=True)
    height = models.CharField(max_length=50, blank=True, null=True)
    age = models.CharField(max_length=50, blank=True, null=True)
    rings = models.CharField(max_length=50, blank=True, null=True)
    ogew1 = models.CharField(max_length=50, blank=True, null=True)
    ogew2 = models.CharField(max_length=50, blank=True, null=True)
    tissue_type = models.CharField(max_length=50, blank=True, null=True)
    vial = models.CharField(max_length=50, blank=True, null=True)
    dna_sample = models.BooleanField(blank=True, null=True)
    comment = models.TextField(max_length=256, blank=True, null=True)
    micro_plastic = models.BooleanField(blank=True, null=True)
    
    # changed_by = models.ForeignKey(User, null=True, blank=True, on_delete=models.SET_NULL)
    last_change = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'fyke_fishdetails'
    
    def __str__(self):
        return f"{self.species} at {self.collectdate}"
    
    def save(self, *args, **kwargs):
        # Normalize floating-point fields
        for field in self._meta.fields:
            value = getattr(self, field.name)

            # Convert empty strings to None
            if value == '':
                setattr(self, field.name, None)
            
            # Convert ',' to '.' for FloatField inputs
            if isinstance(value, str) and ',' in value:
                try:
                    setattr(self, field.name, float(value.replace('.', ',')))
                except ValueError:
                    setattr(self, field.name, None)
                    
        # Automatically set the changed_by and last_change fields
        # if not self.changed_by and hasattr(self, 'user') and self.user:
        #     self.changed_by = self.user

        super().save(*args, **kwargs)
        
class CatchLocations(models.Model):
    LOCATION_CHOICES = [
        ('Texel', 'Texel'),
        ('Lauwersoog', 'Lauwersoog'),
    ]

    name = models.CharField(max_length=255, verbose_name="Fyke name")
    type = models.CharField(max_length=255, verbose_name="Type")
    latitude = models.DecimalField(max_digits=9, decimal_places=0, verbose_name="Latitude")
    longitude = models.DecimalField(max_digits=9, decimal_places=0, verbose_name="Longitude")
    remarks = models.TextField(blank=True, verbose_name="Remarks")
    
    collect_group = models.CharField(
        max_length=50, 
        choices=LOCATION_CHOICES, 
        verbose_name="Collect Group"
    )
    print_label = models.CharField(
        max_length=50, 
        choices=LOCATION_CHOICES, 
        verbose_name="Print Label"
    )
    
    class Meta:
        db_table = 'fyke_catchlocations'

    def save(self, *args, **kwargs):
        # Normalize floating-point fields
        for field in self._meta.fields:
            value = getattr(self, field.name)

            # Convert empty strings to None
            if value == '':
                setattr(self, field.name, None)
            
            # Convert ',' to '.' for FloatField inputs
            if isinstance(value, str) and ',' in value:
                try:
                    setattr(self, field.name, float(value.replace('.', ',')))
                except ValueError:
                    setattr(self, field.name, None)
                    
        # Automatically set the changed_by and last_change fields
        # if not self.changed_by and hasattr(self, 'user') and self.user:
        #     self.changed_by = self.user  # This assumes you're passing the user as part of the save

        super().save(*args, **kwargs)
        
class bioticData(models.Model):
    id = models.AutoField(primary_key=True)
    fdatex = models.CharField(max_length=50, blank=True,null=True)
    species = models.ForeignKey(
        'maintenance.MaintenanceSpeciesList',
        on_delete=models.CASCADE,
    )
    measurecode = models.CharField(max_length=50, default=10)
    totallength = models.CharField(max_length=255, blank=True, null=True)
    fdetailx = models.CharField(max_length=50, default=0)
    regtime = models.DateTimeField(auto_now=True)
    subsample = models.CharField(max_length=50, default=1)
    datacollection = models.ForeignKey(
        DataCollection,
        on_delete=models.CASCADE,
        # related_name='biotic_data'
    )
    nspecies = models.CharField(max_length=50, default=1)
    collectno = models.IntegerField(default=0)
    origin = models.CharField(max_length=50, default=1)
    freshweight = models.CharField(max_length=50, blank=True, null=True)
    collectlocation = models.CharField(max_length=50, default=1)
    lengthestimate = models.BooleanField(default=False)
    remarks = models.TextField(blank=True, null=True)
    
    class Meta:
        db_table = 'fyke_bioticdata'
    
    def save(self, *args, **kwargs):
        # Normalize floating-point fields
        for field in self._meta.fields:
            value = getattr(self, field.name)

            # Convert empty strings to None
            if value == '':
                setattr(self, field.name, None)
            
            # Convert ',' to '.' for FloatField inputs
            if isinstance(value, str) and ',' in value:
                try:
                    setattr(self, field.name, float(value.replace('.', ',')))
                except ValueError:
                    setattr(self, field.name, None)
                    
        # Automatically set the changed_by and last_change fields
        # if not self.changed_by and hasattr(self, 'user') and self.user:
        #     self.changed_by = self.user

        super().save(*args, **kwargs)
        
class StomachData(models.Model):
    fishdetails = models.ForeignKey(
        'FishDetails',
        on_delete=models.CASCADE,
    )
    species = models.ForeignKey(
        'maintenance.MaintenanceSpeciesList',
        on_delete=models.CASCADE,
    )
    number = models.CharField(max_length=255, blank=True, null=True)
    length = models.CharField(max_length=255, blank=True, null=True)

    class Meta:
        db_table = 'fyke_stomachdata'
        verbose_name = 'Fyke Stomach Data'
        verbose_name_plural = 'Fyke Stomach Data'

    def __str__(self):
        return f"StomachData"
    
    def save(self, *args, **kwargs):
        # Normalize floating-point fields
        for field in self._meta.fields:
            value = getattr(self, field.name)

            # Convert empty strings to None
            if value == '':
                setattr(self, field.name, None)
            
            # Convert ',' to '.' for FloatField inputs
            if isinstance(value, str) and ',' in value:
                try:
                    setattr(self, field.name, float(value.replace(',', '.')))
                except ValueError:
                    setattr(self, field.name, None)
                    
        super().save(*args, **kwargs)