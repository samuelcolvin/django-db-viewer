from django.contrib import admin
import DbViewer.models as m

class DbType(admin.ModelAdmin):
    list_display = ('class_name',)

admin.site.register(m.DbType, DbType)

class Database(admin.ModelAdmin):
    list_display = ('name', 'db_type', 'db_name', 'host')

admin.site.register(m.Database, Database)

class Query(admin.ModelAdmin):
    list_display = ('name', 'db', 'function', 'code')

admin.site.register(m.Query, Query)