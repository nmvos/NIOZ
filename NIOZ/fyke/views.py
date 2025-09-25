from django.shortcuts import render, redirect, get_object_or_404
from django.db.models.functions import ExtractYear, ExtractWeek
from django.http import JsonResponse, HttpResponse
from django.db.models import Q
from django.db import transaction
from .models import DataCollection, CatchLocations, FishDetails, bioticData, StomachData
from .forms import DataCollectionForm, CatchLocationsForm, BioticDataForm
from maintenance.models import MaintenanceSpeciesList
from datetime import datetime, date
from math import ceil
from urllib.parse import urlencode
from collections import defaultdict
import csv

# Index
def index(request):
    return render(request, 'index.html')


# DataCollection
def datacollection_view(request):
    # Extract the year and week from the 'date' field in the database
    data = DataCollection.objects.annotate(
        year=ExtractYear('date'),  # Extract year from the date
        week=ExtractWeek('date')    # Extract week from the date
    )
    
    for obj in data:
        for field in obj._meta.fields:
            if getattr(obj, field.name) is None:
                setattr(obj, field.name, "")

    # Get distinct years based on the 'date' field
    years = data.values_list('year', flat=True).distinct().order_by('year')

    # Check if a year filter is applied in the URL
    selected_year = request.GET.get('year')

    # Filter the records by the selected year, if provided
    if selected_year:
        selected_year = int(selected_year)  # Convert to int for comparison
        data = data.filter(year=selected_year)  # Filter data based on extracted year
        
    return render(request, 'datacollection.html', {
        'data': data,
        'years': years,  # Pass the dynamically calculated years
        'selected_year': selected_year
    })

def new_record_view(request):
    reference_date = datetime(1899, 12, 30).date()
    
    now = datetime.now()  # Get the full datetime object for date and time
    formatted_date = now.strftime('%d/%m/%Y')  # Format date as dd/mm/yyyy
    current_time = now.strftime('%H:%M')  # Format time as HH:mm (24-hour format)

    # Calculate the initial fishingday (number of days since the reference date)
    today = datetime.now().date()  # Ensure it's a date object
    fishingday = (today - reference_date).days

    # Get the last record (previous entry) to calculate the duration
    last_record = DataCollection.objects.order_by('-date', '-time').first()  # Get the most recent record

    if last_record:
        # Combine last record's date and time to create a datetime object
        last_datetime = datetime.combine(last_record.date, last_record.time)
        # Calculate the time difference between now and the last record's timestamp
        time_difference = now - last_datetime
        # Convert the difference to hours, round to the nearest whole number
        duration = round(time_difference.total_seconds() / 3600)  # No decimal places, rounding to the nearest hour
    else:
        # If there is no previous record, set the duration to 0
        duration = 0

    # Initialize the form with initial values
    form = DataCollectionForm(initial={
        'fishingday': fishingday,
        'duration': duration,  # Set the initial value of duration
    })

    if request.method == 'POST':
        form = DataCollectionForm(request.POST)
        
        if form.is_valid():
            # Save the form but do not commit yet
            new_record = form.save(commit=False)
            new_record.changed_by = request.user  # This will set the user who is logged in

            # Get the selected date and calculate derived fields
            date_input = form.cleaned_data.get('date')  # Use cleaned_data to get the parsed date
            if date_input:
                new_record.year = date_input.year
                new_record.week = date_input.isocalendar()[1]
                new_record.fishingday = (date_input - reference_date).days
            else:
                # Default to the current date if no date is provided
                new_record.year = today.year
                new_record.week = today.isocalendar()[1]
                new_record.fishingday = fishingday

            # Save the record to the database
            new_record.save()

            # Redirect after successful submission
            return redirect('datacollection')
        else:
            # Log errors for debugging
            print(form.errors)

    return render(request, 'datacollection/new_record.html', {
        'fishingday': fishingday,
        'form': form,
        'current_date': formatted_date,
        'current_time': current_time,  # Pass formatted time to template
    })
    
def edit_record_view(request, pk):
    # Retrieve the record from the database or return 404 if it doesn't exist
    record = get_object_or_404(DataCollection, pk=pk)
    
    for field in record._meta.fields:
        if getattr(record, field.name) is None:
            setattr(record, field.name, "")
    
    if request.method == 'POST':
        form = DataCollectionForm(request.POST, instance=record)  # Bind the form with the existing record
        if form.is_valid():
            # Set the user who made the change
            record.changed_by = request.user

            # Repopulate missing fields if needed
            if not form.cleaned_data.get('time'):
                form.cleaned_data['time'] = record.time
            
            # Save the updated record
            form.save()
            return redirect('datacollection')  # Redirect after successful edit
        else:
            print(form.errors)
    else:
        form = DataCollectionForm(instance=record)

    # Render the edit form template
    return render(request, 'datacollection/edit_record.html', {
        'form': form,
    })

