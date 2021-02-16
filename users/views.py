from django.shortcuts import render, redirect
from .forms import UserRegisterForm
from django.contrib.auth.decorators import login_required


def register(request):
    error = False
    if request.method == "POST":
        form = UserRegisterForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('login')
        else:
            error = True
    else:
        form = UserRegisterForm()
    return render(request, 'users/register.html', {'form': form, 'error': error})


@login_required
def profile(request):
    return render(request, 'users/profile.html')
