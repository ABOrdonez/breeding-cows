from .models import Sanitary
from .forms import SanitaryForm
from django.utils import timezone
from django.shortcuts import render, get_object_or_404, redirect
from animals.models import AnimalSanitary, Animals
from django.core.paginator import Paginator
from rest_framework.views import APIView
from rest_framework.response import Response
from django.views.decorators.csrf import csrf_exempt


def sanitary_book_list(request):
    sanitary_list = Sanitary.objects.filter(
        delete_date__isnull=True,
    ).order_by(
        'name'
    )
    sanitaries = []

    for sanitary in sanitary_list:
        sanitaries.append([
            sanitary,
            AnimalSanitary.objects.all().filter(sanitary=sanitary).count()
        ])

    paginator = Paginator(sanitaries, 4)
    page = request.GET.get('page')
    sanitaries_pagenated = paginator.get_page(page)

    return render(
        request,
        'sanitarybook/sanitary_book_list.html',
        {'sanitary_list': sanitaries_pagenated}
    )


def sanitary_book_edit(request, pk):
    sanitary = get_object_or_404(Sanitary, pk=pk)
    if request.method == "POST":
        form = SanitaryForm(request.POST, instance=sanitary)
        if form.is_valid():
            sanitary = form.save(commit=False)
            if not sanitary.copper:
                sanitary.copper = 0
            if not sanitary.clostridiosis:
                sanitary.clostridiosis = 0
            sanitary.save()
            return redirect('sanitary_book_detail', pk=sanitary.pk)
    else:
        form = SanitaryForm(instance=sanitary)
    return render(request, 'sanitarybook/sanitary_book_edit.html', {'form': form})


def sanitary_book_detail(request, pk):
    sanitary = get_object_or_404(Sanitary, pk=pk)
    animals = AnimalSanitary.objects.values_list(
        'animal',
        flat=True
    ).filter(
        sanitary=sanitary
    )
    breeding_cows_list = []

    for animal in animals:
        animalposta = get_object_or_404(Animals, pk=animal)
        breeding_cows_list.append(animalposta.breeding_cows)

    return render(
        request,
        'sanitarybook/sanitary_book_detail.html',
        {
            'sanitary': sanitary,
            'animal_count': len(animals),
            'breeding_cows_count': len(set(breeding_cows_list))
        }
    )


def sanitary_book_new(request):
    if request.method == "POST":
        form = SanitaryForm(request.POST)
        if form.is_valid():
            sanitary = form.save(commit=False)
            sanitary.created_date = timezone.now()
            sanitary.owner = request.user
            if not sanitary.copper:
                sanitary.copper = 0
            if not sanitary.clostridiosis:
                sanitary.clostridiosis = 0
            sanitary.save()
            return redirect('sanitary_book_detail', pk=sanitary.pk)
    else:
        form = SanitaryForm()
        return render(
            request,
            'sanitarybook/sanitary_book_edit.html',
            {'form': form}
        )


def sanitary_book_delete(request, pk):
    sanitaryBook = get_object_or_404(Sanitary, pk=pk)
    Sanitary.add_delete_date(sanitaryBook)

    return redirect('sanitary_book_list')


@csrf_exempt
def sanitary_book_undo_delete(request):
    if request.method == "POST":
        sanitaryBook = get_object_or_404(
            Sanitary,
            id=request.POST['idSanitary']
        )
        sanitaryBook.delete_date = None
        sanitaryBook.save()

    sanitaryBooksList = Sanitary.objects.filter(
        delete_date__isnull=False,
    ).order_by(
        'name'
    )

    return render(
        request,
        'sanitarybook/sanitary_undo_delete.html',
        {
            'sanitaryBooks': sanitaryBooksList,
        }
    )


class ChartData(APIView):
    authentication_classes = []
    permission_classes = []

    def get(self, request, format=None):
        sanitaries_all = Sanitary.objects.filter(
            delete_date__isnull=True,
        ).order_by(
            'name'
        )
        sanitary_name = Sanitary.objects.filter(
            delete_date__isnull=True,
        ).order_by(
            'name'
        ).values_list(
            'name',
            flat=True
        )
        sanitary_animal_types = Sanitary.objects.filter(
            delete_date__isnull=True,
        ).order_by(
            'name'
        ).values_list(
            'animal_type',
            flat=True
        )
        sanitary_copper = Sanitary.objects.filter(
            delete_date__isnull=True,
        ).order_by(
            'name'
        ).values_list(
            'copper',
            flat=True
        )
        sanitary_clostridiosis = Sanitary.objects.filter(
            delete_date__isnull=True,
        ).order_by(
            'name'
        ).values_list(
            'clostridiosis',
            flat=True
        )

        sanitary_animal_count = []
        for sanitary in sanitaries_all:
            sanitary_animal_count.append(
                AnimalSanitary.objects.all().filter(sanitary=sanitary).count()
            )

        data = {
            "sanitary": sanitary_name,
            "sanitary_animal_types": sanitary_animal_types,
            "sanitary_copper": sanitary_copper,
            "sanitary_clostridiosis": sanitary_clostridiosis,
            "sanitary_animal_count": sanitary_animal_count,
        }
        return Response(data)