def biotic(request, pk):
    # Retrieve the specific record from the DataCollection model using the primary key
    datacollectionobject = get_object_or_404(DataCollection.objects.annotate(
        year=ExtractYear('date'),
        week=ExtractWeek('date'),
    ), pk=pk)
    
    biotic_id = request.GET.get('biotic')
    
    biotic_delete = request.POST.get('delete')
    
    # Prepare variables for later use
    biotic_record = None
       
    # Handle the form submission
    if request.method == 'POST':
        # if the user wants to delete:
        if biotic_delete != '0':
            try:
                biotic_record = bioticData.objects.get(id=biotic_id)  # Retrieve the record
                biotic_record.delete()  # Delete the record
                return redirect(request.path)
            except bioticData.DoesNotExist:
                print('failed to delete. unknown record.')
        
        # Check if the biotic_id is provided in the URL
        if biotic_id:
            try:
                biotic_record = bioticData.objects.get(id=biotic_id)
                form = BioticDataForm(request.POST, instance=biotic_record)
            except bioticData.DoesNotExist:
                form = BioticDataForm(request.POST)
        else:
            form = BioticDataForm(request.POST)
        # Validate the form and save the data
        if form.is_valid():
            record = form.save(commit=False)
            record.datacollection = datacollectionobject
            record.species = form.cleaned_data['species']
            record.save()  # Save the bioticData instance first
            
            # Update or create the FishDetails record based on the bioticData record
            if record.collectno == 0:
                FishDetails.objects.filter(
                    collectdate=datacollectionobject.date,
                    biotic_id=record.id
                ).delete()
            else:
                FishDetails.objects.update_or_create(
                    collectdate=datacollectionobject.date,
                    collectno=record.collectno,
                    defaults={
                        'species_id': record.species.id,
                        'biotic': record,
                    },
                )
            
            return redirect(request.path)
        else:
            print(form.errors)
    
    else:
        if biotic_id:
            try:
                biotic_record = bioticData.objects.get(id=biotic_id)
                form = BioticDataForm(instance=biotic_record)
            except bioticData.DoesNotExist:
                form = BioticDataForm()
        else:
            form = BioticDataForm()
    
    # Filter bioticData records where the date matches the date of the DataCollection record
    data = bioticData.objects.filter(datacollection=datacollectionobject).annotate(
        year=ExtractYear('datacollection__date'),
        week=ExtractWeek('datacollection__date'),
    )
    
    # Aggregate data by species
    species_aggregation = defaultdict(lambda: {'count': 0, 'lengths': defaultdict(int)})
    for item in data:
        species_aggregation[item.species]['count'] += 1
        species_aggregation[item.species]['lengths'][item.totallength] += 1
    
    # Prepare the aggregated data for the template
    species_data = []
    for species, details in species_aggregation.items():
        lengths = ', '.join(f"{length}({count})" if count > 1 else f"{length}" for length, count in details['lengths'].items() if length is not None)
        species_data.append({
            'species': species,
            'count': details['count'],
            'lengths': lengths
        })  
    
    # Calculate the n'th record in the bioticData table for that week
    week_data = FishDetails.objects.filter(
        collectdate__week=datacollectionobject.week,
        collectdate__year=datacollectionobject.year
    )
    
    nth_record = week_data.count() + 1
    
    # Check if any field is None and set it to an empty string
    for value in data:
        for field in value.__class__._meta.fields:
            if getattr(value, field.name) is None:
                setattr(value, field.name, "")  # Set to empty string if None

    return render(request, 'datacollection/biotic.html', {
        'record': datacollectionobject, # The DataCollection record
        'biotic_record' : biotic_record,
        'species_data': species_data, # The aggregated bioticData records
        'data': data, # The bioticData records
        'form': form, # The form for adding new bioticData records
        'nth_record': nth_record, # The n'th record in the bioticData table for that week
    })

