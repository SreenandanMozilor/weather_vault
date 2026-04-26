export function getWeatherClass(code) {
    // Grouping codes by visual category
    if (code === 0) return 'sunny';
    if (code >= 1 && code <= 3) return 'cloudy';
    if ([45, 48].includes(code)) return 'foggy';
    if ([51, 53, 55, 61, 63, 65, 80, 81, 82].includes(code)) return 'rainy';
    if ([71, 73, 75, 77, 85, 86].includes(code)) return 'snowy';
    if (code >= 95) return 'stormy';
    
    return 'default'; // Fallback
}

export function getWeatherIcon(code) {
    if (code === 0) return '☀️';
    if (code >= 1 && code <= 3) return '⛅';
    if ([45, 48].includes(code)) return '🌫️';
    if ([51, 53, 55, 61, 63, 65, 80, 81, 82].includes(code)) return '🌧️';
    if ([71, 73, 75, 77, 85, 86].includes(code)) return '❄️';
    if (code >= 95) return '⛈️';
    
    return '🌤️'; // Fallback
}