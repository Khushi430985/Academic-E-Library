from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import authenticate, get_user_model
from .models import Student, Faculty, Branch, Batch, Year, Semester, Subject, Note

User = get_user_model()  

# Faculty Signup Form
class FacultySignupForm(UserCreationForm):
    first_name = forms.CharField(max_length=30, required=True, help_text="Required")
    last_name = forms.CharField(max_length=30, required=True, help_text="Required")
    email = forms.EmailField(max_length=200, help_text="Required")
    
    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'email', 'password1', 'password2']

    def clean_email(self):
        email = self.cleaned_data.get('email')
        if User.objects.filter(email=email).exists():  # FIXED
            raise forms.ValidationError("This email is already in use.")
        return email

    def save(self, commit=True):
        user = super().save(commit=False)
        user.user_type = 'faculty'
        user.first_name = self.cleaned_data.get('first_name')
        user.last_name = self.cleaned_data.get('last_name')
        if commit:
            user.save()
            Faculty.objects.create(user=user)
        return user

from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError

class StudentSignupForm(UserCreationForm):
    first_name = forms.CharField(
        max_length=30, 
        widget=forms.TextInput(attrs={'class': 'form-control'})
    )
    last_name = forms.CharField(
        max_length=30, 
        widget=forms.TextInput(attrs={'class': 'form-control'})
    )
    email = forms.EmailField(
        max_length=200, 
        widget=forms.EmailInput(attrs={'class': 'form-control'})
    )
    roll_number = forms.CharField(
        max_length=20, 
        widget=forms.TextInput(attrs={'class': 'form-control'})
    )
    branch = forms.ModelChoiceField(
        queryset=Branch.objects.all(),  
        required=True, 
        widget=forms.Select(attrs={'class': 'form-control'})
    )
    batch = forms.ModelChoiceField(
        queryset=Batch.objects.all(),  
        required=True, 
        widget=forms.Select(attrs={'class': 'form-control'})
    )

    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'email', 'password1', 'password2', 'roll_number', 'branch', 'batch']

    def clean_email(self):
        """Check if email already exists."""
        email = self.cleaned_data.get('email')
        if User.objects.filter(email=email).exists():  
            raise forms.ValidationError("This email is already in use.")
        return email

    def clean_roll_number(self):
        """Check if roll number is already registered."""
        roll_number = self.cleaned_data.get('roll_number')
        if Student.objects.filter(roll_number=roll_number).exists():
            raise forms.ValidationError("This roll number is already registered.")
        return roll_number

    def clean_password1(self):
        """Validate password rules and prevent first name in password."""
        password = self.cleaned_data.get("password1")
        first_name = self.cleaned_data.get("first_name", "").lower()

        if first_name in password.lower():
            raise forms.ValidationError("Password cannot contain your first name!")

        try:
            validate_password(password)
        except ValidationError as e:
            raise forms.ValidationError(e.messages) 
        return password

    def save(self, commit=True):
        """Create user and associate student details."""
        user = super().save(commit=False)
        user.user_type = 'student'
        if commit:
            user.save()
            Student.objects.create(
                user=user,
                roll_number=self.cleaned_data['roll_number'],
                branch=self.cleaned_data['branch'],
                batch=self.cleaned_data['batch']
            )
        return user


# Login Form
class LoginForm(forms.Form):
    email = forms.EmailField(max_length=200)
    password = forms.CharField(widget=forms.PasswordInput)

    def clean(self):
        cleaned_data = super().clean()
        email = cleaned_data.get('email')
        password = cleaned_data.get('password')

        user = User.objects.filter(email=email).first()
        if not user:
            raise forms.ValidationError("This email is not registered.")

        authenticated_user = authenticate(email=email, password=password)
        if authenticated_user is None:
            raise forms.ValidationError("Invalid email or password.")

        return cleaned_data

# Note Upload Form
class NoteUploadForm(forms.ModelForm):
    batch = forms.ModelChoiceField(queryset=Batch.objects.all(), required=True)
    year = forms.ModelChoiceField(queryset=Year.objects.all(), required=True)
    branch = forms.ModelChoiceField(queryset=Branch.objects.all(), required=True)
    semester = forms.ModelChoiceField(queryset=Semester.objects.all(), required=True)
    subject = forms.ModelChoiceField(queryset=Subject.objects.all(), required=True)  

    class Meta:
        model = Note
        fields = ['batch', 'year', 'branch', 'semester', 'subject', 'title', 'description', 'file']
        widgets = {'description': forms.Textarea(attrs={'rows': 3})}

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if 'initial' in kwargs:
            initial = kwargs['initial']
            batch = initial.get('batch')
            branch = initial.get('branch')
            year = initial.get('year')
            if batch and branch and year:
                self.fields['semester'].queryset = Semester.objects.filter(year__batch=batch, year__branch=branch, year=year)
                self.fields['subject'].queryset = Subject.objects.filter(batch=batch, branch=branch, year=year)

    def clean(self):
        cleaned_data = super().clean()
        semester = cleaned_data.get('semester')
        subject = cleaned_data.get('subject')

        if subject and semester and subject.semester != semester:
            self.add_error('subject', 'The selected subject does not belong to the selected semester.')
        return cleaned_data

# Note File Form
class NoteFileForm(forms.ModelForm):
    class Meta:
        model = Note
        fields = ["file"]
        widgets = {
            "file": forms.ClearableFileInput(attrs={"class": "form-control"}),
        }

# Subject Form 
class SubjectForm(forms.ModelForm):
    class Meta:
        model = Subject
        fields = ['name', 'branch', 'semester', 'batch', 'year']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        batch = self.initial.get('batch')
        year = self.initial.get('year')
        branch = self.initial.get('branch')  
        if batch and year and branch:
            self.fields['semester'].queryset = Semester.objects.filter(year__batch=batch, year__branch=branch, year=year)
            self.fields['year'].queryset = Year.objects.filter(batch=batch)