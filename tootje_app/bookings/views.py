from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import HttpResponseForbidden, JsonResponse
from django.utils import timezone
import pytz  # Voeg deze import toe
from .models import Booking
from cars.models import Car
from django.core.exceptions import ValidationError
from datetime import datetime, timedelta
from decimal import Decimal
from .forms import BookingForm

def get_available_dates(car, days_ahead=14):
    """
    Get available dates for a car for the next X days.
    Returns a list of dates that are available for booking.
    """
    today = datetime.now().date()
    date_list = []
    
    # Get all existing bookings for this car within the date range
    end_date = today + timedelta(days=days_ahead)
    existing_bookings = Booking.objects.filter(
        car=car,
        start_time__date__lte=end_date,
        end_time__date__gte=today,
        status__in=['CONFIRMED', 'PENDING']  # Check beide statussen
    )
    
    # Check each day
    for i in range(days_ahead):
        current_date = today + timedelta(days=i)
        is_available = True
        
        # Check if the date conflicts with any existing booking
        for booking in existing_bookings:
            if (booking.start_time.date() <= current_date <= booking.end_time.date()):
                is_available = False
                break
        
        if is_available:
            date_list.append(current_date)
    
    return date_list

@login_required
def booking_create(request, car_id):
    print("\n=== DEBUG: Starting booking_create ===")
    print(f"car_id: {car_id}")
    
    car = get_object_or_404(Car, id=car_id)
    print(f"Found car: {car}")
    
    # Get initial dates from GET parameters
    initial = {}
    if 'start' in request.GET:
        initial['start'] = request.GET.get('start')
    if 'end' in request.GET:
        initial['end'] = request.GET.get('end')
    
    if request.method == 'POST':
        print("\n=== POST Request Data ===")
        print("POST data:", request.POST)
        
        form = BookingForm(data=request.POST, car=car)
        print("\n=== Form Initialization ===")
        print(f"Form bound: {form.is_bound}")
        print(f"Form data: {form.data}")
        
        # Eerst de instance voorbereiden met car en user
        booking = form.instance
        booking.car = car
        booking.user = request.user
        
        if form.is_valid():
            print("\n=== Form is Valid ===")
            try:
                print("\n=== Attempting Save ===")
                form.save()  # Nu direct opslaan omdat car en user al zijn ingesteld
                print("Save successful")
                
                messages.success(request, 'Reservering succesvol aangemaakt.')
                return redirect('bookings:my_bookings')
            except ValidationError as e:
                print("\n=== ValidationError Caught ===")
                print(f"Validation error: {e}")
                print(f"Error dict: {e.message_dict if hasattr(e, 'message_dict') else 'No message dict'}")
                
                for field, errors in (e.message_dict.items() if hasattr(e, 'message_dict') else {'': [str(e)].items()}):
                    for error in errors:
                        print(f"Adding error to form - Field: {field}, Error: {error}")
                        form.add_error(field if field != '__all__' else None, error)
        else:
            print("\n=== Form Invalid ===")
            print("Form errors:", form.errors)
            print("Form non field errors:", form.non_field_errors())
    else:
        print("\n=== GET Request ===")
        form = BookingForm(car=car, initial=initial)
    
    available_dates = get_available_dates(car)
    print(f"\nAvailable dates: {available_dates}")
    
    context = {
        'form': form,
        'car': car,
        'available_dates': available_dates
    }
    
    print("\n=== Final Context ===")
    print(f"Context car: {context['car']}")
    print(f"Form in context is bound: {context['form'].is_bound}")
    print("=== End booking_create ===\n")
    
    return render(request, 'bookings/booking_form.html', context)

@login_required
def booking_list(request):
    # Haal de boekingen op die de gebruiker zelf heeft gemaakt
    user_bookings = request.user.bookings.all().order_by('-start_time')
    
    # Haal de boekingen op voor auto's waarvan de gebruiker eigenaar is
    owner_bookings = Booking.objects.filter(
        car__owner=request.user
    ).exclude(
        user=request.user  # Excludeer eigen boekingen
    ).order_by('-start_time')
    
    return render(request, 'bookings/booking_list.html', {
        'user_bookings': user_bookings,
        'owner_bookings': owner_bookings
    })

