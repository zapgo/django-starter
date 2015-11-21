# IMPORTS
# ---------------------------------------------------------------------------------------------------------------------#
from django.db import models
from logging import getLogger


# LOGGING
# ---------------------------------------------------------------------------------------------------------------------#
logger = getLogger('django')


# BASE MODELS
# ---------------------------------------------------------------------------------------------------------------------#
class NaturalManager(models.Manager):
    def get_by_natural_key(self, name):
        return self.get(name=name)


class NaturalModel(models.Model):
    name = models.CharField(max_length=150, unique=True)
    description = models.TextField()

    date_created = models.DateTimeField(auto_created=True)
    date_updated = models.DateTimeField(auto_now=True)

    # created_by = models.ForeignKey(User)
    # updated_by = models.ForeignKey(User)

    def natural_key(self):
        return self.name,

    objects = NaturalManager()

    def __str__(self):
        return self.name

    class Meta:
        abstract = True


# MODELS
# ---------------------------------------------------------------------------------------------------------------------#
class Dream(NaturalModel):
    pass


