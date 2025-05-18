"""
Views for property management functionality.
"""
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.views.decorators.http import require_http_methods

from ..models.property import Property, PropertyType
from ..models.location import Location
from ..services import property_service, energy_service

@login_required
def property_view(request):
    """
    Main property management view.
    """
    player = request.player
    
    # Get player's properties
    properties = property_service.get_player_properties(player)
    
    # Get available property types for purchase
    available_properties = property_service.get_available_properties(player)
    
    # Get locations for property placement
    locations = Location.objects.filter(min_level__lte=player.level)
    
    context = {
        'player': player,
        'properties': properties,
        'available_properties': available_properties,
        'locations': locations,
    }
    
    return render(request, 'game/property.html', context)

@login_required
@require_http_methods(["POST"])
def purchase_property_view(request):
    """
    Purchase a new property.
    """
    player = request.player
    
    try:
        property_type_id = int(request.POST.get('property_type_id'))
        location_id = int(request.POST.get('location_id'))
        name = request.POST.get('name', '').strip()
        
        if not name:
            raise ValueError("Property name is required.")
        
        new_property = property_service.purchase_property(
            player=player,
            property_type_id=property_type_id,
            location_id=location_id,
            name=name
        )
        
        messages.success(request, f"Congratulations! You now own '{new_property.name}'!")
        
    except ValueError as e:
        messages.error(request, str(e))
    except Exception as e:
        messages.error(request, f"Error purchasing property: {str(e)}")
    
    return redirect('property')

@login_required
@require_http_methods(["POST"])
def collect_income_view(request, property_id=None):
    """
    Collect income from a specific property or all properties.
    """
    player = request.player
    
    try:
        # Check if player has enough energy
        if not energy_service.use_energy(player, 5):
            messages.error(request, "You don't have enough energy to collect income.")
            return redirect('property')
        
        # Collect income
        if property_id:
            total_income = property_service.collect_property_income(player, property_id)
            messages.success(request, f"You collected {total_income} cash from your property!")
        else:
            total_income = property_service.collect_property_income(player)
            messages.success(request, f"You collected {total_income} cash from all your properties!")
        
    except ValueError as e:
        messages.error(request, str(e))
    except Exception as e:
        messages.error(request, f"Error collecting income: {str(e)}")
    
    return redirect('property')

@login_required
@require_http_methods(["POST"])
def upgrade_property_view(request, property_id):
    """
    Upgrade a property to increase its income.
    """
    player = request.player
    
    try:
        upgraded_property = property_service.upgrade_property(player, property_id)
        
        messages.success(
            request, 
            f"Property '{upgraded_property.name}' upgraded to level {upgraded_property.level}! " +
            f"New income rate: {upgraded_property.income_rate} per day."
        )
        
    except ValueError as e:
        messages.error(request, str(e))
    except Exception as e:
        messages.error(request, f"Error upgrading property: {str(e)}")
    
    return redirect('property')

@login_required
@require_http_methods(["POST"])
def sell_property_view(request, property_id):
    """
    Sell a property back to the game.
    """
    player = request.player
    
    try:
        sell_price = property_service.sell_property(player, property_id)
        messages.success(request, f"Property sold for {sell_price} cash!")
        
    except ValueError as e:
        messages.error(request, str(e))
    except Exception as e:
        messages.error(request, f"Error selling property: {str(e)}")
    
    return redirect('property')

@login_required
def property_detail_view(request, property_id):
    """
    View detailed information about a property.
    """
    player = request.player
    
    try:
        player_property = get_object_or_404(Property, id=property_id, player=player)
        
        # Calculate time until next income collection
        time_since_collection = player_property.last_income_collection
        
        context = {
            'player': player,
            'property': player_property,
            'upgrade_cost': int(player_property.current_value * 0.5),
            'sell_value': int(player_property.current_value * 0.7),
            'time_since_collection': time_since_collection,
        }
        
        return render(request, 'game/property_detail.html', context)
        
    except Exception as e:
        messages.error(request, f"Error loading property details: {str(e)}")
        return redirect('property')
