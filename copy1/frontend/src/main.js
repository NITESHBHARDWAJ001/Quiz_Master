import { createApp } from 'vue';
import App from './App.vue';
import router from './router';
import 'bootstrap/dist/css/bootstrap.min.css';
import 'bootstrap/dist/js/bootstrap.bundle.min.js';
import 'bootstrap-icons/font/bootstrap-icons.css'; // Add Bootstrap Icons
import axios from 'axios';

// Set up Axios globally
axios.defaults.baseURL = 'http://127.0.0.1:5000'; // Flask backend base URL
axios.defaults.headers = {
  'Content-Type': 'application/json',
};

const app = createApp(App);
app.config.globalProperties.$http = axios;  // Make Axios available globally in all components

app.use(router).mount('#app');
