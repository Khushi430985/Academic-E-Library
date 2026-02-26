from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth import get_user_model
from django.db import IntegrityError
from django.http import JsonResponse, HttpResponse
from django.contrib.auth.tokens import default_token_generator
from django.core.mail import send_mail
from django.utils.http import urlsafe_base64_encode
from django.utils.encoding import force_bytes
from django.contrib.sites.shortcuts import get_current_site
from django.template.loader import render_to_string
from django.urls import reverse
from .forms import FacultySignupForm, StudentSignupForm, LoginForm, NoteUploadForm, NoteFileForm
from .models import Student, Faculty, Note, Semester, Subject, Batch, Branch, Year

User = get_user_model()  

# Home Page
def home(request):
    return render(request, 'home/home.html')

# Faculty Signup
def faculty_signup(request):
    if request.method == 'POST':
        form = FacultySignupForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Faculty account created successfully! You can now log in.')
            return redirect('login')
    else:
        form = FacultySignupForm()
    return render(request, 'signup/faculty_signup.html', {'form': form})

# Student Signup
def student_signup(request):
    batches = Batch.objects.all()
    branches = Branch.objects.all()
    
    if request.method == 'POST':
        form = StudentSignupForm(request.POST)
        if form.is_valid():
            email = form.cleaned_data['email']
            password = form.cleaned_data['password1']
            first_name = form.cleaned_data['first_name']
            last_name = form.cleaned_data['last_name']
            roll_number = form.cleaned_data['roll_number']
            batch_id = form.cleaned_data['batch'].id  
            branch_id = form.cleaned_data['branch'].id  

            # Ensure batch and branch exist before proceeding
            batch = Batch.objects.get(id=batch_id)
            branch = Branch.objects.get(id=branch_id)

            # Check if email already exists
            if User.objects.filter(email=email).exists():
                messages.error(request, "Email already registered. Please use another email.")
                return render(request, 'signup/student_signup.html', {
                    'form': form, 'batches': batches, 'branches': branches
                })

            try:
                # Create User
                user = User.objects.create_user(
                    email=email,
                    password=password,
                    first_name=first_name,
                    last_name=last_name,
                    user_type="student"
                )
                
                # Create Student Profile
                Student.objects.create(
                    user=user,
                    roll_number=roll_number,
                    batch=batch,
                    branch=branch
                )
                
                messages.success(request, 'Student account created successfully! You can now log in.')
                return redirect('login')
            
            except IntegrityError:
                messages.error(request, "A database error occurred. Please try again.")
            except Exception as e:
                messages.error(request, f"An error occurred: {e}")
    else:
        form = StudentSignupForm()

    return render(request, 'signup/student_signup.html', {
        'form': form,
        'batches': batches,
        'branches': branches
    })

# Login
def user_login(request):
    if request.method == 'POST':
        form = LoginForm(request.POST)
        if form.is_valid():
            email = form.cleaned_data['email']
            password = form.cleaned_data['password']
            user = authenticate(request, email=email, password=password)
            if user:
                login(request, user)
                messages.success(request, 'You have successfully logged in.')
                if user.user_type == "faculty":
                    return redirect('faculty_dashboard')
                else:
                    return redirect('student_dashboard')
            else:
                messages.error(request, 'Invalid email or password.')
    else:
        form = LoginForm()
    
    return render(request, 'login/login.html', {'form': form})

# Student Dashboard
@login_required
def student_dashboard(request):
    student = get_object_or_404(Student, user=request.user)
    batch = student.batch  
    branch = student.branch  

    years = Year.objects.filter(batch=batch, branch=branch).order_by("year")

    selected_year = request.GET.get("year")
    selected_semester = request.GET.get("semester")
    selected_subject = request.GET.get("subject")

    semesters, subjects, notes = [], [], []
    selected_subject_obj = None  

    if selected_year:
        semesters = Semester.objects.filter(year__id=int(selected_year))

    if selected_semester:
        subjects = Subject.objects.filter(semester__id=int(selected_semester), branch=branch)

    if selected_subject:
        selected_subject_obj = Subject.objects.filter(id=int(selected_subject)).first()
        if selected_subject_obj:
            notes = Note.objects.filter(subject=selected_subject_obj)

    return render(request, "dashboard/student/student_dashboard.html", {
        "years": years,  
        "semesters": semesters,
        "subjects": subjects,
        "notes": notes,
        "selected_year": int(selected_year) if selected_year else None,
        "selected_semester": int(selected_semester) if selected_semester else None,
        "selected_subject": selected_subject_obj,
    })

