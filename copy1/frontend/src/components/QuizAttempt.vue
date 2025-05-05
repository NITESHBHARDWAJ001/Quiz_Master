<template>
  <div class="container py-4">
    <div v-if="loading" class="text-center py-5">
      <div class="spinner-border text-primary" role="status">
        <span class="visually-hidden">Loading...</span>
      </div>
      <p class="mt-3">Loading quiz...</p>
    </div>

    <div v-else-if="quizStarted" class="quiz-container">
      <!-- Quiz Header with Timer -->
      <div class="quiz-header mb-4">
        <h2 class="quiz-title">{{ quizInfo.quiz_name }}</h2>
        <div class="timer" :class="{ 'danger': timeLeft < 60 }">
          <i class="bi bi-clock"></i>
          <span>{{ formatTime(timeLeft) }}</span>
        </div>
      </div>

      <!-- Progress Bar -->
      <div class="progress mb-4">
        <div 
          class="progress-bar" 
          role="progressbar" 
          :style="{ width: `${(currentQuestionIndex + 1) / questions.length * 100}%` }"
          :aria-valuenow="(currentQuestionIndex + 1) / questions.length * 100" 
          aria-valuemin="0" 
          aria-valuemax="100">
          Question {{ currentQuestionIndex + 1 }} of {{ questions.length }}
        </div>
      </div>

      <!-- Question Display -->
      <div class="question-container">
        <div class="question-card card">
          <div class="card-body">
            <h4 class="question-text mb-4">{{ currentQuestion.question_statement }}</h4>
            
            <div class="options-container">
              <div 
                v-for="(option, index) in questionOptions" 
                :key="index" 
                class="option"
                :class="{
                  'selected': userAnswers[currentQuestionIndex] === option,
                  'correct': showAnswer && option === currentQuestion.correct_option,
                  'incorrect': showAnswer && userAnswers[currentQuestionIndex] === option && option !== currentQuestion.correct_option
                }"
                @click="selectOption(option)"
              >
                <div class="option-label">{{ ['A', 'B', 'C', 'D'][index] }}</div>
                <div class="option-text">{{ option }}</div>
              </div>
            </div>

            <div v-if="showAnswer" class="answer-feedback mt-4">
              <div v-if="userAnswers[currentQuestionIndex] === currentQuestion.correct_option" class="alert alert-success">
                <i class="bi bi-check-circle-fill me-2"></i>Correct answer!
              </div>
              <div v-else class="alert alert-danger">
                <i class="bi bi-x-circle-fill me-2"></i>Incorrect. The correct answer is: {{ currentQuestion.correct_option }}
              </div>
            </div>
          </div>
        </div>
      </div>

      <!-- Navigation Buttons -->
      <div class="navigation-buttons mt-4">
        <button 
          class="btn btn-outline-secondary" 
          @click="prevQuestion"
          :disabled="currentQuestionIndex === 0 || submittingAnswer"
        >
          <i class="bi bi-arrow-left me-2"></i>Previous
        </button>
        
        <div>
          <button 
            v-if="!showAnswer" 
            class="btn btn-primary" 
            @click="submitAnswer"
            :disabled="!userAnswers[currentQuestionIndex] || submittingAnswer"
          >
            Submit Answer
            <i class="bi bi-check2 ms-2"></i>
          </button>
          
          <button 
            v-else-if="currentQuestionIndex < questions.length - 1" 
            class="btn btn-primary" 
            @click="nextQuestion"
          >
            Next Question
            <i class="bi bi-arrow-right ms-2"></i>
          </button>
          
          <button 
            v-else 
            class="btn btn-success" 
            @click="finishQuiz"
          >
            Finish Quiz
            <i class="bi bi-flag-fill ms-2"></i>
          </button>
        </div>
      </div>
    </div>
    
    <div v-else-if="quizCompleted" class="quiz-results">
      <div class="card shadow-sm p-4 text-center">
        <i class="bi bi-trophy-fill text-warning result-icon"></i>
        <h2 class="fw-bold mb-3">Quiz Completed!</h2>
        
        <div class="score-display mb-4">
          <p class="lead">Your Score</p>
          <h3 class="display-4 fw-bold text-primary">{{ score }} / {{ totalPossibleScore }}</h3>
          <p class="text-muted">{{ Math.round(score/totalPossibleScore * 100) }}%</p>
        </div>
        
        <div class="d-grid gap-2 d-md-flex justify-content-md-center">
          <router-link to="/quiz" class="btn btn-outline-secondary px-4">
            <i class="bi bi-list-check me-2"></i>All Quizzes
          </router-link>
          <router-link to="/progress" class="btn btn-primary px-4">
            <i class="bi bi-graph-up me-2"></i>View Progress
          </router-link>
        </div>
      </div>
    </div>

    <div v-else class="quiz-intro">
      <div class="card shadow-sm">
        <div class="card-body text-center p-5">
          <h2 class="mb-4">{{ quizInfo.quiz_name }}</h2>
          
          <div class="quiz-details mb-4">
            <div class="detail-item">
              <i class="bi bi-clock"></i>
              <span>{{ quizInfo.timing }} minutes</span>
            </div>
            <div class="detail-item">
              <i class="bi bi-question-circle"></i>
              <span>{{ questions.length }} questions</span>
            </div>
          </div>
          
          <div class="alert alert-info mb-4">
            <p class="mb-0"><strong>Note:</strong> Once you start the quiz, the timer will begin. The quiz will automatically submit when the time is up.</p>
          </div>
          
          <button @click="startQuiz" class="btn btn-lg btn-success px-5">
            <i class="bi bi-play-fill me-2"></i>Start Quiz Now
          </button>
        </div>
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
  name: 'QuizAttempt',
  data() {
    return {
      quizId: null,
      quizInfo: {},
      questions: [],
      loading: true,
      error: null,
      quizStarted: false,
      quizCompleted: false,
      currentQuestionIndex: 0,
      userAnswers: [],
      showAnswer: false,
      timeLeft: 0,
      timer: null,
      score: 0,
      totalPossibleScore: 0,
      submittingAnswer: false
    };
  },
  computed: {
    currentQuestion() {
      return this.questions[this.currentQuestionIndex] || {};
    },
    questionOptions() {
      if (!this.currentQuestion) return [];
      return [
        this.currentQuestion.option1,
        this.currentQuestion.option2,
        this.currentQuestion.option3,
        this.currentQuestion.option4
      ];
    }
  },
  created() {
    this.quizId = this.$route.params.quizId;
    if (this.quizId) {
      this.fetchQuizData();
    } else {
      this.error = 'Invalid quiz. Please select a valid quiz.';
      this.loading = false;
    }
  },
  beforeUnmount() {
    this.clearTimer();
  },
  methods: {
    async fetchQuizData() {
      try {
        this.loading = true;
        
        // Add debug token check
        try {
          const debugResponse = await axios.get("/api/debug-token");
          console.log("Token debug in quiz details:", debugResponse.data);
        } catch (err) {
          console.error("Token debug error in quiz details:", err);
        }
        
        // Fetch quiz info without passing token for now
        const quizResponse = await axios.get(`/api/quizzes/${this.quizId}`);
        this.quizInfo = quizResponse.data;
        
        // Fetch quiz questions without passing token for now
        const questionsResponse = await axios.get(`/api/quizzes/${this.quizId}/questions`);
        this.questions = questionsResponse.data.questions;
        
        // Initialize user answers array
        this.userAnswers = new Array(this.questions.length).fill(null);
        
        // Calculate total possible score
        this.totalPossibleScore = this.questions.reduce((sum, q) => sum + q.marks, 0);
        
        this.loading = false;
      } catch (error) {
        console.error('Error fetching quiz data:', error);
        this.error = 'Failed to load quiz data. Please try again later.';
        this.loading = false;
      }
    },
    async fetchQuizDetails() {
      try {
        this.loading = true;
        
        // Add token debug check
        try {
          const debugResponse = await axios.get("/api/debug-token");
          console.log("Token debug in quiz attempt:", debugResponse.data);
        } catch (err) {
          console.error("Token debug error in quiz attempt:", err);
        }
        
        const response = await axios.get(`/api/quizzes/${this.quizId}/questions`);
        
        this.quiz = response.data.quiz;
        this.questions = response.data.questions;
        this.loading = false;
        
        // Initialize answers array with empty values
        this.answers = this.questions.map(() => null);
        
        // Start timer if specified
        if (this.timeLimit > 0) {
          this.startTimer();
        }
      } catch (error) {
        console.error('Error fetching quiz questions:', error);
        this.error = 'Failed to load quiz questions. Please try again later.';
        this.loading = false;
      }
    },
    startQuiz() {
      this.quizStarted = true;
      this.timeLeft = this.quizInfo.timing * 60; // Convert minutes to seconds
      this.startTimer();
    },
    startTimer() {
      this.timer = setInterval(() => {
        this.timeLeft--;
        if (this.timeLeft <= 0) {
          this.clearTimer();
          this.autoSubmitQuiz();
        }
      }, 1000);
    },
    clearTimer() {
      if (this.timer) {
        clearInterval(this.timer);
        this.timer = null;
      }
    },
    formatTime(seconds) {
      const minutes = Math.floor(seconds / 60);
      const remainingSeconds = seconds % 60;
      return `${minutes}:${remainingSeconds < 10 ? '0' : ''}${remainingSeconds}`;
    },
    selectOption(option) {
      if (!this.showAnswer) {
        // Replace this line:
        // this.$set(this.userAnswers, this.currentQuestionIndex, option);
        
        // With this direct assignment (Vue 3 way):
        this.userAnswers[this.currentQuestionIndex] = option;
      }
    },
    async submitAnswer() {
      if (this.submittingAnswer) return;
      
      this.submittingAnswer = true;
      this.showAnswer = true;
      
      // Calculate score for this question
      if (this.userAnswers[this.currentQuestionIndex] === this.currentQuestion.correct_option) {
        this.score += this.currentQuestion.marks;
      }
      
      this.submittingAnswer = false;
    },
    nextQuestion() {
      if (this.currentQuestionIndex < this.questions.length - 1) {
        this.currentQuestionIndex++;
        this.showAnswer = false;
      }
    },
    prevQuestion() {
      if (this.currentQuestionIndex > 0) {
        this.currentQuestionIndex--;
        // Show answer if the user has already answered this question
        this.showAnswer = this.userAnswers[this.currentQuestionIndex] !== null;
      }
    },
    async finishQuiz() {
      this.clearTimer();
      await this.submitQuizResults();
      this.quizStarted = false;
      this.quizCompleted = true;
    },
    async autoSubmitQuiz() {
      // Calculate scores for unanswered questions
      for (let i = 0; i < this.questions.length; i++) {
        if (this.userAnswers[i] === this.questions[i].correct_option) {
          this.score += this.questions[i].marks;
        }
      }
      
      await this.submitQuizResults();
      this.quizStarted = false;
      this.quizCompleted = true;
    },
    async submitQuizResults() {
      try {
        // Don't pass token for now
        await axios.post('/api/submit-quiz', {
          quiz_id: this.quizId,
          user_id: localStorage.getItem('user_id'),
          score: this.score,
          total_possible: this.totalPossibleScore,
          answers: this.userAnswers
        });
        
      } catch (error) {
        console.error('Error submitting quiz results:', error);
        this.error = 'Failed to save quiz results. Please try again.';
      }
    }
  }
};
</script>

