from django.contrib import admin
from .models import ActionDefinition
from .models import Action
from .models import ActionDetail


admin.site.register(ActionDefinition)
admin.site.register(Action)
admin.site.register(ActionDetail)
