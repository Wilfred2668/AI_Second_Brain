// API Configuration
const API_URL = process.env.REACT_APP_API_URL || 'http://localhost:8001';

// Helper to add ngrok headers if using ngrok
export const getHeaders = () => {
  const headers = {
    'Content-Type': 'application/json'
  };
  
  // Add ngrok bypass header if using ngrok URL
  if (API_URL.includes('ngrok')) {
    headers['ngrok-skip-browser-warning'] = 'true';
  }
  
  return headers;
};

export default API_URL;
