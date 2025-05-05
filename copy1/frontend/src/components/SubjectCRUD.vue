<template>
  <div class="container mt-4">
    <h2>Manage Subjects</h2>
    <button class="btn btn-primary mb-3" @click="showForm = !showForm">
      Add Subject
    </button>
    <div v-if="showForm">
      <form @submit.prevent="addSubject">
        <div class="form-group">
          <label for="subjectName">Subject Name</label>
          <input type="text" id="subjectName" v-model="subjectName" class="form-control" required />
        </div>
        <div class="form-group">
          <label for="subjectDescription">Description</label>
          <textarea id="subjectDescription" v-model="subjectDescription" class="form-control" required></textarea>
        </div>
        <button type="submit" class="btn btn-success mt-3">Save</button>
      </form>
    </div>

    <table class="table mt-4">
      <thead>
        <tr>
          <th>Subject Name</th>
          <th>Description</th>
          <th>Actions</th>
        </tr>
      </thead>
      <tbody>
        <tr v-for="subject in subjects" :key="subject.id">
          <td>{{ subject.name }}</td>
          <td>{{ subject.description }}</td>
          <td>
            <button class="btn btn-danger" @click="deleteSubject(subject.id)">Delete</button>
          </td>
        </tr>
      </tbody>
    </table>
  </div>
</template>

<script>
import axios from '@/axios.js';
import notificationService from '@/services/notificationService';

export default {
  data() {
    return {
      showForm: false,
      subjectName: '',
      subjectDescription: '',
      subjects: [],
    };
  },
  methods: {
    async fetchSubjects() {
      try {
        const response = await axios.get('/api/subjects', {
          headers: { Authorization: `Bearer ${localStorage.getItem('auth_token')}` },
        });
        this.subjects = response.data;
      } catch (error) {
        console.error('Error fetching subjects:', error);
        alert('Failed to fetch subjects.');
      }
    },
    async addSubject() {
      try {
        // Ensure the correct data is sent to the backend
        const response = await axios.post('/api/admin/subjects', {
          name: this.subjectName,
          description: this.subjectDescription,
        }, {
          headers: { Authorization: `Bearer ${localStorage.getItem('auth_token')}` },
        });
        console.log('Response:', response.data);
        
        // Send notification about new subject
        const subjectId = response.data.subject?.id || response.data.id;
        if (subjectId) {
          await notificationService.notifyNewSubject(subjectId, this.subjectName);
        }
        
        alert(response.data.message);
        this.fetchSubjects();
        this.subjectName = '';
        this.subjectDescription = '';
        this.showForm = false;
      } catch (error) {
        console.error('Error adding subject:', error);
        alert(error.response?.data?.message || 'Failed to add subject.');
      }
    },
    async deleteSubject(id) {
      try {
        await axios.delete(`/api/subjects/${id}`, {
          headers: { Authorization: `Bearer ${localStorage.getItem('auth_token')}` },
        });
        this.fetchSubjects();
      } catch (error) {
        console.error('Error deleting subject:', error);
        alert('Failed to delete subject.');
      }
    },
  },
  created() {
    this.fetchSubjects();
  },
};
</script>

<style scoped>
/* Add any styling specific to this component here */
</style>
