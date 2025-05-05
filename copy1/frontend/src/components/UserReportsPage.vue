<template>
  <div class="container mt-4">
    <div class="d-flex justify-content-between align-items-center mb-4">
      <h2>User Engagement Reports</h2>
      <button class="btn btn-secondary" @click="$router.push('/AdminDashboard')">
        <i class="bi bi-arrow-left me-1"></i> Back to Dashboard
      </button>
    </div>

    <!-- Loading State -->
    <div v-if="loading" class="text-center py-5">
      <div class="spinner-border text-primary" role="status">
        <span class="visually-hidden">Loading...</span>
      </div>
      <p class="mt-2">Loading user engagement data...</p>
    </div>

    <!-- Error State -->
    <div v-else-if="error" class="alert alert-danger">
      <i class="bi bi-exclamation-triangle-fill me-2"></i> {{ error }}
    </div>

    <!-- User Engagement Dashboard -->
    <div v-else>
      <!-- Overall Summary -->
      <div class="row mb-4">
        <div class="col-md-3">
          <div class="card border-primary h-100">
            <div class="card-body text-center">
              <h2 class="display-4 fw-bold text-primary">{{ userStats.totalUsers }}</h2>
              <p class="text-muted mb-0">Total Users</p>
            </div>
          </div>
        </div>
        <div class="col-md-3">
          <div class="card border-success h-100">
            <div class="card-body text-center">
              <h2 class="display-4 fw-bold text-success">{{ userStats.activeUsers }}</h2>
              <p class="text-muted mb-0">Active Users</p>
            </div>
          </div>
        </div>
        <div class="col-md-3">
          <div class="card border-info h-100">
            <div class="card-body text-center">
              <h2 class="display-4 fw-bold text-info">{{ userStats.quizzesPerUser.toFixed(1) }}</h2>
              <p class="text-muted mb-0">Avg Quizzes per User</p>
            </div>
          </div>
        </div>
        <div class="col-md-3">
          <div class="card border-warning h-100">
            <div class="card-body text-center">
              <h2 class="display-4 fw-bold text-warning">{{ userStats.averageScore }}%</h2>
              <p class="text-muted mb-0">Average Score</p>
            </div>
          </div>
        </div>
      </div>

      <!-- User Activity Chart -->
      <div class="card mb-4">
        <div class="card-header bg-primary text-white">
          <h4 class="m-0">User Activity Over Time</h4>
        </div>
        <div class="card-body">
          <div v-if="userActivity.labels.length === 0" class="alert alert-info">
            <i class="bi bi-info-circle me-2"></i> Not enough data to generate activity chart.
          </div>
          <div v-else ref="userActivityChart" style="height: 300px;"></div>
        </div>
      </div>

      <!-- Most Active Users -->
      <div class="card mb-4">
        <div class="card-header bg-success text-white">
          <h4 class="m-0">Most Active Users</h4>
        </div>
        <div class="card-body">
          <div v-if="mostActiveUsers.length === 0" class="alert alert-info">
            <i class="bi bi-info-circle me-2"></i> No active users data available.
          </div>
          <div v-else class="table-responsive">
            <table class="table table-hover">
              <thead class="table-light">
                <tr>
                  <th>User</th>
                  <th>Email</th>
                  <th class="text-center">Quizzes Taken</th>
                  <th class="text-center">Average Score</th>
                  <th>Last Active</th>
                  <th>Actions</th>
                </tr>
              </thead>
              <tbody>
                <tr v-for="user in mostActiveUsers" :key="user.id">
                  <td>{{ user.username }}</td>
                  <td>{{ user.email }}</td>
                  <td class="text-center">
                    <span class="badge bg-primary">{{ user.quizzesTaken }}</span>
                  </td>
                  <td class="text-center">
                    <span :class="['badge', getScoreColorClass(user.averageScore)]">
                      {{ user.averageScore }}%
                    </span>
                  </td>
                  <td>{{ formatDate(user.lastActive) }}</td>
                  <td>
                    <button class="btn btn-sm btn-info" @click="viewUserProfile(user.id)">
                      <i class="bi bi-person me-1"></i>View Profile
                    </button>
                  </td>
                </tr>
              </tbody>
            </table>
          </div>
        </div>
      </div>

      <!-- Subject Popularity -->
      <div class="card">
        <div class="card-header bg-info text-white">
          <h4 class="m-0">Subject Popularity</h4>
        </div>
        <div class="card-body">
          <div v-if="subjectPopularity.length === 0" class="alert alert-info">
            <i class="bi bi-info-circle me-2"></i> Not enough data to compare subject popularity.
          </div>
          <div v-else class="row">
            <div class="col-md-8">
              <div ref="subjectPopularityChart" style="height: 300px;"></div>
            </div>
            <div class="col-md-4">
              <h5>Most Popular Subjects</h5>
              <ol class="list-group list-group-numbered">
                <li v-for="subject in subjectPopularity" :key="subject.id" 
                    class="list-group-item d-flex justify-content-between align-items-center">
                  <div>
                    <strong>{{ subject.name }}</strong>
                    <div class="text-muted small">{{ subject.quizCount }} quizzes</div>
                  </div>
                  <span class="badge bg-primary">
                    {{ subject.userCount }} users
                  </span>
                </li>
              </ol>
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
  data() {
    return {
      loading: true,
      error: null,
      userStats: {
        totalUsers: 0,
        activeUsers: 0,
        quizzesPerUser: 0,
        averageScore: 0
      },
      userActivity: {
        labels: [],
        data: []
      },
      mostActiveUsers: [],
      subjectPopularity: [],
      charts: {}
    };
  },
  methods: {
    async fetchUserEngagementData() {
      try {
        this.loading = true;
        this.error = null;

        // Create an array of all API requests to be made
        const apiRequests = [
          { url: '/api/admin/user-statistics', property: 'userStats', default: {
            totalUsers: 0,
            activeUsers: 0,
            quizzesPerUser: 0,
            averageScore: 0
          }},
          { url: '/api/admin/user-activity-timeline', property: 'userActivity', default: {
            labels: [],
            data: []
          }},
          { url: '/api/admin/most-active-users', property: 'mostActiveUsers', default: [] },
          { url: '/api/admin/subject-popularity', property: 'subjectPopularity', default: [] }
        ];
        
        // Process each request individually so one failure doesn't stop others
        for (const request of apiRequests) {
          try {
            const response = await axios.get(request.url);
            this[request.property] = response.data;
          } catch (error) {
            console.error(`Error fetching ${request.url}:`, error);
            // On failure, use default data structure
            this[request.property] = request.default;
          }
        }

        this.loading = false;
        
        // Render charts after data is loaded
        this.$nextTick(() => {
          this.renderCharts();
        });
      } catch (error) {
        console.error('Error fetching user engagement data:', error);
        this.error = 'Failed to load some user engagement data. The page may display partial information.';
        this.loading = false;
      }
    },
    
    renderCharts() {
      // Only attempt to render charts if Chart.js is available
      if (window.Chart) {
        this.renderUserActivityChart();
        this.renderSubjectPopularityChart();
      } else {
        console.warn('Chart.js not available. Charts will not be rendered.');
      }
    },
    
    renderUserActivityChart() {
      if (!this.$refs.userActivityChart || this.userActivity.labels.length === 0) return;
      
      const ctx = document.createElement('canvas');
      this.$refs.userActivityChart.innerHTML = '';
      this.$refs.userActivityChart.appendChild(ctx);
      
      try {
        this.charts.userActivity = new window.Chart(ctx, {
          type: 'line',
          data: {
            labels: this.userActivity.labels,
            datasets: [{
              label: 'Active Users',
              data: this.userActivity.data,
              backgroundColor: 'rgba(40, 167, 69, 0.2)',
              borderColor: 'rgba(40, 167, 69, 1)',
              borderWidth: 2,
              tension: 0.3,
              fill: true
            }]
          },
          options: {
            responsive: true,
            maintainAspectRatio: false,
            scales: {
              y: {
                beginAtZero: true,
                title: {
                  display: true,
                  text: 'Number of Users'
                }
              },
              x: {
                title: {
                  display: true,
                  text: 'Date'
                }
              }
            }
          }
        });
      } catch (error) {
        console.error('Error rendering user activity chart:', error);
        this.$refs.userActivityChart.innerHTML = '<div class="alert alert-warning">Could not render chart: ' + error.message + '</div>';
      }
    },
    
    renderSubjectPopularityChart() {
      if (!this.$refs.subjectPopularityChart || this.subjectPopularity.length === 0) return;
      
      const ctx = document.createElement('canvas');
      this.$refs.subjectPopularityChart.innerHTML = '';
      this.$refs.subjectPopularityChart.appendChild(ctx);
      
      const labels = this.subjectPopularity.map(subject => subject.name);
      const data = this.subjectPopularity.map(subject => subject.userCount);
      
      try {
        this.charts.subjectPopularity = new window.Chart(ctx, {
          type: 'bar',
          data: {
            labels: labels,
            datasets: [{
              label: 'Number of Users',
              data: data,
              backgroundColor: 'rgba(23, 162, 184, 0.6)',
              borderColor: 'rgba(23, 162, 184, 1)',
              borderWidth: 1
            }]
          },
          options: {
            responsive: true,
            maintainAspectRatio: false,
            scales: {
              y: {
                beginAtZero: true,
                title: {
                  display: true,
                  text: 'Number of Users'
                }
              }
            }
          }
        });
      } catch (error) {
        console.error('Error rendering subject popularity chart:', error);
        this.$refs.subjectPopularityChart.innerHTML = '<div class="alert alert-warning">Could not render chart: ' + error.message + '</div>';
      }
    },
    
    getScoreColorClass(score) {
      if (score >= 90) return 'bg-success';
      if (score >= 70) return 'bg-info';
      if (score >= 50) return 'bg-warning';
      return 'bg-danger';
    },
    
    formatDate(dateString) {
      if (!dateString) return 'Never';
      const date = new Date(dateString);
      return date.toLocaleDateString('en-US', {
        year: 'numeric',
        month: 'short',
        day: 'numeric',
        hour: '2-digit',
        minute: '2-digit'
      });
    },
    
    viewUserProfile(userId) {
      // Navigate to user profile page
      this.$router.push(`/user-profile/${userId}`);
    }
  },
  mounted() {
    // Load Chart.js from CDN if it's not already available
    if (!window.Chart) {
      const script = document.createElement('script');
      script.src = 'https://cdn.jsdelivr.net/npm/chart.js';
      script.onload = () => {
        this.fetchUserEngagementData();
      };
      script.onerror = () => {
        console.error('Failed to load Chart.js');
        this.fetchUserEngagementData();
      };
      document.head.appendChild(script);
    } else {
      this.fetchUserEngagementData();
    }
  },
  beforeUnmount() {
    // Clean up charts
    if (this.charts.userActivity) {
      this.charts.userActivity.destroy();
    }
    if (this.charts.subjectPopularity) {
      this.charts.subjectPopularity.destroy();
    }
  }
};
</script>

<style scoped>
.card {
  border-radius: 10px;
  box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
  transition: all 0.3s ease;
  margin-bottom: 20px;
}

.card:hover {
  transform: translateY(-5px);
  box-shadow: 0 6px 12px rgba(0, 0, 0, 0.15);
}

.card-header {
  border-top-left-radius: 10px;
  border-top-right-radius: 10px;
  font-weight: 600;
}

.badge {
  padding: 0.5em 0.8em;
  font-size: 0.85rem;
}

.list-group-numbered > li::before {
  font-weight: bold;
}

.display-4 {
  font-size: 2.5rem;
}

@media (min-width: 768px) {
  .display-4 {
    font-size: 3rem;
  }
}
</style>