@login_required
def booking_detail(request, booking_id):
    print("\n=== DEBUG: booking_detail ===")
    print(f"Booking ID: {booking_id}")
    
    booking = get_object_or_404(Booking, id=booking_id)
    print(f"Found booking: {booking}")
    
    # Controleer of de gebruiker toegang heeft tot deze boeking
    if booking.user != request.user and booking.car.owner != request.user:
        return HttpResponseForbidden("Je hebt geen toegang tot deze boeking.")
    
    # Debug template context
    context = {'booking': booking}
    print(f"Template context: {context}")
    
    try:
        response = render(request, 'bookings/booking_detail.html', context)
        print("Template rendered successfully")
        return response
    except Exception as e:
        print(f"Template error: {str(e)}")
        print(f"Template error type: {type(e)}")
        raise

@login_required
def booking_cancel(request, booking_id):
    booking = get_object_or_404(Booking, id=booking_id)
    
    if booking.user != request.user:
        return HttpResponseForbidden("Je kunt alleen je eigen boekingen annuleren.")
    
    if booking.status != 'PENDING':
        messages.error(request, 'Je kunt alleen boekingen annuleren die nog in afwachting zijn.')
        return redirect('bookings:booking_detail', booking_id=booking.id)
    
    booking.status = 'CANCELLED'
    booking.save()
    messages.success(request, 'Je boeking is geannuleerd.')
    return redirect('bookings:my_bookings')

@login_required
def my_bookings(request):
    bookings = Booking.objects.filter(user=request.user).order_by('start_time')
    return render(request, 'bookings/my_bookings.html', {
        'bookings': bookings
    })

@login_required
def calculate_costs(request):
    """API endpoint voor real-time kostenberekening"""
    start_time = request.GET.get('start_time')
    end_time = request.GET.get('end_time')
    car_id = request.GET.get('car_id')
    expected_km = request.GET.get('expected_kilometers', 50)  # default 50km
    
    if not all([start_time, end_time, car_id]):
        return JsonResponse({'error': 'Missende parameters'}, status=400)
    
    try:
        car = Car.objects.get(id=car_id)
        booking = Booking(
            car=car,
            start_time=datetime.fromisoformat(start_time),
            end_time=datetime.fromisoformat(end_time),
            expected_kilometers=Decimal(expected_km)
        )
        total_cost = booking.calculate_total_cost()
        costs = {
            'total': float(total_cost),
            'breakdown': {
                'base_cost': float(booking.car.hourly_rate),
                'fuel': float(booking.fuel_cost),
                'insurance': float(booking.insurance_cost),
                'maintenance': float(booking.maintenance_cost),
                'depreciation': float(booking.depreciation_cost)
            }
        }
        return JsonResponse(costs)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=400)

@login_required
def booking_calendar(request, car_id):
    car = get_object_or_404(Car, id=car_id)
    
    # Check if we're editing an existing booking
    edit_booking_id = request.GET.get('edit')
    edit_booking = None
    if edit_booking_id:
        print(f"\n=== DEBUG: Editing booking {edit_booking_id} ===")
        edit_booking = get_object_or_404(Booking, id=edit_booking_id)
        print(f"Found booking: {edit_booking}")
        print(f"Current status: {edit_booking.status}")
        # Verify that the user owns this booking and it's still pending
        if edit_booking.user != request.user or edit_booking.status != 'PENDING':
            print(f"Edit validation failed - User match: {edit_booking.user == request.user}, Status: {edit_booking.status}")
            messages.error(request, 'Je kunt deze boeking niet wijzigen.')
            return redirect('bookings:booking_detail', booking_id=edit_booking_id)
    
    if request.method == 'POST':
        try:
            print("\n=== Processing POST request ===")
            # Parse de UTC tijden van de client
            start_time = datetime.fromisoformat(request.POST.get('start_time').replace('Z', '+00:00'))
            end_time = datetime.fromisoformat(request.POST.get('end_time').replace('Z', '+00:00'))
            
            # Zorg ervoor dat de tijden in UTC zijn
            start_time = timezone.make_aware(start_time.replace(tzinfo=None), pytz.UTC)
            end_time = timezone.make_aware(end_time.replace(tzinfo=None), pytz.UTC)
            
            expected_kilometers = Decimal(request.POST.get('expected_kilometers', '50'))
            notes = request.POST.get('notes', '')
            
            if edit_booking:
                try:
                    # Update existing booking
                    edit_booking.start_time = start_time
                    edit_booking.end_time = end_time
                    edit_booking.expected_kilometers = expected_kilometers
                    edit_booking.notes = notes
                    edit_booking.save()
                    messages.success(request, 'Je boeking is succesvol bijgewerkt!')
                    return redirect('bookings:my_bookings')
                except ValidationError as e:
                    messages.error(request, f'Validatiefout: {str(e)}')
                    return render(request, 'bookings/booking_calendar.html', {
                        'car': car,
                        'edit_booking': edit_booking,
                        'error': str(e)
                    })
            else:
                # Create new booking
                booking = Booking(
                    car=car,
                    user=request.user,
                    start_time=start_time,
                    end_time=end_time,
                    expected_kilometers=expected_kilometers,
                    notes=notes
                )
                booking.save()
                messages.success(request, 'Je boeking is succesvol aangemaakt!')
            
            return redirect('bookings:my_bookings')
            
        except (ValueError, ValidationError) as e:
            messages.error(request, f'Er ging iets mis: {str(e)}')
            return JsonResponse({'error': str(e)}, status=400)
    
    return render(request, 'bookings/booking_calendar.html', {
        'car': car,
        'edit_booking': edit_booking
    })

