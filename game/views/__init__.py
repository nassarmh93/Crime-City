# Import views for easy access
from .auth_views import (
    login_view,
    register_view,
    logout_view
)

from .player_views import (
    dashboard_view,
    profile_view,
    locations_view,
    travel_view,
    train_view,
    inventory_view
)

from .combat_views import (
    combat_view,
    attack_player_view,
    combat_detail_view
)

from .market_views import (
    market_view,
    create_listing_view,
    cancel_listing_view,
    purchase_listing_view,
    player_listings_view,
    api_get_inventory_items
)

from .property_views import (
    property_view,
    purchase_property_view,
    collect_income_view,
    upgrade_property_view,
    sell_property_view,
    property_detail_view
)

from .crime_views import (
    crimes_view,
    commit_crime_view,
    crime_detail_view,
    crime_stats_view
)
