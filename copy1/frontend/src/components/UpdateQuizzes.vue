<template>
    <div class="container quizzes-page">
      <h2 class="text-center my-4">Manage Quizzes for Chapter {{ chapterId }}</h2>
  
      <div class="card shadow-lg p-3 mb-5 bg-white rounded">
        <div class="card-header bg-success text-white d-flex justify-content-between align-items-center">
          <h4 class="m-0">Quizzes</h4>
          <button class="btn btn-light btn-sm" @click="addQuiz">+ Add Quiz</button>
        </div>
        <div class="card-body">
          <ul class="list-group">
            <li class="list-group-item d-flex justify-content-between align-items-center" v-for="quiz in quizzes" :key="quiz.id">
              <div>
                <strong>{{ quiz.title }}</strong> <br />
                <small>ID: {{ quiz.id }} | Score: {{ quiz.score }}</small>
              </div>
              <div>
                <button class="btn btn-info btn-sm me-2" @click="viewQuestions(quiz.id)">View Questions</button>
                <button class="btn btn-warning btn-sm me-2" @click="updateQuiz(quiz.id)">Update</button>

                <button class="btn btn-danger btn-sm" @click="deleteQuiz(quiz.id)">Delete</button>
              </div>
            </li>
          </ul>
        </div>
      </div>
  
      <button class="btn btn-secondary mt-3" @click="$router.go(-1)">Go Back</button>
    </div>
  </template>
  
  <script>
  import axios from '@/axios.js';
  
  export default {
    data() {
      return {
        subjectId: null,
        chapterId: null,
        quizzes: [],
      };
    },
    created() {
      this.subjectId = this.$route.params.subjectId;
      this.chapterId = this.$route.params.chapterId;
      this.fetchQuizzes();
    },
    methods: {
      async fetchQuizzes() {
        try {
          const response = await axios.get(`/chapters/${this.chapterId}/quizzes`);
          this.quizzes = response.data;
        } catch (error) {
          console.error('Error fetching quizzes:', error);
        }
      },
      async deleteQuiz(quizId) {
        try {
          await axios.delete(`/quizzes/${quizId}`);
          this.fetchQuizzes();
        } catch (error) {
          console.error('Error deleting quiz:', error);
        }
      },
      updateQuiz(quizId) {
        this.$router.push(`/update-quiz/${this.subjectId}/${this.chapterId}/${quizId}`);
      },
      viewQuestions(quizId) {
        this.$router.push(`/questions/${this.subjectId}/${this.chapterId}/${quizId}`);
      },
      addQuiz() {
        this.$router.push(`/add-quiz/${this.subjectId}/${this.chapterId}`);
      }
    }
  };
  </script>
  
  <style scoped>
  .quizzes-page {
    max-width: 800px;
    margin: auto;
  }
  </style>
  