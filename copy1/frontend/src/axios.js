import axios from 'axios';

const instance = axios.create({
  baseURL: 'http://127.0.0.1:5000', // Backend URL
  timeout: 10000, // Increased timeout for notification requests which may take longer
  headers: {
    'Content-Type': 'application/json',
  },
});

// Add a request interceptor to include the Authorization header
instance.interceptors.request.use(
  (config) => {
    // Better debug logging for API calls
    const methodColor = config.method === 'get' ? 'color:blue' : 'color:green';
    console.log(`%c${config.method.toUpperCase()} ${config.url}`, methodColor, config.data || '');
    
    const token = localStorage.getItem('auth_token');
    if (token) {
      // Ensure token is properly formatted with Bearer prefix
      if (!token.startsWith('Bearer ')) {
        config.headers.Authorization = `Bearer ${token}`;
        console.log('Added Bearer prefix to token');
      } else {
        config.headers.Authorization = token;
        console.log('Token already had Bearer prefix');
      }
      
      // Debug full headers
      console.log('Request headers:', JSON.stringify(config.headers));
    } else {
      console.warn('No auth token found in localStorage');
    }
    
    // For notification endpoints, increase timeout
    if (config.url && (
      config.url.includes('notify') || 
      config.url.includes('notification') ||
      config.url.includes('email')
    )) {
      config.timeout = 30000; // 30 seconds for notification requests
    }
    
    return config;
  },
  (error) => {
    console.error('Request interceptor error:', error);
    return Promise.reject(error);
  }
);

// Add a response interceptor to handle common errors
instance.interceptors.response.use(
  (response) => {
    return response;
  },
  (error) => {
    console.error('Response error:', error.response || error);
    
    // Handle authentication errors
    if (error.response && error.response.status === 401) {
      console.log('Authentication error detected, clearing session data');
      localStorage.removeItem('auth_token');
      localStorage.removeItem('user_id');
      localStorage.removeItem('username');
      localStorage.removeItem('user_type');
      
      // Redirect to login page
      window.location.href = '/login';
    }
    
    return Promise.reject(error);
  }
);

export default instance;
