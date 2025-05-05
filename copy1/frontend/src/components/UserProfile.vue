<template>
  <div class="container py-4">
    <div class="row">
      <!-- User Profile Card -->
      <div class="col-md-4 mb-4">
        <div class="card shadow-sm h-100">
          <div class="card-body text-center">
            <div class="profile-avatar mb-3">
              <i class="bi bi-person-circle"></i>
            </div>
            <h3 class="card-title">{{ profile.fullname || 'Loading...' }}</h3>
            <p class="text-muted">{{ profile.username || '' }}</p>
            
            <div class="profile-details text-start mt-4">
              <div class="detail-item">
                <i class="bi bi-envelope"></i>
                <span>{{ profile.email || 'No email available' }}</span>
              </div>
              <div class="detail-item">
                <i class="bi bi-mortarboard"></i>
                <span>{{ profile.qualification || 'No qualification available' }}</span>
              </div>
            </div>
            
            <p class="mt-4">{{ profile.self_description || 'No description available' }}</p>
          </div>
        </div>
      </div>
      
      <!-- Statistics Card -->
      <div class="col-md-8 mb-4">
        <div class="card shadow-sm h-100">
          <div class="card-body">
            <h4 class="card-title">Quiz Statistics</h4>
            
            <div v-if="statsLoading" class="text-center py-4">
              <div class="spinner-border text-primary" role="status">
                <span class="visually-hidden">Loading...</span>
              </div>
            </div>
            
            <div v-else class="row stats-container">
              <div class="col-md-6 col-lg-3 mb-3">
                <div class="stat-card">
                  <div class="stat-icon bg-primary">
                    <i class="bi bi-pencil-square"></i>
                  </div>
                  <div class="stat-details">
                    <h3>{{ stats.total_quizzes_attempted }}</h3>
                    <p>Quizzes Taken</p>
                  </div>
                </div>
              </div>
              
              <div class="col-md-6 col-lg-3 mb-3">
                <div class="stat-card">
                  <div class="stat-icon bg-success">
                    <i class="bi bi-graph-up"></i>
                  </div>
                  <div class="stat-details">
                    <h3>{{ stats.average_score }}%</h3>
                    <p>Average Score</p>
                  </div>
                </div>
              </div>
              
              <div class="col-md-6 col-lg-3 mb-3">
                <div class="stat-card">
                  <div class="stat-icon bg-warning">
                    <i class="bi bi-trophy"></i>
                  </div>
                  <div class="stat-details">
                    <h3>{{ stats.highest_score }}%</h3>
                    <p>Highest Score</p>
                  </div>
                </div>
              </div>
              
              <div class="col-md-6 col-lg-3 mb-3">
                <div class="stat-card">
                  <div class="stat-icon bg-info">
                    <i class="bi bi-clock-history"></i>
                  </div>
                  <div class="stat-details">
                    <h3>{{ stats.total_time_spent }}</h3>
                    <p>Minutes Spent</p>
                  </div>
                </div>
              </div>
            </div>
            
            <div class="mt-4">
              <router-link to="/progress" class="btn btn-primary">
                <i class="bi bi-bar-chart me-2"></i>View Progress Details
              </router-link>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import axios from '@/axios.js';

export default {
  name: 'UserProfile',
  data() {
    return {
      profile: {},
      stats: {
        total_quizzes_attempted: 0,
        average_score: 0,
        highest_score: 0,
        total_time_spent: 0
      },
      loading: true,
      statsLoading: true,
      error: null
    };
  },
  created() {
    this.fetchUserProfile();
    this.fetchQuizStats();
  },
  methods: {
    async fetchUserProfile() {
      try {
        const userId = localStorage.getItem('user_id');
        
        if (!userId) {
          this.error = "User ID not found. Please log in again.";
          this.loading = false;
          return;
        }
        
        // Use the correct URL with /api/ prefix
        const response = await axios.get(`/api/users/${userId}`);
        this.profile = response.data;
        this.loading = false;
      } catch (error) {
        console.error('Error fetching user profile:', error);
        this.loading = false;
      }
    },
    async fetchQuizStats() {
      try {
        const userId = localStorage.getItem('user_id');
        
        if (!userId) {
          this.statsLoading = false;
          return;
        }
        
        // Use the correct URL with /api/ prefix
        const response = await axios.get(`/api/users/${userId}/quiz-stats`);
        this.stats = response.data;
        this.statsLoading = false;
      } catch (error) {
        console.error('Error fetching quiz stats:', error);
        this.statsLoading = false;
      }
    }
  }
};
</script>

<style scoped>
.profile-avatar {
  font-size: 5rem;
  color: #4a6bdf;
}

.profile-details {
  margin-top: 1.5rem;
}

.detail-item {
  display: flex;
  align-items: center;
  margin-bottom: 0.75rem;
}

.detail-item i {
  margin-right: 1rem;
  color: #6c757d;
  font-size: 1.25rem;
}

.stats-container {
  margin-top: 1rem;
}

.stat-card {
  display: flex;
  background-color: #f8f9fa;
  border-radius: 10px;
  padding: 1rem;
  height: 100%;
}

.stat-icon {
  display: flex;
  align-items: center;
  justify-content: center;
  width: 50px;
  height: 50px;
  border-radius: 8px;
  color: white;
  font-size: 1.5rem;
  margin-right: 1rem;
}

.stat-details h3 {
  font-weight: bold;
  margin-bottom: 0.25rem;
  font-size: 1.5rem;
}

.stat-details p {
  margin-bottom: 0;
  color: #6c757d;
  font-size: 0.875rem;
}
</style>
