<template>
    <div class="container py-4">
      <div v-if="chapter" class="mb-4">
        <div class="d-flex align-items-center">
          <router-link to="/quiz" class="btn btn-outline-secondary me-3">
            <i class="bi bi-arrow-left"></i> Back to Subjects
          </router-link>
          <h1 class="mb-0">{{ chapter.chapter_name }}</h1>
        </div>
      </div>
  
      <h2 class="fw-bold mb-4">Available Quizzes</h2>
      
      <div class="row">
        <div v-for="quiz in quizzes" :key="quiz.id" class="col-md-6 mb-4">
          <div class="card quiz-card h-100">
            <div class="card-body">
              <h3 class="card-title">{{ quiz.quiz_name }}</h3>
              <div class="quiz-info">
                <div class="info-item">
                  <i class="bi bi-calendar3"></i>
                  <span>{{ formatDate(quiz.date_of_quiz) }}</span>
                </div>
                <div class="info-item">
                  <i class="bi bi-clock"></i>
                  <span>{{ quiz.timing }} minutes</span>
                </div>
              </div>
            </div>
            <div class="card-footer bg-transparent border-0">
              <button 
                @click="startQuiz(quiz.id)" 
                class="btn btn-success w-100"
              >
                <i class="bi bi-play-fill me-2"></i>Attempt Quiz
              </button>
            </div>
          </div>
        </div>
      </div>
  
      <div v-if="loading" class="text-center py-5">
        <div class="spinner-border text-primary" role="status">
          <span class="visually-hidden">Loading...</span>
        </div>
      </div>
  
      <div v-if="error" class="alert alert-danger mt-4">
        {{ error }}
      </div>
    </div>
  </template>
  
  <script>
  import axios from '@/axios.js';
  
  export default {
    name: 'UserQuizzesPage',
    props: {
      chapterId: {
        type: [Number, String],
        required: true
      }
    },
    data() {
      return {
        chapter: null,
        quizzes: [],
        loading: true,
        error: null
      };
    },
    created() {
      this.fetchQuizzes();
    },
    methods: {
      async fetchQuizzes() {
        try {
          this.loading = true;
          
          // Add token debug check
          try {
            const debugResponse = await axios.get("/api/debug-token");
            console.log("Token debug in quizzes page:", debugResponse.data);
          } catch (err) {
            console.error("Token debug error in quizzes page:", err);
          }
          
          const token = localStorage.getItem('auth_token');
          
          const response = await axios.get(`/api/chapters/${this.chapterId}/quizzes`, {
            headers: { Authorization: `Bearer ${token}` }
          });
          
          this.chapter = response.data.chapter;
          this.quizzes = response.data.quizzes;
          this.loading = false;
        } catch (error) {
          console.error('Error fetching quizzes:', error);
          this.error = 'Failed to load quizzes. Please try again later.';
          this.loading = false;
        }
      },
      formatDate(dateString) {
        const date = new Date(dateString);
        return date.toLocaleDateString('en-US', { 
          year: 'numeric', 
          month: 'long', 
          day: 'numeric' 
        });
      },
      startQuiz(quizId) {
        // Use the correct named route for quiz attempts
        this.$router.push({
          name: 'quiz-attempt',
          params: { quizId: quizId }
        });
      }
    }
  };
  </script>
  
  <style scoped>
  .quiz-card {
    transition: transform 0.3s ease, box-shadow 0.3s ease;
    border-radius: 10px;
  }
  
  .quiz-card:hover {
    transform: translateY(-5px);
    box-shadow: 0 10px 20px rgba(0, 0, 0, 0.1) !important;
  }
  
  .card-title {
    color: #4a6bdf;
    font-weight: 600;
  }
  
  .quiz-info {
    margin-top: 1rem;
  }
  
  .info-item {
    display: flex;
    align-items: center;
    margin-bottom: 0.5rem;
  }
  
  .info-item i {
    margin-right: 0.5rem;
    color: #6c757d;
  }
  </style>