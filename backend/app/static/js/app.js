// Product Search Application
(function() {
    'use strict';

    // DOM Elements
    const searchForm = document.getElementById('searchForm');
    const productNameInput = document.getElementById('productName');
    const searchBtn = document.getElementById('searchBtn');
    const loadingDiv = document.getElementById('loading');
    const errorDiv = document.getElementById('error');
    const resultsDiv = document.getElementById('results');
    const resultsTitle = document.getElementById('resultsTitle');
    const resultsContainer = document.getElementById('resultsContainer');

    // API Base URL - matches backend config.api_prefix
    const API_BASE = '/api/v1';

    /**
     * Show loading state
     */
    function showLoading() {
        loadingDiv.classList.remove('hidden');
        errorDiv.classList.add('hidden');
        resultsDiv.classList.add('hidden');
        searchBtn.disabled = true;
    }

    /**
     * Hide loading state
     */
    function hideLoading() {
        loadingDiv.classList.add('hidden');
        searchBtn.disabled = false;
    }

    /**
     * Show error message
     */
    function showError(message) {
        errorDiv.textContent = message;
        errorDiv.classList.remove('hidden');
        resultsDiv.classList.add('hidden');
    }

    /**
     * Format price to Romanian Lei format
     */
    function formatPrice(price) {
        return new Intl.NumberFormat('ro-RO', {
            style: 'currency',
            currency: 'RON',
            minimumFractionDigits: 2,
            maximumFractionDigits: 2
        }).format(price);
    }

    /**
     * Calculate discount percentage
     */
    function calculateDiscount(originalPrice, currentPrice) {
        if (!originalPrice || originalPrice <= currentPrice) {
            return null;
        }
        return Math.round(((originalPrice - currentPrice) / originalPrice) * 100);
    }

    /**
     * Flatten and sort results from all retailers
     * Groups by unique products (using URL) and returns top 3 best prices from different products
     */
    function processResults(apiResponse) {
        const allPrices = [];
        
        // Flatten results from all retailers
        Object.entries(apiResponse.results).forEach(([retailer, prices]) => {
            prices.forEach(price => {
                allPrices.push({
                    ...price,
                    retailer: retailer
                });
            });
        });

        console.log(`Total prices found: ${allPrices.length}`);

        // Group by unique product (using URL as identifier)
        const uniqueProducts = new Map();
        
        allPrices.forEach((price, index) => {
            // Use full URL as identifier to differentiate products
            let productKey;
            if (price.url) {
                productKey = price.url;
            } else {
                productKey = `${price.retailer}-${price.price}-${index}`;
            }
            
            // If we already have this exact URL, keep the one with lower price
            if (!uniqueProducts.has(productKey)) {
                uniqueProducts.set(productKey, price);
            } else {
                const existing = uniqueProducts.get(productKey);
                if (price.price < existing.price) {
                    uniqueProducts.set(productKey, price);
                }
            }
        });

        console.log(`Unique products found: ${uniqueProducts.size}`);

        // Convert map to array and sort by price (ascending) - best prices first
        const uniquePrices = Array.from(uniqueProducts.values());
        uniquePrices.sort((a, b) => a.price - b.price);

        // Return top 3 best prices from different products
        const result = uniquePrices.slice(0, 3);
        
        console.log(`Total prices: ${allPrices.length}, Unique products: ${uniqueProducts.size}, Returning: ${result.length}`);
        console.log('Result URLs:', result.map(r => r.url));
        
        return result;
    }

    /**
     * Create price card HTML
     */
    function createPriceCard(priceData, index) {
        const discount = priceData.original_price 
            ? calculateDiscount(priceData.original_price, priceData.price)
            : null;

        return `
            <div class="price-card">
                ${priceData.image_url 
                    ? `<div class="product-image-container">
                        <img src="${priceData.image_url}" alt="Product image" class="product-image" onerror="this.style.display='none'; this.parentElement.querySelector('.image-placeholder').style.display='flex';">
                        <div class="image-placeholder" style="display: none;">
                            <span>No Image</span>
                        </div>
                    </div>`
                    : `<div class="product-image-container">
                        <div class="image-placeholder">
                            <span>No Image</span>
                        </div>
                    </div>`
                }
                <div class="price-card-content">
                    <div class="price-card-header">
                        <span class="retailer-name">${priceData.retailer}</span>
                        <span class="availability-badge ${priceData.availability ? 'in-stock' : 'out-of-stock'}">
                            ${priceData.availability ? 'In Stock' : 'Out of Stock'}
                        </span>
                    </div>
                    <div class="price-info">
                        <div class="price-row">
                            <span class="current-price">${formatPrice(priceData.price)}</span>
                            ${priceData.original_price && priceData.original_price > priceData.price
                                ? `<span class="original-price">${formatPrice(priceData.original_price)}</span>`
                                : ''}
                        </div>
                        ${discount ? `<span class="promotion-badge">-${discount}% OFF</span>` : ''}
                        ${priceData.promotion_text ? `<div class="promotion-text">${priceData.promotion_text}</div>` : ''}
                        ${priceData.delivery_info ? `<div class="delivery-info">${priceData.delivery_info}</div>` : ''}
                    </div>
                    ${priceData.url && priceData.availability
                        ? `<a href="${priceData.url}" target="_blank" rel="noopener noreferrer" class="product-link">Buy Now</a>`
                        : priceData.url
                            ? `<a href="${priceData.url}" target="_blank" rel="noopener noreferrer" class="product-link" style="background: var(--text-secondary);">View Product</a>`
                            : '<div class="product-link" style="background: var(--text-secondary); cursor: not-allowed;">Link Not Available</div>'}
                </div>
            </div>
        `;
    }

    /**
     * Display search results
     */
    function displayResults(apiResponse) {
        const topPrices = processResults(apiResponse);
        const retailerStatus = apiResponse.retailer_status || {};

        if (topPrices.length === 0) {
            resultsContainer.innerHTML = '<div class="no-results">No prices found for this product. Try a different search term.</div>';
            resultsTitle.textContent = `No results for "${apiResponse.query}"`;
        } else {
            resultsTitle.textContent = `Top ${topPrices.length} Best Offers (Different Products) for "${apiResponse.query}"`;
            resultsContainer.innerHTML = topPrices.map((price, index) => 
                createPriceCard(price, index)
            ).join('');
        }

        // Add retailer status information
        const searchedRetailers = Object.keys(retailerStatus);
        const successfulRetailers = searchedRetailers.filter(r => retailerStatus[r].success);
        const failedRetailers = searchedRetailers.filter(r => !retailerStatus[r].success);

        if (failedRetailers.length > 0) {
            const statusInfo = document.createElement('div');
            statusInfo.className = 'retailer-status';
            statusInfo.innerHTML = `
                <p class="status-info">
                    <strong>Searched:</strong> ${searchedRetailers.join(', ')} | 
                    <strong>Found results:</strong> ${successfulRetailers.join(', ') || 'None'} | 
                    <strong>No results:</strong> ${failedRetailers.join(', ') || 'None'}
                </p>
            `;
            resultsContainer.insertBefore(statusInfo, resultsContainer.firstChild);
        }

        resultsDiv.classList.remove('hidden');
    }

    /**
     * Search for products
     */
    async function searchProduct(productName) {
        try {
            showLoading();

            const response = await fetch(
                `${API_BASE}/scraper/search?product_name=${encodeURIComponent(productName)}`
            );

            if (!response.ok) {
                const errorData = await response.json().catch(() => ({}));
                throw new Error(errorData.detail || `HTTP error! status: ${response.status}`);
            }

            const data = await response.json();
            hideLoading();
            displayResults(data);

        } catch (error) {
            hideLoading();
            console.error('Search error:', error);
            showError(`Error searching for products: ${error.message}. Please try again.`);
        }
    }

    /**
     * Handle form submission
     */
    searchForm.addEventListener('submit', (e) => {
        e.preventDefault();
        
        const productName = productNameInput.value.trim();
        
        if (productName.length < 2) {
            showError('Please enter at least 2 characters');
            return;
        }

        searchProduct(productName);
    });

    // Focus input on page load
    productNameInput.focus();

})();

