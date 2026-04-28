export class ApiClient {
    static getHeaders() {
        const token = localStorage.getItem('weather_jwt');
        return {
            'Content-Type': 'application/json',
            'Authorization': `Bearer ${token}`,
            'ngrok-skip-browser-warning': 'true'
        };
    }

    static async request(endpoint, options = {}, retries = 2) {
        const BASE_URL = 'https://puzzle-vanquish-gala.ngrok-free.dev';
        const fetchUrl = `${BASE_URL}/api${endpoint}`;
        const fetchOptions = {
            method: options.method || 'GET',
            headers: this.getHeaders(),
            cache: 'no-store',
            ...options
        };

        try {
            const response = await fetch(fetchUrl, fetchOptions);
            const data = await response.json();
            
            if (!response.ok) {
                if (response.status === 401 && data.detail === "Could not validate credentials") {
                    alert("Could not validate credentials. Your session has expired, logging you out...");
                    localStorage.removeItem('weather_jwt'); // Clear the bad token
                    window.location.reload(); // Reloads the page to exit dashboard
                    return; // Stop execution
                }
                // Translate any Pydantic validation arrays into readable text
                if (Array.isArray(data.detail)) {
                    throw new Error(data.detail.map(err => err.msg).join(', '));
                }
                throw new Error(data.detail || 'API request failed');
            }
            return data;

        } catch (error) {
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

    static async getCurrentUser() {
        return this.request('/users/me');
    }
}