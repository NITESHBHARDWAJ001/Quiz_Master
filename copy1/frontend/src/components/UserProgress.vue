<template>
  <div class="container py-4">
    <!-- Header with title and toggle/action buttons -->
    <div class="d-flex justify-content-between align-items-center mb-4">
      <h1 class="fw-bold">My Quiz Progress</h1>
      <div class="d-flex gap-2">
        <button class="btn btn-success" @click="showEmailReportModal = true">
          <i class="bi bi-envelope-fill me-1"></i>
          Email Report
        </button>
        
        <button class="btn btn-info" @click="downloadReport">
          <i class="bi bi-download me-1"></i>
          Download Report
        </button>
        
        <button class="btn btn-primary" @click="togglePerformanceChart">
          <i class="bi" :class="showPerformanceChart ? 'bi-table' : 'bi-bar-chart-fill'"></i>
          {{ showPerformanceChart ? 'Show History' : 'View Performance Charts' }}
        </button>
      </div>
    </div>
    
    <!-- Loading state -->
    <div v-if="loading" class="text-center py-5">
      <div class="spinner-border text-primary" role="status">
        <span class="visually-hidden">Loading...</span>
      </div>
      <p class="mt-3">Loading your progress data...</p>
    </div>
    
    <!-- Error state -->
    <div v-else-if="error" class="alert alert-danger">
      {{ error }}
    </div>
    
    <!-- Empty state -->
    <div v-else-if="progressData.length === 0" class="alert alert-info">
      <p class="mb-0">You haven't taken any quizzes yet. <router-link to="/quiz">Start a quiz now</router-link>!</p>
    </div>
    
    <!-- Content state -->
    <div v-else>
      <!-- Performance Chart View -->
      <PerformanceChart 
        v-if="showPerformanceChart"
        :userId="userId"
      />
      
      <!-- Regular Quiz History View -->
      <div v-else class="row">
        <div class="col-md-12 mb-4">
          <div class="card shadow-sm">
            <div class="card-body">
              <h5 class="card-title">Quiz History</h5>
              <div class="table-responsive">
                <table class="table table-hover">
                  <thead>
                    <tr>
                      <th>Quiz Name</th>
                      <th>Subject</th>
                      <th>Chapter</th>
                      <th>Score</th>
                      <th>Date Attempted</th>
                      <th>Actions</th>
                    </tr>
                  </thead>
                  <tbody>
                    <tr v-for="item in progressData" :key="item.performance_id">
                      <td>{{ item.quiz_name }}</td>
                      <td>{{ item.subject_name }}</td>
                      <td>{{ item.chapter_name }}</td>
                      <td>
                        <span class="badge bg-success">{{ item.score }}%</span>
                      </td>
                      <td>{{ formatDate(item.attempted_at) }}</td>
                      <td>
                        <router-link 
                          :to="{ name: 'quiz-attempt', params: { quizId: item.quiz_id }}" 
                          class="btn btn-sm btn-primary"
                        >
                          <i class="bi bi-arrow-repeat me-1"></i>Retry
                        </router-link>
                      </td>
                    </tr>
                  </tbody>
                </table>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
    
    <!-- Email Report Modal -->
    <div class="modal" :class="{'show d-block': showEmailReportModal}" tabindex="-1">
      <div class="modal-dialog">
        <div class="modal-content">
          <div class="modal-header">
            <h5 class="modal-title">Email Performance Report</h5>
            <button type="button" class="btn-close" @click="showEmailReportModal = false"></button>
          </div>
          <div class="modal-body">
            <p>We'll send a detailed performance report to your registered email address.</p>
            
            <div v-if="userProfile">
              <div class="alert alert-info d-flex align-items-center">
                <i class="bi bi-info-circle-fill me-2"></i>
                <div>
                  Report will be sent to: <strong>{{ userProfile.email }}</strong>
                </div>
              </div>
            </div>
            
            <div v-if="emailStatus" :class="emailStatusClass">
              {{ emailStatus }}
            </div>
          </div>
          <div class="modal-footer">
            <button type="button" class="btn btn-secondary" @click="showEmailReportModal = false">Cancel</button>
            <button type="button" class="btn btn-success" @click="sendEmailReport" :disabled="sendingEmail">
              <span v-if="sendingEmail" class="spinner-border spinner-border-sm me-2"></span>
              Send Report
            </button>
          </div>
        </div>
      </div>
    </div>
    <div v-if="showEmailReportModal" class="modal-backdrop fade show"></div>
  </div>
