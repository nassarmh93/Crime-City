from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Q

from game.models import Player, Location, LocationConnection
from game.services import use_energy
from game.forms import PlayerProfileForm

@login_required
def dashboard_view(request):
    """Display the player's dashboard"""
    player = request.user.player
    
    # Get connected locations for travel options
    connected_locations = LocationConnection.objects.filter(
        from_location=player.current_location
    ).select_related('to_location')
    
    # Get other players at this location
    nearby_players = Player.objects.filter(
        current_location=player.current_location
    ).exclude(id=player.id)[:10]
    
    # Get potential properties to buy at this location
    nearby_properties = []
    
    # Recent events (placeholder)
    recent_events = [
        {
            'title': 'Welcome to Crime City',
            'description': 'Start your criminal empire by exploring the city.',
            'timestamp': player.created_at
        }
    ]
    
    context = {
        'player': player,
        'connected_locations': connected_locations,
        'nearby_players': nearby_players,
        'nearby_properties': nearby_properties,
        'recent_events': recent_events
    }
    
    return render(request, 'game/dashboard.html', context)

@login_required
def profile_view(request):
    """Display the player's profile"""
    player = request.user.player
    
    if request.method == 'POST':
        form = PlayerProfileForm(request.POST, instance=player)
        if form.is_valid():
            form.save()
            messages.success(request, "Profile updated successfully.")
            return redirect('profile')
    else:
        form = PlayerProfileForm(instance=player)
    
    context = {
        'player': player,
        'form': form
    }
    
    return render(request, 'game/profile.html', context)

@login_required
def locations_view(request):
    """Display all locations in the game"""
    player = request.user.player
    
    # Get all locations grouped by district
    locations = Location.objects.all().order_by('district', 'name')
    
    # Group locations by district
    districts = {}
    for location in locations:
        if location.district not in districts:
            districts[location.district] = []
        districts[location.district].append(location)
    
    context = {
        'player': player,
        'districts': districts
    }
    
    return render(request, 'game/locations.html', context)

@login_required
def travel_view(request, location_id):
    """Travel to a new location"""
    player = request.user.player
    destination = get_object_or_404(Location, id=location_id)
    
    # Check if player meets level requirement
    if player.level < destination.min_level:
        messages.error(request, f"You need to be at least level {destination.min_level} to travel to {destination.name}.")
        return redirect('locations')
    
    # Check if location is connected to current location
    connection = LocationConnection.objects.filter(
        from_location=player.current_location,
        to_location=destination
    ).first()
    
    if not connection and player.current_location.id != destination.id:
        # Check if we're allowing direct travel to any location (for prototype)
        messages.warning(request, f"Traveling to {destination.name} without a direct route.")
    
    # Update player location
    player.current_location = destination
    player.save()
    
    messages.success(request, f"You have traveled to {destination.name}.")
    return redirect('dashboard')

@login_required
def train_view(request):
    """Train player stats"""
    player = request.user.player
    
    if request.method == 'POST':
        stat = request.POST.get('stat')
        if stat in ['strength', 'defense', 'speed', 'dexterity', 'intelligence']:
            # Use energy to train stat
            success, message = player.train_stat(stat)
            if success:
                messages.success(request, message)
            else:
                messages.error(request, message)
        else:
            messages.error(request, "Invalid stat selection.")
        
        return redirect('train')
    
    context = {
        'player': player,
        'stats': [
            {'name': 'strength', 'value': player.strength, 'display': 'Strength'},
            {'name': 'defense', 'value': player.defense, 'display': 'Defense'},
            {'name': 'speed', 'value': player.speed, 'display': 'Speed'},
            {'name': 'dexterity', 'value': player.dexterity, 'display': 'Dexterity'},
            {'name': 'intelligence', 'value': player.intelligence, 'display': 'Intelligence'}
        ]
    }
    
    return render(request, 'game/train.html', context)

@login_required
def inventory_view(request):
    """Display player's inventory"""
    player = request.user.player
    
    # Get player's inventory items
    inventory_items = player.inventory.all().select_related('item')
    
    context = {
        'player': player,
        'inventory': inventory_items
    }
    
    return render(request, 'game/inventory.html', context)
