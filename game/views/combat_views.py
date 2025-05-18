from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import HttpResponseBadRequest
from django.db.models import Q

from game.models import Player, Combat
from game.services import get_available_opponents, initiate_combat, get_recent_combat_logs

@login_required
def combat_view(request):
    """Display combat options and history"""
    player = request.user.player
    
    # Get potential opponents at the current location
    opponents = get_available_opponents(player, player.current_location)
    
    # Get recent combat logs
    combat_logs = get_recent_combat_logs(player)
    
    context = {
        'player': player,
        'opponents': opponents,
        'combat_logs': combat_logs
    }
    
    return render(request, 'game/combat.html', context)

@login_required
def attack_player_view(request, player_id):
    """Attack another player"""
    attacker = request.user.player
    defender = get_object_or_404(Player, id=player_id)
    
    # Check if attacker is trying to attack themselves
    if attacker.id == defender.id:
        messages.error(request, "You cannot attack yourself.")
        return redirect('combat')
    
    # Check if attacker or defender is in hospital or jail
    if attacker.is_in_hospital:
        messages.error(request, "You cannot attack while in the hospital.")
        return redirect('combat')
        
    if attacker.is_in_jail:
        messages.error(request, "You cannot attack while in jail.")
        return redirect('combat')
        
    if defender.is_in_hospital or defender.is_in_jail:
        messages.error(request, "You cannot attack a player who is in hospital or jail.")
        return redirect('combat')
    
    # Check if both players are at the same location
    if attacker.current_location != defender.current_location:
        messages.error(request, "You cannot attack a player who is in a different location.")
        return redirect('combat')
    
    # Check if in a safe zone
    if attacker.current_location.is_safe_zone:
        messages.error(request, "You cannot attack in a safe zone.")
        return redirect('combat')
    
    # Initiate combat
    combat, log_messages, result_message = initiate_combat(
        attacker, defender, attacker.current_location
    )
    
    if combat:
        messages.info(request, result_message)
    else:
        messages.error(request, result_message)
    
    return redirect('combat')

@login_required
def combat_detail_view(request, combat_id):
    """View details of a specific combat"""
    player = request.user.player
    combat = get_object_or_404(
        Combat.objects.filter(
            Q(attacker=player) | Q(defender=player)
        ), id=combat_id
    )
    
    context = {
        'player': player,
        'combat': combat,
        'logs': combat.logs.all().order_by('timestamp')
    }
    
    return render(request, 'game/combat_detail.html', context)
