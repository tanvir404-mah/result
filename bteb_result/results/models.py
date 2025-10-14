from django.db import models

class ResultPDF(models.Model):
    file = models.FileField(upload_to='results_pdfs/')
    uploaded_at = models.DateTimeField(auto_now_add=True)
    processed = models.BooleanField(default=False)

class StudentResult(models.Model):
    pdf = models.ForeignKey(ResultPDF, on_delete=models.CASCADE)
    roll = models.CharField(max_length=50)
    
    gpa1 = models.CharField(max_length=10, null=True, blank=True)
    gpa2 = models.CharField(max_length=10, null=True, blank=True)
    gpa3 = models.CharField(max_length=10, null=True, blank=True)
    gpa4 = models.CharField(max_length=10, null=True, blank=True)
    gpa5 = models.CharField(max_length=10, null=True, blank=True)
    gpa6 = models.CharField(max_length=10, null=True, blank=True)
    gpa7 = models.CharField(max_length=10, null=True, blank=True)
    gpa8 = models.CharField(max_length=10, null=True, blank=True)
    
    ref_subjects = models.TextField(blank=True)
