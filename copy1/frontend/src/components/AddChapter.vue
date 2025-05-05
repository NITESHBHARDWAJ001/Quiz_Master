<template>
  <div class="container mt-4">
    <div class="card shadow">
      <div class="card-header bg-primary text-white d-flex justify-content-between align-items-center">
        <h3>Add New Chapter to {{ subjectName }}</h3>
        <button class="btn btn-light" @click="goBack">Back</button>
      </div>
      <div class="card-body">
        <form @submit.prevent="addChapter">
          <div class="form-group mb-3">
            <label for="chapterName">Chapter Name</label>
            <input 
              type="text" 
              id="chapterName" 
              v-model="chapter.chapter_name" 
              class="form-control" 
              placeholder="Enter chapter name"
              required 
            />
          </div>
          
          <div class="form-group mb-3">
            <label for="chapterDescription">Description</label>
            <textarea 
              id="chapterDescription" 
              v-model="chapter.description" 
              class="form-control" 
              rows="5"
              placeholder="Enter chapter description"
              required
            ></textarea>
          </div>
          
          <div class="d-flex justify-content-between mt-4">
            <button type="button" class="btn btn-secondary" @click="goBack">Cancel</button>
            <button type="submit" class="btn btn-success">Save Chapter</button>
          </div>
        </form>
      </div>
    </div>
  </div>
</template>

<script>
import axios from '@/axios.js';

export default {
  props: {
    subjectId: {
      type: [Number, String],
      required: false // Make it not required so we can fetch from route
    }
  },
  data() {
    return {
      subjectName: '',
      chapter: {
        chapter_name: '',
        description: ''
      },
      loading: false,
      error: null
    };
  },
  computed: {
    // Simplified computed property to get subject ID from either props or route
    validSubjectId() {
      // First try to get ID from route params
      const routeId = this.$route.params.subjectId;
      if (routeId) {
        console.log("Using subject ID from route params:", routeId);
        return routeId;
      }
      
      // Then try props
      if (this.subjectId) {
        console.log("Using subject ID from props:", this.subjectId);
        return this.subjectId;
      }
      
      console.error("Could not determine subject ID");
      return null;
    }
  },
  methods: {
    async fetchSubjectInfo() {
      try {
        const id = this.validSubjectId;
        console.log("Fetching subject info for ID:", id);
        
        if (!id) {
          this.error = "No subject ID found";
          this.subjectName = "Unknown Subject";
          return;
        }
        
        const response = await axios.get(`/api/subjects/${id}`);
        console.log("Subject data received:", response.data);
        this.subjectName = response.data.name || 'Unknown Subject';
      } catch (error) {
        console.error('Error fetching subject info:', error);
        this.error = 'Failed to load subject information';
        this.subjectName = 'Unknown Subject';
      }
    },
    async addChapter() {
      this.loading = true;
      try {
        const id = this.validSubjectId;
        
        if (!id) {
          alert('No subject ID found. Cannot add chapter.');
          this.loading = false;
          return;
        }
        
        console.log(`Adding chapter to subject ID: ${id}`);
        console.log('Chapter data:', this.chapter);
        
        const response = await axios.post(`/api/subjects/${id}/chapters`, this.chapter);
        
        console.log('Chapter added:', response.data);
        
        // Trigger notification emails about the new chapter
        try {
          const chapterId = response.data.chapter.id || response.data.id;
          await axios.post('/api/admin/notify-chapter', {
            chapterId,
            chapterName: this.chapter.chapter_name,
            subjectId: id,
            autoTriggered: true
          });
          console.log('Chapter notification emails triggered successfully');
        } catch (notifyError) {
          console.error('Error sending chapter notifications:', notifyError);
          // Continue with normal flow even if notification fails
        }
        
        alert('Chapter added successfully!');
        
        // Clear form after successful submission
        this.chapter = {
          chapter_name: '',
          description: ''
        };
        
        // Navigate back using the validated ID
        this.$router.push(`/update-subject/${id}`);
      } catch (error) {
        // More detailed error logging
        console.error('Error adding chapter:', error);
        if (error.response) {
          console.error('Response data:', error.response.data);
          console.error('Response status:', error.response.status);
        }
        alert(error.response?.data?.message || 'Failed to add chapter');
      } finally {
        this.loading = false;
      }
    },
    goBack() {
      // Navigate back using the validated ID
      const id = this.validSubjectId;
      this.$router.push(`/update-subject/${id || ''}`);
    }
  },
  created() {
    console.log("AddChapter component created");
    console.log("Full route:", this.$route);
    console.log("Route path:", this.$route.path);
    console.log("Route params:", this.$route.params);
    
    // Extract ID from path as a fallback
    if (!this.validSubjectId) {
      const pathSegments = this.$route.path.split('/');
      const subjectsIndex = pathSegments.indexOf('subjects');
      if (subjectsIndex >= 0 && pathSegments.length > subjectsIndex + 1) {
        console.log("Extracted ID from path:", pathSegments[subjectsIndex + 1]);
      }
    }
    
    this.fetchSubjectInfo();
  },
  mounted() {
    console.log("Component mounted with subject ID:", this.subjectId);
    // If subject name is still empty after mounting, try fetching again
    if (!this.subjectName) {
      this.fetchSubjectInfo();
    }
  }
};
</script>

<style scoped>
.card {
  border: none;
  border-radius: 10px;
  box-shadow: 0 4px 8px rgba(0, 0, 0, 0.1);
}

.card-header {
  border-radius: 10px 10px 0 0;
  padding: 15px 20px;
}

.form-group label {
  font-weight: 500;
  margin-bottom: 8px;
}

.form-control:focus {
  box-shadow: 0 0 0 0.2rem rgba(0, 123, 255, 0.25);
  border-color: #80bdff;
}

button {
  padding: 8px 20px;
}

button.btn-success {
  background-color: #28a745;
  border-color: #28a745;
}

button.btn-success:hover {
  background-color: #218838;
  border-color: #1e7e34;
}
</style>
