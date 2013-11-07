from django.db import models

# Create your models here.


class BasicModel(models.Model):
    name = models.CharField(max_length=100)
    
    def __unicode__(self):
        return self.name
    
    class Meta:
        abstract = True

class DbType(BasicModel):
    class_name = models.CharField(unique=True, max_length=100)
    filter_format = models.CharField(max_length=50, choices = (
        ('sql', 'SQL'), 
        ('javascript', 'Javascript'),
        ('python', 'Python'),))
    
    class Meta:
        verbose_name_plural = 'Database Types'
        verbose_name = 'Database Type'

class Database(BasicModel):
    db_type = models.ForeignKey(DbType, related_name='dbs')
    db_name = models.CharField(max_length=100)
    username = models.CharField(max_length=100, null=True, blank=True)
    password = models.CharField(max_length=100, null=True, blank=True)
    host = models.CharField(max_length=200, default = 'localhost')
    path = models.CharField(max_length=200, null=True, blank=True)
    port = models.IntegerField(null=True, blank=True)
    live = models.BooleanField(default=True)
    
    def conn_values(self):
        d = []
        d.append(('db_name',self.db_name))
        d.append(('username', self.username))
        d.append(('password',self.password))
        d.append(('host', self.host))
        d.append(('path', self.path))
        d.append(('port', self.port))
        return d
    
class Filter(models.Model):
    db = models.ForeignKey(Database, related_name='filters')
    code = models.TextField()
    
    def __unicode__(self):
        c = self.code[:20]
        if len(self.code) > 20:
            c += '...'
        return '%s: %s' % (self.db.name, c)
    