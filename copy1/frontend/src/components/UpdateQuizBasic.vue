<template>
  <div class="container mt-4">
    <h2>Update Quiz Basic Details</h2>
    <form @submit.prevent="updateQuizBasic">
      <div class="form-group">
        <label for="quizName">Quiz Name</label>
        <input type="text" id="quizName" v-model="quizName" class="form-control" required />
      </div>
      <div class="form-group">
        <label for="dateOfQuiz">Date of Quiz</label>
        <input type="date" id="dateOfQuiz" v-model="dateOfQuiz" class="form-control" required />
      </div>
      <div class="form-group">
        <label for="timing">Timing (in minutes)</label>
        <input type="number" id="timing" v-model="timing" class="form-control" required />
      </div>
      <button type="submit" class="btn btn-success mt-3">Update</button>
    </form>
  </div>
</template>

<script>
import axios from '@/axios.js';

export default {
  props: ['id'],
  data() {
    return {
      quizName: '',
      dateOfQuiz: '',
      timing: '',
    };
  },
  methods: {
    async fetchQuizDetails() {
      try {
        const response = await axios.get(`/api/quizzes/${this.id}/basic`, {
          headers: { Authorization: `Bearer ${localStorage.getItem('auth_token')}` },
        });
        const quiz = response.data;
        this.quizName = quiz.quiz_name;
        this.dateOfQuiz = quiz.date_of_quiz;
        this.timing = quiz.timing;
      } catch (error) {
        console.error('Error fetching quiz details:', error);
        alert('Failed to fetch quiz details.');
      }
    },
    async updateQuizBasic() {
      try {
        await axios.put(`/api/quizzes/${this.id}/basic`, {
          quiz_name: this.quizName,
          date_of_quiz: this.dateOfQuiz,
          timing: this.timing,
        }, {
          headers: { Authorization: `Bearer ${localStorage.getItem('auth_token')}` },
        });
        alert('Quiz basic details updated successfully.');
        this.$router.push('/'); // Redirect to home or another page
      } catch (error) {
        console.error('Error updating quiz basic details:', error);
        alert('Failed to update quiz basic details.');
      }
    },
  },
  created() {
    this.fetchQuizDetails();
  },
};
</script>

<style scoped>
/* Add any styling specific to this component here */
</style>
