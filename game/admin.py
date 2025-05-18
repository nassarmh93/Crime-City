from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.contrib.auth.models import User  # Use default User model
from game.models import (
    # User,  # Commented out temporarily
    Player, Location, LocationConnection,
    ItemType, Item, PlayerInventory,
    PropertyType, Property,
    Combat, CombatLog,
    MarketListing,
    CrimeType, CrimeResult
)

# Register user model with custom admin
# admin.site.register(User, UserAdmin)  # Commented out temporarily

# Player admin
@admin.register(Player)
class PlayerAdmin(admin.ModelAdmin):
    list_display = ('nickname', 'level', 'cash', 'energy', 'health')
    search_fields = ('nickname', 'user__username')
    list_filter = ('level', 'is_in_hospital', 'is_in_jail')

# Location admin
@admin.register(Location)
class LocationAdmin(admin.ModelAdmin):
    list_display = ('name', 'district', 'is_safe_zone', 'min_level')
    search_fields = ('name', 'district')
    list_filter = ('is_safe_zone', 'district')

admin.site.register(LocationConnection)

# Item admin
@admin.register(ItemType)
class ItemTypeAdmin(admin.ModelAdmin):
    list_display = ('name',)
    search_fields = ('name',)

@admin.register(Item)
class ItemAdmin(admin.ModelAdmin):
    list_display = ('name', 'item_type', 'buy_price', 'min_level', 'is_equippable', 'is_consumable')
    search_fields = ('name',)
    list_filter = ('item_type', 'is_equippable', 'is_consumable')

@admin.register(PlayerInventory)
class PlayerInventoryAdmin(admin.ModelAdmin):
    list_display = ('player', 'item', 'quantity', 'is_equipped')
    search_fields = ('player__nickname', 'item__name')
    list_filter = ('is_equipped', 'item__item_type')

# Property admin
@admin.register(PropertyType)
class PropertyTypeAdmin(admin.ModelAdmin):
    list_display = ('name', 'base_price', 'base_income', 'min_level')
    search_fields = ('name',)

@admin.register(Property)
class PropertyAdmin(admin.ModelAdmin):
    list_display = ('name', 'property_type', 'player', 'income_rate', 'level', 'is_active')
    search_fields = ('name', 'player__nickname')
    list_filter = ('property_type', 'is_active', 'level')

# Combat admin
@admin.register(Combat)
class CombatAdmin(admin.ModelAdmin):
    list_display = ('attacker', 'defender', 'winner', 'started_at')
    search_fields = ('attacker__nickname', 'defender__nickname')
    list_filter = ('started_at',)

admin.site.register(CombatLog)

# Market admin
@admin.register(MarketListing)
class MarketListingAdmin(admin.ModelAdmin):
    list_display = ('item', 'quantity', 'price', 'seller', 'status', 'created_at')
    search_fields = ('item__name', 'seller__nickname')
    list_filter = ('status', 'created_at')

# Crime admin
@admin.register(CrimeType)
class CrimeTypeAdmin(admin.ModelAdmin):
    list_display = ('name', 'min_level', 'energy_cost', 'jail_risk', 'base_success_chance')
    search_fields = ('name', 'description')
    list_filter = ('min_level',)

@admin.register(CrimeResult)
class CrimeResultAdmin(admin.ModelAdmin):
    list_display = ('player', 'crime_type', 'result', 'cash_reward', 'created_at')
    search_fields = ('player__nickname', 'crime_type__name')
    list_filter = ('result', 'created_at')
