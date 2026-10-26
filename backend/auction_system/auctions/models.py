from django.db import models
from django.utils import timezone


class Auction(models.Model):
    # Dostępne statusy aukcji
    STATUS_CHOICES = [
        ("planned", "Planned"),
        ("active", "Active"),
        ("ended", "Ended"),
    ]

    # Nazwa przedmiotu
    name = models.CharField(max_length=255)

    # Opis aukcji
    description = models.TextField()

    # Kategoria
    category = models.CharField(max_length=100)

    # Cena wywoławcza
    starting_price = models.DecimalField(max_digits=10, decimal_places=2, default=0)

    # Aktualna najwyższa cena
    current_price = models.DecimalField(max_digits=10, decimal_places=2)

    # Data rozpoczęcia
    start_date = models.DateTimeField()

    # Data zakończenia
    end_date = models.DateTimeField()

    # Id właściciela
    owner_id = models.IntegerField()

    # Status aukcji
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="planned")

    def __str__(self):
        return self.name

    def update_status(self):
        now = timezone.now()

        if now < self.start_date:
            new_status = "planned"
        elif now >= self.end_date:
            new_status = "ended"
        else:
            new_status = "active"

        if self.status != new_status:
            self.status = new_status
            self.save(update_fields=["status"])


class Bid(models.Model):
    auction = models.ForeignKey(Auction, on_delete=models.CASCADE)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.auction} - {self.amount}"
