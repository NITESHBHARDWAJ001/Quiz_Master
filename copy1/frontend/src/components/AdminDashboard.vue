<template>
  <div class="admin-dashboard container">
    <div class="d-flex justify-content-between align-items-center mb-4">
      <h2 class="my-4">Admin Dashboard</h2>
      <button class="btn btn-danger" @click="clearSession">Log Out</button>
    </div>

    <div v-if="error" class="alert alert-danger">{{ error }}</div>
    <div v-else>
      <!-- New Analytics Card -->
      <div class="card shadow-lg p-3 mb-5 bg-white rounded">
        <div class="card-header bg-primary text-white">
          <h4 class="m-0">Analytics & Reports</h4>
        </div>
        <div class="card-body">
          <div class="row">
            <div class="col-md-6">
              <div class="card mb-3">
                <div class="card-body">
                  <h5 class="card-title">Quiz Performance Summary</h5>
                  <p class="card-text">View comprehensive statistics about quiz performance and user engagement.</p>
                  <button class="btn btn-primary" @click="$router.push('/quiz-summary')">
                    <i class="bi bi-bar-chart-fill me-2"></i>View Quiz Summary
                  </button>
                </div>
              </div>
            </div>
            <div class="col-md-6">
              <div class="card mb-3">
                <div class="card-body">
                  <h5 class="card-title">User Engagement Reports</h5>
                  <p class="card-text">Generate and view reports about user participation and achievements.</p>
                  <button class="btn btn-success" @click="$router.push('/user-reports')">
                    <i class="bi bi-people-fill me-2"></i>View User Reports
                  </button>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>

      <!-- New Notification Card -->
      <div class="card shadow-lg p-3 mb-5 bg-white rounded">
        <div class="card-header bg-info text-white">
          <h4 class="m-0">Notifications</h4>
        </div>
        <div class="card-body">
          <div class="d-flex justify-content-between align-items-center">
            <div>
              <h5 class="mb-2">Quiz Notifications</h5>
              <p class="text-muted">Send email notifications to all users about new quizzes.</p>
            </div>
            <div>
              <button 
                class="btn btn-primary" 
                @click="notifyAllUsersAboutQuizzes"
                :disabled="notificationInProgress"
              >
                <span v-if="notificationInProgress">
                  <span class="spinner-border spinner-border-sm" role="status" aria-hidden="true"></span>
                  Sending...
                </span>
                <span v-else>
                  <i class="bi bi-envelope me-2"></i>Notify All Users
                </span>
              </button>
            </div>
          </div>
          <div v-if="notificationResult" :class="['alert mt-3', notificationResult.success ? 'alert-success' : 'alert-danger']">
            {{ notificationResult.message }}
          </div>
        </div>
      </div>

      <div class="row">
        <!-- Subjects Section -->
        <div class="col-md-6">
          <div class="card shadow-lg p-3 mb-5 bg-white rounded">
            <div class="card-header bg-primary text-white d-flex justify-content-between align-items-center">
              <h4 class="m-0">Subjects</h4>
              <button class="btn btn-light" @click="toggleSubjectForm">+ Add Subject</button>
            </div>
            <div class="card-body">
              <!-- Add Subject Form -->
              <div v-if="showSubjectForm" class="mb-4 p-3 border rounded">
                <h5>Add New Subject</h5>
                <form @submit.prevent="addSubject">
                  <div class="form-group mb-3">
                    <label for="subjectName">Subject Name</label>
                    <input 
                      type="text" 
                      id="subjectName" 
                      v-model="newSubject.name" 
                      class="form-control" 
                      required 
                    />
                  </div>
                  <div class="form-group mb-3">
                    <label for="subjectDescription">Description</label>
                    <textarea 
                      id="subjectDescription" 
                      v-model="newSubject.description" 
                      class="form-control" 
                      required
                    ></textarea>
                  </div>
                  <div class="d-flex justify-content-end">
                    <button type="button" class="btn btn-secondary me-2" @click="toggleSubjectForm">Cancel</button>
                    <button type="submit" class="btn btn-success">Save</button>
                  </div>
                </form>
              </div>

              <!-- Subjects List -->
              <ul class="list-group">
                <li class="list-group-item d-flex justify-content-between align-items-center" v-for="subject in subjects" :key="subject.id">
                  <div>
                    <h5>{{ subject.name }}</h5>
                    <p class="text-muted">ID: {{ subject.id }}</p>
                  </div>
                  <div>
                    <button class="btn btn-info btn-sm me-2" @click="navigateToUpdateSubject(subject.id)">Update</button>
                    <button class="btn btn-danger btn-sm" @click="deleteSubject(subject.id)">Delete</button>
                  </div>
                </li>
              </ul>
            </div>
          </div>
        </div>

        <!-- Users Section -->
        <div class="col-md-6">
          <div class="card shadow-lg p-3 mb-5 bg-white rounded">
            <div class="card-header bg-secondary text-white d-flex justify-content-between align-items-center">
              <h4 class="m-0">Manage Users</h4>
              <div>
                <button class="btn btn-light me-2" @click="$router.push('/register')">+ Add User</button>
                <button class="btn btn-info" @click="$router.push('/manage-users')">
                  <i class="bi bi-people-fill me-1"></i>User Management
                </button>
              </div>
            </div>
            <div class="card-body">
              <ul class="list-group">
                <li class="list-group-item d-flex justify-content-between align-items-center" v-for="user in users.slice(0, 5)" :key="user.id">
                  <div>
                    <h5>{{ user.username }}</h5>
                    <p class="text-muted">{{ user.email }}</p>
                  </div>
                  <div>
                    <button class="btn btn-primary btn-sm me-2" @click="viewUserProfile(user.id)">View</button>
                    <button class="btn btn-warning btn-sm" @click="blockUnblockUser(user.id, user.active)">
                      {{ user.active ? 'Block' : 'Unblock' }}
                    </button>
                  </div>
                </li>
              </ul>
              <div class="text-center mt-3" v-if="users.length > 5">
                <button class="btn btn-outline-primary" @click="$router.push('/manage-users')">
                  View All {{ users.length }} Users
                </button>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import axios from '@/axios.js';