<style scoped>
.quiz-container {
  max-width: 800px;
  margin: 0 auto;
}

.quiz-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.quiz-title {
  font-weight: bold;
  color: #4a6bdf;
}

.timer {
  font-size: 1.5rem;
  font-weight: bold;
  display: flex;
  align-items: center;
  padding: 0.5rem 1rem;
  background-color: #f0f0f0;
  border-radius: 8px;
}

.timer.danger {
  color: #dc3545;
  animation: pulse 1s infinite;
}

.timer i {
  margin-right: 0.5rem;
}

.question-container {
  margin-bottom: 2rem;
}

.question-card {
  border-radius: 12px;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
}

.question-text {
  font-weight: 600;
  line-height: 1.5;
}

.options-container {
  display: grid;
  grid-template-columns: 1fr;
  gap: 12px;
}

.option {
  display: flex;
  align-items: center;
  padding: 12px 16px;
  border: 2px solid #dee2e6;
  border-radius: 8px;
  cursor: pointer;
  transition: all 0.2s ease;
}

.option:hover:not(.selected, .correct, .incorrect) {
  border-color: #4a6bdf;
  background-color: #f8f9fa;
}

.option.selected {
  border-color: #4a6bdf;
  background-color: #e8eeff;
}

.option.correct {
  border-color: #28a745;
  background-color: #d4edda;
}

.option.incorrect {
  border-color: #dc3545;
  background-color: #f8d7da;
}

.option-label {
  display: flex;
  align-items: center;
  justify-content: center;
  width: 30px;
  height: 30px;
  background-color: #e9ecef;
  border-radius: 50%;
  margin-right: 12px;
  font-weight: bold;
}

.option-text {
  flex: 1;
}

.navigation-buttons {
  display: flex;
  justify-content: space-between;
}

.quiz-results, .quiz-intro {
  max-width: 600px;
  margin: 0 auto;
}

.result-icon {
  font-size: 4rem;
  margin-bottom: 1rem;
}

.score-display {
  background-color: #f8f9fa;
  border-radius: 12px;
  padding: 1.5rem;
  margin: 1.5rem 0;
}

.quiz-details {
  display: flex;
  justify-content: center;
  gap: 2rem;
}

.detail-item {
  display: flex;
  align-items: center;
}

.detail-item i {
  margin-right: 0.5rem;
  color: #6c757d;
}

@keyframes pulse {
  0% {
    opacity: 1;
  }
  50% {
    opacity: 0.5;
  }
  100% {
    opacity: 1;
  }
}
</style>