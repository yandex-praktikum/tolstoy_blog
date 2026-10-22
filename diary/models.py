from django.db import models


class Entry(models.Model):
    date = models.DateField()
    title = models.CharField(max_length=200)
    text = models.TextField()
    source = models.URLField()

    class Meta:
        ordering = ['date', 'pk']