import notificationService from '@/services/notificationService';

export default {
  data() {
    return {
      subjects: [],
      users: [],
      error: null,
      showSubjectForm: false,
      newSubject: {
        name: '',
        description: ''
      },
      notificationInProgress: false,
      notificationResult: null
    };
  },
  methods: {
    toggleSubjectForm() {
      this.showSubjectForm = !this.showSubjectForm;
      if (!this.showSubjectForm) {
        // Reset form when closing
        this.newSubject = { name: '', description: '' };
      }
    },
    async addSubject() {
      try {
        console.log('Adding subject:', this.newSubject);
        const response = await axios.post('/api/admin/subjects', {
          name: this.newSubject.name,
          description: this.newSubject.description
        });
        
        console.log('Subject added:', response.data);
        
        // Trigger notification about the new subject
        const subjectId = response.data.subject?.id || response.data.id;
        if (subjectId) {
          await notificationService.notifyNewSubject(subjectId, this.newSubject.name);
        }
        
        alert('Subject added successfully!');
        
        // Clear form and hide it
        this.newSubject = { name: '', description: '' };
        this.showSubjectForm = false;
        
        // Refresh subjects list
        this.fetchAdminDashboardData();
      } catch (error) {
        console.error('Error adding subject:', error);
        alert(error.response?.data?.message || 'Failed to add subject');
      }
    },
    async fetchAdminDashboardData() {
      try {
        console.log('Fetching admin dashboard data...');
        // Use the axios interceptor which will automatically add the Authorization header
        const response = await axios.get('/api/admin-dashboard-data');
        
        console.log('Response from admin dashboard API:', response.data);
        
        // Check if data exists and has the expected structure
        if (response.data && response.data.subjects && response.data.users) {
          this.subjects = response.data.subjects || [];
          this.users = response.data.users || [];
          console.log(`Loaded ${this.subjects.length} subjects and ${this.users.length} users`);
        } else {
          console.error('Invalid data structure received:', response.data);
          this.error = 'Received invalid data structure from server';
        }
      } catch (error) {
        console.error('Error fetching admin dashboard data:', error);
        this.error = 'Failed to fetch admin dashboard data: ' + (error.response?.data?.message || error.message);
      }
    },
    async deleteSubject(id) {
      try {
        await axios.delete(`/api/subjects/${id}`, {
          headers: { Authorization: `Bearer ${localStorage.getItem('auth_token')}` },
        });
        this.fetchAdminDashboardData();
      } catch (error) {
        console.error('Error deleting subject:', error);
      }
    },
    navigateToUpdateSubject(subjectId) {
      this.$router.push(`/update-subject/${subjectId}`);
    },
    async blockUnblockUser(id, isActive) {
      try {
        await axios.patch(`/api/users/${id}/toggle-status`, {}, {
          headers: { Authorization: `Bearer ${localStorage.getItem('auth_token')}` },
        });
        this.fetchAdminDashboardData();
      } catch (error) {
        console.error('Error updating user status:', error);
      }
    },
    viewUserProfile(userId) {
      this.$router.push(`/user-profile/${userId}`);
    },
    // Add clear session method
    clearSession() {
      // Clear all authentication data from localStorage
      localStorage.removeItem('auth_token');
      localStorage.removeItem('user_id');
      localStorage.removeItem('username');
      localStorage.removeItem('user_type');
      
      // Redirect to login page
      this.$router.push('/login');
      alert('You have been logged out successfully.');
    },
    async notifyAllUsersAboutQuizzes() {
      this.notificationInProgress = true;
      this.notificationResult = null;
      
      try {
        // Call the notification service
        const response = await notificationService.notifyAllUsersAboutQuizzes();
        
        if (response.error) {
          this.notificationResult = {
            success: false,
            message: `Failed to send notifications: ${response.error.message || 'Unknown error'}`
          };
        } else {
          this.notificationResult = {
            success: true,
            message: `Successfully sent ${response.data?.sentCount || 'all'} notifications. ${response.data?.message || ''}`
          };
        }
      } catch (error) {
        console.error('Error sending notifications:', error);
        this.notificationResult = {
          success: false,
          message: `Error: ${error.response?.data?.message || error.message || 'Failed to send notifications'}`
        };
      } finally {
        this.notificationInProgress = false;
        
        // Auto-hide the notification after 5 seconds
        setTimeout(() => {
          this.notificationResult = null;
        }, 5000);
      }
    },
  },
  created() {
    // Make sure we're using the latest token when the component is created
    console.log('Admin Dashboard created with token:', localStorage.getItem('auth_token'));
    this.fetchAdminDashboardData();
  },
  // Add mounted hook to try again if it failed in created
  mounted() {
    if (this.subjects.length === 0 || this.users.length === 0) {
      console.log('No data was loaded in created hook, trying again...');
      this.fetchAdminDashboardData();
    }
  }
};
</script>

<style scoped>
/* Add any styling specific to this component here */

/* Add button animation for notification */
@keyframes pulse {
  0% { transform: scale(1); }
  50% { transform: scale(1.05); }
  100% { transform: scale(1); }
}

.btn-primary:not(:disabled) {
  transition: all 0.3s ease;
}

.btn-primary:not(:disabled):hover {
  animation: pulse 1s infinite;
  box-shadow: 0 0 10px rgba(0, 123, 255, 0.5);
}
</style>
