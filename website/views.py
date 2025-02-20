from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from .forms import RegisterForm
import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import numpy as np
import os
from .forms import LoginForm
from django.contrib.auth.decorators import login_required #restricting access to home page
from .forms import UserUpdateForm, ProfileUpdateForm
from .models import Profile  # Import the Profile model



# Create your views here.

@login_required
def home(request):
    user_profile = Profile.objects.filter(user=request.user).first()
    recommended_jobs = []

    if user_profile and user_profile.skills:
        # Load cleaned data
        file_path = os.path.join(os.path.dirname(__file__), 'cleaned_jobs_data.csv')
        cleaned_data = pd.read_csv(file_path)
        cleaned_data['job_details'] = cleaned_data['job_details'].fillna('')

        # Vectorize job details and user skills
        vectorizer = TfidfVectorizer(stop_words='english')
        job_details_matrix = vectorizer.fit_transform(cleaned_data['job_details'])
        user_skills_vector = vectorizer.transform([user_profile.skills])

        # Calculate similarity
        similarity_scores = cosine_similarity(user_skills_vector, job_details_matrix)
        scores = list(enumerate(similarity_scores[0]))
        scores = sorted(scores, key=lambda x: x[1], reverse=True)

        # Get top 5 job recommendations
        top_jobs = scores[:5]
        recommended_jobs = [cleaned_data.iloc[i[0]].to_dict() for i in top_jobs]

    return render(request, 'home.html', {'recommended_jobs': recommended_jobs})


@login_required
def recommend_jobs(request):
    # Load cleaned data
    file_path = os.path.join(os.path.dirname(__file__), 'cleaned_jobs_data.csv')
    cleaned_data = pd.read_csv(file_path)
    cleaned_data = cleaned_data.drop_duplicates(subset=['job_ID'])
    cleaned_data['job_details'] = cleaned_data['job_details'].fillna('')

    # Get user profile skills
    user_profile = request.user.profile
    user_skills = user_profile.skills if user_profile and user_profile.skills else ''

    # Generate recommendations based on user skills
    similar_jobs = []
    if user_skills:
        vectorizer = TfidfVectorizer(stop_words='english')
        job_details_matrix = vectorizer.fit_transform(cleaned_data['job_details'])
        skills_vector = vectorizer.transform([user_skills])
        similarity_scores = cosine_similarity(skills_vector, job_details_matrix)[0]
        top_indices = np.argsort(similarity_scores)[::-1][:5]
        similar_jobs = [cleaned_data.iloc[i].to_dict() for i in top_indices]

    return render(request, 'home.html', {'similar_jobs': similar_jobs})

def register(request):
    if request.method == "POST":
        form = RegisterForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.set_password(form.cleaned_data['password'])
            user.save()
            login(request, user)  # Log in the user automatically
            return redirect('home')  # Redirect to home page
    else:
        form = RegisterForm()
    
    return render(request, 'register.html', {'form': form})

def user_login(request):
    if request.method == 'POST':
        form = LoginForm(request.POST)
        if form.is_valid():
            username = form.cleaned_data['username']
            password = form.cleaned_data['password']
            user = authenticate(request, username=username, password=password)
            if user is not None:
                login(request, user)
                return redirect('home')  # Redirect to home page after login
            else:
                return render(request, 'login.html', {'form': form, 'error': 'Invalid username or password'})
    else:
        form = LoginForm()
    
    return render(request, 'login.html', {'form': form})

def user_logout(request):
    logout(request)
    return redirect('login')  # Redirect to login page after logout

@login_required
def profile(request):
    try:
        # Check if user has a profile
        profile = request.user.profile
    except Profile.DoesNotExist:
        profile = None  # Avoid redirection; just handle the missing profile gracefully

    if request.method == 'POST':
        user_form = UserUpdateForm(request.POST, instance=request.user)
        profile_form = ProfileUpdateForm(request.POST, request.FILES, instance=profile)

        if user_form.is_valid() and profile_form.is_valid():
            user_form.save()
            profile_form.save()
            return redirect('profile')

    else:
        user_form = UserUpdateForm(instance=request.user)
        profile_form = ProfileUpdateForm(instance=profile)

    # Pass the profile object to the template for display
    return render(request, 'profile.html', {
        'user_form': user_form,
        'profile_form': profile_form,
        'profile': profile
    })


@login_required
def edit_profile(request):
    if request.method == 'POST':
        user_form = UserUpdateForm(request.POST, instance=request.user)
        profile_form = ProfileUpdateForm(request.POST, request.FILES, instance=request.user.profile)

        if user_form.is_valid() and profile_form.is_valid():
            user_form.save()
            profile_form.save()
            return redirect('profile')  # Redirect back to profile page

    else:
        user_form = UserUpdateForm(instance=request.user)
        profile_form = ProfileUpdateForm(instance=request.user.profile)

    return render(request, 'edit_profile.html', {'user_form': user_form, 'profile_form': profile_form})
