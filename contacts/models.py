from django.db import models


class Contact(models.Model):
    name = models.CharField(max_length=120)
    email = models.EmailField(unique=True)
    company = models.CharField(max_length=120, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self) -> str:
        return f"{self.name} <{self.email}>"
