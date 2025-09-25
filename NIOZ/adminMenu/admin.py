from django.contrib import admin
from .models import Person 

# Admin configuration for the Person model
class PersonAdmin(admin.ModelAdmin):
    list_display = ('user', 'realName', 'collectlocation', 'yearFrom', 'yearUntil')
    search_fields = ('user__username', 'realName', 'collectlocation')
    list_filter = ('yearFrom', 'yearUntil')
    ordering = ('user',)

# Register the model with the Django Admin
admin.site.register(Person, PersonAdmin)