from django.contrib import admin
from django.contrib.auth.models import User
from datamodel.models import Game, Move

# Register your models here.
#
#
# class PageAdmin (admin.ModelAdmin):
#     list_display = ['title', 'category', 'url']
#
#
# class CategoryAdmin (admin.ModelAdmin):
#     prepopulated_fields = {'slug': ('name',)}


# Register your models here.
admin.site.register(Game)
admin.site.register(Move)
# admin.site.register(Category, CategoryAdmin)
# admin.site.register(Page, PageAdmin)
# admin.site.register(UserProfile)
