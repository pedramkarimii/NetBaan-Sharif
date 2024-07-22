from django.db import models


class TimestampsStatusFlagMixin(models.Model):
    """
    A mixin to add timestamp and status flag fields to a model.
    """

    create_time = models.DateTimeField(auto_now_add=True, editable=False)
    update_time = models.DateTimeField(auto_now=True, editable=False)
    is_deleted = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)

    class Meta:
        abstract = True
