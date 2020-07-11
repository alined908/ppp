from django.db import models

class Business(models.Model):
    name = models.TextField()
    address = models.TextField()
    city = models.CharField(max_length=255)
    state = models.CharField(max_length=2)
    zip_code = models.IntegerField()
    latitude = models.FloatField()
    longitude = models.FloatField()
    naics_code = models.IntegerField()
    business_type = models.CharField(max_length=100)
    ethnicity = models.CharField(max_length=255, null=True, blank=True)
    gender = models.CharField(max_length=100, null=True, blank=True)
    veteran = models.CharField(max_length=100, null=True, blank=True)
    nonprofit = models.BooleanField(null=True, blank=True)
    employee_lower_bound = models.IntegerField(null=True, blank=True)
    employee_upper_bound = models.IntegerField(null=True, blank=True)
    
class Lender(models.Model):
    name = models.CharField(max_length=255)
    loans_given = models.IntegerField(default=0)

class Loan(models.Model):
    business = models.ForeignKey(Business, null=True, blank=True, on_delete=models.SET_NULL)
    lender = models.ForeignKey(Lender, null=True, blank=True, on_delete=models.SET_NULL)
    loan_lower_bound = models.FloatField()
    loan_upper_bound = models.FloatField()
    jobs_retained = models.IntegerField(null=True, blank=True)
    date_approved = models.DateField()

    def __save__(self, *args, **kwargs):
        if self.pk is None and self.lender:
            self.lender.loans_given += 1
            self.lender.save()
        super(Loan).save(*args, **kwargs)

