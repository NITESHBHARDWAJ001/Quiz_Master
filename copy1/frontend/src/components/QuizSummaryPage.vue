<template>
  <div class="container mt-4">
    <div class="d-flex justify-content-between align-items-center mb-4">
      <h2>Quiz Summary & Analytics</h2>
      <button class="btn btn-secondary" @click="$router.push('/AdminDashboard')">
        <i class="bi bi-arrow-left me-1"></i> Back to Dashboard
      </button>
    </div>

    <!-- Loading State -->
    <div v-if="loading" class="text-center py-5">
      <div class="spinner-border text-primary" role="status">
        <span class="visually-hidden">Loading...</span>
      </div>
      <p class="mt-2">Loading analytics data...</p>
    </div>

    <!-- Error State -->
    <div v-else-if="error" class="alert alert-danger">
      <i class="bi bi-exclamation-triangle-fill me-2"></i> {{ error }}
    </div>

    <!-- Analytics Dashboard -->
    <div v-else>
      <!-- Overall Summary -->
      <div class="row mb-4">
        <div class="col-md-3">
          <div class="card border-primary h-100">
            <div class="card-body text-center">
              <h2 class="display-4 fw-bold text-primary">{{ summary.totalQuizzes }}</h2>
              <p class="text-muted mb-0">Total Quizzes</p>
            </div>
          </div>
        </div>
        <div class="col-md-3">
          <div class="card border-success h-100">
            <div class="card-body text-center">
              <h2 class="display-4 fw-bold text-success">{{ summary.totalAttempts }}</h2>
              <p class="text-muted mb-0">Total Attempts</p>
            </div>
          </div>
        </div>
        <div class="col-md-3">
          <div class="card border-info h-100">
            <div class="card-body text-center">
              <h2 class="display-4 fw-bold text-info">{{ summary.averageScore }}%</h2>
              <p class="text-muted mb-0">Average Score</p>
            </div>
          </div>
        </div>
        <div class="col-md-3">
          <div class="card border-warning h-100">
            <div class="card-body text-center">
              <h2 class="display-4 fw-bold text-warning">{{ summary.activeUsers }}</h2>
              <p class="text-muted mb-0">Active Users</p>
            </div>
          </div>
        </div>
      </div>

      <!-- Most Attempted Quizzes -->
      <div class="card mb-4">
        <div class="card-header bg-primary text-white">
          <h4 class="m-0">Most Attempted Quizzes</h4>
        </div>
        <div class="card-body">
          <div v-if="mostAttemptedQuizzes.length === 0" class="alert alert-info">
            <i class="bi bi-info-circle me-2"></i> No quiz attempts recorded yet.
          </div>
          <div v-else class="table-responsive">
            <table class="table table-hover">
              <thead class="table-light">
                <tr>
                  <th>Quiz Name</th>
                  <th>Subject</th>
                  <th>Chapter</th>
                  <th class="text-center">Total Attempts</th>
                  <th class="text-center">Average Score</th>
                  <th>Actions</th>
                </tr>
              </thead>
              <tbody>
                <tr v-for="quiz in mostAttemptedQuizzes" :key="quiz.id">
                  <td>{{ quiz.quiz_name }}</td>
                  <td>{{ quiz.subject_name }}</td>
                  <td>{{ quiz.chapter_name }}</td>
                  <td class="text-center">
                    <span class="badge bg-primary">{{ quiz.attempts }}</span>
                  </td>
                  <td class="text-center">
                    <span :class="['badge', getScoreColorClass(quiz.average_score)]">
                      {{ quiz.average_score }}%
                    </span>
                  </td>
                  <td>
                    <button class="btn btn-sm btn-info" @click="viewQuizDetails(quiz.id)">
                      <i class="bi bi-graph-up me-1"></i>View Details
                    </button>
                  </td>
                </tr>
              </tbody>
            </table>
          </div>
        </div>
      </div>

      <!-- Highest Scores -->
      <div class="card mb-4">
        <div class="card-header bg-success text-white">
          <h4 class="m-0">Highest Scores by Quiz</h4>
        </div>
        <div class="card-body">
          <div v-if="highestScores.length === 0" class="alert alert-info">
            <i class="bi bi-info-circle me-2"></i> No scores recorded yet.
          </div>
          <div v-else class="table-responsive">
            <table class="table table-hover">
              <thead class="table-light">
                <tr>
                  <th>Quiz Name</th>
                  <th>User</th>
                  <th class="text-center">Score</th>
                  <th>Date</th>
                  <th>Actions</th>
                </tr>
              </thead>
              <tbody>
                <tr v-for="score in highestScores" :key="`${score.quiz_id}-${score.user_id}`">
                  <td>{{ score.quiz_name }}</td>
                  <td>{{ score.username }}</td>
                  <td class="text-center">
                    <span :class="['badge', getScoreColorClass(score.score)]">
                      {{ score.score }}%
                    </span>
                  </td>
                  <td>{{ formatDate(score.attempted_at) }}</td>
                  <td>
                    <button class="btn btn-sm btn-primary" @click="viewUserProfile(score.user_id)">
                      <i class="bi bi-person me-1"></i>View User
                    </button>
                  </td>
                </tr>
              </tbody>
            </table>
          </div>
        </div>
      </div>

      <!-- Quiz Participation Over Time -->
      <div class="card mb-4">
        <div class="card-header bg-info text-white">
          <h4 class="m-0">Quiz Participation Over Time</h4>
        </div>
        <div class="card-body">
          <div v-if="participationData.labels.length === 0" class="alert alert-info">
            <i class="bi bi-info-circle me-2"></i> Not enough data to generate chart.
          </div>
          <div v-else ref="participationChart" style="height: 300px;"></div>
        </div>
      </div>

      <!-- Subject Performance Comparison -->
      <div class="card">
        <div class="card-header bg-warning text-dark">
          <h4 class="m-0">Subject Performance Comparison</h4>
        </div>
        <div class="card-body">
          <div v-if="subjectPerformance.length === 0" class="alert alert-info">
            <i class="bi bi-info-circle me-2"></i> Not enough data to compare subjects.
          </div>
          <div v-else class="row">
            <div class="col-md-8">
              <div ref="subjectChart" style="height: 300px;"></div>
            </div>
            <div class="col-md-4">
              <h5>Subject Rankings</h5>
              <ol class="list-group list-group-numbered">
                <li v-for="(subject, index) in subjectPerformance" :key="subject.id" 
                    class="list-group-item d-flex justify-content-between align-items-center">
                  <div>
                    <strong>{{ subject.name }}</strong>
                    <div class="text-muted small">{{ subject.quizzes }} quizzes</div>
                  </div>
                  <span :class="['badge', getScoreColorClass(subject.average_score)]">
                    {{ subject.average_score }}%
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
      summary: {
        totalQuizzes: 0,
        totalAttempts: 0,
        averageScore: 0,
        activeUsers: 0
      },
      mostAttemptedQuizzes: [],
      highestScores: [],
      participationData: {
        labels: [],
        data: []
      },
      subjectPerformance: [],
      charts: {}
    };
  },
  methods: {
    async fetchSummaryData() {
      try {
        this.loading = true;
        this.error = null;
        
        // Create an array of all API requests to be made
        const apiRequests = [
          { url: '/api/admin/quiz-summary', property: 'summary', default: { totalQuizzes: 0, totalAttempts: 0, averageScore: 0, activeUsers: 0 } },
          { url: '/api/admin/most-attempted-quizzes', property: 'mostAttemptedQuizzes', default: [] },
          { url: '/api/admin/highest-scores', property: 'highestScores', default: [] },
          { url: '/api/admin/quiz-participation-timeline', property: 'participationData', default: { labels: [], data: [] } },
          { url: '/api/admin/subject-performance', property: 'subjectPerformance', default: [] }
        ];
        
        // Process each request individually, so one failure doesn't stop others
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
        console.error('Error fetching quiz summary data:', error);
        this.error = 'Failed to load some analytics data. The page may display partial information.';
        this.loading = false;
      }
    },
    
    renderCharts() {
      // Only attempt to render charts if Chart.js is available
      if (window.Chart) {
        this.renderParticipationChart();
        this.renderSubjectChart();
      } else {
        console.warn('Chart.js not available. Charts will not be rendered.');
      }
    },
    
    renderParticipationChart() {
      if (!this.$refs.participationChart || this.participationData.labels.length === 0) return;
      
      const ctx = document.createElement('canvas');
      this.$refs.participationChart.innerHTML = '';
      this.$refs.participationChart.appendChild(ctx);
      
      this.charts.participation = new window.Chart(ctx, {
        type: 'line',
        data: {
          labels: this.participationData.labels,
          datasets: [{
            label: 'Quiz Attempts',
            data: this.participationData.data,
            backgroundColor: 'rgba(54, 162, 235, 0.2)',
            borderColor: 'rgba(54, 162, 235, 1)',
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
                text: 'Number of Attempts'
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
    },
    
    renderSubjectChart() {
      if (!this.$refs.subjectChart || this.subjectPerformance.length === 0) return;
      
      const ctx = document.createElement('canvas');
      this.$refs.subjectChart.innerHTML = '';
      this.$refs.subjectChart.appendChild(ctx);
      
      const labels = this.subjectPerformance.map(subject => subject.name);
      const data = this.subjectPerformance.map(subject => subject.average_score);
      const backgroundColors = this.subjectPerformance.map(subject => 
        this.getChartColorForScore(subject.average_score)
      );
      
      try {
        this.charts.subject = new window.Chart(ctx, {
          type: 'bar',
          data: {
            labels: labels,
            datasets: [{
              label: 'Average Score (%)',
              data: data,
              backgroundColor: backgroundColors,
              borderColor: backgroundColors.map(color => color.replace('0.6', '1')),
              borderWidth: 1
            }]
          },
          options: {
            responsive: true,
            maintainAspectRatio: false,
            scales: {
              y: {
                beginAtZero: true,
                max: 100,
                title: {
                  display: true,
                  text: 'Average Score (%)'
                }
              }
            }
          }
        });
      } catch (error) {
        console.error('Error rendering subject chart:', error);
        // Show an error message in the chart container
        this.$refs.subjectChart.innerHTML = '<div class="alert alert-warning">Could not render chart: ' + error.message + '</div>';
      }
    },
    
    getScoreColorClass(score) {
      if (score >= 90) return 'bg-success';
      if (score >= 70) return 'bg-info';
      if (score >= 50) return 'bg-warning';
      return 'bg-danger';
    },
    
    getChartColorForScore(score) {
      if (score >= 90) return 'rgba(40, 167, 69, 0.6)';  // success
      if (score >= 70) return 'rgba(23, 162, 184, 0.6)'; // info
      if (score >= 50) return 'rgba(255, 193, 7, 0.6)';  // warning
      return 'rgba(220, 53, 69, 0.6)';                   // danger
    },
    
    formatDate(dateString) {
      if (!dateString) return '';
      const date = new Date(dateString);
      return date.toLocaleDateString('en-US', {
        year: 'numeric',
        month: 'short',
        day: 'numeric'
      });
    },
    
    viewQuizDetails(quizId) {
      // Navigate to quiz details page
      this.$router.push(`/quizzes/${quizId}/statistics`);
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
        this.fetchSummaryData();
      };
      script.onerror = () => {
        console.error('Failed to load Chart.js');
        this.fetchSummaryData();
      };
      document.head.appendChild(script);
    } else {
      this.fetchSummaryData();
    }
  },
  beforeUnmount() {
    // Clean up charts
    if (this.charts.participation) {
      this.charts.participation.destroy();
    }
    if (this.charts.subject) {
      this.charts.subject.destroy();
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