# Fishdetails
def fishdetails(request):
    # Extract the year and week from the 'collectdate' field in the database
    data = FishDetails.objects.annotate(
        year=ExtractYear('collectdate'),
        week=ExtractWeek('collectdate'))
    
    # Get distinct years based on the 'collectdate' field
    years = data.values_list('year', flat=True).distinct().order_by('year')
    weeks = []

    # Check if a year filter is applied in the URL
    selected_year = request.GET.get('year')
    selected_week = request.GET.get('week')
    selected_range = request.GET.get('range')
    selected_collectno = request.GET.get('collectno')
    
    # Initialize variables for later use
    fishdetailobject = None
    biotic_data = None
    stomach_data = None
    range_groups = []

    # Start with filtering by year
    if selected_year:
        selected_year = int(selected_year)  # Convert to int for comparison
        data = data.filter(year=selected_year)  # Filter data based on extracted year
        
        # Get distinct weeks for the selected year
        weeks = data.values_list('week', flat=True).distinct().order_by('week')

        # If a week filter is applied, filter further by week
        if selected_week:
            selected_week = int(selected_week)  # Convert to int for comparison
            data = data.filter(week=selected_week)
        
        # Retrieve 'collectno' values from the filtered data
        collect_numbers = data.values_list('collectno', flat=True).distinct()

        # Group the collect numbers into ranges (1-5, 6-10, etc.)
        max_collect = max(collect_numbers) if collect_numbers else 0
        range_groups = []
        
        # Generate the range groups dynamically
        for i in range(1, ceil(max_collect / 5) + 1):
            start = (i - 1) * 5 + 1
            end = i * 5
            range_groups.append({
                'start': start,
                'end': end,
                'collect_in_range': [c for c in collect_numbers if start <= c <= end]
            })

        if collect_numbers:
            min_collect = min(collect_numbers)
            max_collect = max(collect_numbers)
            range_groups.insert(0, {
                'start': min_collect,
                'end': max_collect,
                'collect_in_range': collect_numbers,
                'label': 'all'  # Add a label for easier HTML handling
            })

        if selected_range:
            if selected_range != 'all':
                # Split the range into start and end values
                range_start, range_end = map(int, selected_range.split('-'))

                # Filter the data based on collectno range
                data = data.filter(collectno__gte=range_start, collectno__lte=range_end)
            
            data = data.order_by('collectno')
                

        if selected_collectno:
            try:
                # Filter data based on collectno
                fishdetailobject = data.filter(collectno=selected_collectno)
                biotic_data = bioticData.objects.filter(id=fishdetailobject[0].biotic.id).first()
                stomach_data = StomachData.objects.filter(fishdetails__in=fishdetailobject)
        
                # Set None values to empty strings
                for dataset in [fishdetailobject, [biotic_data] if biotic_data else [], stomach_data]:
                    for obj in dataset:
                        for field in obj._meta.fields:
                            if getattr(obj, field.name) is None:
                                setattr(obj, field.name, "")
            except (ValueError, FishDetails.DoesNotExist, bioticData.DoesNotExist, StomachData.DoesNotExist, IndexError):
                fishdetailobject = biotic_data = stomach_data = None

    # Handle the form submission
    if request.method == 'POST':
        # Get the fish_id from the POST data
        fish_id = request.POST.get('fish_id')

        # Retrieve the FishDetails object or raise a 404 if it doesn't exist
        fish = get_object_or_404(FishDetails, id=fish_id)
        
        fish.changed_by = request.user  # This will set the user who is logged in

        # Define the fields that need to be updated
        fields_to_update = [
            'condition', 'total_length', 'fork_length', 'standard_length',
            'fresh_weight', 'liver_weight', 'total_wet_mass', 'stomach_content', 'gonad_mass',
            'sexe', 'ripeness', 'otolith', 'total_length_frozen', 'fork_length_frozen',
            'standard_length_frozen', 'frozen_mass', 'height', 'age', 'rings',
            'ogew1', 'ogew2', 'tissue_type', 'vial', 'comment'
        ]

        # Update the fields dynamically
        for field in fields_to_update:
            value = request.POST.get(field, getattr(fish, field))
            setattr(fish, field, value)

        # Special handling for boolean fields
        fish.dna_sample = 'dna_sample' in request.POST
        fish.micro_plastic = 'micro_plastic' in request.POST


        # Special handling for the species field
        species_id = request.POST.get('species')
        if species_id:
            try:
                # Retrieve the species object based on the species_id
                species_instance = MaintenanceSpeciesList.objects.get(species_id=species_id)
                fish.biotic.species = species_instance
                fish.biotic.save()  # Save the bioticData instance
                fish.species = species_instance
            except MaintenanceSpeciesList.DoesNotExist:
                # Handle the case where the species_id does not exist
                fish.biotic.species = None
                fish.biotic.save()  # Save the bioticData instance
                fish.species = species_instance
        
        # Save the updated fish object
        fish.save()
        
        # Save the stomach data separately
        stomach_inputs = request.POST.get('stomach_input', '').split(';')
        stomach_lengths = request.POST.get('stomach_length', '').split(';')
        stomach_numbers = request.POST.get('stomach_number', '').split(';')
        stomach_deletes = request.POST.get('stomach_delete', '').split(';')
        stomach_ids = request.POST.get('stomach_id', '').split(';')
        
        for input_value, length_value, number_value, delete_value, data_id in zip(stomach_inputs, stomach_lengths, stomach_numbers, stomach_deletes, stomach_ids):
            if delete_value == '1' and data_id:
                # Delete the existing record
                try:
                    stomach_data = StomachData.objects.get(id=data_id)
                    stomach_data.delete()
                except StomachData.DoesNotExist:
                    print(f"Stomach data with id {data_id} does not exist, cannot delete")
                continue
            
            if input_value or length_value or number_value:
                try:
                    species_instance = MaintenanceSpeciesList.objects.get(species_id=input_value)
                    if data_id:
                        # Update the existing record
                        try:
                            stomach_data = StomachData.objects.get(id=data_id)
                            stomach_data.length = length_value if length_value else None
                            stomach_data.number = number_value if number_value else None
                            stomach_data.species = species_instance
                            stomach_data.save()
                        except StomachData.DoesNotExist:
                            stomach_data = StomachData.objects.create(
                                fishdetails=fish,
                                species=species_instance,
                                length=length_value if length_value else None,
                                number=number_value if number_value else None
                            )
                    else:
                        # Create a new record
                        stomach_data, created = StomachData.objects.update_or_create(
                            fishdetails=fish,
                            species=species_instance,
                            defaults={
                                'length': length_value if length_value else None,
                                'number': number_value if number_value else None
                            }
                        )
                except MaintenanceSpeciesList.DoesNotExist:
                    # Skip creating the record if the species_id does not exist
                    print(f"Species with id {input_value} does not exist")
                    continue
        

        # Build the redirect URL with existing query parameters
        current_url = request.path
        query_params = request.GET.copy()  # Get the current query parameters

        # Redirect to the current URL with the updated query parameters
        return redirect(f'{current_url}?{urlencode(query_params)}')
    
    return render(request, 'fishdetails.html', {
        'data': data,
        'years': years,
        'weeks': weeks,
        'range_groups': range_groups,
        'selected_year': selected_year,
        'selected_week': selected_week,
        'selected_range': selected_range,
        'selected_collectno' : selected_collectno,
        'fishdetailobject': fishdetailobject,
        'biotic_data' : biotic_data,
        'stomach_data' : stomach_data,
    })

