from datetime import date, datetime, time
from django.db import models

from accounts.models import User, UserProfile
from accounts.utils import send_notification

# Create your models here.
class Vendor(models.Model):
  user = models.OneToOneField(User, related_name='user_vendor', on_delete=models.CASCADE)
  user_profile = models.OneToOneField(UserProfile, related_name='vendor_by_user_profile', on_delete=models.CASCADE)
  vendor_name = models.CharField(max_length=50)
  vendor_slug = models.SlugField(max_length=100, unique=True)
  vendor_license = models.ImageField(upload_to='vendor/license')
  is_approved = models.BooleanField(default=False)
  created_at = models.DateTimeField(auto_now_add=True)
  modified_at = models.DateTimeField(auto_now=True)

  def __str__(self):
    return self.vendor_name
  
  def is_open(self):
    # Check current day's opening hours
    today_date = date.today()
    today = today_date.isoweekday()
    current_opening_hours = OpeningHour.objects.filter(vendor=self, day=today)
    # Check current time now
    now = datetime.now()
    current_time = now.strftime("%H:%M:%S")

    is_open = None
    for c_o_hour in current_opening_hours:
      if c_o_hour.from_hour and c_o_hour.to_hour:
        start = str(datetime.strptime(c_o_hour.from_hour, '%I:%M %p').time())
        end = str(datetime.strptime(c_o_hour.to_hour, '%I:%M %p').time())
        if start < current_time < end:
          is_open = True
          break
        else:
          is_open = False
    return is_open
    
  def save(self, *args, **kwargs):
    if self.pk is not None:
      # Update
      origin = Vendor.objects.get(pk=self.pk)
      if origin.is_approved != self.is_approved:
        mail_template = 'accounts/emails/admin_approval_email.html'
        context = {
            'user': self.user,
            'is_approved': self.is_approved,
            'to_email': self.user.email,
        }
        if self.is_approved == True:
          # Send notification email
          mail_subject = 'Congratulations! Your restaurant has been approved!'
          send_notification(mail_subject, mail_template, context)
        else:
          # Send notification email
          mail_subject = "We're sorry! You are not eligible for publishing your food menu on our marketplace."
          send_notification(mail_subject, mail_template, context)
    return super(Vendor, self).save(*args, **kwargs)
  
DAYS = [
  (1, ("Monday")),
  (2, ("Tuesday")),
  (3, ("Wednesday")),
  (4, ("Thursday")),
  (5, ("Friday")),
  (6, ("Saturday")),
  (7, ("Sunday")),
]

HOUR_OF_DAYS = [(time(hour, minute).strftime('%I:%M %p'), time(hour, minute).strftime('%I:%M %p')) for hour in range(0, 24) for minute in (0, 30)]
class OpeningHour(models.Model):
  vendor = models.ForeignKey(Vendor, on_delete=models.CASCADE)
  day = models.IntegerField(choices=DAYS)
  from_hour = models.CharField(choices=HOUR_OF_DAYS, max_length=10, blank=True)
  to_hour = models.CharField(choices=HOUR_OF_DAYS, max_length=10, blank=True)
  is_closed = models.BooleanField(default=False)
  created_at = models.DateTimeField(auto_now_add=True)

  class Meta:
    ordering = ('day', 'from_hour')
    unique_together = ('vendor', 'day', 'from_hour', 'to_hour')

  def __str__(self):
    return self.get_day_display()