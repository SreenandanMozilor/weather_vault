import { Auth } from './auth.js';
import { initDashboard } from './ui.js';

// 1. Grab all DOM Elements
const loginView = document.getElementById('login-view');
const dashboardView = document.getElementById('dashboard-view');
const loginForm = document.getElementById('login-form');
const loginError = document.getElementById('login-error');
const logoutBtn = document.getElementById('logout-btn');

const loginContainer = document.getElementById('login-container');
const signupContainer = document.getElementById('signup-container');
const signupForm = document.getElementById('signup-form');
const signupError = document.getElementById('signup-error');
const showSignupBtn = document.getElementById('show-signup');
const showLoginBtn = document.getElementById('show-login');

// 2. Determine which screen to show
function updateUI() {
    if (Auth.isAuthenticated()) {
        loginView.classList.add('hidden');
        dashboardView.classList.remove('hidden');
        initDashboard(); 
    } else {
        loginView.classList.remove('hidden');
        dashboardView.classList.add('hidden');
    }
}

// 3. Toggle between Login and Sign Up views
showSignupBtn?.addEventListener('click', (e) => {
    e.preventDefault();
    loginContainer.classList.add('hidden');
    signupContainer.classList.remove('hidden');
    loginError.classList.add('hidden'); // Clear old errors
});

showLoginBtn?.addEventListener('click', (e) => {
    e.preventDefault();
    signupContainer.classList.add('hidden');
    loginContainer.classList.remove('hidden');
    signupError.classList.add('hidden');
});

// 4. Handle Login Submit
loginForm?.addEventListener('submit', async (e) => {
    e.preventDefault();
    try {
        loginError.classList.add('hidden');
        // Grab the new dual-purpose identifier field
        const identifier = document.getElementById('login-identifier').value;
        const password = document.getElementById('password').value;
        
        await Auth.login(identifier, password);
        updateUI();
    } catch (error) {
        loginError.textContent = error.message;
        loginError.classList.remove('hidden');
    }
});

// 5. Handle Sign Up Submit
signupForm?.addEventListener('submit', async (e) => {
    e.preventDefault();
    try {
        signupError.classList.add('hidden');
        // Grab all three identical-looking fields
        const email = document.getElementById('signup-email').value;
        const username = document.getElementById('signup-username').value;
        const password = document.getElementById('signup-password').value;
        
        await Auth.register(email, username, password);
        await Auth.login(username, password); // Auto-login after registering
        updateUI();
    } catch (error) {
        signupError.textContent = error.message;
        signupError.classList.remove('hidden');
    }
});

// 6. Handle Logout
logoutBtn?.addEventListener('click', () => Auth.logout());

// Start the engine
updateUI();