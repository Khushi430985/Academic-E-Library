from django.contrib import admin
from .models import User, Branch, Batch, Year, Semester, Subject, Faculty, Student, Note
from .forms import SubjectForm
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin

# Batch Admin
class BatchAdmin(admin.ModelAdmin):
    list_display = ('year',)
    search_fields = ('year',)

admin.site.register(Batch, BatchAdmin)

# Custom User Admin
class CustomUserAdmin(BaseUserAdmin):
    fieldsets = (
        (None, {'fields': ('email', 'password')}), 
        ('Personal info', {'fields': ('first_name', 'last_name')}), 
        ('User Type', {'fields': ('user_type',)}),
        ('Permissions', {'fields': ('is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions')}), 
        ('Important dates', {'fields': ('last_login', 'date_joined')}), 
    )
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('email', 'password1', 'password2', 'first_name', 'last_name'),
        }),
    )
    list_display = ('email', 'first_name', 'last_name', 'user_type', 'is_staff')
    search_fields = ('email', 'first_name', 'last_name')
    list_filter = ('user_type', 'is_staff', 'is_superuser', 'is_active', 'groups')
    ordering = ('email',)

admin.site.register(User, CustomUserAdmin)

# Note Admin
class NoteAdmin(admin.ModelAdmin):
    list_display = ('title', 'faculty', 'subject', 'created_at')
    search_fields = ('title', 'faculty__email', 'subject__name')
    list_filter = ('subject', 'created_at')
    readonly_fields = ('created_at',)

admin.site.register(Note, NoteAdmin)

# Branch Admin
class BranchAdmin(admin.ModelAdmin):
    list_display = ('name', 'batch')
    search_fields = ('name', 'batch__year')

admin.site.register(Branch, BranchAdmin)


# Year Admin
class YearAdmin(admin.ModelAdmin):
    list_display = ('year', 'get_batch', 'get_branch')  # Updated to use related fields
    search_fields = ('year', 'batch__year', 'branch__name')  # Searching by batch and branch

    def get_batch(self, obj):
        return obj.batch.year if obj.batch else '-'
    get_batch.short_description = 'Batch'

    def get_branch(self, obj):
        return obj.branch.name if obj.branch else '-'
    get_branch.short_description = 'Branch'

admin.site.register(Year, YearAdmin)



# Semester Admin
class SemesterAdmin(admin.ModelAdmin):
    list_display = ('get_semester_name', 'get_year', 'get_branch', 'get_batch') 
    search_fields = ('batch__year', 'year__year', 'branch__name')  
    list_filter = ('year',)  

    def get_semester_name(self, obj):
        return f"Year {obj.year.year} - Semester {obj.sem_number}"
    get_semester_name.short_description = 'Semester Name'

    def get_year(self, obj):
        return obj.year.year if obj.year else '-'
    get_year.short_description = 'Year'

    def get_branch(self, obj):
        return obj.year.branch.name if obj.year else '-'
    get_branch.short_description = 'Branch'

    def get_batch(self, obj):
        return obj.year.batch.year if obj.year else '-'
    get_batch.short_description = 'Batch'

admin.site.register(Semester, SemesterAdmin)


# Subject Admin
from django.contrib import admin
from .models import Subject, Year, Semester, Batch, Branch
from django import forms
from django.utils.html import format_html


class SubjectForm(forms.ModelForm):
    class Meta:
        model = Subject
        fields = "__all__"

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.fields["year"].queryset = Year.objects.none()
        self.fields["semester"].queryset = Semester.objects.none()

        if 'batch' in self.data and 'branch' in self.data:
            try:
                batch_id = int(self.data.get('batch'))
                branch_id = int(self.data.get('branch'))

                #  Filtering Years based on Batch & Branch
                self.fields['year'].queryset = Year.objects.filter(batch_id=batch_id, branch_id=branch_id)

                if 'year' in self.data and self.data.get('year').isdigit():
                    year_id = int(self.data.get('year'))

                    #  Filtering Semesters based on selected Year
                    self.fields['semester'].queryset = Semester.objects.filter(year_id=year_id)
                else:
                    self.fields['semester'].queryset = Semester.objects.none()  # Empty if no valid year
            except (ValueError, TypeError):
                self.fields['year'].queryset = Year.objects.none()
                self.fields['semester'].queryset = Semester.objects.none()


class SubjectAdmin(admin.ModelAdmin):
    form = SubjectForm
    list_display = ('name', 'branch', 'semester', 'batch', 'year')
    search_fields = ('name', 'branch__name', 'semester__sem_number', 'batch__year', 'year__year')
    list_filter = ('branch', 'semester', 'batch', 'year')

    
    class Media:
        js = ('js/admin_custom.js',)  

        def get_form(self, request, obj=None, **kwargs):
            form = super().get_form(request, obj, **kwargs)

            batch_id = request.GET.get('batch')
            branch_id = request.GET.get('branch')

            if batch_id and branch_id:
                try:
                    batch_id = int(batch_id)
                    branch_id = int(branch_id)

                    # Filter Years based on selected Batch & Branch
                    form.base_fields['year'].queryset = Year.objects.filter(batch_id=batch_id, branch_id=branch_id)

                    # Get all years matching the batch and branch
                    matching_years = Year.objects.filter(batch_id=batch_id, branch_id=branch_id)

                    # Filter Semesters based on matching Years
                    form.base_fields['semester'].queryset = Semester.objects.filter(year__in=matching_years)

                except (ValueError, TypeError):
                    pass  # If invalid data is provided, just use the default empty queryset

                
            return form



admin.site.register(Subject, SubjectAdmin)
