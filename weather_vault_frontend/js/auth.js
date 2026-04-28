export class Auth {
    static async register(email, username, password) {
        const BASE_URL = 'https://puzzle-vanquish-gala.ngrok-free.dev';
        try {
            const response = await fetch(`${BASE_URL}/api/users/register`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ email, username, password }) // Added email
            });

            const data = await response.json();

            if (!response.ok) {
                // If it's a 422 Validation Error, translate it for humans
                if (Array.isArray(data.detail)) {
                    const friendlyErrors = data.detail.map(err => {
                        // Find out exactly which field caused the error (e.g., 'password' or 'username')
                        const fieldName = err.loc[err.loc.length - 1]; 
                        
                        // Translate specific Pydantic errors into plain English
                        if (fieldName === 'password' && err.type === 'string_too_short') {
                            return "Your password is too short. Please use at least 8 characters.";
                        }
                        if (fieldName === 'username' && err.type === 'string_too_short') {
                            return "Your username must be at least 3 characters long.";
                        }
                        if (err.type === 'missing') {
                            return `Oops! You forgot to enter a ${fieldName}.`;
                        }
                        
                        // Generic fallback: Capitalize the field name and show the message
                        return `${fieldName.charAt(0).toUpperCase() + fieldName.slice(1)}: ${err.msg}`;
                    }).join(' \n ');
                    
                    throw new Error(friendlyErrors);
                }
                
                // For standard 400/401 errors (like "Username already taken")
                throw new Error(data.detail || 'Registration failed.');
            }
            return true;
            
        } catch (error) {
            console.error("Registration Error:", error);
            throw error;
        }
    }
    
    static async login(identifier, password) {
        try {
            const response = await fetch(`${BASE_URL}/api/users/login`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ identifier, password }) // Changed to identifier
            });

            const data = await response.json();

            if (!response.ok) {
                // If it's a 422 Validation Error, translate it for humans
                if (Array.isArray(data.detail)) {
                    const friendlyErrors = data.detail.map(err => {
                        // Find out exactly which field caused the error (e.g., 'password' or 'username')
                        const fieldName = err.loc[err.loc.length - 1]; 
                        
                        // Translate specific Pydantic errors into plain English
                        if (fieldName === 'password' && err.type === 'string_too_short') {
                            return "Your password is too short. Please use at least 8 characters.";
                        }
                        if (fieldName === 'username' && err.type === 'string_too_short') {
                            return "Your username must be at least 3 characters long.";
                        }
                        if (err.type === 'missing') {
                            return `Oops! You forgot to enter a ${fieldName}.`;
                        }
                        
                        // Generic fallback: Capitalize the field name and show the message
                        return `${fieldName.charAt(0).toUpperCase() + fieldName.slice(1)}: ${err.msg}`;
                    }).join(' \n ');
                    
                    throw new Error(friendlyErrors);
                }
                
                // For standard 400/401 errors (like "Username already taken")
                throw new Error(data.detail || 'Registration failed.');
            }

            localStorage.setItem('weather_jwt', data.access_token);
            return true;
            
        } catch (error) {
            console.error("Auth Error:", error);
            throw error;
        }
    }

    static logout() {
        localStorage.removeItem('weather_jwt');
        window.location.reload();
    }

    static isAuthenticated() {
        return localStorage.getItem('weather_jwt') !== null;
    }
}