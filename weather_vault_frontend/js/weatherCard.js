import { getWeatherClass, getWeatherIcon } from './ui-utils.js';

export function createCard(city, isCelsius, onRemove) {
    const current = city.current_weather || {};
    
    const weatherCode = current.weather_code || 0;
    const temp = current.temperature_2m || 0;
    const feelsLike = current.apparent_temperature || 0;
    const humidity = current.relative_humidity_2m || 0;
    const wind = current.wind_speed_10m || 0;
    
    const themeClass = getWeatherClass(weatherCode);
    const displayTemp = isCelsius ? temp : (temp * 9/5 + 32);
    const displayFeels = isCelsius ? feelsLike : (feelsLike * 9/5 + 32);
    const unit = isCelsius ? '°C' : '°F';
    const currentIcon = getWeatherIcon(weatherCode);

    // --- THE FIX: Smart Title Formatting ---
    // If the city_name already contains the country, don't append it again!
    let formattedTitle = city.city_name;
    if (city.country && !formattedTitle.includes(city.country)) {
        formattedTitle += `, ${city.country}`;
    }

    const card = document.createElement('div');
    card.className = `weather-card ${themeClass}`;
    
    card.innerHTML = `
        <button class="remove-btn">✖</button>
        <h2>${formattedTitle}</h2>
        <div class="current-weather">
            <div>
                <h1 class="temp">${Math.round(displayTemp)}${unit}</h1>
                <p class="feels-like">Feels like: ${Math.round(displayFeels)}${unit}</p>
            </div>
            <div class="current-icon">${currentIcon}</div>
        </div>
        
        <div class="details">
            <span>💧 ${humidity}%</span>
            <span>💨 ${wind} km/h</span>
        </div>
    `;

    card.querySelector('.remove-btn').addEventListener('click', onRemove);
    return card;
}

export function createErrorCard(err, onRemove, onRetry) {
    const icon = err.type === 'NOT_FOUND' ? '🌐' : '⚡';
    const title = err.type === 'NOT_FOUND' ? 'City Not Found' : 'Network Error';
    const btnLabel = err.type === 'NOT_FOUND' ? 'Try Again' : '↺ Retry';
    
    const card = document.createElement('div');
    card.className = 'weather-card error-card';
    card.setAttribute('data-error-id', err.id);

    card.innerHTML = `
        <button class="remove-error-btn">✖</button>
        <div class="error-icon">${icon}</div>
        <h3>${title}</h3>
        <p>${err.type === 'NOT_FOUND' 
            ? `We couldn't find "${err.cityName}". Check the spelling.`
            : `Failed to fetch weather for "${err.cityName}".`}</p>
        <button class="retry-error-btn">${btnLabel}</button>
    `;

    card.querySelector('.remove-error-btn').addEventListener('click', onRemove);
    card.querySelector('.retry-error-btn').addEventListener('click', () => onRetry(err.cityName));
    
    return card;
}

export function createSkeletonCard() {
    const card = document.createElement('div');
    card.className = 'weather-card skeleton card';
    card.innerHTML = '<div class="shimmer"></div>';
    return card;
}