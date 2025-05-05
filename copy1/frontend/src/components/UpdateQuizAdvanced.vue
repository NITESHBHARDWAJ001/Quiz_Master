<template>
  <div class="container mt-4">
    <h2>Update Quiz Advanced Details</h2>
    <form @submit.prevent="updateQuizAdvanced">
      <div class="form-group">
        <label for="title">Title</label>
        <input type="text" id="title" v-model="title" class="form-control" required />
      </div>
      <div class="form-group">
        <label for="description">Description</label>
        <textarea id="description" v-model="description" class="form-control" required></textarea>
      </div>
      <div class="form-group">
        <label for="numberOfQuestions">Number of Questions</label>
        <input type="number" id="numberOfQuestions" v-model="numberOfQuestions" class="form-control" required />
      </div>
      <div class="form-group">
        <label for="duration">Duration (in minutes)</label>
        <input type="number" id="duration" v-model="duration" class="form-control" required />
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
      title: '',
      description: '',
      numberOfQuestions: '',
      duration: '',
    };
  },
  methods: {
    async fetchQuizDetails() {
      try {
        const response = await axios.get(`/api/quizzes/${this.id}/advanced`, {
          headers: { Authorization: `Bearer ${localStorage.getItem('auth_token')}` },
        });
        const quiz = response.data;
        this.title = quiz.title;
        this.description = quiz.description;
        this.numberOfQuestions = quiz.number_of_questions;
        this.duration = quiz.duration;
      } catch (error) {
        console.error('Error fetching quiz details:', error);
        alert('Failed to fetch quiz details.');
      }
    },
    async updateQuizAdvanced() {
      try {
        await axios.put(`/api/quizzes/${this.id}/advanced`, {
          title: this.title,
          description: this.description,
          numberOfQuestions: this.numberOfQuestions,
          duration: this.duration,
        }, {
          headers: { Authorization: `Bearer ${localStorage.getItem('auth_token')}` },
        });
        alert('Quiz advanced details updated successfully.');
        this.$router.push('/'); // Redirect to home or another page
      } catch (error) {
        console.error('Error updating quiz advanced details:', error);
        alert('Failed to update quiz advanced details.');
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