@login_required
def faculty_dashboard(request):
    faculty = get_object_or_404(Faculty, user=request.user)

    batches = Batch.objects.all()
    branches, years, semesters, subjects = [], [], [], []
    notes = Note.objects.filter(faculty=faculty)  # Fetch all notes uploaded by this faculty 

    # GET request values 
    selected_batch = request.GET.get("batch")
    selected_branch = request.GET.get("branch")
    selected_year = request.GET.get("year")
    selected_semester = request.GET.get("semester")
    selected_subject = request.GET.get("subject")

    # Convert to int if not None
    selected_batch = int(selected_batch) if selected_batch else None
    selected_branch = int(selected_branch) if selected_branch else None
    selected_year = int(selected_year) if selected_year else None
    selected_semester = int(selected_semester) if selected_semester else None
    selected_subject = int(selected_subject) if selected_subject else None

    
    selected_subject_obj = None

    if selected_batch:
        branches = Branch.objects.filter(batch_id=selected_batch)

    if selected_branch:
        years = Year.objects.filter(batch_id=selected_batch, branch_id=selected_branch)

    if selected_year:
        semesters = Semester.objects.filter(year_id=selected_year)

    if selected_semester:
        subjects = Subject.objects.filter(semester_id=selected_semester, branch_id=selected_branch)

    if selected_subject:
        selected_subject_obj = Subject.objects.filter(id=selected_subject).first()
        if selected_subject_obj:
            notes = notes.filter(subject=selected_subject_obj)  # Filter notes by selected subject

    return render(request, "dashboard/faculty/faculty_dashboard.html", {
        "batches": batches,
        "branches": branches,
        "years": years,
        "semesters": semesters,
        "subjects": subjects,
        "notes": notes,
        "selected_batch": selected_batch,
        "selected_branch": selected_branch,
        "selected_year": selected_year,
        "selected_semester": selected_semester,
        "selected_subject": selected_subject_obj,  
    })


@login_required
def get_subjects(request):
    semester_id = request.GET.get('semester')
    subjects = Subject.objects.filter(semester_id=semester_id).values('id', 'name')
    return JsonResponse({'subjects': list(subjects)})

@login_required
def edit_notes(request, note_id):
    note = get_object_or_404(Note, id=note_id, faculty=request.user.faculty)  # Ensure only the correct faculty can edit

    if request.method == "POST":
        form = NoteFileForm(request.POST, request.FILES, instance=note)
        if form.is_valid():
            form.save()
            messages.success(request, "Note updated successfully!")  # Success message added
            return redirect("faculty_dashboard")  # Redirect after saving
        else:
            messages.error(request, "Failed to update note. Please check the form.")  # Error message if form fails

    else:
        form = NoteFileForm(instance=note)  

    return render(request, "faculty12/edit_notes.html", {"form": form, "note": note})

@login_required
def delete_notes(request, note_id):
    note = get_object_or_404(Note, id=note_id)

    if request.method == "POST":
        note.delete()
        messages.success(request, "Note deleted successfully!")
        return redirect("faculty_dashboard")

    return render(request, "faculty12/delete_notes.html", {"note": note})

def user_logout(request):
    logout(request)
    messages.success(request, 'You have successfully logged out.')
    return redirect('login')

def batch_list(request):
    batches = Batch.objects.all()
    return render(request, 'batch_list.html', {'batches': batches})

def year_list(request, batch_id):
    batch = get_object_or_404(Batch, id=batch_id)
    
    
    years = Year.objects.filter(batch=batch).order_by("year").distinct("year")

    return render(request, 'year_list.html', {
        'batch': batch,
        'years': years
    })

