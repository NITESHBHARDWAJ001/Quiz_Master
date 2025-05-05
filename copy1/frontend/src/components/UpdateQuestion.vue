<template>
    <div class="container update-question-page">
      <h2 class="text-center my-4">Update Question</h2>
  
      <div class="card shadow-lg p-4 mb-5 bg-white rounded">
        <div class="card-header bg-info text-white">
          <h4 class="m-0">Edit Question Details</h4>
        </div>
        <div class="card-body">
          <form @submit.prevent="updateQuestion">
            <div class="mb-3">
              <label class="form-label">Question Title</label>
              <input type="text" class="form-control" v-model="question.title" required />
            </div>
  
            <div class="mb-3">
              <label class="form-label">Options</label>
              <div v-for="(option, index) in question.options" :key="index" class="input-group mb-2">
                <input type="text" class="form-control" v-model="question.options[index]" required />
                <div class="input-group-text">
                  <input type="radio" name="correctOption" :value="index" v-model="question.correctOption" />
                </div>
              </div>
            </div>
  
            <div class="mb-3">
              <label class="form-label">Correct Answer</label>
              <select class="form-select" v-model="question.correctOption" required>
                <option v-for="(option, index) in question.options" :key="index" :value="index">
                  {{ option }}
                </option>
              </select>
            </div>
  
            <button type="submit" class="btn btn-success">Update Question</button>
            <button type="button" class="btn btn-secondary ms-2" @click="$router.go(-1)">Cancel</button>
          </form>
        </div>
      </div>
    </div>
  </template>
  
  <script>
  import axios from '@/axios.js';
  
  export default {
    data() {
      return {
        questionId: null,
        question: {
          title: '',
          options: ['', '', '', ''],
          correctOption: 0,
        },
      };
    },
    created() {
      this.questionId = this.$route.params.questionId;
      this.fetchQuestion();
    },
    methods: {
      async fetchQuestion() {
        try {
          const response = await axios.get(`/questions/${this.questionId}`);
          this.question = response.data;
        } catch (error) {
          console.error('Error fetching question:', error);
        }
      },
      async updateQuestion() {
        try {
          await axios.put(`/questions/${this.questionId}`, this.question);
          alert('Question updated successfully!');
          this.$router.go(-1);
        } catch (error) {
          console.error('Error updating question:', error);
        }
      },
    },
  };
  </script>
  
  <style scoped>
  .update-question-page {
    max-width: 600px;
    margin: auto;
  }
  
  .card {
    border-radius: 10px;
  }
  </style>
  