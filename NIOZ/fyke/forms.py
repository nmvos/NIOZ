from django import forms
from django.shortcuts import render, redirect
from django.forms import ModelForm
from .models import DataCollection, CatchLocations, bioticData
from maintenance.models import MaintenanceSpeciesList

class DataCollectionForm(forms.ModelForm):
    class Meta:
        model = DataCollection
        fields = [
            'tidal_phase',
            'salinity',
            'temperature',
            'wind_direction',
            'wind_speed',
            'secchi_depth',
            'fu_scale',
            'date',
            'time',
            'fishingday',
            'fyke',
            'duration',
            'remarks',
            'observer',
        ]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # Set specific fields to not be required
        for field in [
            'observer', 'tidal_phase', 'salinity', 'temperature',
            'wind_direction', 'wind_speed', 'secchi_depth', 'fu_scale', 'remarks'
        ]:
            self.fields[field].required = False

        # Set initial value for new records
        if not self.instance.pk:  # Check if it's a new instance
            self.fields['remarks'].initial = ""  # Set initial value to empty for new records

class CatchLocationsForm(ModelForm):
    class Meta:
        model = CatchLocations
        fields = ['name', 'type', 'latitude', 'longitude', 'remarks', 'collect_group', 'print_label']
        
class BioticDataForm(forms.ModelForm):
    species = forms.IntegerField(label='Species ID')

    class Meta:
        model = bioticData
        fields = [
            'species', 'subsample', 'nspecies', 'totallength', 'lengthestimate', 'freshweight', 'collectno', 'remarks'
        ]
        
        widgets = {
            'collectno': forms.HiddenInput(),
            'remarks': forms.Textarea(attrs={'rows': 1, 'cols': 10}),
            'lengthestimate': forms.CheckboxInput(),
        }

    def clean_species(self):
        species_id = self.cleaned_data['species']
        try:
            species = MaintenanceSpeciesList.objects.get(species_id=species_id)
            return species  # Return the species instance instead of species.id
        except MaintenanceSpeciesList.DoesNotExist:
            raise forms.ValidationError(f"Species with ID {species_id} does not exist.")