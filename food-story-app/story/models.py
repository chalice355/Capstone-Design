from django.db import models


class Diary(models.Model):
    food_name = models.CharField(max_length=100)
    place     = models.CharField(max_length=200, blank=True)
    date      = models.DateField()
    tabs_json = models.JSONField(default=dict)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.date} — {self.food_name} ({self.place})"
