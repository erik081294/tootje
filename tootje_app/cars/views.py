from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import Car
from .forms import CarForm

@login_required
def car_list(request):
    my_cars = Car.objects.filter(owner=request.user).order_by('-created_at')
    available_cars = Car.objects.exclude(owner=request.user)
    return render(request, 'cars/car_list.html', {
        'my_cars': my_cars,
        'available_cars': available_cars
    })

@login_required
def car_detail(request, car_id):
    car = get_object_or_404(Car, id=car_id)
    return render(request, 'cars/car_detail.html', {
        'car': car
    })

@login_required
def car_create(request):
    if request.method == 'POST':
        form = CarForm(request.POST)
        if form.is_valid():
            car = form.save(commit=False)
            car.owner = request.user
            car.save()
            messages.success(request, 'Auto succesvol toegevoegd.')
            return redirect('cars:car_detail', car_id=car.id)
    else:
        form = CarForm()
    
    return render(request, 'cars/car_form.html', {
        'form': form
    })

@login_required
def car_edit(request, car_id):
    car = get_object_or_404(Car, id=car_id, owner=request.user)
    
    if request.method == 'POST':
        form = CarForm(request.POST, instance=car)
        if form.is_valid():
            form.save()
            messages.success(request, 'Auto succesvol bijgewerkt.')
            return redirect('cars:car_detail', car_id=car.id)
    else:
        form = CarForm(instance=car)
    
    return render(request, 'cars/car_form.html', {
        'form': form,
        'car': car
    })

@login_required
def car_delete(request, car_id):
    car = get_object_or_404(Car, id=car_id)
    
    if car.owner != request.user:
        messages.error(request, 'Je hebt geen toestemming om deze auto te verwijderen.')
        return redirect('cars:car_detail', car_id=car.id)
    
    if request.method == 'POST':
        car.delete()
        messages.success(request, 'Auto succesvol verwijderd.')
        return redirect('cars:car_list')
    
    return render(request, 'cars/car_confirm_delete.html', {
        'car': car
    })
