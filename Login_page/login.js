// No longer defining handleCredentialResponse here as it's in login.html

// Global variables for DOM elements (initialized to null, will be assigned on DOMContentLoaded)
let loginSection = null;
let signupSection = null;
let forgotSection = null;
let profileSection = null;

let switchToSignup = null;

let signupForm = null;
let signupName = null;
let signupEmail = null;
let signupPassword = null;
let signupNameError = null;
let signupEmailError = null;
let signupPasswordError = null;
let toggleSignupPassword = null;

let userEmailElement = null;
let memberSinceElement = null;
let historyList = null;
let logoutBtn = null;

document.addEventListener('DOMContentLoaded', function() {
    // Assign references inside DOMContentLoaded
    loginSection = document.getElementById('loginSection');
    signupSection = document.getElementById('signupSection');
    forgotSection = document.getElementById('forgotSection');
    profileSection = document.getElementById('profileSection');

    switchToSignup = document.getElementById('switchToSignup');

    signupForm = document.getElementById('signupForm');
    signupName = document.getElementById('signupName');
    signupEmail = document.getElementById('signupEmail');
    signupPassword = document.getElementById('signupPassword');
    signupNameError = document.getElementById('signupNameError');
    signupEmailError = document.getElementById('signupEmailError');
    signupPasswordError = document.getElementById('signupPasswordError');
    toggleSignupPassword = document.getElementById('toggleSignupPassword');

    userEmailElement = document.getElementById('userEmail');
    memberSinceElement = document.getElementById('memberSince');
    historyList = document.getElementById('historyList');
    logoutBtn = document.getElementById('logoutBtn');

    // Check if a Google credential response was received before DOMContentLoaded
    if (window.googleCredentialResponse) {
        processGoogleLoginResponse(window.googleCredentialResponse);
    } else {
        console.log('No Google credential response yet on DOMContentLoaded. Waiting for user interaction.');
    }

    if (switchToSignup) {
        switchToSignup.addEventListener('click', function(e) {
            e.preventDefault();
            showSection(signupSection);
        });
    }

    // Toggle password visibility (signup form only)
    if (toggleSignupPassword && signupPassword) {
        toggleSignupPassword.addEventListener('click', function() {
            const type = signupPassword.getAttribute('type') === 'password' ? 'text' : 'password';
            signupPassword.setAttribute('type', type);
            this.querySelector('i').classList.toggle('fa-eye');
            this.querySelector('i').classList.toggle('fa-eye-slash');
        });
    }

    // Validation helpers
    function validateEmail(email) {
        const re = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
        return re.test(email);
    }

    function showError(element, message) {
        if (element) {
            element.style.display = 'block';
            element.textContent = message;
        }
    }

    function hideError(element) {
         if (element) {
            element.style.display = 'none';
         }
    }

    // Handle signup form submission
    if (signupForm) {
        signupForm.addEventListener('submit', async function(e) {
            e.preventDefault();

            hideError(signupNameError);
            hideError(signupEmailError);
            hideError(signupPasswordError);

            const username = signupName.value;
            const email = signupEmail.value;
            const password = signupPassword.value;

            let valid = true;
            if (username.trim().length === 0) {
                showError(signupNameError, 'Name is required');
                valid = false;
            }
            if (!validateEmail(email)) {
                showError(signupEmailError, 'Please enter a valid email address');
                valid = false;
            }
            if (password.length < 6) {
                showError(signupPasswordError, 'Password must be at least 6 characters');
                valid = false;
            }

            if (!valid) {
                return; // Stop if validation fails
            }

            try {
                // API call to backend register endpoint
                const response = await fetch('http://127.0.0.1:5500/register', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                    },
                    body: JSON.stringify({ username, email, password }),
                });

                const data = await response.json();

                if (response.ok) {
                    // Signup successful
                     const forgotSuccessMsg = document.getElementById('forgotSuccessMsg'); // Get ref here as it's in a different section
                    if (forgotSuccessMsg) {
                        forgotSuccessMsg.textContent = data.msg || 'Account created successfully! Please log in.';
                        forgotSuccessMsg.style.display = 'block';
                    }
                     // Clear form
                    signupForm.reset();
                     // Switch to login section (Google sign-in view)
                    setTimeout(() => { // Small delay before switching
                         if (forgotSuccessMsg) forgotSuccessMsg.style.display = 'none'; // Hide success message
                        showSection(loginSection);
                     }, 2000);

                } else {
                    // Signup failed
                    const errorMessage = data.msg || 'Signup failed';
                    showError(signupEmailError, errorMessage); // Display error message
                }

            } catch (error) {
                console.error('Error during signup:', error);
                showError(signupEmailError, 'An error occurred during signup. Please try again.');
            }
        });
    }

    // Initial check for login status when the page loads
    checkIframeLoginStatus();

    // Add event listener for the logout button
    if (logoutBtn) {
        logoutBtn.addEventListener('click', handleLogout);
    }

    // Event listener for messages from parent window (if any)
    window.addEventListener('message', function(event) {
        // Check event.origin for security in a real app
        if (event.data.type === 'googleCredential') {
            processGoogleLoginResponse(event.data.credential);
        }
    });
});

