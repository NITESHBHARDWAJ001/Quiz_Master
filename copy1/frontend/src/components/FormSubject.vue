<template>
  <div class="subject-form-container">
    <div class="card shadow-lg">
      <div class="card-header bg-primary text-white">
        <h3 class="mb-0">Add New Subject</h3>
      </div>
      <div class="card-body">
        <form @submit.prevent="submitForm">
          <!-- Subject Name -->
          <div class="mb-3">
            <label for="name" class="form-label">Subject Name</label>
            <input type="text" id="name" class="form-control" v-model="name" required />
          </div>

          <!-- Description -->
          <div class="mb-3">
            <label for="description" class="form-label">Description</label>
            <textarea id="description" class="form-control" rows="4" v-model="description" required></textarea>
          </div>

          <!-- Buttons -->
          <div class="d-flex justify-content-end">
            <button type="submit" class="btn btn-success me-2">Submit</button>
            <button type="button" class="btn btn-secondary" @click="closeForm">Cancel</button>
          </div>
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
      name: '',
      description: '',
    };
  },
  methods: {
    async submitForm() {
      try {
        console.log("Submitting form with data:", { name: this.name, description: this.description });
        const response = await axios.post('/api/subjects', {
          name: this.name,
          description: this.description,
        }, {
          headers: {
            'Content-Type': 'application/json', // Ensure JSON content type
            Authorization: `Bearer ${localStorage.getItem('auth_token')}`, // Include JWT token
          },
        });
        console.log("Response from server:", response.data);
        
        // Send notification to users about the new subject
        try {
          await axios.post('/api/admin/notify-subject', {
            subjectId: response.data.subject.id || response.data.id,
            subjectName: this.name,
            autoTriggered: true
          });
          console.log('Subject notification emails triggered successfully');
        } catch (notifyError) {
          console.error('Error sending subject notifications:', notifyError);
          // Continue with normal flow even if notification fails
        }
        
        alert(response.data.message); // Show success message from the server
        this.$emit('close'); // Close the form
      } catch (error) {
        console.error('Error adding subject:', error);
        alert(error.response?.data?.message || 'Failed to add subject.'); // Show error message from the server
      }
    },
    closeForm() {
      this.$emit('close');
    },
  },
};
</script>

<style scoped>
.subject-form-container {
  max-width: 500px;
  margin: auto;
  padding-top: 20px;
}

.card {
  border-radius: 12px;
}

.card-header {
  font-weight: bold;
  text-align: center;
}

.form-label {
  font-weight: 600;
}

.btn {
  border-radius: 6px;
}
</style>
