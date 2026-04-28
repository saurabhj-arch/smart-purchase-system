/**
 * API utility functions for making authenticated requests
 */

const API_BASE_URL = "http://127.0.0.1:8000/api";

/**
 * Get the authorization headers with JWT token if available
 */
function getAuthHeaders() {
  const headers = { "Content-Type": "application/json" };
  const token = localStorage.getItem("access");
  if (token) {
    headers["Authorization"] = `Bearer ${token}`;
  }
  return headers;
}

/**
 * Generic fetch wrapper that includes auth headers
 */
async function apiCall(endpoint, options = {}) {
  const url = `${API_BASE_URL}${endpoint}`;
  const headers = getAuthHeaders();
  
  const response = await fetch(url, {
    ...options,
    headers: { ...headers, ...options.headers },
  });

  if (!response.ok) {
    const error = await response.json().catch(() => ({}));
    throw new Error(error.error || error.detail || `HTTP ${response.status}`);
  }

  return response.json();
}

/**
 * Search for products
 */
export function searchProducts(query) {
  return apiCall("/search/", {
    method: "POST",
    body: JSON.stringify({ query }),
  });
}

/**
 * Get all products
 */
export function getAllProducts() {
  return apiCall("/products/");
}

/**
 * Get product prices and details
 */
export function getProductPrices(productId) {
  return apiCall(`/search/product/${productId}/`);
}

/**
 * User registration
 */
export function register(userData) {
  return apiCall("/accounts/register/", {
    method: "POST",
    body: JSON.stringify(userData),
  });
}

/**
 * User login
 */
export function login(username, password) {
  return apiCall("/accounts/login/", {
    method: "POST",
    body: JSON.stringify({ username, password }),
  });
}

/**
 * Get user profile
 */
export function getUserProfile() {
  return apiCall("/accounts/profile/");
}

/**
 * Get recently viewed products for authenticated user
 */
export function getRecentlyViewed() {
  return apiCall("/accounts/recently-viewed/");
}

export default {
  searchProducts,
  getAllProducts,
  getProductPrices,
  register,
  login,
  getUserProfile,
  getRecentlyViewed,
};
