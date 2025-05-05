<template>
  <div class="container mt-4">
    <div class="d-flex justify-content-between align-items-center mb-4">
      <h2>Manage Quizzes for Chapter: {{ chapterName }}</h2>
      <button class="btn btn-secondary" @click="goBack">Back to Subject</button>
    </div>

    <!-- Quiz Form -->
    <div class="card shadow mb-4">
      <div class="card-header bg-primary text-white d-flex justify-content-between align-items-center">
        <h4>Add New Quiz</h4>
        <button class="btn btn-light" @click="toggleForm">
          {{ showForm ? 'Cancel' : '+ Add Quiz' }}
        </button>
      </div>
      <div class="card-body" v-if="showForm">
        <form @submit.prevent="addQuiz">
          <div class="form-group mb-3">
            <label for="quizName">Quiz Name</label>
            <input type="text" id="quizName" v-model="newQuiz.quiz_name" class="form-control" required />
          </div>
          <div class="form-group mb-3">
            <label for="quizDate">Date of Quiz</label>
            <input type="date" id="quizDate" v-model="newQuiz.date_of_quiz" class="form-control" required />
          </div>
          <div class="form-group mb-3">
            <label for="quizTiming">Timing (minutes)</label>
            <input type="number" id="quizTiming" v-model="newQuiz.timing" class="form-control" required />
          </div>
          <button type="submit" class="btn btn-success">Save Quiz</button>
        </form>
      </div>
    </div>

    <!-- Quizzes List -->
    <div class="card shadow">
      <div class="card-header bg-info text-white">
        <h4 class="m-0">Quizzes</h4>
      </div>
      <div class="card-body">
        <!-- Loading State -->
        <div v-if="loading" class="text-center p-3">
          <p>Loading quizzes...</p>
        </div>

        <!-- No Quizzes State -->
        <div v-else-if="quizzes.length === 0" class="alert alert-info">
          No quizzes found for this chapter. Add your first quiz!
        </div>

        <!-- Quizzes List -->
        <div v-else class="table-responsive">
          <table class="table table-striped">
            <thead>
              <tr>
                <th>Quiz Name</th>
                <th>Date</th>
                <th>Duration (min)</th>
                <th>Actions</th>
              </tr>
            </thead>
            <tbody>
              <tr v-for="quiz in quizzes" :key="quiz.id">
                <td>{{ quiz.quiz_name }}</td>
                <td>{{ formatDate(quiz.date_of_quiz) }}</td>
                <td>{{ quiz.timing }}</td>
                <td>
                  <div class="btn-group">
                    <button class="btn btn-sm btn-primary me-2" @click="navigateToQuestions(quiz.id)">
                      Manage Questions
                    </button>
                    <button class="btn btn-sm btn-warning me-2" @click="editQuiz(quiz)">
                      Edit
                    </button>
                    <button class="btn btn-sm btn-danger" @click="deleteQuiz(quiz.id)">
                      Delete
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
  
  <!-- Add Quiz Modal -->
  <div class="modal fade" id="addQuizModal" tabindex="-1">
    <div class="modal-dialog">
      <div class="modal-content">
        <div class="modal-header">
          <h5 class="modal-title">Add New Quiz</h5>
          <button type="button" class="btn-close" data-bs-dismiss="modal" aria-label="Close"></button>
        </div>
        <div class="modal-body">
          <!-- ...existing form fields... -->
        </div>
        <div class="modal-footer">
          <button type="button" class="btn btn-secondary" data-bs-dismiss="modal">Close</button>
          <button type="button" class="btn btn-primary" @click="addQuiz" :disabled="isLoading">
            <span v-if="isLoading" class="spinner-border spinner-border-sm me-1" role="status"></span>
            Add Quiz
          </button>
        </div>
      </div>
    </div>
  </div>
  
  <!-- Notification Toast for Quiz Added -->
  <div class="position-fixed bottom-0 end-0 p-3" style="z-index: 5">
    <div id="quizNotificationToast" class="toast align-items-center text-white bg-success border-0" role="alert" aria-live="assertive" aria-atomic="true">
      <div class="d-flex">
        <div class="toast-body">
          <i class="bi bi-check-circle-fill me-2"></i>
          Quiz added successfully! Email notifications are being sent to users.
        </div>
        <button type="button" class="btn-close btn-close-white me-2 m-auto" data-bs-dismiss="toast" aria-label="Close"></button>
      </div>
    </div>
  </div>
  
  <!-- Simple notification alert (fallback for when Bootstrap toast isn't available) -->
  <div v-if="showNotification" class="position-fixed bottom-0 end-0 p-3" style="z-index: 5">
    <div class="alert alert-success d-flex align-items-center" role="alert">
      <i class="bi bi-check-circle-fill me-2"></i>
      <div>
        Quiz added successfully! Email notifications are being sent to users.
        <button type="button" class="btn-close ms-3" @click="showNotification = false" aria-label="Close"></button>
      </div>
    </div>
  </div>
</template>

<script>
import axios from '@/axios.js';
import notificationService from '@/services/notificationService.js';

// Try to import Bootstrap JavaScript if needed
let bootstrap;
try {
  bootstrap = require('bootstrap');
} catch (e) {
  console.warn('Bootstrap JavaScript not available:', e);
}

export default {
  props: {
    subjectId: {
      type: [Number, String],
      required: false
    },
    chapterId: {
      type: [Number, String],
      required: true
    }
  },
  data() {
    return {
      chapterName: '',
      quizzes: [],
      loading: true,
      error: null,
      showForm: false,
      newQuiz: {
        quiz_name: '',
        date_of_quiz: new Date().toISOString().split('T')[0], // Default to today
        timing: 30 // Default timing in minutes
      },
      editingQuiz: null,
      notificationToast: null,
      isLoading: false,
      showNotification: false
    };
  },
  computed: {
    validChapterId() {
      return this.chapterId || this.$route.params.chapterId;
    },
    validSubjectId() {
      return this.subjectId || this.$route.params.subjectId;
    }
  },
  methods: {
    toggleForm() {
      this.showForm = !this.showForm;
      if (!this.showForm) {
        // Reset form data
        this.newQuiz = {
          quiz_name: '',
          date_of_quiz: new Date().toISOString().split('T')[0],
          timing: 30
        };
      }
    },
    formatDate(dateStr) {
      if (!dateStr) return '';
      const date = new Date(dateStr);
      return date.toLocaleDateString('en-US', {
        year: 'numeric',
        month: 'short',
        day: 'numeric'
      });
    },
    async fetchChapterInfo() {
      try {
        const response = await axios.get(`/api/chapters/${this.validChapterId}`);
        this.chapterName = response.data.chapter_name;
      } catch (error) {
        console.error('Error fetching chapter info:', error);
        this.error = 'Failed to load chapter information';
        this.chapterName = 'Unknown Chapter';
      }
    },
    async fetchQuizzes() {
      try {
        this.loading = true;
        const response = await axios.get(`/api/chapters/${this.validChapterId}/quizzes`);
        console.log('Quizzes data:', response.data);
        this.quizzes = response.data.quizzes || [];
        if (!this.chapterName && response.data.chapter) {
          this.chapterName = response.data.chapter.chapter_name;
        }
      } catch (error) {
        console.error('Error fetching quizzes:', error);
        this.error = 'Failed to fetch quizzes';
      } finally {
        this.loading = false;
      }
    },
    async addQuiz() {
      if (!this.newQuiz.quiz_name || !this.newQuiz.date_of_quiz || !this.newQuiz.timing) {
        this.error = 'All fields are required';
        return;
      }
      
      this.isLoading = true;
      this.error = null;
      
      try {
        const response = await axios.post(`/api/chapters/${this.validChapterId}/quizzes`, {
          quiz_name: this.newQuiz.quiz_name,
          date_of_quiz: this.newQuiz.date_of_quiz,
          timing: parseInt(this.newQuiz.timing)
        });
        
        // Show notification - try toast first, fallback to alert
        this.showQuizAddedNotification();
        
        // For backup - trigger notification if needed
        try {
          const quizId = response.data.quiz.id;
          console.log(`Triggering notification for quiz ID: ${quizId}`);
          notificationService.notifyNewQuiz(quizId).catch(err => 
            console.warn('Frontend notification trigger failed (not critical):', err)
          );
        } catch (notifyError) {
          console.warn('Could not parse quiz ID from response:', notifyError);
        }
        
        // Refresh the quizzes list 
        this.fetchQuizzes();
        
        // Reset form
        this.newQuiz = {
          quiz_name: '',
          date_of_quiz: new Date().toISOString().split('T')[0],
          timing: 30
        };
        
        // Close form
        this.showForm = false;
      } catch (error) {
        console.error('Error adding quiz:', error);
        this.error = error.response?.data?.message || 'Error adding quiz';
      } finally {
        this.isLoading = false;
      }
    },
    showQuizAddedNotification() {
      // Try to use Bootstrap toast if available
      if (this.notificationToast) {
        try {
          this.notificationToast.show();
        } catch (e) {
          console.warn('Error showing Bootstrap toast:', e);
          this.showFallbackNotification();
        }
      } else {
        this.showFallbackNotification();
      }
    },
    showFallbackNotification() {
      // Use simple alert as fallback
      this.showNotification = true;
      setTimeout(() => {
        this.showNotification = false;
      }, 5000);
    },
    closeAddQuizModal() {
      if (this.addQuizModal) {
        this.addQuizModal.hide();
      }
    },
    editQuiz(quiz) {
      this.editingQuiz = quiz;
      this.newQuiz = { ...quiz };
      this.showForm = true;
    },
    async deleteQuiz(quizId) {
      if (!confirm('Are you sure you want to delete this quiz?')) return;
      
      try {
        await axios.delete(`/api/quizzes/${quizId}`);
        alert('Quiz deleted successfully!');
        this.fetchQuizzes();
      } catch (error) {
        console.error('Error deleting quiz:', error);
        alert(error.response?.data?.message || 'Failed to delete quiz');
      }
    },
    navigateToQuestions(quizId) {
      console.log(`Navigating to questions for quiz ID: ${quizId}`);
      this.$router.push(`/quizzes/${quizId}/questions`);
    },
    goBack() {
      this.$router.push(`/update-subject/${this.validSubjectId}`);
    }
  },
  created() {
    console.log('QuizzesPage created with chapterId:', this.validChapterId);
    console.log('Route params:', this.$route.params);
    
    this.fetchChapterInfo();
    this.fetchQuizzes();
  },
  mounted() {
    try {
      // Try to initialize Bootstrap toast
      const toastEl = document.getElementById('quizNotificationToast');
      if (toastEl && bootstrap && bootstrap.Toast) {
        this.notificationToast = new bootstrap.Toast(toastEl, {
          delay: 5000,
          animation: true
        });
      } else {
        console.warn('Bootstrap Toast initialization failed. Will use fallback notification.');
      }
    } catch (error) {
      console.error('Error initializing Bootstrap Toast:', error);
    }
  }
};
</script>

<style scoped>
.card {
  border-radius: 10px;
  overflow: hidden;
  margin-bottom: 20px;
}

.card-header {
  font-weight: bold;
}

.btn-group .btn {
  margin-right: 5px;
}

.table-responsive {
  overflow-x: auto;
}

/* Add styles for the notification toast */
.toast {
  box-shadow: 0 0.5rem 1rem rgba(0, 0, 0, 0.15);
}

/* Animation for the notification toast */
@keyframes fadeIn {
  from { opacity: 0; transform: translateY(20px); }
  to { opacity: 1; transform: translateY(0); }
}

.toast.showing {
  animation: fadeIn 0.3s ease;
}

/* Add animation for fallback notification */
.alert-success {
  animation: fadeIn 0.3s ease;
  box-shadow: 0 0.5rem 1rem rgba(0, 0, 0, 0.15);
}

@keyframes fadeIn {
  from { opacity: 0; transform: translateY(20px); }
  to { opacity: 1; transform: translateY(0); }
}
</style>