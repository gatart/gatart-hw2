from django.contrib import admin

from .models import Location, Category, Post


empty_value_display = 'Не задано'


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = (
        'title',
        'description',
        'is_published',
        'slug',
        'created_at',
    )
    list_editable = ('is_published',)
    search_fields = ('title', 'slug',)
    list_filter = ('is_published',)
    list_display_links = ('title',)


@admin.register(Location)
class LocationAdmin(admin.ModelAdmin):
    list_display = (
        'name',
        'is_published',
        'created_at',
    )
    list_editable = ('is_published',)
    search_fields = ('name',)
    list_filter = ('is_published',)
    list_display_links = ('name',)


@admin.register(Post)
class PostAdmin(admin.ModelAdmin):
    list_display = (
        'title',
        'text',
        'pub_date',
        'author',
        'location',
        'category',
        'is_published',
        'created_at',
    )
    list_editable = ('is_published',)
    search_fields = (
        'title',
        'pub_date',
        'author',
        'location',
    )
    list_filter = ('category', 'is_published',)
    list_display_links = ('title',)
