import { ApiClient } from './api.js';
import { createCard, createErrorCard, createSkeletonCard } from './weatherCard.js';

let currentCities = []; 
let isCelsius = true; 
let errorCards = [];
let searchHistoryState = []; // <-- NEW: State for search history

// --- DOM Elements ---
const grid = document.getElementById('weather-grid');
const addBtn = document.getElementById('add-city-button');
const searchInput = document.getElementById('city-name');
const unitToggle = document.querySelector('.unit-toggle');
const locateBtn = document.getElementById('current-location-btn');

// Fetch live history from our local state
function getHistory() {
    return searchHistoryState;
}

// --- Initialization ---
export async function initDashboard(expectedCount = null) {
    showSkeleton(expectedCount); 
    try {
        // Fetch weather dashboard data
        const data = await ApiClient.request('/weather/dashboard');
        currentCities = data.dashboard || [];
        
        // NEW: Fetch the user's personal search history on login!
        const historyData = await ApiClient.request('/weather/history');
        searchHistoryState = historyData.history || [];
    } catch (error) {
        showToast(error.message, 'error');
    }
    renderGrid();
}

// --- Render Logic ---
function renderGrid() {
    grid.innerHTML = ''; // Clear grid first
    const cities = currentCities;

    // 1. The Empty State
    if (cities.length === 0 && errorCards.length === 0) {
        grid.innerHTML = `
            <div class="empty-state">
                <div class="empty-icon">🌍</div>
                
                <h2>No cities yet</h2>
                <p>Search for a city above to start tracking weather across the world.<br>You can track up to 8 cities at once.</p>
                <button class="add-first-city-btn">+ Add Your First City</button>
            </div>
        `;
        
        // Attach listener to the empty state button
        grid.querySelector('.add-first-city-btn')?.addEventListener('click', () => searchInput.focus());
        return;
    }

    // 2. Append Weather Cards
    cities.forEach(city => {
        const cardNode = createCard(city, isCelsius, async () => {
            // Delete from Python Vault
            await ApiClient.request(`/weather/cities/${city.city_id}`, { method: 'DELETE' });
            showToast(`${city.city_name} removed`, 'success');
            
            // Tell the dashboard we expect 1 less card now!
            initDashboard(Math.max(0, currentCities.length - 1)); 
        });
        grid.appendChild(cardNode);
    });

    // 3. Append Error Cards
    errorCards.forEach(err => {
        const errNode = createErrorCard(
            err, 
            () => {
                errorCards = errorCards.filter(e => e.id !== err.id);
                renderGrid();
            },
            (cityName) => {
                errorCards = errorCards.filter(e => e.id !== err.id);
                renderGrid(); 
                handleAddCity(cityName); 
            }
        );
        grid.appendChild(errNode);
    });
}

// --- Core Application Logic ---
async function handleAddCity(cityName) {
    const skeletonEl = createSkeletonCard();
    grid.appendChild(skeletonEl);

    try {
        // NEW: Save the search to the History Vault
        await ApiClient.request('/weather/history', {
            method: 'POST',
            body: JSON.stringify({ city_name: cityName })
        });
        
        // Update local UI state immediately to feel snappy
        searchHistoryState = [cityName, ...searchHistoryState.filter(c => c !== cityName)].slice(0, 5);

        // Post to Python Vault!
        await ApiClient.request('/weather/save', {
            method: 'POST',
            body: JSON.stringify({ city_name: cityName })
        });
        showToast(`${cityName} added!`, 'success');
        await initDashboard(currentCities.length + 1); // Reload data
    } catch (error) {
        showToast(error.message, 'error');
    } finally {
        skeletonEl?.remove();
    }
}

function showSkeleton(expectedCount = null) {
    grid.innerHTML = '';
    let count = 1;
    if (expectedCount !== null) {
        count = expectedCount;
    } else if (currentCities.length > 0) {
        count = currentCities.length;
    }
    
    for (let i = 0; i < count; i++) {
        grid.appendChild(createSkeletonCard());
    }
}

const historyDropdown = document.getElementById('search-history');
let searchTimeout;

// 3. The Dropdown Renderer
function renderDropdownList(historyList, apiList, query = "") {
    const filteredApiList = apiList.filter(apiCity => !historyList.includes(apiCity));

    if (historyList.length === 0 && filteredApiList.length === 0) {
        historyDropdown.style.display = 'none';
        return;
    }

    historyDropdown.style.display = 'block';
    
    let html = '';

    if (historyList.length > 0) {
        html += `<div class="dropdown-section-title">Recent Searches</div>`;
        html += historyList.map(city => `
            <div class="history-item" data-city="${city}">
                <span>🕒 ${highlightMatch(city, query)}</span>
            </div>
        `).join('');
    }

    if (filteredApiList.length > 0) {
        html += `<div class="dropdown-section-title">Global Cities</div>`;
        html += filteredApiList.map(city => `
            <div class="history-item" data-city="${city}">
                <span>📍 ${highlightMatch(city, query)}</span>
            </div>
        `).join('');
    }

    historyDropdown.innerHTML = html;
}

