import { ApiClient } from './api.js';

export class Auth {
    static async register(username, password) {
        try {
            const response = await fetch('http://127.0.0.1:8000/api/users/register', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json', // Registration expects standard JSON!
                },
                body: JSON.stringify({ username, password })
            });

            const data = await response.json();

            if (!response.ok) {
                // Pydantic validation errors or duplicate usernames will trigger this
                throw new Error(data.detail || 'Registration failed. Username may be taken.');
            }

            return true;
            
        } catch (error) {
            console.error("Registration Error:", error);
            throw error;
        }
    }
    
    static async login(username, password) {
        // FastAPI's OAuth2PasswordRequestForm requires URL Encoded data, not JSON!
        const formData = new URLSearchParams();
        formData.append('username', username);
        formData.append('password', password);

        try {
            // We use standard fetch here because the headers are slightly different for login
            const response = await fetch('http://127.0.0.1:8000/api/users/login', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/x-www-form-urlencoded',
                },
                body: formData.toString()
            });

            const data = await response.json();

            if (!response.ok) {
                throw new Error(data.detail || 'Login failed');
            }

            // Save the passport to the browser's vault!
            localStorage.setItem('weather_jwt', data.access_token);
            return true;
            
        } catch (error) {
            console.error("Auth Error:", error);
            throw error;
        }
    }

    static logout() {
        localStorage.removeItem('weather_jwt');
        // Refresh the page to clear out the UI
        window.location.reload();
    }

    static isAuthenticated() {
        return localStorage.getItem('weather_jwt') !== null;
    }
}