def species_search(request):
    query = request.GET.get('q', '')
    if query:
        # If the query is a number, search by species_id
        if query.isdigit():
            search = int(query)
            results = MaintenanceSpeciesList.objects.filter(species_id=search)[:10]
        else:
            # Search by 'nl_name' or 'latin_name' if it's not a number
            results = MaintenanceSpeciesList.objects.filter(
                Q(nl_name__icontains=query) | Q(latin_name__icontains=query) | Q(en_name__icontains=query)
            )[:10]
            
        results_data = [
            {'species_id': species.species_id, 'nl_name': species.nl_name, 'latin_name': species.latin_name, 'en_name': species.en_name} 
            for species in results
        ]
    else:
        results_data = []

    return JsonResponse({'results': results_data})


# Catchlocations
def catchlocations(request):
    # Retrieve all records from the FykeLocations table
    data = CatchLocations.objects.all()  # This gets all entries in the table
    
    return render(request, 'catchlocations.html', {
        'data': data  # Pass the data to the template
    })

def new_location(request):
    if request.method == 'POST':
        # Initialize the form with POST data
        form = CatchLocationsForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('catchlocations')
    else:
        # Render an empty form for GET requests
        form = CatchLocationsForm()

    # Pass the form to the context
    context = {
        'form': form,
    }
    return render(request, 'catchlocations/new_location.html', context)
    
