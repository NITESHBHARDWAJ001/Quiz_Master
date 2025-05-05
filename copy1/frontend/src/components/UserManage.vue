<template>
  <div class="container mt-4">
    <div class="d-flex justify-content-between align-items-center mb-4">
      <h2>Manage Users</h2>
      <button class="btn btn-secondary" @click="$router.push('/AdminDashboard')">
        <i class="bi bi-arrow-left me-1"></i> Back to Dashboard
      </button>
    </div>
    
    <!-- Search Bar -->
    <div class="card mb-4 shadow-sm">
      <div class="card-body">
        <div class="input-group">
          <span class="input-group-text bg-primary text-white">
            <i class="bi bi-search"></i>
          </span>
          <input 
            type="text" 
            class="form-control form-control-lg" 
            placeholder="Search users by name, username or email..." 
            v-model="searchQuery"
            @input="debouncedSearch"
          />
          <button 
            class="btn btn-outline-secondary" 
            type="button" 
            @click="clearSearch" 
            v-if="searchQuery"
          >
            <i class="bi bi-x-lg"></i>
          </button>
        </div>
        <div class="mt-2 text-muted small" v-if="filteredUsers.length !== totalUsers">
          Showing {{ filteredUsers.length }} of {{ totalUsers }} users
        </div>
      </div>
    </div>
    
    <!-- Loading state -->
    <div v-if="loading" class="text-center my-5">
      <div class="spinner-border text-primary" role="status">
        <span class="visually-hidden">Loading...</span>
      </div>
      <p class="mt-2">Loading users...</p>
    </div>
    
    <!-- Error state -->
    <div v-else-if="error" class="alert alert-danger">
      {{ error }}
    </div>
    
    <!-- Empty search results -->
    <div v-else-if="filteredUsers.length === 0 && searchQuery" class="alert alert-info">
      <p class="mb-0">
        <i class="bi bi-info-circle me-2"></i>
        No users found matching "<strong>{{ searchQuery }}</strong>".
      </p>
      <button class="btn btn-sm btn-outline-primary mt-2" @click="clearSearch">
        Clear search
      </button>
    </div>
    
    <!-- User table -->
    <div v-else-if="filteredUsers.length > 0">
      <div class="card shadow-sm">
        <div class="card-body">
          <div class="table-responsive">
            <table class="table table-hover">
              <thead class="bg-light">
                <tr>
                  <th>ID</th>
                  <th>Username</th>
                  <th>Full Name</th>
                  <th>Email</th>
                  <th>Status</th>
                  <th>Actions</th>
                </tr>
              </thead>
              <tbody>
                <tr v-for="user in filteredUsers" :key="user.id">
                  <td>{{ user.id }}</td>
                  <td>{{ user.username }}</td>
                  <td>{{ user.fullname }}</td>
                  <td>{{ user.email }}</td>
                  <td>
                    <span :class="['badge', user.active ? 'bg-success' : 'bg-danger']">
                      {{ user.active ? 'Active' : 'Blocked' }}
                    </span>
                  </td>
                  <td>
                    <div class="btn-group">
                      <button 
                        class="btn btn-sm" 
                        :class="user.active ? 'btn-warning' : 'btn-success'" 
                        @click="toggleUserStatus(user.id, user.active)"
                        :disabled="statusInProgress === user.id"
                      >
                        <span v-if="statusInProgress === user.id" class="spinner-border spinner-border-sm me-1"></span>
                        {{ user.active ? 'Block' : 'Unblock' }}
                      </button>
                      
                      <button class="btn btn-sm btn-info ms-2" @click="viewUserProgress(user.id)">
                        <i class="bi bi-graph-up me-1"></i>Progress
                      </button>
                      
                      <button class="btn btn-sm btn-primary ms-2" @click="viewUserProfile(user.id)">
                        <i class="bi bi-person-circle me-1"></i>Profile
                      </button>
                    </div>
                  </td>
                </tr>
              </tbody>
            </table>
          </div>
        </div>
      </div>
    </div>
    
    <!-- User progress modal -->
    <div class="modal fade" :class="{'show d-block': showProgressModal}" tabindex="-1">
      <div class="modal-dialog modal-lg">
        <div class="modal-content">
          <div class="modal-header">
            <h5 class="modal-title">User Progress: {{ selectedUser?.username }}</h5>
            <button type="button" class="btn-close" @click="closeProgressModal"></button>
          </div>
          <div class="modal-body">
            <div v-if="progressLoading" class="text-center py-5">
              <div class="spinner-border text-primary" role="status">
                <span class="visually-hidden">Loading...</span>
              </div>
              <p class="mt-2">Loading progress data...</p>
            </div>
            
            <div v-else-if="progressError" class="alert alert-danger">
              {{ progressError }}
            </div>
            
            <div v-else-if="progressData && progressData.performances.length === 0" class="alert alert-info">
              <p class="mb-0">This user hasn't taken any quizzes yet.</p>
            </div>
            
            <div v-else-if="progressData">
              <!-- Progress summary -->
              <div class="row mb-4">
                <div class="col-md-4">
                  <div class="card bg-light">
                    <div class="card-body text-center">
                      <h3 class="mb-0">{{ progressData.summary.total_quizzes }}</h3>
                      <p class="text-muted">Quizzes Taken</p>
                    </div>
                  </div>
                </div>
                <div class="col-md-4">
                  <div class="card bg-light">
                    <div class="card-body text-center">
                      <h3 class="mb-0">{{ progressData.summary.average_score }}%</h3>
                      <p class="text-muted">Average Score</p>
                    </div>
                  </div>
                </div>
                <div class="col-md-4">
                  <div class="card bg-light">
                    <div class="card-body text-center">
                      <h3 class="mb-0">{{ progressData.summary.highest_score }}%</h3>
                      <p class="text-muted">Highest Score</p>
                    </div>
                  </div>
                </div>
              </div>
              
              <!-- Progress table -->
              <h5>Quiz History</h5>
              <div class="table-responsive">
                <table class="table table-striped">
                  <thead>
                    <tr>
                      <th>Quiz</th>
                      <th>Subject</th>
                      <th>Chapter</th>
                      <th>Score</th>
                      <th>Date</th>
                    </tr>
                  </thead>
                  <tbody>
                    <tr v-for="perf in progressData.performances" :key="perf.performance_id">
                      <td>{{ perf.quiz_name }}</td>
                      <td>{{ perf.subject_name }}</td>
                      <td>{{ perf.chapter_name }}</td>
                      <td>
                        <span class="badge bg-success">{{ perf.score }}%</span>
                      </td>
                      <td>{{ formatDate(perf.attempted_at) }}</td>
                    </tr>
                  </tbody>
                </table>
              </div>
            </div>
          </div>
          <div class="modal-footer">
            <button type="button" class="btn btn-secondary" @click="closeProgressModal">Close</button>
          </div>
        </div>
      </div>
    </div>
    <div v-if="showProgressModal" class="modal-backdrop fade show"></div>
  </div>
