from django import forms
from .models import MaintenanceSpeciesList

class MaintenanceSpeciesListForm(forms.ModelForm):
    class Meta:
        model = MaintenanceSpeciesList
        fields = [
            'species_id',  
            'active',  # Checkbox to toggle the active/inactive state
            'nl_name',  # Dutch name
            'en_name',  # English name
            'latin_name',  # Latin name
            'WoRMS',  # WoRMS number
            'pauly_trophic_level',  # Pauly Trophic Level
            'var_x',  # Free text field
            'fishflag',  # Checkbox for fish species
            'collecting_per_week',  # Number of times to collect per week
            'always_collecting'  # Checkbox for always collecting
        ]
        widgets = {
            'species_id': forms.NumberInput(), 
            'active': forms.CheckboxInput(),  # Widget for the checkbox
            'fishflag': forms.CheckboxInput(),  # Widget for fishflag checkbox
            'always_collecting': forms.CheckboxInput(),  # Widget for always_collecting checkbox
            'nl_name': forms.TextInput(attrs={'placeholder': 'Voer de Nederlandse naam in'}),
            'en_name': forms.TextInput(attrs={'placeholder': 'Voer de Engelse naam in'}),
            'latin_name': forms.TextInput(attrs={'placeholder': 'Voer de Latijnse naam in'}),
            'WoRMS': forms.TextInput(attrs={'placeholder': 'Voer het WoRMS nummer in'}),
            'pauly_trophic_level': forms.NumberInput(attrs={'placeholder': 'Voer het Pauly Trophic Level in'}),
            'var_x': forms.Textarea(attrs={'placeholder': 'Voer hier extra informatie in', 'rows': 3}),
            'collecting_per_week': forms.NumberInput(attrs={'placeholder': 'Voer het aantal verzamelingen per week in'}),
        }
