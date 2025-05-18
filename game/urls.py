from django.urls import path
from game.views import (
    # Auth views
    login_view, register_view, logout_view,
    
    # Player views
    dashboard_view, profile_view, locations_view, 
    travel_view, train_view, inventory_view,
    
    # Combat views
    combat_view, attack_player_view, combat_detail_view,
    
    # Market views
    market_view, create_listing_view, cancel_listing_view,
    purchase_listing_view, player_listings_view, api_get_inventory_items,
    
    # Property views
    property_view, purchase_property_view, collect_income_view,
    upgrade_property_view, sell_property_view, property_detail_view,
    
    # Crime views
    crimes_view, commit_crime_view, crime_detail_view, crime_stats_view
)

urlpatterns = [
    # Authentication
    path('login/', login_view, name='login'),
    path('register/', register_view, name='register'),
    path('logout/', logout_view, name='logout'),
    
    # Main game views
    path('', dashboard_view, name='dashboard'),
    path('profile/', profile_view, name='profile'),
    path('locations/', locations_view, name='locations'),
    path('travel/<int:location_id>/', travel_view, name='travel'),
    path('train/', train_view, name='train'),
    path('inventory/', inventory_view, name='inventory'),
    
    # Combat
    path('combat/', combat_view, name='combat'),
    path('combat/attack/<int:player_id>/', attack_player_view, name='attack_player'),
    path('combat/detail/<int:combat_id>/', combat_detail_view, name='combat_detail'),
    
    # Market
    path('market/', market_view, name='market'),
    path('market/create/', create_listing_view, name='create_listing'),
    path('market/cancel/<int:listing_id>/', cancel_listing_view, name='cancel_listing'),
    path('market/buy/<int:listing_id>/', purchase_listing_view, name='purchase_listing'),
    path('market/my-listings/', player_listings_view, name='player_listings'),
    path('market/api/inventory-items/', api_get_inventory_items, name='api_inventory_items'),
    
    # Property
    path('property/', property_view, name='property'),
    path('property/buy/', purchase_property_view, name='purchase_property'),
    path('property/collect/', collect_income_view, name='collect_all_income'),
    path('property/collect/<int:property_id>/', collect_income_view, name='collect_property_income'),
    path('property/upgrade/<int:property_id>/', upgrade_property_view, name='upgrade_property'),
    path('property/sell/<int:property_id>/', sell_property_view, name='sell_property'),
    path('property/detail/<int:property_id>/', property_detail_view, name='property_detail'),
    
    # Crimes
    path('crimes/', crimes_view, name='crimes'),
    path('crimes/commit/<int:crime_type_id>/', commit_crime_view, name='commit_crime'),
    path('crimes/detail/<int:result_id>/', crime_detail_view, name='crime_detail'),
    path('crimes/stats/', crime_stats_view, name='crime_stats'),
]