</template>

<script>
import axios from '@/axios.js';

export default {
  data() {
    return {
      users: [],
      loading: true,
      error: null,
      statusInProgress: null,
      showProgressModal: false,
      selectedUser: null,
      progressData: null,
      progressLoading: false,
      progressError: null,
      searchQuery: '',
      searchTimeout: null
    };
  },
  computed: {
    filteredUsers() {
      if (!this.searchQuery) {
        return this.users;
      }
      
      const query = this.searchQuery.toLowerCase();
      return this.users.filter(user => 
        user.username.toLowerCase().includes(query) ||
        user.fullname.toLowerCase().includes(query) ||
        user.email.toLowerCase().includes(query)
      );
    },
    totalUsers() {
      return this.users.length;
    }
  },
  methods: {
    async fetchUsers(query = '') {
      try {
        this.loading = true;
        this.error = null;
        
        // Build the URL with query parameter if provided
        const url = query 
          ? `/api/admin/users?q=${encodeURIComponent(query)}`
          : '/api/admin/users';
          
        const response = await axios.get(url);
        this.users = response.data;
        this.loading = false;
      } catch (error) {
        console.error('Error fetching users:', error);
        this.error = 'Failed to fetch users. Please try again.';
        this.loading = false;
      }
    },
    
    debouncedSearch() {
      // Clear any pending timeouts
      if (this.searchTimeout) {
        clearTimeout(this.searchTimeout);
      }
      
      // Set a new timeout for the search
      this.searchTimeout = setTimeout(() => {
        // If search query is short, don't perform API search, just use client filtering
        if (this.searchQuery.length >= 3) {
          this.fetchUsers(this.searchQuery);
        } else if (!this.searchQuery) {
          // If search is cleared, fetch all users
          this.fetchUsers();
        }
      }, 300); // 300ms debounce
    },
    
    clearSearch() {
      this.searchQuery = '';
      this.fetchUsers();
    },
    
    async toggleUserStatus(id, currentStatus) {
      try {
        this.statusInProgress = id;
        
        await axios.patch(`/api/users/${id}/toggle-status`);
        
        // Update the user in the local array
        const user = this.users.find(u => u.id === id);
        if (user) {
          user.active = !currentStatus;
        }
        
        // Optional: Show success message
        this.$root.$emit('show-toast', {
          message: `User has been ${!currentStatus ? 'activated' : 'blocked'} successfully`,
          type: 'success'
        });
      } catch (error) {
        console.error('Error updating user status:', error);
        
        // Show error message
        this.$root.$emit('show-toast', {
          message: 'Failed to update user status',
          type: 'danger'
        });
      } finally {
        this.statusInProgress = null;
      }
    },
    
    viewUserProfile(userId) {
      this.$router.push(`/user-profile/${userId}`);
    },
    
    async viewUserProgress(userId) {
      try {
        this.selectedUser = this.users.find(u => u.id === userId) || { id: userId, username: 'User' };
        this.showProgressModal = true;
        this.progressLoading = true;
        this.progressError = null;
        this.progressData = null;
        
        const response = await axios.get(`/api/admin/user-progress/${userId}`);
        this.progressData = response.data;
        this.progressLoading = false;
      } catch (error) {
        console.error('Error fetching user progress:', error);
        this.progressError = 'Failed to load progress data. Please try again.';
        this.progressLoading = false;
      }
    },
    
    closeProgressModal() {
      this.showProgressModal = false;
      this.selectedUser = null;
      this.progressData = null;
    },
    
    formatDate(dateString) {
      if (!dateString) return '';
      
      const date = new Date(dateString);
      return date.toLocaleString('en-US', {
        year: 'numeric',
        month: 'short',
        day: 'numeric',
        hour: '2-digit',
        minute: '2-digit'
      });
    }
  },
  created() {
    this.fetchUsers();
  }
};
</script>

<style scoped>
.modal {
  background-color: rgba(0, 0, 0, 0.5);
}

.table th {
  font-weight: 600;
}

.badge {
  font-size: 0.75rem;
  padding: 0.35em 0.65em;
}

/* Ensure proper spacing in button groups */
.btn-group .btn {
  margin-right: 0;
}

/* Improve button hover states */
.btn-sm {
  transition: all 0.2s;
}

.btn-sm:hover {
  transform: translateY(-1px);
  box-shadow: 0 2px 5px rgba(0,0,0,0.1);
}

/* Animation for modal */
.modal.show {
  animation: fadeIn 0.3s;
}

@keyframes fadeIn {
  from { opacity: 0; }
  to { opacity: 1; }
}

/* Add styling for search input */
.input-group-text {
  border-top-right-radius: 0;
  border-bottom-right-radius: 0;
}

.form-control-lg:focus {
  box-shadow: 0 0 0 0.25rem rgba(13, 110, 253, 0.25);
  border-color: #86b7fe;
}
</style>
