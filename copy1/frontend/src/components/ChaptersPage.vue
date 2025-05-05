<template>
  <div class="container py-4">
    <div v-if="subject" class="mb-4">
      <div class="d-flex align-items-center">
        <router-link to="/quiz" class="btn btn-outline-secondary me-3">
          <i class="bi bi-arrow-left"></i> Back to Subjects
        </router-link>
        <h1 class="mb-0">{{ subject.name }}</h1>
      </div>
      <p class="lead mt-2">{{ subject.description }}</p>
    </div>

    <h2 class="fw-bold mb-4">Chapters</h2>
    
    <div class="row row-cols-1 row-cols-md-2 g-4">
      <div v-for="chapter in chapters" :key="chapter.id" class="col">
        <div class="card h-100 shadow-sm chapter-card">
          <div class="card-body">
            <h3 class="card-title">{{ chapter.chapter_name }}</h3>
            <p class="card-text">{{ chapter.description }}</p>
          </div>
          <div class="card-footer bg-transparent border-0">
            <router-link 
              :to="{ name: 'user-quizzes', params: { chapterId: chapter.id }}" 
              class="btn btn-primary w-100"
            >
              <i class="bi bi-journal-check me-2"></i>View Quizzes
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
  name: 'ChaptersPage',
  props: {
    subjectId: {
      type: [Number, String],
      required: true
    }
  },
  data() {
    return {
      subject: null,
      chapters: [],
      loading: true,
      error: null
    };
  },
  created() {
    this.fetchChapters(this.subjectId);
  },
  methods: {
    async fetchChapters(subjectId) {
      try {
        this.loading = true;
        const token = localStorage.getItem('auth_token');
        
        // Add debug call to check token
        try {
          const debugResponse = await axios.get("/api/debug-token");
          console.log("Token debug info:", debugResponse.data);
        } catch (err) {
          console.error("Token debug error:", err);
        }

        const response = await axios.get(`/api/subjects/${subjectId}/chapters`, {
          headers: { Authorization: `Bearer ${token}` }
        });
        
        this.subject = response.data.subject;
        this.chapters = response.data.chapters;
        this.loading = false;
      } catch (error) {
        console.error('Error fetching chapters:', error);
        this.error = 'Failed to load chapters. Please try again later.';
        this.loading = false;
      }
    }
  }
};
</script>

<style scoped>
.chapter-card {
  transition: transform 0.3s ease, box-shadow 0.3s ease;
  border-radius: 10px;
}

.chapter-card:hover {
  transform: translateY(-5px);
  box-shadow: 0 10px 20px rgba(0, 0, 0, 0.1) !important;
}

.card-title {
  color: #4a6bdf;
  font-weight: 600;
}
</style>