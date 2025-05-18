# Import service functions for easy access
from .combat_service import (
    get_available_opponents, 
    initiate_combat,
    process_combat,
    get_recent_combat_logs
)

from .energy_service import (
    calculate_energy_regeneration,
    regenerate_player_energy,
    use_energy,
    refill_energy
)

from .market_service import (
    get_active_listings,
    get_player_listings,
    create_listing,
    cancel_listing,
    purchase_listing,
    get_expired_listings,
    process_expired_listings
)

from .property_service import (
    get_available_properties,
    get_player_properties,
    purchase_property,
    collect_property_income,
    upgrade_property,
    sell_property
)

from .crime_service import (
    get_available_crimes,
    commit_crime,
    calculate_success_chance,
    get_recent_crimes,
    get_crime_stats,
    notify_player
)
