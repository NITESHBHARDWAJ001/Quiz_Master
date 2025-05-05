<template>
  <nav class="navbar navbar-expand-lg navbar-light bg-light px-4">
    <div class="container-fluid">
      <!-- Left Side: Brand Name -->
      <a class="navbar-brand fw-bold" href="#">
        <span class="d-block">Quiz</span>
        <span class="d-block">Master</span>
      </a>

      <!-- Navbar Toggle for Mobile -->
      <button
        class="navbar-toggler"
        type="button"
        data-bs-toggle="collapse"
        data-bs-target="#navbarNav"
      >
        <span class="navbar-toggler-icon"></span>
      </button>

      <div class="collapse navbar-collapse" id="navbarNav">
        <!-- Center: Navigation Links -->
        <ul class="navbar-nav mx-auto">
          <li class="nav-item">
            <router-link to="/" class="nav-link active">Home</router-link>
          </li>
          <!-- Admin sees AdminDashboard, normal users see Quiz - these are now highlighted better -->
          <li class="nav-item" v-if="isAdmin">
            <router-link to="/AdminDashboard" class="nav-link btn btn-outline-primary mx-1">
              <i class="bi bi-speedometer2 me-1"></i>Admin Dashboard
            </router-link>
          </li>
          <li class="nav-item" v-if="!isAdmin && isLoggedIn">
            <router-link to="/quiz" class="nav-link btn btn-outline-success mx-1">
              <i class="bi bi-question-circle me-1"></i>Take Quiz
            </router-link>
          </li>
          <li class="nav-item">
            <router-link to="/search" class="nav-link">Search</router-link>
          </li>
        </ul>

        <!-- Search Bar -->
        <form class="d-flex search-bar-container" @submit.prevent="performSearch">
          <div class="input-group">
            <input 
              class="form-control search-bar" 
              type="search" 
              placeholder="Search by subject, chapter, quiz, or user..." 
              v-model="searchQuery"
              aria-label="Search"
              aria-describedby="search-addon"
            />
            <select v-model="searchType" class="form-select search-type" aria-label="Search type">
              <option value="all">All</option>
              <option value="subjects">Subjects</option>
              <option value="chapters">Chapters</option>
              <option value="quizzes">Quizzes</option>
              <option v-if="isAdmin" value="users">Users</option>
            </select>
            <button type="submit" class="btn btn-primary">
              <i class="bi bi-search"></i>
            </button>
          </div>
        </form>

        <!-- Right Side: User Links -->
        <ul class="navbar-nav">
          <li class="nav-item" v-if="!isAdmin && isLoggedIn">
            <router-link to="/progress" class="nav-link">User Progress</router-link>
          </li>
          <li class="nav-item" v-if="!isLoggedIn">
            <router-link to="/register" class="nav-link">Register</router-link>
          </li>
          <li class="nav-item">
            <router-link v-if="!isLoggedIn" to="/login" class="nav-link">Login</router-link>
            <a v-else @click="logout" class="nav-link" style="cursor: pointer;">
              <span class="badge bg-secondary me-1">{{ isAdmin ? 'Admin' : 'User' }}</span>
              Logout ({{ username }})
            </a>
          </li>
          <li class="nav-item">
            <button class="btn btn-outline-info" @click="checkConnection">Check Backend</button>
          </li>
        </ul>
      </div>
    </div>
    
  </nav>

  <!-- Main Content Section -->
  <div class="container mt-4">
    <!-- Welcome Section - Only show on home route -->
    <div v-if="$route.path === '/'" class="welcome-section text-center py-5 mb-4">
      <div class="row justify-content-center">
        <div class="col-md-8">
          <h1 class="display-4 fw-bold text-primary mb-3">Welcome to Quiz Master!</h1>
          <p class="lead mb-4">Expand your knowledge and challenge yourself with our interactive quizzes.</p>
          
          <div v-if="isLoggedIn" class="welcome-user mb-4">
            <h3 class="text-success">Hello, {{ username }}!</h3>
            <p>Ready for your next knowledge adventure?</p>
          </div>
          
          <div class="d-grid gap-3 d-sm-flex justify-content-sm-center mt-4">
            <router-link to="/quiz" class="btn btn-primary btn-lg px-4 gap-3">
              <i class="bi bi-play-circle me-2"></i>Start a Quiz
            </router-link>
            <router-link to="/progress" class="btn btn-outline-secondary btn-lg px-4">
              <i class="bi bi-graph-up me-2"></i>View My Progress
            </router-link>
          </div>
        </div>
      </div>
    </div>

    <!-- Feature Cards - Only show on home route -->
    <div v-if="$route.path === '/'" class="row gx-4 gx-lg-5 mb-5">
      <div class="col-md-4 mb-4">
        <div class="card h-100 shadow-sm">
          <div class="card-body text-center">
            <i class="bi bi-lightning-charge feature-icon text-warning"></i>
            <h3 class="card-title mb-3">Challenge Yourself</h3>
            <p class="card-text">Test your knowledge with quizzes across various subjects and difficulty levels.</p>
            <router-link to="/quiz" class="btn btn-sm btn-primary">Take a Quiz</router-link>
          </div>
        </div>
      </div>
      
      <div class="col-md-4 mb-4">
        <div class="card h-100 shadow-sm">
          <div class="card-body text-center">
            <i class="bi bi-trophy feature-icon text-success"></i>
            <h3 class="card-title mb-3">Track Progress</h3>
            <p class="card-text">Monitor your performance and see how you improve over time.</p>
            <router-link to="/progress" class="btn btn-sm btn-primary">View Progress</router-link>
          </div>
        </div>
      </div>
      
      <div class="col-md-4 mb-4">
        <div class="card h-100 shadow-sm">
          <div class="card-body text-center">
            <i class="bi bi-search feature-icon text-info"></i>
            <h3 class="card-title mb-3">Find Quizzes</h3>
            <p class="card-text">Discover new quizzes on topics that interest you.</p>
            <router-link to="/search" class="btn btn-sm btn-primary">Search Quizzes</router-link>
          </div>
        </div>
      </div>
    </div>
    
    <router-view></router-view>
    <!-- Display Connection Status -->
    <div v-if="connectionStatus" class="alert alert-info mt-3">
      {{ connectionStatus }}
    </div>
  </div>
