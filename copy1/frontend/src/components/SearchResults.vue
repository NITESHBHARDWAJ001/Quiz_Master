<template>
  <div class="search-results container py-4">
    <h2 class="mb-4">Search Results</h2>

    <!-- Search information -->
    <div class="alert alert-info">
      <span v-if="isLoading"><i class="bi bi-hourglass-split me-2"></i>Searching...</span>
      <span v-else>
        <i class="bi bi-search me-2"></i>
        Found {{ totalResults }} results for "{{ searchQuery }}" 
        <span v-if="searchType !== 'all'">in {{ searchType }}</span>
      </span>
    </div>

    <!-- Loading spinner -->
    <div v-if="isLoading" class="text-center py-5">
      <div class="spinner-border text-primary" role="status">
        <span class="visually-hidden">Loading...</span>
      </div>
    </div>

    <!-- No results message -->
    <div v-else-if="!isLoading && totalResults === 0" class="alert alert-warning">
      <i class="bi bi-exclamation-triangle me-2"></i>
      No results found for "{{ searchQuery }}". Try a different search term.
    </div>

    <!-- Results display -->
    <div v-else>
      <!-- Filter tabs if there are results in multiple categories -->
      <ul class="nav nav-tabs mb-4" v-if="hasCategorizedResults">
        <li class="nav-item">
          <a class="nav-link" :class="{ active: activeTab === 'all' }" href="#" @click.prevent="activeTab = 'all'">
            All ({{ totalResults }})
          </a>
        </li>
        <li class="nav-item" v-if="results.subjects && results.subjects.length > 0">
          <a class="nav-link" :class="{ active: activeTab === 'subjects' }" href="#" @click.prevent="activeTab = 'subjects'">
            Subjects ({{ results.subjects.length }})
          </a>
        </li>
        <li class="nav-item" v-if="results.chapters && results.chapters.length > 0">
          <a class="nav-link" :class="{ active: activeTab === 'chapters' }" href="#" @click.prevent="activeTab = 'chapters'">
            Chapters ({{ results.chapters.length }})
          </a>
        </li>
        <li class="nav-item" v-if="results.quizzes && results.quizzes.length > 0">
          <a class="nav-link" :class="{ active: activeTab === 'quizzes' }" href="#" @click.prevent="activeTab = 'quizzes'">
            Quizzes ({{ results.quizzes.length }})
          </a>
        </li>
        <li class="nav-item" v-if="isAdmin && results.users && results.users.length > 0">
          <a class="nav-link" :class="{ active: activeTab === 'users' }" href="#" @click.prevent="activeTab = 'users'">
            Users ({{ results.users.length }})
          </a>
        </li>
      </ul>

      <!-- Results list -->
      <div class="row row-cols-1 row-cols-md-2 g-4">
        <div v-for="(item, index) in filteredResults" :key="index" class="col">
          <div class="card h-100 result-card">
            <div class="card-body">
              <!-- Different display for different result types -->
              <!-- Subject result -->
              <div v-if="item.type === 'subject'">
                <h5 class="card-title">
                  <i class="bi bi-book me-2 text-primary"></i>
                  {{ item.name }}
                </h5>
                <p class="card-text">{{ item.description }}</p>
                <router-link :to="{ name: 'chapters', params: { subjectId: item.id }}" class="btn btn-primary">
                  <i class="bi bi-arrow-right me-1"></i>View Chapters
                </router-link>
              </div>

              <!-- Chapter result -->
              <div v-else-if="item.type === 'chapter'">
                <h5 class="card-title">
                  <i class="bi bi-journal-text me-2 text-success"></i>
                  {{ item.chapter_name }}
                </h5>
                <p class="card-text">{{ item.description }}</p>
                <p class="card-text"><small class="text-muted">Subject: {{ item.subject_name }}</small></p>
                <router-link :to="{ name: 'user-quizzes', params: { chapterId: item.id }}" class="btn btn-success">
                  <i class="bi bi-arrow-right me-1"></i>View Quizzes
                </router-link>
              </div>

              <!-- Quiz result -->
              <div v-else-if="item.type === 'quiz'">
                <h5 class="card-title">
                  <i class="bi bi-question-circle me-2 text-warning"></i>
                  {{ item.quiz_name }}
                </h5>
                <p class="card-text"><small class="text-muted">Time: {{ item.timing }} minutes</small></p>
                <p class="card-text"><small class="text-muted">Chapter: {{ item.chapter_name }}</small></p>
                <router-link :to="{ name: 'quiz-attempt', params: { quizId: item.id }}" class="btn btn-warning">
                  <i class="bi bi-play-fill me-1"></i>Take Quiz
                </router-link>
              </div>

              <!-- User result (admin only) -->
              <div v-else-if="item.type === 'user' && isAdmin">
                <h5 class="card-title">
                  <i class="bi bi-person me-2 text-info"></i>
                  {{ item.fullname }}
                </h5>
                <p class="card-text">Username: {{ item.username }}</p>
                <p class="card-text">Email: {{ item.email }}</p>
                <p class="card-text"><small class="text-muted">Qualification: {{ item.qualification }}</small></p>
                <router-link :to="`/user-profile/${item.id}`" class="btn btn-info">
                  <i class="bi bi-eye me-1"></i>View Profile
                </router-link>
              </div>
            </div>
          </div>
        </div>
      </div>

      <!-- Pagination -->
      <nav v-if="totalPages > 1" class="mt-4">
        <ul class="pagination justify-content-center">
          <li class="page-item" :class="{ disabled: currentPage === 1 }">
            <a class="page-link" href="#" @click.prevent="changePage(currentPage - 1)">Previous</a>
          </li>
          <li v-for="page in pageNumbers" :key="page" class="page-item" :class="{ active: currentPage === page }">
            <a class="page-link" href="#" @click.prevent="changePage(page)">{{ page }}</a>
          </li>
          <li class="page-item" :class="{ disabled: currentPage === totalPages }">
            <a class="page-link" href="#" @click.prevent="changePage(currentPage + 1)">Next</a>
          </li>
        </ul>
      </nav>
    </div>

    <!-- Search metadata for debugging -->
    <div v-if="debug" class="mt-5 p-3 bg-light border rounded small">
      <h6>Search Metadata:</h6>
      <pre>{{ JSON.stringify(results.meta || {}, null, 2) }}</pre>
      <h6>Query Parameters:</h6>
      <pre>{{ JSON.stringify($route.query, null, 2) }}</pre>
      <h6>Result Structure:</h6>
      <pre>{{ JSON.stringify({
        all: Array.isArray(results.all) ? results.all.length : 'not array',
        subjects: Array.isArray(results.subjects) ? results.subjects.length : 'not array',
        chapters: Array.isArray(results.chapters) ? results.chapters.length : 'not array',
        quizzes: Array.isArray(results.quizzes) ? results.quizzes.length : 'not array',
        users: Array.isArray(results.users) ? results.users.length : 'not array',
      }, null, 2) }}</pre>
    </div>
  </div>
