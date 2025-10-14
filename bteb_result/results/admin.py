from django.contrib import admin
from .models import ResultPDF, StudentResult

@admin.register(ResultPDF)
class ResultPDFAdmin(admin.ModelAdmin):
    list_display = ('id', 'file', 'uploaded_at', 'processed')
    readonly_fields = ('processed',)

@admin.register(StudentResult)
class StudentResultAdmin(admin.ModelAdmin):
    list_display = ('roll', 'pdf', 'gpa1','gpa2','gpa3','gpa4','gpa5','gpa6','gpa7','gpa8','ref_subjects')
    search_fields = ('roll',)
