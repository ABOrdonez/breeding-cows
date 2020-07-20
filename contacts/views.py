from .models import Contact
from breedingcows.models import WorkPosition
from django.shortcuts import render, get_object_or_404, redirect
from .forms import ContactForm
from django.utils import timezone
from django.core.paginator import Paginator


def contacts_list(request):
    contacts = Contact.objects.order_by('last_name')

    paginator = Paginator(contacts, 7)
    page = request.GET.get('page')
    contacts_pagenated = paginator.get_page(page)

    return render(
        request,
        'contacts/contacts_list.html',
        {'contacts': contacts_pagenated}
    )


def contact_detail(request, pk):
    contact = get_object_or_404(Contact, pk=pk)

    work_positions = WorkPosition.objects.all().filter(person=contact)

    return render(request, 'contacts/contact_detail.html',
                  {'contact': contact, 'work_positions': work_positions})


def contact_edit(request, pk):
    contact = get_object_or_404(Contact, pk=pk)
    if request.method == "POST":
        form = ContactForm(request.POST, instance=contact)
        if form.is_valid():
            contact = form.save(commit=False)
            contact.save()
            return redirect('contact_detail', pk=contact.pk)
    else:
        form = ContactForm(instance=contact)
    return render(request, 'contacts/contact_edit.html', {'form': form})


def contact_new(request):
    if request.method == "POST":
        form = ContactForm(request.POST)
        if form.is_valid():
            contact = form.save(commit=False)
            contact.entry_date = timezone.now()
            contact.owner = request.user
            contact.save()
            return redirect('contact_detail', pk=contact.pk)
    else:
        form = ContactForm()
        return render(request, 'contacts/contact_edit.html', {'form': form})