</template>

<script>
import axios from '@/axios.js';

export default {
  name: 'SearchResults',
  data() {
    return {
      searchQuery: '',
      searchType: 'all',
      results: {
        subjects: [],
        chapters: [],
        quizzes: [],
        users: [],
        all: [],
        meta: {}
      },
      isLoading: true,
      activeTab: 'all',
      currentPage: 1,
      itemsPerPage: 10,
      pollInterval: null,
      taskId: null,
      debug: true, // Enable debugging
      error: null
    };
  },
  computed: {
    isAdmin() {
      return localStorage.getItem('user_type') === 'admin';
    },
    totalResults() {
      // Safely get the length of all results
      return Array.isArray(this.results.all) ? this.results.all.length : 0;
    },
    hasCategorizedResults() {
      // Check if we have results in more than one category
      let categories = 0;
      if (Array.isArray(this.results.subjects) && this.results.subjects.length > 0) categories++;
      if (Array.isArray(this.results.chapters) && this.results.chapters.length > 0) categories++;
      if (Array.isArray(this.results.quizzes) && this.results.quizzes.length > 0) categories++;
      if (this.isAdmin && Array.isArray(this.results.users) && this.results.users.length > 0) categories++;
      return categories > 1;
    },
    filteredResults() {
      // Get results based on active tab
      let items = [];
      if (this.activeTab === 'all') {
        items = Array.isArray(this.results.all) ? this.results.all : [];
      } else {
        items = Array.isArray(this.results[this.activeTab]) ? this.results[this.activeTab] : [];
      }
      
      // Apply pagination
      const startIndex = (this.currentPage - 1) * this.itemsPerPage;
      const endIndex = startIndex + this.itemsPerPage;
      return items.slice(startIndex, endIndex);
    },
    totalPages() {
      let items = [];
      if (this.activeTab === 'all') {
        items = Array.isArray(this.results.all) ? this.results.all : [];
      } else {
        items = Array.isArray(this.results[this.activeTab]) ? this.results[this.activeTab] : [];
      }
      return Math.ceil(items.length / this.itemsPerPage) || 1;
    },
    pageNumbers() {
      const pages = [];
      const maxButtons = 5; // Show up to 5 page buttons
      
      if (this.totalPages <= maxButtons) {
        // Show all pages if total is less than max buttons
        for (let i = 1; i <= this.totalPages; i++) {
          pages.push(i);
        }
      } else {
        // Show first page, current page - 1, current page, current page + 1, last page
        pages.push(1);
        
        const startPage = Math.max(2, this.currentPage - 1);
        const endPage = Math.min(this.totalPages - 1, this.currentPage + 1);
        
        if (startPage > 2) pages.push('...');
        
        for (let i = startPage; i <= endPage; i++) {
          pages.push(i);
        }
        
        if (endPage < this.totalPages - 1) pages.push('...');
        
        pages.push(this.totalPages);
      }
      
      return pages;
    }
  },
  watch: {
    // Watch for route changes to update search
    '$route.query': {
      handler(newQuery) {
        console.log('Route query changed:', newQuery);
        this.searchQuery = newQuery.q || '';
        this.searchType = newQuery.type || 'all';
        if (this.searchQuery) {
          this.performSearch();
        } else {
          // If no search query, reset results
          this.resetResults();
        }
      },
      immediate: true
    }
  },
  methods: {
    resetResults() {
      this.results = {
        subjects: [],
        chapters: [],
        quizzes: [],
        users: [],
        all: [],
        meta: {}
      };
      this.isLoading = false;
    },
    async performSearch() {
      if (!this.searchQuery) {
        this.resetResults();
        return;
      }
      
      console.log('Performing search for:', this.searchQuery, 'type:', this.searchType);
      this.isLoading = true;
      this.activeTab = 'all';
      this.currentPage = 1;
      this.error = null;
      
      try {
        // Get auth token for headers
        const token = localStorage.getItem('auth_token');
        console.log('Using auth token:', token ? 'Yes (authenticated)' : 'No');
        
        // Determine if we should use async search
        const useAsync = this.$route.query.async === 'true';
        console.log('Using async search:', useAsync);
        
        // Make API request for search
        console.log('Making search request to /api/search');
        const response = await axios.get('/api/search', {
          params: {
            q: this.searchQuery,
            type: this.searchType,
            async: useAsync,
            page: 1,
            per_page: 100 // Get more results initially
          },
          headers: token ? { Authorization: `Bearer ${token}` } : {}
        });
        
        console.log('Search response received:', response.data);
        
        // Ensure the response has the expected structure
        const data = response.data || {};
        this.results = {
          subjects: Array.isArray(data.subjects) ? data.subjects : [],
          chapters: Array.isArray(data.chapters) ? data.chapters : [],
          quizzes: Array.isArray(data.quizzes) ? data.quizzes : [],
          users: Array.isArray(data.users) ? data.users : [],
          all: Array.isArray(data.all) ? data.all : [],
          meta: data.meta || {}
        };
        
        // Check if results are properly structured
        console.log('Processed search results:', {
          subjects: this.results.subjects.length,
          chapters: this.results.chapters.length,
          quizzes: this.results.quizzes.length,
          users: this.results.users.length,
          all: this.results.all.length
        });
        
        // If async and task ID provided, start polling
        if (useAsync && data.meta && data.meta.task_id) {
          this.taskId = data.meta.task_id;
          console.log('Starting polling for task:', this.taskId);
          this.startPolling();
        } else {
          this.isLoading = false;
        }
      } catch (error) {
        console.error('Search error:', error);
        this.error = error.response?.data?.message || 'Search failed';
        this.isLoading = false;
        
        // Initialize empty results structure on error
        this.results = {
          subjects: [],
          chapters: [],
          quizzes: [],
          users: [],
          all: [],
          meta: { error: this.error }
        };
      }
    },
    startPolling() {
      // Poll for async search results
      if (!this.taskId) return;
      
      this.pollInterval = setInterval(async () => {
        try {
          console.log('Polling for task results:', this.taskId);
          const response = await axios.get(`/api/search/task/${this.taskId}`);
          
          if (response.data.status === 'success') {
            // Success - update results and stop polling
            console.log('Task completed successfully:', response.data);
            
            // Ensure the results have the expected structure
            const data = response.data.results || {};
            this.results = {
              subjects: Array.isArray(data.subjects) ? data.subjects : [],
              chapters: Array.isArray(data.chapters) ? data.chapters : [],
              quizzes: Array.isArray(data.quizzes) ? data.quizzes : [],
              users: Array.isArray(data.users) ? data.users : [],
              all: Array.isArray(data.all) ? data.all : [],
              meta: data.meta || {}
            };
            
            this.isLoading = false;
            this.stopPolling();
          } else if (response.data.status !== 'pending') {
            // Error or other status - stop polling
            console.warn('Search task status:', response.data.status);
            this.error = response.data.message || 'Task failed';
            this.isLoading = false;
            this.stopPolling();
          }
        } catch (error) {
          console.error('Error polling search task:', error);
          this.error = error.response?.data?.message || 'Error checking task status';
          this.isLoading = false;
          this.stopPolling();
        }
      }, 1000); // Poll every 1 second
    },
    stopPolling() {
      if (this.pollInterval) {
        clearInterval(this.pollInterval);
        this.pollInterval = null;
      }
    },
    changePage(page) {
      if (page >= 1 && page <= this.totalPages) {
        this.currentPage = page;
        window.scrollTo(0, 0); // Scroll to top when page changes
      }
    }
  },
  mounted() {
    console.log('SearchResults component mounted');
    // Initial search if query is in URL
    if (this.searchQuery) {
      this.performSearch();
    } else {
      this.isLoading = false;
    }
  },
  beforeUnmount() {
    this.stopPolling(); // Clean up polling interval
  }
};
</script>

<style scoped>
.search-results {
  min-height: 60vh;
}

.result-card {
  transition: transform 0.2s ease, box-shadow 0.2s ease;
  border-radius: 10px;
  overflow: hidden;
}

.result-card:hover {
  transform: translateY(-5px);
  box-shadow: 0 10px 20px rgba(0, 0, 0, 0.1);
}

.card-title {
  color: #4a6bdf;
  font-weight: 600;
}

/* Pagination styles */
.pagination .page-link {
  color: #4a6bdf;
}

.pagination .page-item.active .page-link {
  background-color: #4a6bdf;
  border-color: #4a6bdf;
}

/* Tab styles */
.nav-tabs .nav-link {
  color: #6c757d;
}

.nav-tabs .nav-link.active {
  color: #4a6bdf;
  font-weight: 600;
  border-bottom-color: #4a6bdf;
}
</style>
