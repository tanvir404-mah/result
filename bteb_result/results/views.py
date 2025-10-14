from django.shortcuts import render, redirect
from .models import ResultPDF, StudentResult
import pdfplumber
import re

# Extract text from uploaded PDF
def extract_text_from_pdf(pdf_path):
    text = ""
    with pdfplumber.open(pdf_path) as pdf:
        for page in pdf.pages:
            text += page.extract_text() or ""
    return text

# Parse PDF text and save StudentResult
def parse_results(text, pdf_obj):
    # Example line: 748010 { gpa4: ref, gpa3: 2.60, gpa2: 3.01, gpa1: 2.95, ref_sub: 27141(T) }
    pattern = r'(\d+)\s*\{([^\}]+)\}'
    matches = re.findall(pattern, text)

    for match in matches:
        roll = match[0]
        data = match[1]

        gpa_fields = {}
        # GPA: can be number or 'ref'
        gpa_pattern = r'gpa(\d+):\s*([\d.]+|ref)'
        for gpa_match in re.findall(gpa_pattern, data):
            sem, value = gpa_match
            gpa_fields[f"gpa{sem}"] = value  # Save as string to allow 'ref'

        # Ref subjects
        ref_match = re.search(r'ref:\s*([0-9T,P, ]+)', data)
        ref_subjects = ref_match.group(1).strip() if ref_match else ""

        # Create StudentResult
        student_data = {'pdf': pdf_obj, 'roll': roll, 'ref_subjects': ref_subjects}
        student_data.update(gpa_fields)
        StudentResult.objects.create(**student_data)

# Upload PDF view
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

# Search result by roll
def search_result(request):
    query = request.GET.get('q', '')
    result = None
    if query:
        try:
            result = StudentResult.objects.get(roll=query)
        except StudentResult.DoesNotExist:
            result = None
    return render(request, 'search.html', {'result': result, 'q': query})

from .models import StudentResult
import pdfplumber
import re

def process_pdf(pdf_obj):
    text = ""
    with pdfplumber.open(pdf_obj.file.path) as pdf:
        for page in pdf.pages:
            text += page.extract_text() or ""

    # Match each student's result line
    # Example: 747990 { gpa4: ref, gpa3: ref, gpa2: 3.08, gpa1: 2.93, ref_sub: 26811(T), 27041(T), 27141(T) }
    pattern = r'(\d+)\s*\{([^\}]+)\}'
    matches = re.findall(pattern, text)

    for match in matches:
        roll = match[0]
        data = match[1]

        # Extract GPA (number or 'ref')
        gpa_fields = {}
        gpa_pattern = r'gpa(\d+):\s*([\d.]+|ref)'
        for gpa_match in re.findall(gpa_pattern, data):
            sem, value = gpa_match
            gpa_fields[f"gpa{sem}"] = value  # CharField handles both number & 'ref'

        # Extract ref subjects (everything after ref_sub:)
        ref_match = re.search(r'ref_sub:\s*([0-9T,P, ,]+)', data)
        ref_subjects = ref_match.group(1).strip() if ref_match else ""

        # Save in DB
        student_data = {'pdf': pdf_obj, 'roll': roll, 'ref_subjects': ref_subjects}
        student_data.update(gpa_fields)
        StudentResult.objects.create(**student_data)

    pdf_obj.processed = True
    pdf_obj.save()