@login_required
def get_availability(request):
    car_id = request.GET.get('car_id')
    date = request.GET.get('date')
    
    print(f"\n=== DEBUG get_availability ===")
    print(f"Requested car_id: {car_id}")
    print(f"Requested date: {date}")

    if not car_id:
        return JsonResponse({'error': 'Car ID is required'}, status=400)

    try:
        # Converteer de datum string naar een datetime object
        date_obj = datetime.strptime(date, '%Y-%m-%d')
        start_of_day = timezone.make_aware(
            datetime.combine(date_obj, datetime.min.time()),
            timezone.get_current_timezone()
        )
        end_of_day = timezone.make_aware(
            datetime.combine(date_obj, datetime.max.time()),
            timezone.get_current_timezone()
        )

        # Haal alle boekingen op voor deze dag
        bookings = Booking.objects.filter(
            car_id=car_id,
            status__in=['PENDING', 'APPROVED'],
            start_time__lt=end_of_day,
            end_time__gt=start_of_day
        ).order_by('start_time')

        # Converteer boekingen naar JSON formaat
        booking_data = []
        for booking in bookings:
            data = {
                'start': booking.start_time.isoformat(),
                'end': booking.end_time.isoformat(),
                'title': f"{booking.user.first_name} {booking.user.last_name}"[:1] + ".",
                'status': booking.status
            }
            booking_data.append(data)
            print(f"Added booking data: {data}")

        return JsonResponse(booking_data, safe=False)
        
    except Exception as e:
        print(f"Error in get_availability: {str(e)}")
        return JsonResponse({'error': str(e)}, status=500)

@login_required
def booking_approve(request, booking_id):
    booking = get_object_or_404(Booking, id=booking_id)
    
    # Check if the user is the owner of the car
    if request.user != booking.car.owner:
        messages.error(request, 'Je hebt geen toestemming om deze boeking goed te keuren.')
        return redirect('bookings:booking_detail', booking_id=booking.id)
    
    if request.method == 'POST':
        approval_note = request.POST.get('approval_note', '')
        if approval_note:
            if booking.notes:
                booking.notes += f"\n\nOpmerking bij goedkeuring: {approval_note}"
            else:
                booking.notes = f"Opmerking bij goedkeuring: {approval_note}"
        booking.status = 'APPROVED'
        try:
            booking.save()
            messages.success(request, 'De boeking is goedgekeurd.')
            return redirect('bookings:booking_detail', booking_id=booking.id)
        except ValidationError as e:
            messages.error(request, 'Deze auto is al geboekt voor (een deel van) deze periode. De boeking kan niet worden goedgekeurd.')
            return redirect('bookings:booking_detail', booking_id=booking.id)
    
    return render(request, 'bookings/booking_approve.html', {'booking': booking})

@login_required
def booking_reject(request, booking_id):
    booking = get_object_or_404(Booking, id=booking_id)
    
    # Check if the user is the car owner
    if booking.car.owner != request.user:
        return HttpResponseForbidden("Je kunt alleen boekingen voor je eigen auto's afwijzen.")
    
    # Allow status changes from any status except cancelled
    if booking.status == 'CANCELLED':
        messages.error(request, 'Je kunt geen geannuleerde boekingen meer afwijzen.')
        return redirect('bookings:booking_detail', booking_id=booking.id)
    
    if request.method == 'POST':
        rejection_note = request.POST.get('rejection_note', '')
        if rejection_note:
            if booking.notes:
                booking.notes += f"\n\nAfwijzingsreden: {rejection_note}"
            else:
                booking.notes = f"Afwijzingsreden: {rejection_note}"
        booking.status = 'REJECTED'
        booking.save()
        messages.success(request, 'De boeking is afgewezen.')
        return redirect('bookings:booking_detail', booking_id=booking.id)
    
    return render(request, 'bookings/booking_reject.html', {'booking': booking})