from django.db import models
from django.conf import settings


class Route(models.Model):
    GENDER_PREFERENCE_CHOICES = [
        ('ANY', 'Any'),
        ('MALE_ONLY', 'Male Only'),
        ('FEMALE_ONLY', 'Female Only'),
    ]

    STATUS_CHOICES = [
        ('ACTIVE', 'Active'),
        ('PAUSED', 'Paused'),
        ('CLOSED', 'Closed'),
    ]

    owner = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='posted_routes'
    )
    home_area = models.CharField(max_length=150)
    destination = models.CharField(max_length=150)
    departure_time_start = models.TimeField(null=True, blank=True)
    departure_time_end = models.TimeField(null=True, blank=True)
    days_active = models.CharField(
        max_length=100,
        default='Sun,Mon,Tue,Wed,Thu',
        help_text='Comma-separated days active, e.g. Sun,Mon,Tue,Wed,Thu'
    )
    transport_mode = models.CharField(
        max_length=100,
        blank=True,
        help_text='Preferred transport mode e.g. Rickshaw, Bus, Ride-share'
    )
    note = models.TextField(blank=True)
    gender_preference = models.CharField(
        max_length=20,
        choices=GENDER_PREFERENCE_CHOICES,
        default='ANY'
    )
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='ACTIVE'
    )
    contact_info = models.CharField(
        max_length=15,
        blank=True,
        help_text='Contact info unlocked only after a match request is accepted'
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.home_area} ➔ {self.destination} ({self.owner.username})"


class RouteJoinRequest(models.Model):
    STATUS_CHOICES = [
        ('PENDING', 'Pending'),
        ('ACCEPTED', 'Accepted'),
        ('REJECTED', 'Rejected'),
        ('CANCELLED', 'Cancelled'),
    ]

    route = models.ForeignKey(
        Route,
        on_delete=models.CASCADE,
        related_name='join_requests'
    )
    requester = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='route_join_requests'
    )
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='PENDING'
    )
    note = models.TextField(blank=True)
    requester_contact_info = models.CharField(
        max_length=15,
        blank=True,
        help_text='Contact details shared by requester once request is accepted'
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']
        unique_together = ('route', 'requester')

    def __str__(self):
        return f"Request by {self.requester.username} for Route {self.route.id} ({self.status})"
