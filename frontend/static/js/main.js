// HR Compliance Platform - Main JavaScript

// Global configuration
const API_BASE_URL = '/api';
let authToken = localStorage.getItem('authToken');

// Utility functions
function showAlert(message, type = 'info') {
    const alertDiv = document.createElement('div');
    alertDiv.className = `alert alert-${type}`;
    alertDiv.textContent = message;
    
    const container = document.querySelector('.main-content .container');
    if (container) {
        container.insertBefore(alertDiv, container.firstChild);
        
        // Remove alert after 5 seconds
        setTimeout(() => {
            alertDiv.remove();
        }, 5000);
    }
}

function formatDate(dateString) {
    if (!dateString) return '-';
    const date = new Date(dateString);
    return date.toLocaleDateString() + ' ' + date.toLocaleTimeString([], {hour: '2-digit', minute:'2-digit'});
}

function formatFileSize(bytes) {
    if (bytes === 0) return '0 Bytes';
    const k = 1024;
    const sizes = ['Bytes', 'KB', 'MB', 'GB'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
}

// API request helper
async function apiRequest(endpoint, options = {}) {
    const url = `${API_BASE_URL}${endpoint}`;
    const defaultOptions = {
        headers: {
            'Content-Type': 'application/json',
        },
    };
    
    if (authToken) {
        defaultOptions.headers['Authorization'] = `Bearer ${authToken}`;
    }
    
    const finalOptions = { ...defaultOptions, ...options };
    
    // Don't set Content-Type for FormData
    if (options.body instanceof FormData) {
        delete finalOptions.headers['Content-Type'];
    }
    
    try {
        const response = await fetch(url, finalOptions);
        
        if (response.status === 401) {
            // Unauthorized - redirect to login
            localStorage.removeItem('authToken');
            window.location.href = '/login';
            return;
        }
        
        const data = await response.json();
        
        if (!response.ok) {
            throw new Error(data.detail || 'An error occurred');
        }
        
        return data;
    } catch (error) {
        console.error('API Request Error:', error);
        throw error;
    }
}

// Authentication functions
async function login(email, password) {
    try {
        const response = await apiRequest('/auth/login', {
            method: 'POST',
            body: JSON.stringify({ email, password }),
        });
        
        localStorage.setItem('authToken', response.access_token);
        authToken = response.access_token;
        
        // Get user info to determine redirect
        const userInfo = await apiRequest('/auth/me');
        
        if (userInfo.is_admin) {
            window.location.href = '/admin/dashboard';
        } else {
            window.location.href = '/client/portal';
        }
    } catch (error) {
        showAlert(error.message, 'danger');
    }
}

function logout() {
    localStorage.removeItem('authToken');
    authToken = null;
    window.location.href = '/login';
}

// Check if user is authenticated
function checkAuth() {
    if (!authToken) {
        window.location.href = '/login';
        return false;
    }
    return true;
}

// Document upload handler
async function uploadDocument(formData) {
    try {
        const response = await apiRequest('/documents/upload', {
            method: 'POST',
            body: formData,
        });
        
        showAlert('Document uploaded successfully', 'success');
        return response;
    } catch (error) {
        showAlert(error.message, 'danger');
        throw error;
    }
}

// File download handler
function downloadDocument(documentId, filename) {
    if (!authToken) {
        showAlert('Please log in to download documents', 'danger');
        return;
    }
    
    const link = document.createElement('a');
    link.href = `${API_BASE_URL}/documents/${documentId}/download`;
    link.download = filename;
    link.style.display = 'none';
    
    // Add authorization header by creating a temporary form
    const form = document.createElement('form');
    form.method = 'GET';
    form.action = link.href;
    form.style.display = 'none';
    
    document.body.appendChild(form);
    document.body.appendChild(link);
    
    // For downloads with auth, we need to open in new window
    window.open(`${API_BASE_URL}/documents/${documentId}/download?token=${authToken}`, '_blank');
    
    document.body.removeChild(form);
    document.body.removeChild(link);
}

// Form submission helpers
function handleFormSubmit(formElement, submitHandler) {
    formElement.addEventListener('submit', async (e) => {
        e.preventDefault();
        
        const submitButton = formElement.querySelector('button[type="submit"]');
        const originalText = submitButton.textContent;
        
        // Show loading state
        submitButton.disabled = true;
        submitButton.textContent = 'Processing...';
        
        try {
            await submitHandler(new FormData(formElement));
        } catch (error) {
            console.error('Form submission error:', error);
        } finally {
            // Reset button state
            submitButton.disabled = false;
            submitButton.textContent = originalText;
        }
    });
}

// Table sorting functionality
function makeSortable(tableElement) {
    const headers = tableElement.querySelectorAll('th[data-sortable]');
    
    headers.forEach(header => {
        header.style.cursor = 'pointer';
        header.addEventListener('click', () => {
            const column = header.dataset.sortable;
            const direction = header.dataset.direction === 'asc' ? 'desc' : 'asc';
            
            // Update header
            headers.forEach(h => h.classList.remove('sorted-asc', 'sorted-desc'));
            header.classList.add(`sorted-${direction}`);
            header.dataset.direction = direction;
            
            // Sort table rows
            sortTable(tableElement, column, direction);
        });
    });
}

function sortTable(table, column, direction) {
    const tbody = table.querySelector('tbody');
    const rows = Array.from(tbody.querySelectorAll('tr'));
    
    rows.sort((a, b) => {
        const aValue = a.querySelector(`[data-column="${column}"]`)?.textContent.trim() || '';
        const bValue = b.querySelector(`[data-column="${column}"]`)?.textContent.trim() || '';
        
        if (direction === 'asc') {
            return aValue.localeCompare(bValue, undefined, { numeric: true });
        } else {
            return bValue.localeCompare(aValue, undefined, { numeric: true });
        }
    });
    
    // Re-append sorted rows
    rows.forEach(row => tbody.appendChild(row));
}

// Modal functionality
function showModal(modalId) {
    const modal = document.getElementById(modalId);
    if (modal) {
        modal.style.display = 'block';
        document.body.style.overflow = 'hidden';
    }
}

function hideModal(modalId) {
    const modal = document.getElementById(modalId);
    if (modal) {
        modal.style.display = 'none';
        document.body.style.overflow = 'auto';
    }
}

// Initialize common functionality
document.addEventListener('DOMContentLoaded', function() {
    // Add logout functionality to logout buttons
    const logoutButtons = document.querySelectorAll('[data-action="logout"]');
    logoutButtons.forEach(button => {
        button.addEventListener('click', (e) => {
            e.preventDefault();
            logout();
        });
    });
    
    // Add click handlers for modal close buttons
    const modalCloseButtons = document.querySelectorAll('[data-dismiss="modal"]');
    modalCloseButtons.forEach(button => {
        button.addEventListener('click', (e) => {
            const modal = button.closest('.modal');
            if (modal) {
                hideModal(modal.id);
            }
        });
    });
    
    // Make tables sortable
    const sortableTables = document.querySelectorAll('.table[data-sortable]');
    sortableTables.forEach(makeSortable);
    
    // Auto-refresh functionality for dashboards
    const autoRefresh = document.querySelector('[data-auto-refresh]');
    if (autoRefresh) {
        const interval = parseInt(autoRefresh.dataset.autoRefresh) || 30000;
        setInterval(() => {
            if (typeof refreshDashboard === 'function') {
                refreshDashboard();
            }
        }, interval);
    }
});

// Export functions for use in other scripts
window.HRApp = {
    login,
    logout,
    checkAuth,
    uploadDocument,
    downloadDocument,
    apiRequest,
    showAlert,
    formatDate,
    formatFileSize,
    handleFormSubmit,
    showModal,
    hideModal
};