// 4. Helper function to make the matching letters bold
function highlightMatch(cityStr, query) {
    if (!query) return cityStr;
    const escapedQuery = query.replace(/[-[\]{}()*+?.,\\^$|#\s]/g, '\\$&');
    const regex = new RegExp(`(${escapedQuery})`, "gi");
    return cityStr.replace(regex, "<strong>$1</strong>");
}

// 5. Hide dropdown on click outside
document.addEventListener('click', (event) => {
    if (!searchInput.contains(event.target) && !historyDropdown.contains(event.target)) {
        historyDropdown.style.display = 'none';
    }
});

// --- TOAST NOTIFICATION SYSTEM ---
function showToast(message, type = 'success') {
    const container = document.getElementById('toast-container');
    if (!container) return;

    const toast = document.createElement('div');
    toast.className = `toast ${type}`;
    toast.textContent = message;

    container.appendChild(toast);

    requestAnimationFrame(() => {
        toast.classList.add('show');
    });

    setTimeout(() => {
        toast.classList.remove('show'); 
        setTimeout(() => toast.remove(), 300); 
    }, 3000);
}

// --- Event Listeners ---

searchInput.addEventListener('focus', () => {
    const query = searchInput.value.trim().toLowerCase();
    
    if (!query) {
        renderDropdownList(getHistory(), [], "");
    } else {
        searchInput.dispatchEvent(new Event('input'));
    }
});

searchInput.addEventListener('input', () => {
    clearTimeout(searchTimeout);
    const query = searchInput.value.trim().toLowerCase();

    if (!query) {
        renderDropdownList(getHistory(), [], query);
        return;
    }

    searchTimeout = setTimeout(async () => {
        const matchedHistory = getHistory().filter(city =>
            city.toLowerCase().startsWith(query) || city.toLowerCase().includes(query)
        );

        let apiSuggestions = [];
        try {
            const res = await fetch(`https://geocoding-api.open-meteo.com/v1/search?name=${encodeURIComponent(query)}&count=5&language=en&format=json`);
            if (res.ok) {
                const data = await res.json();
                if (data.results) {
                    apiSuggestions = data.results.map(r => `${r.name}, ${r.country}`);
                }
            }
        } catch (e) {}

        renderDropdownList(matchedHistory, apiSuggestions, query);
    }, 300);
});

searchInput.addEventListener('keydown', (e) => {
    if (e.key === 'Enter') addBtn.click();
});

addBtn.addEventListener('click', () => {
    const cityName = searchInput.value.trim();
    if (!cityName) return;

    searchInput.value = '';
    historyDropdown.style.display = 'none';
    
    handleAddCity(cityName);
});

unitToggle.addEventListener('click', () => {
    isCelsius = !isCelsius;
    
    const celsiusLabel = document.querySelector('.celsius');
    const fahrenheitLabel = document.querySelector('.fahrenheit');
    
    if (isCelsius) {
        unitToggle.classList.remove('fahrenheit-active');
        celsiusLabel.classList.add('active');
        fahrenheitLabel.classList.remove('active');
    } else {
        unitToggle.classList.add('fahrenheit-active');
        fahrenheitLabel.classList.add('active');
        celsiusLabel.classList.remove('active');
    }
    
    renderGrid();
});

historyDropdown.addEventListener('click', (event) => {
    const clickedItem = event.target.closest('.history-item');
    if (!clickedItem) return; 

    const cityName = clickedItem.getAttribute('data-city');

    historyDropdown.style.display = 'none';
    searchInput.value = '';

    handleAddCity(cityName);
});

// --- DARK MODE LOGIC ---
const themeToggle = document.getElementById('theme-toggle');
const savedTheme = localStorage.getItem('weather_theme') || 'light';
if (savedTheme === 'dark') {
    document.documentElement.setAttribute('data-theme', 'dark');
    themeToggle.textContent = '☀️';
}

themeToggle.addEventListener('click', () => {
    const currentTheme = document.documentElement.getAttribute('data-theme');
    
    if (currentTheme === 'dark') {
        document.documentElement.removeAttribute('data-theme');
        localStorage.setItem('weather_theme', 'light');
        themeToggle.textContent = '🌙';
    } else {
        document.documentElement.setAttribute('data-theme', 'dark');
        localStorage.setItem('weather_theme', 'dark');
        themeToggle.textContent = '☀️';
    }
});

// --- GEO HELPER FUNCTIONS ---
function getUserLocation() {
    return new Promise((resolve, reject) => {
        if (!navigator.geolocation) {
            reject(new Error("Geolocation is not supported by your browser."));
        } else {
            navigator.geolocation.getCurrentPosition(
                (position) => resolve({ lat: position.coords.latitude, lon: position.coords.longitude }),
                () => reject(new Error("Unable to retrieve your location."))
            );
        }
    });
}

async function getGeoCityName(lat, lon) {
    const res = await fetch(`https://api.bigdatacloud.net/data/reverse-geocode-client?latitude=${lat}&longitude=${lon}&localityLanguage=en`);
    if (!res.ok) throw new Error("Could not determine city name from coordinates.");
    const data = await res.json();
    return data.city || data.locality || data.principalSubdivision;
}

locateBtn.addEventListener('click', async () => {
    if (locateBtn.disabled) return;
    locateBtn.disabled = true;

    const svgIcon = locateBtn.querySelector('svg');
    svgIcon.classList.add('loading-spin');

    try {
        const { lat, lon } = await getUserLocation();
        const cityName = await getGeoCityName(lat, lon);
        
        if (cityName) {
            await handleAddCity(cityName);
        }
    } catch (error) {
        showToast(error.message, 'error');
    } finally {
        svgIcon.classList.remove('loading-spin');
        locateBtn.disabled = false; 
    }
});