def edit_location(request, pk):
    record = get_object_or_404(CatchLocations, pk=pk)

    if request.method == 'POST':
        # Initialize the form with POST data
        form = CatchLocationsForm(request.POST, instance=record)
        if form.is_valid():
            form.save()
            return redirect('catchlocations')  # Replace 'datacollection' with your actual URL name
    else:
        # Render an empty form for GET requests
        form = CatchLocationsForm(instance=record)

    # Pass the form to the context
    context = {
        'form': form,
    }
    return render(request, 'catchlocations/edit_location.html', context)


# Exportdata
def exportdata(request):
    data = DataCollection.objects.annotate(
        year=ExtractYear('date'),  # Extract year from the date
    )

    # Get distinct years based on the 'date' field
    years = data.values_list('year', flat=True).distinct().order_by('year')

    return render(request, 'exportdata.html', {
        'years': years  # Pass the data to the template
    })

def generate_csv_response(filename, headers, rows):
    """
    Generate a CSV HttpResponse.
    :param filename: The name of the file to download.
    :param headers: List of CSV header fields.
    :param rows: Iterable of row data.
    :return: HttpResponse with CSV content.
    """
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = f'attachment; filename="{filename}"'
    
    writer = csv.writer(response)
    writer.writerow(headers)
    writer.writerows(rows)
    
    return response

def abiotic_csv(request, year):
    headers = [
        'tidal_phase', 'salinity', 'temperature', 'wind_direction', 'wind_speed',
        'secchi_depth', 'fu_scale', 'date', 'time', 'fishingday', 'fyke', 'duration',
        'remarks', 'observer', 'changed_by_id', 'last_change'
    ]

    if year == 0:
        data_queryset = DataCollection.objects.all()
    else:
        data_queryset = DataCollection.objects.annotate(year=ExtractYear('date')).filter(year=year)

    rows = [
        [
            data.tidal_phase, data.salinity, data.temperature, data.wind_direction,
            data.wind_speed, data.secchi_depth, data.fu_scale, data.date, data.time,
            data.fishingday, data.fyke, data.duration, data.remarks,
            data.observer, data.changed_by_id, data.last_change
        ]
        for data in data_queryset
    ]

    return generate_csv_response('abiotic_fyke_fishdetails.csv', headers, rows)

def biotic_csv(request, year):
    headers = [
        # //
    ]

    if year == 0:
        data_queryset = DataCollection.objects.all()
    else:
        data_queryset = DataCollection.objects.annotate(year=ExtractYear('date')).filter(year=year)

    rows = [
        [
            # //
        ]
        for data in data_queryset
    ]

    return generate_csv_response('biotic_fyke_fishdetails.csv', headers, rows)

def cutting_csv(request, year):
    headers = [
        'collectdate', 'registrationtime', 'collectno', 'species', 'condition', 'total_length', 'fork_length', 'standard_length',
        'fresh_weight', 'liver_weight', 'total_wet_mass', 'stomach_content', 'gonad_mass',
        'sexe', 'ripeness', 'otolith', 'total_length_frozen', 'fork_length_frozen',
        'standard_length_frozen', 'frozen_mass', 'height', 'age', 'rings',
        'ogew1', 'ogew2', 'tissue_type', 'vial', 'comment'
    ]

    if year == 0:
        fish_queryset = FishDetails.objects.all()
    else:
        fish_queryset = FishDetails.objects.annotate(year=ExtractYear('collectdate')).filter(year=year)
    
    rows = [
        [
            fish.collectdate, fish.registrationtime, fish.collectno, fish.species, fish.condition, fish.total_length, fish.fork_length, fish.standard_length,
            fish.fresh_weight, fish.liver_weight, fish.total_wet_mass, fish.stomach_content, fish.gonad_mass,
            fish.sexe, fish.ripeness, fish.otolith, fish.total_length_frozen, fish.fork_length_frozen,
            fish.standard_length_frozen, fish.frozen_mass, fish.height, fish.age, fish.rings,
            fish.ogew1, fish.ogew2, fish.tissue_type, fish.vial, fish.comment
        ]
        for fish in fish_queryset
    ]
    return generate_csv_response('cutting_fyke_fishdetails.csv', headers, rows)

def stomach_csv(request, year):
    headers = [
        # //
    ]

    if year == 0:
        data_queryset = DataCollection.objects.all()
    else:
        data_queryset = DataCollection.objects.annotate(year=ExtractYear('date')).filter(year=year)

    rows = [
        [
            # //
        ]
        for data in data_queryset
    ]
    return generate_csv_response('stomach_fyke_fishdetails.csv', headers, rows)