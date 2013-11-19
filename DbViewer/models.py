from django.db import models
import DbInspect


class BasicModel(models.Model):
    name = models.CharField(max_length=100)
    
    def __unicode__(self):
        return self.name
    
    class Meta:
        abstract = True

class DbType(models.Model):
    class_name = models.CharField(unique=True, max_length=100, choices = (
        ('MySql', 'MySql'), 
        ('SqlLite', 'SqlLite'),
        ('MongoDb', 'MongoDb'),))
    filter_format = models.CharField(max_length=50, choices = (
        ('sql', 'SQL'), 
        ('javascript', 'Javascript'),
        ('python', 'Python'),))
    dft_port = models.IntegerField('Default Port', null=True, blank=True)
    
    def __unicode__(self):
        return self.class_name
    
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
    port.help_text = 'Leave Blank to use DB type default'
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
    
    def get_comms(self):
        Comms = getattr(DbInspect, self.db_type.class_name)
        return Comms(dict(self.conn_values()))
    
    def save(self, *args, **kw):
        super(Database, self).save(*args, **kw)
        if self.port is None:
            self.port = self.db_type.dft_port
        super(Database, self).save(*args, **kw)
    
class Query(BasicModel):
    db = models.ForeignKey(Database, related_name='filters',
                           verbose_name = 'Database')
    code = models.TextField()
    function = models.CharField(max_length=50, default='dft', choices = (
        ('dft', 'Default'),
        ('aggregate', 'Aggregate (MongoDB Only)'),
        ('map_reduce', 'Map/Reduce (MongoDB Only)'),))
    
    def __unicode__(self):
        return '%s: %s' % (self.db.name, self.name)
    
    class Meta:
        verbose_name_plural = 'Queries'
        verbose_name = 'Query'
    