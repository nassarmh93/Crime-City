"""
Views for crime-related functionality.
"""
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.views.decorators.http import require_http_methods
from django.db.models import Sum

from ..models.crime import CrimeType, CrimeResult
from ..services import crime_service

@login_required
def crimes_view(request):
    """
    Main view for crimes list and operations.
    """
    player = request.player
    
    # Get available crimes for player
    available_crimes = crime_service.get_available_crimes(player)
    
    # Get recent crime results
    recent_results = crime_service.get_recent_crimes(player)
    
    # Get crime stats
    if recent_results.exists():
        crime_stats = crime_service.get_crime_stats(player)
    else:
        crime_stats = None
    
    context = {
        'player': player,
        'available_crimes': available_crimes,
        'recent_results': recent_results,
        'crime_stats': crime_stats,
    }
    
    return render(request, 'game/crimes.html', context)

@login_required
@require_http_methods(["POST"])
def commit_crime_view(request, crime_type_id):
    """
    Handle a player attempting to commit a crime.
    """
    player = request.player
    
    # Check if player is in jail
    if player.is_in_jail:
        messages.error(request, "You can't commit crimes while in jail!")
        return redirect('crimes')
    
    try:
        # Get the current location
        location = player.current_location
        if not location:
            raise ValueError("You need to be in a location to commit crimes.")
        
        # Commit the crime
        result = crime_service.commit_crime(player, crime_type_id, location)
        
        # Show message based on result
        if result.result == 'success':
            messages.success(
                request, 
                f"Crime successful! You earned ${result.cash_reward} and {result.exp_reward} XP."
            )
            if result.item_reward:
                messages.info(request, f"You also found: {result.item_reward.name}!")
                
        elif result.result == 'failed':
            messages.warning(
                request, 
                "You failed to commit the crime but managed to escape without being noticed."
            )
            
        elif result.result == 'jailed':
            jail_time_minutes = result.jail_time // 60
            messages.error(
                request, 
                f"You were caught and sent to jail for {jail_time_minutes} minutes!"
            )
        
    except ValueError as e:
        messages.error(request, str(e))
    except Exception as e:
        messages.error(request, f"Error committing crime: {str(e)}")
    
    return redirect('crimes')

@login_required
def crime_detail_view(request, result_id):
    """
    View detailed information about a crime result.
    """
    player = request.player
    
    try:
        # Get the crime result
        result = get_object_or_404(CrimeResult, id=result_id, player=player)
        
        context = {
            'player': player,
            'result': result,
            'crime_type': result.crime_type,
        }
        
        return render(request, 'game/crime_detail.html', context)
        
    except Exception as e:
        messages.error(request, f"Error loading crime details: {str(e)}")
        return redirect('crimes')

@login_required
def crime_stats_view(request):
    """
    View detailed crime statistics for a player.
    """
    player = request.player
    
    # Get basic stats
    crime_stats = crime_service.get_crime_stats(player)
    
    # Get stats per crime type
    crime_types = CrimeType.objects.filter(
        results__player=player
    ).distinct()
    
    crime_type_stats = []
    for crime_type in crime_types:
        total = CrimeResult.objects.filter(
            player=player, 
            crime_type=crime_type
        ).count()
        
        successes = CrimeResult.objects.filter(
            player=player, 
            crime_type=crime_type,
            result='success'
        ).count()
        
        success_rate = (successes / total * 100) if total > 0 else 0
        
        earnings = CrimeResult.objects.filter(
            player=player, 
            crime_type=crime_type,
            result='success'
        ).values('cash_reward').aggregate(
            total=Sum('cash_reward')
        )['total'] or 0
        
        crime_type_stats.append({
            'name': crime_type.name,
            'total': total,
            'successes': successes,
            'success_rate': round(success_rate, 1),
            'earnings': earnings,
        })
    
    context = {
        'player': player,
        'stats': crime_stats,
        'crime_type_stats': crime_type_stats,
    }
    
    return render(request, 'game/crime_stats.html', context) 