</template>

<script>
import axios from "axios";

export default {
  name: "HomePage",
  data() {
    return {
      connectionStatus: null,
      isLoggedIn: false,
      username: "Guest",
      searchQuery: "",
      searchType: "all",
      isSearching: false
    };
  },
  computed: {
    // Add a computed property to check if user is admin
    isAdmin() {
      return localStorage.getItem("user_type") === "admin";
    }
  },
  methods: {
    async checkConnection() {
      try {
        const response = await axios.get("http://localhost:5000/check-session");
        this.connectionStatus = response.data.message;
      } catch (error) {
        this.connectionStatus = "Failed to connect to backend. Please check the backend server.";
      }
    },
    logout() {
      // Clear both possible token keys
      localStorage.removeItem("access_token");
      localStorage.removeItem("auth_token");
      localStorage.removeItem("user_id");
      localStorage.removeItem("username");
      localStorage.removeItem("user_type");
      
      this.checkLoginStatus(); // Immediately update the UI state
      this.$router.push("/login"); // Redirect to login page
    },
    performSearch() {
      if (this.searchQuery.trim()) {
        // Show loading indicator
        this.isSearching = true;
        
        // Navigate to search results page with query parameters
        this.$router.push({
          path: '/search-results',
          query: { 
            q: this.searchQuery,
            type: this.searchType,
            async: 'true' // Enable async processing with Celery
          }
        });
        
        // Reset search after submission
        this.searchQuery = "";
      }
    },
    checkLoginStatus() {
      // Debug all localStorage keys
      console.log("Available localStorage keys:");
      for (let i = 0; i < localStorage.length; i++) {
        const key = localStorage.key(i);
        console.log(`- ${key}: ${localStorage.getItem(key)}`);
      }
      
      // Check for tokens with either key (access_token or auth_token)
      const token = localStorage.getItem("access_token") || localStorage.getItem("auth_token");
      const username = localStorage.getItem("username");
      const userId = localStorage.getItem("user_id");
      
      // Update login state
      this.isLoggedIn = token !== null && token !== undefined;
      this.username = username || "Guest";
      
      console.log("Token check:", !!token, "User ID:", userId, "Username:", username);
      console.log("Login status:", this.isLoggedIn, "Admin:", this.isAdmin, "Username:", this.username);
    }
  },
  created() {
    // Auto-check session on page load
    this.checkConnection();
    
    // Call login check with a slight delay to ensure localStorage is loaded
    setTimeout(() => {
      this.checkLoginStatus();
    }, 100);
    
    // Enhanced event listener for login state changes
    window.addEventListener('storage', (event) => {
      if (['access_token', 'auth_token', 'user_id', 'username', 'user_type'].includes(event.key)) {
        console.log("Storage changed, updating login status");
        this.checkLoginStatus();
      }
    });
  },
  // Add a watch for route changes to update login status on every route change
  watch: {
    '$route': {
      handler() {
        this.checkLoginStatus();
      },
      immediate: true
    }
  },
  mounted() {
    // Initialize Bootstrap dropdown if needed
    if (window.bootstrap) {
      const dropdownElementList = document.querySelectorAll('.dropdown-toggle');
      dropdownElementList.forEach(el => {
        new window.bootstrap.Dropdown(el);
      });
    }
  }
};
</script>

<style>
/* Customizing Navbar */
.navbar-brand {
  font-size: 1.5rem;
  font-weight: bold;
  text-align: left;
}

.navbar-nav .nav-link {
  font-weight: 500;
}

/* Search Bar Styling */
.search-bar-container {
  flex-grow: 1;
  display: flex;
  justify-content: center;
  max-width: 500px;
}

.search-bar {
  border-radius: 20px 0 0 20px;
  padding: 5px 15px;
  outline: none;
}

.search-type {
  max-width: 120px;
  border-left: none;
}

.input-group .btn {
  border-radius: 0 20px 20px 0;
}

/* Welcome Section Styling */
.welcome-section {
  background-color: #f8f9fa;
  border-radius: 10px;
  box-shadow: 0 2px 10px rgba(0, 0, 0, 0.05);
  padding: 2rem;
}

.welcome-user {
  background-color: #e8f4ff;
  border-radius: 8px;
  padding: 1rem;
  margin: 1rem 0;
}

/* Feature Icons */
.feature-icon {
  font-size: 2.5rem;
  margin-bottom: 1rem;
  display: block;
}

/* Card hover effects */
.card {
  transition: transform 0.3s ease, box-shadow 0.3s ease;
}

.card:hover {
  transform: translateY(-5px);
  box-shadow: 0 10px 20px rgba(0, 0, 0, 0.1) !important;
}

/* Button styling */
.btn-primary {
  background-color: #4a6bdf;
  border-color: #4a6bdf;
}

.btn-primary:hover {
  background-color: #3955b8;
  border-color: #3955b8;
}

/* Add highlight styles for the admin/quiz buttons */
.btn-outline-primary, .btn-outline-success {
  transition: all 0.3s ease;
}

.btn-outline-primary:hover, .btn-outline-success:hover {
  transform: translateY(-2px);
}

/* Badge styling for user type */
.badge {
  font-size: 0.7em;
  padding: 0.35em 0.65em;
}
</style>
