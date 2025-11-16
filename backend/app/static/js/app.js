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
     * Display search results for multiple products
     */
    function displayResults(allResults) {
        if (allResults.length === 0) {
            resultsContainer.innerHTML = '<div class="no-results">No prices found for any products. Try a different search term.</div>';
            resultsTitle.textContent = 'No results found';
            resultsDiv.classList.remove('hidden');
            return;
        }

        // Group results by product query
        const groupedResults = {};
        allResults.forEach(result => {
            const query = result.query;
            if (!groupedResults[query]) {
                groupedResults[query] = {
                    query: query,
                    topPrices: processResults(result),
                    retailerStatus: result.retailer_status || {}
                };
            }
        });

        // Build HTML for each product row
        let html = '';
        Object.values(groupedResults).forEach((group, groupIndex) => {
            const { query, topPrices, retailerStatus } = group;
            
            if (topPrices.length === 0) {
                html += `
                    <div class="product-row">
                        <h3 class="product-row-title">${query}</h3>
                        <div class="no-results-small">No prices found for this product</div>
                    </div>
                `;
            } else {
                html += `
                    <div class="product-row">
                        <h3 class="product-row-title">${query}</h3>
                        <div class="product-row-cards">
                            ${topPrices.map((price, index) => createPriceCard(price, index)).join('')}
                        </div>
                    </div>
                `;
            }
        });

        resultsTitle.textContent = `Search Results (${allResults.length} product${allResults.length > 1 ? 's' : ''})`;
        resultsContainer.innerHTML = html;
        resultsDiv.classList.remove('hidden');
    }

    /**
     * Parse multiple products from search input
     * Supports comma, period, or slash as separators
     */
    function parseProducts(searchInput) {
        // Split by comma, period, or slash
        const products = searchInput
            .split(/[,.\/]/)
            .map(p => p.trim())
            .filter(p => p.length >= 2); // Minimum 2 characters
        
        // Limit to 5 products
        return products.slice(0, 5);
    }

    /**
     * Search for multiple products
     */
    async function searchProduct(searchInput) {
        try {
            showLoading();

            // Parse multiple products
            const products = parseProducts(searchInput);
            
            if (products.length === 0) {
                hideLoading();
                showError('Please enter at least one product name (minimum 2 characters)');
                return;
            }

            if (products.length > 5) {
                hideLoading();
                showError('Maximum 5 products allowed. Using first 5 products.');
            }

            console.log(`Searching for ${products.length} products:`, products);

            // Search all products in parallel
            const searchPromises = products.map(productName =>
                fetch(`${API_BASE}/scraper/search?product_name=${encodeURIComponent(productName)}`)
                    .then(response => {
                        if (!response.ok) {
                            const errorData = response.json().catch(() => ({}));
                            throw new Error(`HTTP error! status: ${response.status}`);
                        }
                        return response.json();
                    })
                    .catch(error => {
                        console.error(`Error searching for "${productName}":`, error);
                        return {
                            query: productName,
                            total_prices_found: 0,
                            results: {},
                            retailer_status: {}
                        };
                    })
            );

            const allResults = await Promise.all(searchPromises);
            hideLoading();
            displayResults(allResults);

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

