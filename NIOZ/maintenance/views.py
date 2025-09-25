from django.shortcuts import render, redirect, get_object_or_404
from django.http import JsonResponse
from .models import MaintenanceSpeciesList
from .forms import MaintenanceSpeciesListForm
from django.db.models import IntegerField
from django.db.models.functions import Cast

def index(request):
    return render(request, 'maintenance/index.html')


def species_list(request):
    # Default values
    default_sort = 'nl_name'
    default_order = 'asc'

    # Retrieve current sorting settings from GET parameters
    sort_by = request.GET.get('sort', default_sort)
    order = request.GET.get('order', default_order)

    # Lijst van geldige sorteerbare kolommen
    valid_sort_columns = ['species_id', 'active', 'nl_name', 'name', 'latin_name',
                          'WoRMS', 'pauly_trophic_level', 'var_x', 'fishflag',
                          'collecting_per_week', 'always_collecting']

    # Controleer of de opgegeven sorteerwaarde geldig is
    if sort_by not in valid_sort_columns:
        sort_by = default_sort
        order = default_order

    # Verkrijg de vorige sorteerinstellingen uit de sessie
    last_sort = request.session.get('last_sort', default_sort)
    last_order = request.session.get('last_order', default_order)
    
    print("Ophalen Sessiewaarden:", last_sort, last_order)



    # Als de kolom hetzelfde is als de vorige keer, wissel de volgorde
    if sort_by == last_sort:
        # Als het dezelfde kolom is, wissel de volgorde (asc <-> desc)
        order = 'desc' if last_order == 'asc' else 'asc'
    else:
        # Start met ascending wanneer er een nieuwe kolom is
        order = 'asc' 

    # Sla de huidige sorteerinstellingen op in de sessie
    request.session['last_sort'] = sort_by
    request.session['last_order'] = order
    print("Sessiewaarden:", request.session.get('last_sort'), request.session.get('last_order'))

    

    # Haal de records op en pas de sortering toe
    species = MaintenanceSpeciesList.objects.all()

    # Specifieke sortering voor 'WoRMS' als numerieke waarde
    if sort_by == 'WoRMS':
        species = species.annotate(WoRMS_as_int=Cast('WoRMS', IntegerField()))
        display_sort_by = 'WoRMS'  # Houd bij wat de gebruiker heeft geselecteerd
        sort_by = 'WoRMS_as_int'
    else:
        display_sort_by = sort_by

    # Pas de sortering toe afhankelijk van de volgorde
    if order == 'desc':
        species = species.order_by(f'-{sort_by}')
    else:
        species = species.order_by(sort_by)

    # Controleer of het formulier zichtbaar moet zijn
    show_form = 'add' in request.GET
    form = MaintenanceSpeciesListForm() if show_form else None

    return render(request, 'maintenance/species_list.html', {
        'species': species,
        'form': form,
        'show_form': show_form,
        'sort': display_sort_by,  # Gebruik de originele kolomnaam voor consistentie
        'order': order,
        'last_sort': last_sort,
        'last_order': last_order,
    })



def species_create(request):
    if request.method == 'POST':
        form = MaintenanceSpeciesListForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('species_list')
    else:
        form = MaintenanceSpeciesListForm(initial={'active': False})  # Hier stellen we 'active' standaard in op False

    species = MaintenanceSpeciesList.objects.all()  # Voor de weergave van de tabel met bestaande gegevens
    return render(request, 'maintenance/species_list.html', {'form': form, 'species': species})




def species_edit(request, species_id):
    species_instance = get_object_or_404(MaintenanceSpeciesList, species_id=species_id)
    
    if request.method == 'POST':
        form = MaintenanceSpeciesListForm(request.POST, instance=species_instance)
        if form.is_valid():
            form.save()
            return redirect('species_list')
    else:
        form = MaintenanceSpeciesListForm(instance=species_instance)
    
    # Haal alle species op om ze in de tabel weer te geven
    all_species = MaintenanceSpeciesList.objects.all()
    
    return render(request, 'maintenance/species_list.html', {'form': form, 'species': all_species, 'edit_instance': species_instance})






def fishprogrammes(request):
    return render(request, 'maintenance/fishprogrammes.html')

def fishlocations(request):
    return render(request, 'maintenance/fishlocations.html')

def species_detail(request, species_id):
    try:
        species = MaintenanceSpeciesList.objects.get(species_id=species_id)
        data = {
            'id': species.species_id,
            'active': species.active,
            'nl_name': species.nl_name,
            'name': species.name,
            'latin_name': species.latin_name,
            'WoRMS': species.WoRMS,
            'pauly_trophic_level': species.pauly_trophic_level,
            'var_x': species.var_x,
            'fishflag': species.fishflag,
            'collecting_per_week': species.collecting_per_week,
            'always_collecting': species.always_collecting
        }
        return JsonResponse(data)
    except MaintenanceSpeciesList.DoesNotExist:
        return JsonResponse({'error': 'Species not found'}, status=404)
