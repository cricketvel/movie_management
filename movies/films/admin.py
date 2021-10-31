from django.contrib import admin

# Register your models here.
from films.models import *

admin.site.register(Films)
admin.site.register(Review)
admin.site.register(UserFavourite)
admin.site.register(Vote)
