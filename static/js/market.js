/**
 * Market functionality for Crime City
 */
document.addEventListener('DOMContentLoaded', function() {
    // Elements
    const itemSelect = document.getElementById('item_id');
    const quantityInput = document.getElementById('quantity');
    const priceInput = document.getElementById('price');
    const maxQuantitySpan = document.getElementById('max_quantity');
    const suggestedPriceSpan = document.getElementById('suggested_price');
    const createListingBtn = document.getElementById('createListingBtn');
    const sellForm = document.getElementById('sellForm');
    
    // Current inventory items data
    let inventoryItems = [];
    
    // Fetch player's inventory items when opening the sell modal
    const sellModal = document.getElementById('sellModal');
    if (sellModal) {
        sellModal.addEventListener('show.bs.modal', function() {
            fetchInventoryItems();
        });
    }
    
    // Handle item selection
    if (itemSelect) {
        itemSelect.addEventListener('change', function() {
            updateItemDetails();
        });
    }
    
    // Handle quantity change
    if (quantityInput) {
        quantityInput.addEventListener('change', function() {
            validateQuantity();
        });
    }
    
    // Fetch inventory items from API
    function fetchInventoryItems() {
        fetch('/market/api/inventory-items/')
            .then(response => response.json())
            .then(data => {
                inventoryItems = data.items;
                
                // Clear current options
                while (itemSelect.options.length > 1) {
                    itemSelect.remove(1);
                }
                
                // Add items to select
                if (inventoryItems.length > 0) {
                    inventoryItems.forEach(item => {
                        const option = document.createElement('option');
                        option.value = item.id;
                        option.textContent = `${item.name} (x${item.quantity})`;
                        itemSelect.appendChild(option);
                    });
                    
                    // Enable form
                    createListingBtn.disabled = false;
                } else {
                    // If no items, disable form
                    const option = document.createElement('option');
                    option.textContent = "No items available to sell";
                    itemSelect.appendChild(option);
                    createListingBtn.disabled = true;
                }
                
                // Update details for initially selected item
                updateItemDetails();
            })
            .catch(error => {
                console.error('Error fetching inventory:', error);
                createListingBtn.disabled = true;
            });
    }
    
    // Update item details when selection changes
    function updateItemDetails() {
        const selectedItemId = parseInt(itemSelect.value);
        const selectedItem = inventoryItems.find(item => item.id === selectedItemId);
        
        if (selectedItem) {
            // Update max quantity
            maxQuantitySpan.textContent = selectedItem.quantity;
            quantityInput.max = selectedItem.quantity;
            
            // Set default quantity to 1 or max if less than 1
            if (parseInt(quantityInput.value) > selectedItem.quantity) {
                quantityInput.value = selectedItem.quantity;
            }
            
            // Set suggested price
            const suggestedPrice = selectedItem.sell_price * 1.5;
            suggestedPriceSpan.textContent = suggestedPrice;
            priceInput.value = suggestedPrice;
            
            // Enable quantity and price inputs
            quantityInput.disabled = false;
            priceInput.disabled = false;
        } else {
            // Reset fields if no item selected
            maxQuantitySpan.textContent = '0';
            suggestedPriceSpan.textContent = '0';
            quantityInput.value = '1';
            priceInput.value = '';
            
            // Disable inputs
            quantityInput.disabled = true;
            priceInput.disabled = true;
        }
    }
    
    // Validate quantity input
    function validateQuantity() {
        const selectedItemId = parseInt(itemSelect.value);
        const selectedItem = inventoryItems.find(item => item.id === selectedItemId);
        
        if (selectedItem) {
            const maxQuantity = selectedItem.quantity;
            let currentQuantity = parseInt(quantityInput.value);
            
            // Ensure quantity is within valid range
            if (isNaN(currentQuantity) || currentQuantity < 1) {
                currentQuantity = 1;
            } else if (currentQuantity > maxQuantity) {
                currentQuantity = maxQuantity;
            }
            
            quantityInput.value = currentQuantity;
        }
    }
    
    // Form validation before submit
    if (sellForm) {
        sellForm.addEventListener('submit', function(event) {
            const selectedItemId = parseInt(itemSelect.value);
            const quantity = parseInt(quantityInput.value);
            const price = parseInt(priceInput.value);
            
            if (isNaN(selectedItemId) || selectedItemId <= 0) {
                event.preventDefault();
                alert('Please select an item to sell.');
                return;
            }
            
            if (isNaN(quantity) || quantity < 1) {
                event.preventDefault();
                alert('Please enter a valid quantity (minimum 1).');
                return;
            }
            
            if (isNaN(price) || price < 1) {
                event.preventDefault();
                alert('Please enter a valid price (minimum $1).');
                return;
            }
            
            const selectedItem = inventoryItems.find(item => item.id === selectedItemId);
            if (selectedItem && quantity > selectedItem.quantity) {
                event.preventDefault();
                alert(`You only have ${selectedItem.quantity} of this item.`);
                return;
            }
        });
    }
});
