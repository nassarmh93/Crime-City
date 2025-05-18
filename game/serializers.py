"""
Serializers for the Crime City API
"""
from rest_framework import serializers
from .models import (
    Player, Location, Item, ItemType, PlayerInventory,
    Property, PropertyType, Combat, CombatLog, MarketListing
)

class PlayerSerializer(serializers.ModelSerializer):
    """Serializer for Player model"""
    username = serializers.CharField(source='user.username', read_only=True)
    
    class Meta:
        model = Player
        fields = [
            'id', 'username', 'nickname', 'level', 'experience', 'cash', 'bank_balance',
            'strength', 'defense', 'speed', 'dexterity', 'intelligence',
            'energy', 'max_energy', 'health', 'max_health',
            'is_in_hospital', 'is_in_jail'
        ]

class LocationSerializer(serializers.ModelSerializer):
    """Serializer for Location model"""
    class Meta:
        model = Location
        fields = [
            'id', 'name', 'description', 'image', 'is_safe_zone',
            'energy_cost', 'min_level', 'district'
        ]

class ItemTypeSerializer(serializers.ModelSerializer):
    """Serializer for ItemType model"""
    class Meta:
        model = ItemType
        fields = ['id', 'name', 'description']

class ItemSerializer(serializers.ModelSerializer):
    """Serializer for Item model"""
    item_type_name = serializers.CharField(source='item_type.name', read_only=True)
    
    class Meta:
        model = Item
        fields = [
            'id', 'name', 'description', 'image', 'item_type', 'item_type_name',
            'buy_price', 'sell_price', 'min_level',
            'attack_power', 'defense_power', 'speed_bonus',
            'energy_restore', 'health_restore',
            'is_tradable', 'is_equippable', 'is_consumable'
        ]

class PlayerInventorySerializer(serializers.ModelSerializer):
    """Serializer for PlayerInventory model"""
    item_details = ItemSerializer(source='item', read_only=True)
    
    class Meta:
        model = PlayerInventory
        fields = ['id', 'player', 'item', 'item_details', 'quantity', 'is_equipped']

class PropertyTypeSerializer(serializers.ModelSerializer):
    """Serializer for PropertyType model"""
    class Meta:
        model = PropertyType
        fields = [
            'id', 'name', 'description', 'image',
            'base_price', 'base_income', 'min_level'
        ]

class PropertySerializer(serializers.ModelSerializer):
    """Serializer for Property model"""
    property_type_name = serializers.CharField(source='property_type.name', read_only=True)
    location_name = serializers.CharField(source='location.name', read_only=True)
    
    class Meta:
        model = Property
        fields = [
            'id', 'name', 'player', 'property_type', 'property_type_name',
            'purchase_price', 'current_value', 'location', 'location_name',
            'income_rate', 'level', 'is_active', 'purchased_on'
        ]

class CombatLogSerializer(serializers.ModelSerializer):
    """Serializer for CombatLog model"""
    class Meta:
        model = CombatLog
        fields = ['id', 'combat', 'message', 'timestamp']

class CombatSerializer(serializers.ModelSerializer):
    """Serializer for Combat model"""
    attacker_name = serializers.CharField(source='attacker.nickname', read_only=True)
    defender_name = serializers.CharField(source='defender.nickname', read_only=True)
    winner_name = serializers.CharField(source='winner.nickname', read_only=True)
    location_name = serializers.CharField(source='location.name', read_only=True)
    logs = CombatLogSerializer(many=True, read_only=True)
    
    class Meta:
        model = Combat
        fields = [
            'id', 'attacker', 'attacker_name', 'defender', 'defender_name',
            'winner', 'winner_name', 'location', 'location_name',
            'cash_stolen', 'experience_gained', 'started_at', 'ended_at', 'logs'
        ]

class MarketListingSerializer(serializers.ModelSerializer):
    """Serializer for MarketListing model"""
    seller_name = serializers.CharField(source='seller.nickname', read_only=True)
    buyer_name = serializers.CharField(source='buyer.nickname', read_only=True)
    item_name = serializers.CharField(source='item.name', read_only=True)
    item_type_name = serializers.CharField(source='item.item_type.name', read_only=True)
    
    class Meta:
        model = MarketListing
        fields = [
            'id', 'seller', 'seller_name', 'buyer', 'buyer_name',
            'item', 'item_name', 'item_type_name',
            'quantity', 'price', 'description', 'status',
            'created_at', 'expires_at', 'sold_at'
        ]