// Toggle between sections - Now globally accessible
function showSection(section) {
    if (loginSection) loginSection.style.display = 'none';
    if (signupSection) signupSection.style.display = 'none';
    if (forgotSection) forgotSection.style.display = 'none';
    if (profileSection) profileSection.style.display = 'none';
    if (section) section.style.display = 'block';

    // Fetch history if showing profile section
    if (section === profileSection) {
        fetchCheckupHistory();
    }
}

// Functions related to profile and history, now globally accessible
function handleLogout() {
    localStorage.removeItem('accessToken');
    localStorage.removeItem('userEmail');
    showSection(loginSection); // Use global loginSection
}

function checkIframeLoginStatus() {
    const accessToken = localStorage.getItem('accessToken');
    const userEmail = localStorage.getItem('userEmail');
    if (accessToken && userEmail) {
        if (userEmailElement) userEmailElement.textContent = userEmail;
        if (memberSinceElement) memberSinceElement.textContent = 'N/A'; // Placeholder for now
        showSection(profileSection);
    } else {
        showSection(loginSection);
    }
}

async function fetchCheckupHistory() {
    if (!historyList) return;

    const accessToken = localStorage.getItem('accessToken');
    if (!accessToken) {
        historyList.innerHTML = '<p class="text-muted">Please log in to view history.</p>';
        return;
    }

    historyList.innerHTML = '<p class="text-muted">Loading history...</p>'; // Loading indicator

    try {
        const response = await fetch('http://127.0.0.1:5500/history', {
            method: 'GET',
            headers: {
                'Authorization': `Bearer ${accessToken}`,
                'Content-Type': 'application/json',
            },
        });

        const data = await response.json();

        if (response.ok) {
            if (data.history && data.history.length > 0) {
                historyList.innerHTML = '';
                data.history.forEach(item => {
                    const listItem = document.createElement('div');
                    listItem.classList.add('list-group-item', 'd-flex', 'justify-content', 'align-items-center');
                    listItem.innerHTML = `
                        <div>
                            <h6 class="mb-1">${item.type || 'Checkup'}</h6>
                            <small class="text-muted">Date: ${item.date || 'N/A'}</small>
                        </div>
                        <span class="badge bg-primary rounded-pill">${item.result || 'N/A'}</span>
                    `;
                    historyList.appendChild(listItem);
                });
            } else {
                historyList.innerHTML = '<p class="text-muted">No history found.</p>';
            }
        } else {
            console.error('Failed to fetch history:', data.msg || response.statusText);
            historyList.innerHTML = '<p class="text-danger">Failed to load history.</p>';
        }
    } catch (error) {
        console.error('Error fetching history:', error);
        historyList.innerHTML = '<p class="text-danger">An error occurred while loading history.</p>';
    }
}

async function processGoogleLoginResponse(response) {
    console.log("Processing Google credential response:", response);
    const id_token = response.credential;

    try {
        const backendResponse = await fetch('http://127.0.0.1:5500/api/google-login', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ id_token: id_token }),
        });

        const data = await backendResponse.json();

        if (backendResponse.ok) {
            console.log("Backend response:", data);
            // Assuming your backend sends back user info and an access token
            localStorage.setItem('accessToken', data.access_token);
            localStorage.setItem('userEmail', data.user.email);
            // You might want to store user name as well if available
            localStorage.setItem('userName', data.user.name);

            alert("Login successful!");
            showSection(profileSection); // Show profile section on successful login

            // Optionally, refresh page or redirect to dashboard
            // window.location.href = '/dashboard';
        } else {
            console.error("Backend error:", data.error);
            alert("Google login failed: " + (data.error || "Unknown error"));
        }

    } catch (error) {
        console.error("Error sending ID token to backend:", error);
        alert("An error occurred during Google login. Please try again.");
    }
}