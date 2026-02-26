

from django.urls import path
from . import views
from .views import get_branches, upload_notes
from django.contrib.auth import views as auth_views

urlpatterns = [
    # Home
    path('', views.home, name='home'),

    # Authentication
    path('signup/faculty/', views.faculty_signup, name='faculty_signup'),
    path('signup/student/', views.student_signup, name='student_signup'),
    path('login/', views.user_login, name='login'),
    path('logout/', views.user_logout, name='logout'),

    # Dashboards
    path('dashboard/student/', views.student_dashboard, name='student_dashboard'),
    path('dashboard/faculty/', views.faculty_dashboard, name='faculty_dashboard'),
    #path('dashboard/notes/', views.uploaded_notes, name='uploaded_notes'),
    path("faculty/upload_notes/", upload_notes, name="upload_notes"),

    # Batch & Semester 
    path('batches/', views.batch_list, name='batch_list'),
    path('semesters/<int:batch_id>/<int:year_id>/', views.semester_list, name='semester_list'),
    path('subjects/<int:semester_id>/', views.subject_list, name='subject_list'),

    # Faculty Subject Handling
    path('faculty/subjects/', views.faculty_view_subjects, name='faculty_view_subjects'),

    
    path('get_subjects/', views.get_subjects, name='get_subjects'),
    path('get-branches/', get_branches, name='get_branches'),
    
    #upload_notes view
    path('faculty12/notes/edit/<int:note_id>/', views.edit_notes, name='edit_notes'),
    path('faculty12/notes/delete/<int:note_id>/', views.delete_notes, name='delete_notes'),

    #path('admin/simply_notes/subject/filter/', views.filter_year_semester, name='filter_year_semester'),
    path('api/get_semesters/', views.get_semesters, name='get_semesters'),  
    path("api/get_filtered_years/", views.get_filtered_years, name="get_filtered_years"),


#     path('reset_password/', auth_views.PasswordResetView.as_view(template_name="registration/password_reset.html"), name='reset_password'),

#     path('reset_password_sent/', auth_views.PasswordResetDoneView.as_view(template_name="registration/password_reset_sent.html"), name='password_reset_done'),

#     path('reset/<uidb64>/<token>/', auth_views.PasswordResetConfirmView.as_view(template_name="registration/password_reset_confirm.html"), name='password_reset_confirm'),

#     path('reset_password_complete/', auth_views.PasswordResetCompleteView.as_view(template_name="registration/password_reset_complete.html"), name='password_reset_complete'),




    # Request password reset (enter email)
    path(
        'reset_password/', 
        auth_views.PasswordResetView.as_view(
            template_name="registration/password_reset.html",
            email_template_name="registration/password_reset_email.html",  # Custom email template
            subject_template_name="registration/password_reset_subject.txt"  # Custom subject
        ), 
        name='reset_password'
    ),

    # Password reset email sent page
    path(
        'reset_password_sent/', 
        auth_views.PasswordResetDoneView.as_view(
            template_name="registration/password_reset_sent.html"
        ), 
        name='password_reset_done'
    ),

    # Password reset confirm (user sets a new password)
    path(
        'reset/<uidb64>/<token>/', 
        auth_views.PasswordResetConfirmView.as_view(
            template_name="registration/password_reset_confirm.html"
        ), 
        name='password_reset_confirm'
    ),

    # Password reset complete
    path(
        'reset_password_complete/', 
        auth_views.PasswordResetCompleteView.as_view(
            template_name="registration/password_reset_complete.html"
        ), 
        name='password_reset_complete'
    ),

]

