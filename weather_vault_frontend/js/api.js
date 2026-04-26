// The base URL of your Python FastAPI server
const BASE_URL = 'http://127.0.0.1:8000/api';

export class ApiClient {
    // A helper method to automatically attach the JWT passport to requests
    static getHeaders() {
        const token = localStorage.getItem('weather_jwt');
        const headers = {
            'Content-Type': 'application/json'
        };
        
        if (token) {
            headers['Authorization'] = `Bearer ${token}`;
        }
        
        return headers;
    }

    // A unified fetch method that automatically throws errors if the backend rejects it
    static async request(endpoint, options = {}) {
        const url = `${BASE_URL}${endpoint}`;
        const response = await fetch(url, {
            ...options,
            headers: this.getHeaders()
        });

        const data = await response.json();

        if (!response.ok) {
            // This will catch the 400 Bad Request if they try to save a 9th city!
            throw new Error(data.detail || 'An API error occurred');
        }

        return data;
    }
}