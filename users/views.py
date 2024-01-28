from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from .forms import UserSignUp, UserUpdate
from django.contrib import messages

# Create your views here.
# def login(request):
#     return render(request, "users/login.html", {'form': form})

def signup(request):
    if request.method == "POST":
        form = UserSignUp(request.POST)
        if form.is_valid():
            form.save()
            username = form.cleaned_data.get("username")
            messages.success(request, f'Account created for {username}. You can now login.')
            return redirect("login")
    else:
        form = UserSignUp()
    return render(request, "users/signup.html", {'form': form})

@login_required
def profile(request):
    if request.method == "POST":
        file_form = UserUpdate(request.POST, request.FILES, instance=request.user.chatfiles)
        
        if file_form.is_valid():
            file_form.save()
            file_name = file_form.cleaned_data.get("file")
            messages.success(request, f'File {file_name} Uploaded. You can now chat.')
            return redirect("chatbot")
    else:
        file_form = UserUpdate(instance=request.user.chatfiles)

    context = {
        'file_form': file_form
    }
    return render(request, "users/profile.html", context)