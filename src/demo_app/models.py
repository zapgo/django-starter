from django.db import models

# Create your models here.


class NaturalManager(models.Manager):
    def get_by_natural_key(self, name):
        return self.get(name=name)


class Job(models.Model):
    TYPES = (
        ('fibonacci', 'fibonacci'),
        ('power', 'power'),
    )

    STATUSES = (
        ('pending', 'pending'),
        ('started', 'started'),
        ('finished', 'finished'),
        ('failed', 'failed'),
    )

    type = models.CharField(choices=TYPES, max_length=20)
    status = models.CharField(choices=STATUSES, max_length=20)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    argument = models.PositiveIntegerField()
    result = models.IntegerField(null=True)

    def save(self, *args, **kwargs):
        super(Job, self).save(*args, **kwargs)
        if self.status == 'pending':
            from .tasks import TASK_MAPPING
            task = TASK_MAPPING[self.type]
            task.delay(job_id=self.id, n=self.argument)

    def _str__(self):
        return self.type


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


class Dream(NaturalModel):
    pass
