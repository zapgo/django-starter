from django.core.urlresolvers import reverse
from django.db import models
from django.utils.translation import ugettext_lazy as _
from mptt.models import MPTTModel


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


class Thing(MPTTModel):
    name = models.CharField(max_length=250)

    description = models.TextField(blank=True, default='')

    AP = 'AP'
    EC = 'EC'
    GS = 'GS'
    CI = 'CI'
    SL = 'SL'

    STRUCTURAL_LINK_OPTIONS = (
        (AP, _('part')),  # _('Aggregation-Participation')),
        (EC, _('characteristic')),  # _('Exhibition-Characterization')),
        (GS, _('type')),  # _('Generalization-Specialization')),
        (CI, _('instance')),  # _('Classification-Instantiation')),
        (SL, _('state')),  # _('Classification-Instantiation')),
    )

    link_type = models.CharField(
        max_length=2, choices=STRUCTURAL_LINK_OPTIONS,
        default=GS, verbose_name=_('Structural Link Type'),
        help_text=_('https://en.wikipedia.org/wiki/Object_Process_Methodology#Structural_and_Procedural_Links'))

    parent = TreeForeignKey('self', null=True, blank=True, related_name='children', db_index=True)

    data = JSONField(blank=True, null=True)

    order = models.PositiveIntegerField(blank=True, default=0)

    def get_absolute_url(self):
        return reverse('demo_app:thing_detail', kwargs={'pk': str(self.id)})

    def __str__(self):
        return self.name

    class Meta:
        ordering = ['tree_id', 'lft']
        verbose_name = _('Thing')
        verbose_name_plural = _('Things')

        # class MPTTMeta:
        #     order_insertion_by = ['order']


class SubThing(Thing):
    special_attribute = models.CharField(max_length=123)

    class Meta:
        ordering = ['tree_id', 'lft']
        verbose_name = _('Sub Thing')
        verbose_name_plural = _('Sub Things')


class SubThingFiltered(SubThing):
    class Meta:
        proxy = True

