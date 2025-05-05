<template>
  <div class="container py-5">
    <h2 class="text-center mb-4">Search Quizzes</h2>
    
    <div class="row justify-content-center mb-5">
      <div class="col-md-8">
        <form @submit.prevent="submitSearch" class="search-form">
          <div class="input-group input-group-lg">
            <input 
              type="text" 
              class="form-control" 
              placeholder="Search by subject, chapter or quiz..." 
              v-model="searchQuery" 
              aria-label="Search query"
            />
            <button class="btn btn-primary" type="submit">
              <i class="bi bi-search me-2"></i> Search
            </button>
          </div>
          <div class="form-text text-center mt-2">
            Enter keywords to find subjects, chapters, or quizzes
          </div>
        </form>
      </div>
    </div>

    <div v-if="submitted" class="text-center">
      <div class="spinner-border text-primary" role="status" v-if="loading">
        <span class="visually-hidden">Loading...</span>
      </div>
      <p v-else>
        <router-link 
          :to="{ path: '/search-results', query: { q: searchQuery } }" 
          class="btn btn-outline-primary"
        >
          View all results for "{{ searchQuery }}"
        </router-link>
      </p>
    </div>

    <!-- Popular Searches Section -->
    <div v-if="!submitted || (!loading && popularItems.length > 0)" class="mt-5">
      <h3 class="text-center mb-4">Popular Topics</h3>
      <div class="row row-cols-1 row-cols-md-3 g-4">
        <div v-for="item in popularItems" :key="item.id" class="col">
          <div class="card h-100 shadow-sm">
            <div class="card-body text-center">
              <div class="mb-3">
                <i :class="'bi ' + item.icon + ' fs-1 text-' + item.color"></i>
              </div>
              <h4 class="card-title">{{ item.name }}</h4>
              <p class="card-text">{{ item.description }}</p>
            </div>
            <div class="card-footer bg-transparent border-0">
              <router-link :to="item.link" class="btn btn-outline-primary w-100">
                Explore
              </router-link>
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
  name: "SearchPage",
  data() {
    return {
      searchQuery: '',
      submitted: false,
      loading: false,
      popularItems: [
        {
          id: 1,
          name: "Mathematics",
          description: "Explore quizzes on algebra, calculus, and geometry.",
          icon: "bi-calculator",
          color: "primary",
          link: "/search-results?q=mathematics"
        },
        {
          id: 2,
          name: "Science",
          description: "Test your knowledge on physics, chemistry, and biology.",
          icon: "bi-lightbulb",
          color: "success",
          link: "/search-results?q=science"
        },
        {
          id: 3,
          name: "Computer Science",
          description: "Challenge yourself with programming and algorithms quizzes.",
          icon: "bi-laptop",
          color: "info",
          link: "/search-results?q=computer science"
        }
      ]
    };
  },
  methods: {
    submitSearch() {
      if (this.searchQuery.trim()) {
        this.submitted = true;
        this.loading = true;
        
        // Simulate API call
        setTimeout(() => {
          this.loading = false;
          this.$router.push({
            path: '/search-results',
            query: { q: this.searchQuery }
          });
        }, 500);
      }
    }
  }
};
</script>

<style scoped>
.search-form {
  max-width: 700px;
  margin: 0 auto;
}

.card {
  transition: transform 0.3s ease, box-shadow 0.3s ease;
  border-radius: 12px;
}

.card:hover {
  transform: translateY(-5px);
  box-shadow: 0 10px 20px rgba(0, 0, 0, 0.1) !important;
}
</style>
