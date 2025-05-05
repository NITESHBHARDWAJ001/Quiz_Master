<template>
  <div class="container py-4">
    <h1 class="display-5 fw-bold text-center mb-5">Quiz Subjects</h1>
    
    <div class="row row-cols-1 row-cols-md-2 row-cols-lg-3 g-4">
      <div v-for="subject in subjects" :key="subject.id" class="col">
        <div class="card h-100 shadow-sm subject-card">
          <div class="card-body">
            <h3 class="card-title fw-bold">{{ subject.name }}</h3>
            <p class="card-text">{{ subject.description }}</p>
          </div>
          <div class="card-footer bg-transparent border-0 d-flex justify-content-between align-items-center">
            <router-link 
              :to="{ name: 'chapters', params: { subjectId: subject.id }}" 
              class="btn btn-primary px-4"
            >
              <i class="bi bi-book me-2"></i>Explore Chapters
            </router-link>
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
  name: 'SubjectsPage',
  data() {
    return {
      subjects: [],
      loading: true,
      error: null
    };
  },
  created() {
    this.fetchSubjects();
  },
  methods: {
    async fetchSubjects() {
      try {
        this.loading = true;
        // Use auth_token instead of access_token
        const token = localStorage.getItem('auth_token');
        
        // Use axios instance from your configuration 
        // Remove hardcoded URL to avoid CORS issues
        const response = await axios.get('/api/subjects', {
          headers: { Authorization: `Bearer ${token}` }
        });
        
        this.subjects = response.data;
        this.loading = false;
      } catch (error) {
        console.error('Error fetching subjects:', error);
        this.error = 'Failed to load subjects. Please try again later.';
        this.loading = false;
      }
    }
  }
};
</script>

<style scoped>
.subject-card {
  transition: transform 0.3s ease, box-shadow 0.3s ease;
  border-radius: 10px;
  overflow: hidden;
}

.subject-card:hover {
  transform: translateY(-5px);
  box-shadow: 0 10px 20px rgba(0, 0, 0, 0.1) !important;
}

.card-title {
  color: #4a6bdf;
}

.card-footer {
  padding: 1rem;
}
</style>