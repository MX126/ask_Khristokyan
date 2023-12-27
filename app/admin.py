from django.contrib import admin

# Register your models here.
from .models import Profile, Question, Answer, Tag, Vote


admin.site.register(Profile)
admin.site.register(Question)
admin.site.register(Answer)
admin.site.register(Tag)
admin.site.register(Vote)
