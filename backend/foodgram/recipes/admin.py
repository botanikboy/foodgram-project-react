from django.contrib import admin
from models import Ingredient, Recipe, Tag, User

admin.site.register([User, Recipe, Ingredient, Tag])
