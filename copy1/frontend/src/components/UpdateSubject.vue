<template>
  <div class="container mt-4">
    <div class="d-flex justify-content-between align-items-center mb-4">
      <h2>Update Subject: {{ subject.name }}</h2>
      <button class="btn btn-secondary" @click="$router.push('/AdminDashboard')">Back to Dashboard</button>
    </div>

    <!-- Subject Update Form -->
    <div class="card shadow mb-4">
      <div class="card-header bg-primary text-white">
        <h4>Edit Subject Details</h4>
      </div>
      <div class="card-body">
        <form @submit.prevent="updateSubject">
          <div class="form-group mb-3">
            <label for="subjectName">Subject Name</label>
            <input type="text" id="subjectName" v-model="subject.name" class="form-control" required />
          </div>
          <div class="form-group mb-3">
            <label for="subjectDescription">Description</label>
            <textarea id="subjectDescription" v-model="subject.description" class="form-control" rows="3" required></textarea>
          </div>
          <button type="submit" class="btn btn-success">Update Subject</button>
        </form>
      </div>
    </div>

    <!-- Chapters Management Section -->
    <div class="card shadow">
      <div class="card-header bg-info text-white d-flex justify-content-between align-items-center">
        <h4 class="m-0">Chapters</h4>
        <button class="btn btn-light" @click="navigateToAddChapter()">+ Add Chapter</button>
      </div>
      <div class="card-body">
        <!-- Loading State -->
        <div v-if="loading" class="text-center p-3">
          <p>Loading chapters...</p>
        </div>

        <!-- No Chapters State -->
        <div v-else-if="chapters.length === 0" class="alert alert-info">
          No chapters found for this subject. Add your first chapter!
        </div>

        <!-- Chapters List -->
        <div v-else class="table-responsive">
          <table class="table table-striped">
            <thead>
              <tr>
                <th>Chapter Name</th>
                <th>Description</th>
                <th>Actions</th>
              </tr>
            </thead>
            <tbody>
              <tr v-for="chapter in chapters" :key="chapter.id">
                <td>{{ chapter.chapter_name }}</td>
                <td>{{ chapter.description }}</td>
                <td>
                  <div class="btn-group">
                    <button class="btn btn-sm btn-info me-2" @click="navigateToManageQuizzes(chapter.id)">
                      Manage Quizzes
                    </button>
                    <button class="btn btn-sm btn-warning me-2" @click="editChapter(chapter)">
                      Edit
                    </button>
                    <button class="btn btn-sm btn-danger" @click="deleteChapter(chapter.id)">
                      Delete
                    </button>
                  </div>
                </td>
              </tr>
            </tbody>
          </table>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import axios from '@/axios.js';

export default {
  props: {
    id: {
      type: [Number, String],
      required: true
    }
  },
  data() {
    return {
      subject: {
        id: null,
        name: '',
        description: ''
      },
      chapters: [],
      loading: true,
      error: null,
      editingChapter: null,
      showEditModal: false
    };
  },
  methods: {
    async fetchSubject() {
      try {
        const response = await axios.get(`/api/subjects/${this.id}`);
        this.subject = response.data;
      } catch (error) {
        console.error('Error fetching subject:', error);
        this.error = 'Failed to fetch subject details';
      }
    },
    async fetchChapters() {
      try {
        this.loading = true;
        const response = await axios.get(`/api/subjects/${this.id}/chapters`);
        this.chapters = response.data.chapters;
      } catch (error) {
        console.error('Error fetching chapters:', error);
        this.error = 'Failed to fetch chapters';
      } finally {
        this.loading = false;
      }
    },
    async updateSubject() {
      try {
        await axios.put(`/api/subjects/${this.id}`, this.subject);
        alert('Subject updated successfully!');
      } catch (error) {
        console.error('Error updating subject:', error);
        alert('Failed to update subject: ' + (error.response?.data?.message || error.message));
      }
    },
    navigateToAddChapter() {
      // Log ID for debugging
      console.log('Current ID prop:', this.id);
      console.log('Current route params:', this.$route.params);
      
      // Get ID directly from route params if needed
      const subjectId = this.id || this.$route.params.id;
      console.log('Using subject ID for navigation:', subjectId);
      
      // Use plain string for navigation to avoid any object conversion issues
      this.$router.push('/subjects/' + subjectId + '/add-chapter');
    },
    navigateToManageQuizzes(chapterId) {
      console.log(`Navigating to manage quizzes for chapter ID: ${chapterId}, subject ID: ${this.id}`);
      this.$router.push(`/admin/quizzes/${this.id}/${chapterId}`);
    },
    editChapter(chapter) {
      this.editingChapter = { ...chapter };
      this.showEditModal = true;
    },
    async deleteChapter(chapterId) {
      if (confirm('Are you sure you want to delete this chapter?')) {
        try {
          await axios.delete(`/api/chapters/${chapterId}`);
          alert('Chapter deleted successfully!');
          this.fetchChapters();
        } catch (error) {
          console.error('Error deleting chapter:', error);
          alert('Failed to delete chapter: ' + (error.response?.data?.message || error.message));
        }
      }
    }
  },
  created() {
    console.log('UpdateSubject component created with ID:', this.id);
    this.fetchSubject();
    this.fetchChapters();
  }
};
</script>

<style scoped>
.card {
  border-radius: 10px;
  overflow: hidden;
}

.card-header {
  font-weight: bold;
}

.btn-group .btn {
  margin-right: 5px;
}

.table-responsive {
  overflow-x: auto;
}
</style>
