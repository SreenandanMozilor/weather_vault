export class Auth {
    static async register(email, username, password) {
        const BASE_URL = 'https://puzzle-vanquish-gala.ngrok-free.dev';
        try {
            console.log("Base URL for registration:", BASE_URL);
            const response = await fetch(`${BASE_URL}/api/users/register`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ email, username, password })
            });

            const data = await response.json();

            if (!response.ok) {
                if (Array.isArray(data.detail)) {
                    const friendlyErrors = data.detail.map(err => {

                        const fieldName = err.loc[err.loc.length - 1];


                        if (fieldName === 'password' && err.type === 'string_too_short') {
                            return "Your password is too short. Please use at least 8 characters.";
                        }
                        if (fieldName === 'username' && err.type === 'string_too_short') {
                            return "Your username must be at least 3 characters long.";
                        }
                        if (err.type === 'missing') {
                            return `Oops! You forgot to enter a ${fieldName}.`;
                        }


                        return `${fieldName.charAt(0).toUpperCase() + fieldName.slice(1)}: ${err.msg}`;
                    }).join(' \n ');

                    throw new Error(friendlyErrors);
                }


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
            const BASE_URL = 'https://puzzle-vanquish-gala.ngrok-free.dev';
            console.log("Base url",BASE_URL)
            const response = await fetch(`${BASE_URL}/api/users/login`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ identifier, password })
            });

            const data = await response.json();

            if (!response.ok) {

                if (Array.isArray(data.detail)) {
                    const friendlyErrors = data.detail.map(err => {

                        const fieldName = err.loc[err.loc.length - 1];

                        if (fieldName === 'password' && err.type === 'string_too_short') {
                            return "Your password is too short. Please use at least 8 characters.";
                        }
                        if (fieldName === 'username' && err.type === 'string_too_short') {
                            return "Your username must be at least 3 characters long.";
                        }
                        if (err.type === 'missing') {
                            return `Oops! You forgot to enter a ${fieldName}.`;
                        }

                        return `${fieldName.charAt(0).toUpperCase() + fieldName.slice(1)}: ${err.msg}`;
                    }).join(' \n ');

                    throw new Error(friendlyErrors);
                }

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