</template>

<script>
import axios from '@/axios.js';
import PerformanceChart from './PerformanceChart.vue';

export default {
  name: 'UserProgress',
  components: {
    PerformanceChart
  },
  data() {
    return {
      progressData: [],
      loading: true,
      error: null,
      showPerformanceChart: false,
      userId: null,
      showEmailReportModal: false,
      userProfile: null,
      emailStatus: null,
      emailStatusType: null,
      sendingEmail: false,
      downloadingReport: false
    };
  },
  computed: {
    emailStatusClass() {
      return {
        'alert': true,
        'alert-success': this.emailStatusType === 'success',
        'alert-danger': this.emailStatusType === 'error'
      };
    }
  },
  created() {
    this.userId = localStorage.getItem('user_id');
    this.fetchProgressData();
    this.fetchUserProfile();
  },
  methods: {
    async fetchProgressData() {
      try {
        this.loading = true;
        
        if (!this.userId) {
          this.error = "User ID not found. Please log in again.";
          this.loading = false;
          return;
        }
        
        // Use correct URL with /api/ prefix
        const response = await axios.get(`/api/user-progress/${this.userId}`);
        this.progressData = response.data;
        this.loading = false;
      } catch (error) {
        console.error('Error fetching progress data:', error);
        this.error = 'Failed to load progress data. Please try again later.';
        this.loading = false;
      }
    },
    async fetchUserProfile() {
      try {
        if (!this.userId) return;
        
        const response = await axios.get(`/api/users/${this.userId}`);
        this.userProfile = response.data;
      } catch (error) {
        console.error('Error fetching user profile:', error);
      }
    },
    formatDate(dateString) {
      const date = new Date(dateString);
      return date.toLocaleDateString('en-US', { 
        year: 'numeric', 
        month: 'long', 
        day: 'numeric',
        hour: '2-digit',
        minute: '2-digit'
      });
    },
    togglePerformanceChart() {
      this.showPerformanceChart = !this.showPerformanceChart;
    },
    async sendEmailReport() {
      try {
        this.sendingEmail = true;
        this.emailStatus = "Sending report...";
        this.emailStatusType = null;
        
        const response = await axios.post(`/api/user/${this.userId}/email-report`);
        
        this.emailStatus = response.data.message;
        this.emailStatusType = 'success';
        
        // Close modal after a delay
        setTimeout(() => {
          this.showEmailReportModal = false;
          this.emailStatus = null;
        }, 3000);
      } catch (error) {
        console.error('Error sending performance report:', error);
        this.emailStatus = error.response?.data?.message || 'Failed to send report. Please try again.';
        this.emailStatusType = 'error';
      } finally {
        this.sendingEmail = false;
      }
    },
    async downloadReport() {
      try {
        this.downloadingReport = true;
        
        // Create a link element
        const link = document.createElement('a');
        link.href = `${axios.defaults.baseURL}/api/user/${this.userId}/download-report`;
        link.target = '_blank';
        link.download = `performance_report.pdf`;
        
        // Append to the document, click it, and remove it
        document.body.appendChild(link);
        link.click();
        document.body.removeChild(link);
      } catch (error) {
        console.error('Error downloading report:', error);
        alert('Failed to download report. Please try again later.');
      } finally {
        this.downloadingReport = false;
      }
    }
  }
};
</script>

<style scoped>
.table th {
  background-color: #f8f9fa;
  font-weight: 600;
}

.modal {
  background-color: rgba(0, 0, 0, 0.5);
}

/* Animation for modal */
.modal.show {
  animation: fadeIn 0.3s;
}

@keyframes fadeIn {
  from { opacity: 0; }
  to { opacity: 1; }
}
</style>
