from django.contrib import admin
import DbViewer.models as m

class DbType(admin.ModelAdmin):
    list_display = ('name', 'class_name')

admin.site.register(m.DbType, DbType)

class Database(admin.ModelAdmin):
    list_display = ('name', 'db_type', 'db_name', 'host')

admin.site.register(m.Database, Database)

class Filter(admin.ModelAdmin):
    list_display = ('db', 'code')

admin.site.register(m.Filter, Filter)