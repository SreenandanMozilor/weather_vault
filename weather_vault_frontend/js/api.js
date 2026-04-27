export class ApiClient {
    static getHeaders() {
        const token = localStorage.getItem('weather_jwt');
        return {
            'Content-Type': 'application/json',
            'Authorization': `Bearer ${token}`
        };
    }

    static async request(endpoint, options = {}, retries = 2) {
        const fetchUrl = `http://127.0.0.1:8000/api${endpoint}`;
        const fetchOptions = {
            method: options.method || 'GET',
            headers: this.getHeaders(),
            cache: 'no-store', // THE FIX: Forces Chrome to always get fresh data from the DB!
            ...options
        };

        try {
            const response = await fetch(fetchUrl, fetchOptions);
            const data = await response.json();
            
            if (!response.ok) {
                // Translate any Pydantic validation arrays into readable text
                if (Array.isArray(data.detail)) {
                    throw new Error(data.detail.map(err => err.msg).join(', '));
                }
                throw new Error(data.detail || 'API request failed');
            }
            return data;

        } catch (error) {
            // THE SHOCK ABSORBER: If Uvicorn restarts, wait 500ms and try again silently!
            if (error.message.includes('Failed to fetch') && retries > 0) {
                console.warn(`Server reloading... pausing and retrying ${endpoint}`);
                await new Promise(resolve => setTimeout(resolve, 500));
                return this.request(endpoint, options, retries - 1);
            }
            throw error;
        }
    }

    static async getCurrentWeather(cityName) {
        return this.request(`/weather/current?city_name=${encodeURIComponent(cityName)}`);
    }
}