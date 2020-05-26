from .models import Sanitary
from .forms import SanitaryForm
from django.utils import timezone
from django.shortcuts import render, get_object_or_404, redirect


def sanitary_book_list(request):
    sanitary_list = Sanitary.objects.order_by('name')
    return render(request, 'sanitarybook/sanitary_book_list.html', {'sanitary_list': sanitary_list})


def sanitary_book_edit(request, pk):
    sanitary = get_object_or_404(Sanitary, pk=pk)
    if request.method == "POST":
        form = SanitaryForm(request.POST, instance=sanitary)
        if form.is_valid():
            sanitary = form.save(commit=False)
            sanitary.save()
            return redirect('sanitary_book_detail', pk=sanitary.pk)
    else:
        form = SanitaryForm(instance=sanitary)
    return render(request, 'sanitarybook/sanitary_book_edit.html', {'form': form})


def sanitary_book_detail(request, pk):
    sanitary = get_object_or_404(Sanitary, pk=pk)
    return render(request, 'sanitarybook/sanitary_book_detail.html', {'sanitary': sanitary})


def sanitary_book_new(request):
    if request.method == "POST":
        form = SanitaryForm(request.POST)
        if form.is_valid():
            print("ES VALIDO BITCHES")
            sanitary = form.save(commit=False)
            sanitary.created_date = timezone.now()
            sanitary.owner = request.user
            sanitary.save()
            return redirect('sanitary_book_detail', pk=sanitary.pk)

    else:
        form = SanitaryForm()
        return render(request, 'sanitarybook/sanitary_book_edit.html', {'form': form})
