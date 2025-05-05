<template>
  <div class="container mt-4">
    <div class="d-flex justify-content-between align-items-center mb-4">
      <h2>Manage Questions for Quiz: {{ quizName }}</h2>
      <button class="btn btn-secondary" @click="goBack">Back to Quizzes</button>
    </div>

    <!-- Question Form -->
    <div class="card shadow mb-4">
      <div class="card-header bg-primary text-white d-flex justify-content-between align-items-center">
        <h4>Add New Question</h4>
        <button class="btn btn-light" @click="toggleForm">
          {{ showForm ? 'Cancel' : '+ Add Question' }}
        </button>
      </div>
      <div class="card-body" v-if="showForm">
        <form @submit.prevent="addQuestion">
          <div class="form-group mb-3">
            <label for="questionStatement">Question</label>
            <textarea 
              id="questionStatement" 
              v-model="newQuestion.question_statement" 
              class="form-control" 
              rows="3"
              placeholder="Enter your question here"
              required
            ></textarea>
          </div>
          
          <div class="form-group mb-3">
            <label for="option1">Option 1</label>
            <input 
              type="text" 
              id="option1" 
              v-model="newQuestion.option1" 
              class="form-control" 
              placeholder="First option"
              required 
            />
          </div>
          
          <div class="form-group mb-3">
            <label for="option2">Option 2</label>
            <input 
              type="text" 
              id="option2" 
              v-model="newQuestion.option2" 
              class="form-control" 
              placeholder="Second option"
              required 
            />
          </div>
          
          <div class="form-group mb-3">
            <label for="option3">Option 3</label>
            <input 
              type="text" 
              id="option3" 
              v-model="newQuestion.option3" 
              class="form-control" 
              placeholder="Third option"
              required 
            />
          </div>
          
          <div class="form-group mb-3">
            <label for="option4">Option 4</label>
            <input 
              type="text" 
              id="option4" 
              v-model="newQuestion.option4" 
              class="form-control" 
              placeholder="Fourth option"
              required 
            />
          </div>

          <div class="form-group mb-3">
            <label for="option4">Correct Option</label>
            <input 
              type="text" 
              id="correct_Option" 
              v-model="newQuestion.correct_option" 
              class="form-control" 
              placeholder="Correct option"
              required 
            />
          </div>
          
          <div class="form-group mb-3">
            <label for="marks">Marks</label>
            <input 
              type="number" 
              id="marks" 
              v-model="newQuestion.marks" 
              class="form-control" 
              min="1"
              required 
            />
          </div>
          
          <div class="d-flex justify-content-between mt-4">
            <button type="button" class="btn btn-secondary" @click="toggleForm">Cancel</button>
            <button type="submit" class="btn btn-success">Save Question</button>
          </div>
        </form>
      </div>
    </div>

    <!-- Questions List -->
    <div class="card shadow">
      <div class="card-header bg-info text-white">
        <h4 class="m-0">Questions</h4>
      </div>
      <div class="card-body">
        <!-- Loading State -->
        <div v-if="loading" class="text-center p-3">
          <p>Loading questions...</p>
        </div>

        <!-- No Questions State -->
        <div v-else-if="questions.length === 0" class="alert alert-info">
          No questions found for this quiz. Add your first question!
        </div>

        <!-- Questions List -->
        <div v-else class="question-list">
          <div class="question-card card mb-3" v-for="(question, index) in questions" :key="question.id">
            <div class="card-header bg-light d-flex justify-content-between align-items-center">
              <h5 class="m-0">Question {{ index + 1 }} <span class="text-muted">({{ question.marks }} marks)</span></h5>
              <div class="btn-group">
                <button class="btn btn-sm btn-warning me-2" @click="editQuestion(question)">Edit</button>
                <button class="btn btn-sm btn-danger" @click="deleteQuestion(question.id)">Delete</button>
              </div>
            </div>
            <div class="card-body">
              <p class="question-text">{{ question.question_statement }}</p>
              <div class="options-list">
                <div class="option mb-2">
                  <span class="option-label">A:</span> {{ question.option1 }}
                </div>
                <div class="option mb-2">
                  <span class="option-label">B:</span> {{ question.option2 }}
                </div>
                <div class="option mb-2">
                  <span class="option-label">C:</span> {{ question.option3 }}
                </div>
                <div class="option mb-2">
                  <span class="option-label">D:</span> {{ question.option4 }}
                </div>
                <div class="option mb-2">
                  <span class="correct-option-label">Correct:</span> {{ question.correct_option }}
                </div>
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

