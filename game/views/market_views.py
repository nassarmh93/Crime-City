"""
Views for marketplace functionality.
"""
from django.shortcuts import render, redirect, get_object_or_404
from django.http import JsonResponse
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.views.decorators.http import require_http_methods

from ..models.item import Item, ItemType
from ..services import market_service

@login_required
def market_view(request):
    """
    Main marketplace view showing active listings.
    """
    player = request.player
    item_types = ItemType.objects.all()
    
    # Get filter parameters
    item_type_id = request.GET.get('item_type')
    max_price = request.GET.get('max_price')
    
    # Apply filters
    filters = {}
    if item_type_id:
        try:
            filters['item_type'] = ItemType.objects.get(id=item_type_id)
        except ItemType.DoesNotExist:
            pass
    
    if max_price:
        try:
            filters['max_price'] = int(max_price)
        except ValueError:
            pass
    
    # Get listings
    listings = market_service.get_active_listings(
        player=player,
        min_level=player.level,
        **filters
    )
    
    # Get player's own listings
    player_listings = market_service.get_player_listings(player)
    
    context = {
        'player': player,
        'listings': listings,
        'player_listings': player_listings,
        'item_types': item_types,
        'selected_type': filters.get('item_type'),
        'max_price': filters.get('max_price'),
    }
    
    return render(request, 'game/market.html', context)

@login_required
@require_http_methods(["POST"])
def create_listing_view(request):
    """
    Create a new market listing.
    """
    player = request.player
    
    try:
        item_id = int(request.POST.get('item_id'))
        quantity = int(request.POST.get('quantity', 1))
        price = int(request.POST.get('price'))
        duration = int(request.POST.get('duration', 3))
        
        if quantity < 1:
            raise ValueError("Quantity must be at least 1.")
        
        if price < 1:
            raise ValueError("Price must be at least 1.")
        
        if duration not in [1, 3, 7]:
            duration = 3  # Default to 3 days
        
        listing = market_service.create_listing(
            player=player,
            item_id=item_id,
            quantity=quantity,
            price=price,
            duration_days=duration
        )
        
        messages.success(request, f"Listing created for {quantity} {listing.item.name}!")
        return redirect('market')
        
    except ValueError as e:
        messages.error(request, str(e))
        return redirect('market')
    except Exception as e:
        messages.error(request, f"Error creating listing: {str(e)}")
        return redirect('market')

@login_required
@require_http_methods(["POST"])
def cancel_listing_view(request, listing_id):
    """
    Cancel a market listing.
    """
    player = request.player
    
    try:
        market_service.cancel_listing(listing_id=listing_id, player=player)
        messages.success(request, "Listing canceled and items returned to your inventory.")
    except ValueError as e:
        messages.error(request, str(e))
    except Exception as e:
        messages.error(request, f"Error canceling listing: {str(e)}")
    
    return redirect('market')

@login_required
@require_http_methods(["POST"])
def purchase_listing_view(request, listing_id):
    """
    Purchase an item from the marketplace.
    """
    player = request.player
    
    try:
        listing = market_service.purchase_listing(listing_id=listing_id, player=player)
        messages.success(
            request, 
            f"Successfully purchased {listing.quantity} {listing.item.name} for {listing.price} cash!"
        )
    except ValueError as e:
        messages.error(request, str(e))
    except Exception as e:
        messages.error(request, f"Error purchasing item: {str(e)}")
    
    return redirect('market')

@login_required
def player_listings_view(request):
    """
    View showing a player's own listings.
    """
    player = request.player
    include_sold = request.GET.get('include_sold') == 'true'
    
    listings = market_service.get_player_listings(
        player=player,
        include_sold=include_sold
    )
    
    context = {
        'player': player,
        'listings': listings,
        'include_sold': include_sold,
    }
    
    return render(request, 'game/player_listings.html', context)

@login_required
def api_get_inventory_items(request):
    """
    API endpoint to get a player's inventory items for listing creation.
    """
    player = request.player
    items_data = []
    
    # Get items from inventory that can be sold
    inventory_items = player.inventory.filter(
        item__is_tradable=True, 
        is_equipped=False,
        quantity__gt=0
    )
    
    for inv_item in inventory_items:
        items_data.append({
            'id': inv_item.item.id,
            'name': inv_item.item.name,
            'quantity': inv_item.quantity,
            'sell_price': inv_item.item.sell_price,
        })
    
    return JsonResponse({'items': items_data})