def semester_list(request, batch_id, branch_id):
    batch = get_object_or_404(Batch, id=batch_id)
    
    # Ensure correct filtering for semesters
    semesters = Semester.objects.filter(year__batch=batch, year__branch_id=branch_id)

    return render(request, 'semester_list/semester_list.html', {
        'batch': batch,
        'semesters': semesters
    })

def subject_list(request, semester_id):
    semester = get_object_or_404(Semester, id=semester_id)
    subjects = Subject.objects.filter(semester=semester)

    return render(request, 'subject/subject_list.html', {
        'semester': semester,
        'subjects': subjects
    })

def subject_detail(request, subject_id):
    subject = get_object_or_404(Subject, id=subject_id)
    notes = Note.objects.filter(subject=subject)

    return render(request, 'subject_detail/subject_detail.html', {
        'subject': subject,
        'notes': notes
    })

@login_required
def faculty_view_subjects(request):
    faculty = Faculty.objects.filter(user=request.user).first()
    if not faculty:
        return render(request, 'error.html', {'message': 'Access Denied'})

    subjects = faculty.subjects.all()
    
    return render(request, 'faculty/faculty_subjects.html', {'subjects': subjects})

def get_semesters(request):
    year_id = request.GET.get('year')  # Get selected year

    if year_id:
        # Fetch semesters for the selected year
        semesters = Semester.objects.filter(year_id=year_id)
        semesters_data = [{"id": semester.id, "name": f"Semester {semester.sem_number}"} for semester in semesters]
        return JsonResponse({"semesters": semesters_data})

    return JsonResponse({"error": "Invalid parameters. Year is required."}, status=400)

def get_filtered_years(request):
    batch_id = request.GET.get("batch")
    branch_id = request.GET.get("branch")

    if not batch_id or not branch_id:
        return JsonResponse({"error": "Batch and Branch are required."}, status=400)

    
    years = Year.objects.filter(batch_id=batch_id, branch_id=branch_id).order_by("year")
    years_data = [{"id": year.id, "name": f"{year.year} Year"} for year in years]

    return JsonResponse({"years": years_data})

def get_branches(request):
    batch_id = request.GET.get('batch_id')
    if batch_id:
        branches = Branch.objects.filter(batch_id=batch_id).values('id', 'name')
        return JsonResponse({'branches': list(branches)})
    return JsonResponse({'branches': []})

@login_required
def upload_notes(request):
    faculty = get_object_or_404(Faculty, user=request.user)

    if request.method == "POST":
        form = NoteUploadForm(request.POST, request.FILES)
        if form.is_valid():
            note = form.save(commit=False)
            note.faculty = faculty  
            note.save()

            
            batch = request.POST.get("batch", "")
            branch = request.POST.get("branch", "")
            year = request.POST.get("year", "")
            semester = request.POST.get("semester", "")
            subject = request.POST.get("subject", "")

           
            return redirect(f"/dashboard/faculty/?batch={batch}&branch={branch}&year={year}&semester={semester}&subject={subject}")

    return redirect("faculty_dashboard")

def password_reset_request(request):
    if request.method == "POST":
        email = request.POST["email"]
        try:
            user = User.objects.get(email=email)
        except User.DoesNotExist:
            return HttpResponse("No user found with this email.")  

        # Generate password reset token
        token = default_token_generator.make_token(user)
        uid = urlsafe_base64_encode(force_bytes(user.pk))

        # Get current domain
        current_site = get_current_site(request)
        domain = current_site.domain  # This should be "127.0.0.1:8000"

        # Create password reset URL
        reset_link = f"http://{domain}/reset/{uid}/{token}/"

        # Send email
        subject = "Reset Your Password"
        message = render_to_string("password_reset_email.html", {"reset_link": reset_link, "user": user})
        send_mail(subject, message, "your-email@gmail.com", [user.email])

        return HttpResponse("Password reset link has been sent to your email.")

    return render(request, "password_reset_form.html")