export default {
  props: {
    quizId: {
      type: [Number, String],
      required: false
    }
  },
  data() {
    return {
      quizName: '',
      questions: [],
      loading: true,
      error: null,
      showForm: false,
      newQuestion: {
        question_statement: '',
        option1: '',
        option2: '',
        option3: '',
        option4: '',
        correct_option: '',
        marks: 1
      },
      editingQuestion: null
    };
  },
  computed: {
    validQuizId() {
      return this.quizId || this.$route.params.quizId;
    }
  },
  methods: {
    toggleForm() {
      this.showForm = !this.showForm;
      if (!this.showForm) {
        // Reset form data
        this.newQuestion = {
          question_statement: '',
          option1: '',
          option2: '',
          option3: '',
          option4: '',
          correct_option: '',
          marks: 1
        };
        this.editingQuestion = null;
      }
    },
    async fetchQuizInfo() {
      try {
        console.log("Fetching quiz info for ID:", this.validQuizId);
        const response = await axios.get(`/api/quizzes/${this.validQuizId}`);
        console.log("Quiz data received:", response.data);
        this.quizName = response.data.quiz_name;
      } catch (error) {
        console.error('Error fetching quiz info:', error);
        this.error = 'Failed to load quiz information';
        this.quizName = 'Unknown Quiz';
      }
    },
    async fetchQuestions() {
      try {
        this.loading = true;
        console.log(`Fetching questions for quiz ID: ${this.validQuizId}`);
        const response = await axios.get(`/api/quizzes/${this.validQuizId}/questions`);
        console.log('Questions data:', response.data);
        this.questions = response.data.questions || [];
        
        // If quiz name not set, use from response
        if (!this.quizName && response.data.quiz) {
          this.quizName = response.data.quiz.quiz_name;
        }
      } catch (error) {
        console.error('Error fetching questions:', error);
        this.error = 'Failed to fetch questions';
      } finally {
        this.loading = false;
      }
    },
    async addQuestion() {
      try {
        if (this.editingQuestion) {
          // Update existing question
          console.log('Updating question:', this.newQuestion);
          const response = await axios.put(`/api/questions/${this.editingQuestion.id}`, this.newQuestion);
          console.log('Question updated:', response.data);
          alert('Question updated successfully!');
        } else {
          // Add new question
          console.log(`Adding question to quiz ID: ${this.validQuizId}`);
          console.log('Question data:', this.newQuestion);
          
          const response = await axios.post(`/api/quizzes/${this.validQuizId}/questions`, this.newQuestion);
          console.log('Question added:', response.data);
          alert('Question added successfully!');
        }
        
        // Reset form and refresh questions
        this.toggleForm();
        this.fetchQuestions();
      } catch (error) {
        console.error('Error saving question:', error);
        alert(error.response?.data?.message || 'Failed to save question');
      }
    },
    editQuestion(question) {
      this.editingQuestion = question;
      this.newQuestion = { ...question };
      this.showForm = true;
    },
    async deleteQuestion(questionId) {
      if (!confirm('Are you sure you want to delete this question?')) return;
      
      try {
        await axios.delete(`/api/questions/${questionId}`);
        alert('Question deleted successfully!');
        this.fetchQuestions();
      } catch (error) {
        console.error('Error deleting question:', error);
        alert(error.response?.data?.message || 'Failed to delete question');
      }
    },
    goBack() {
      // Go back to the previous page
      this.$router.go(-1);
    }
  },
  created() {
    console.log('QuestionsPage created with quizId:', this.validQuizId);
    console.log('Route params:', this.$route.params);
    
    this.fetchQuizInfo();
    this.fetchQuestions();
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

.question-text {
  font-size: 1.1rem;
  font-weight: 500;
  margin-bottom: 15px;
}

.option-label {
  font-weight: bold;
  margin-right: 10px;
  display: inline-block;
  width: 25px;
}

.correct-option-label {
  font-weight: bold;
  margin-right: 10px;
  display: inline-block;
  width: 70px; /* Increased width to fit "Correct:" text */
}

.btn-group .btn {
  margin-right: 5px;
}

.question-card {
  border: 1px solid #e0e0e0;
}

.question-card .card-header {
  background-color: #f8f9fa;
}
</style>
