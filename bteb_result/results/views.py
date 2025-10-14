from django.shortcuts import render ,redirect
from .models import ResultPDF, StudentResult
import pdfplumber
import re

def extract_text_from_pdf(pdf_path):
    text = ""
    with pdfplumber.open(pdf_path) as pdf:
        for page in pdf.pages:
            text += page.extract_text() or ""
    return text

def parse_results(text, pdf_obj):
    lines = text.split("\n")
    for line in lines:
        match = re.search(r"Roll\s*[:\-]?\s*(\d+)", line)
        if match:
            roll = match.group(1)
            name = re.search(r"Name\s*[:\-]?\s*([A-Za-z ]+)", line)
            grade = re.search(r"GPA\s*[:\-]?\s*([0-9.]+)", line)
            StudentResult.objects.create(
                pdf=pdf_obj,
                roll=roll,
                name=name.group(1).strip() if name else "",
                grade=grade.group(1) if grade else "",
                marks_text=line
            )

def upload_pdf(request):
    message = ""
    if request.method == "POST":
        pdf_file = request.FILES['file']
        pdf_obj = ResultPDF.objects.create(file=pdf_file)
        text = extract_text_from_pdf(pdf_obj.file.path)
        parse_results(text, pdf_obj)
        pdf_obj.processed = True
        pdf_obj.save()
        message = "PDF processed successfully!"
    return render(request, 'upload.html', {'message': message})

def search_result(request):
    query = request.GET.get('q', '')
    result = None
    if query:
        try:
            result = StudentResult.objects.get(roll=query)
        except StudentResult.DoesNotExist:
            result = None

    return render(request, 'search.html', {'result': result, 'q': query})



from django.shortcuts import render
from .models import ResultPDF, StudentResult
import pdfplumber
import re

def process_pdf(pdf_obj):
    text = ""
    with pdfplumber.open(pdf_obj.file.path) as pdf:
        for page in pdf.pages:
            text += page.extract_text() or ""

    # Example line in PDF: 646967 (gpa4: 2.30, gpa3: 2.80, gpa2: 3.10, gpa1: 3.12)
    pattern = r'(\d+)\s*\(gpa4:\s*([\d.]+),\s*gpa3:\s*([\d.]+),\s*gpa2:\s*([\d.]+),\s*gpa1:\s*([\d.]+)\)'
    matches = re.findall(pattern, text)

    for match in matches:
        roll = match[0]
        gpa4 = float(match[1])
        gpa3 = float(match[2])
        gpa2 = float(match[3])
        gpa1 = float(match[4])

        StudentResult.objects.create(
            pdf=pdf_obj,
            roll=roll,
            gpa1=gpa1,
            gpa2=gpa2,
            gpa3=gpa3,
            gpa4=gpa4
        )

    pdf_obj.processed = True
    pdf_obj.save()
