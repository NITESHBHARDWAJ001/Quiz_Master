<template>
  <div class="container d-flex justify-content-center align-items-center py-5">
    <div class="card p-4 shadow-lg register-box">
      <h2 class="text-center mb-4">Create Account</h2>
      
      <!-- Registration Form -->
      <form @submit.prevent="registerUser">
        <!-- Full Name -->
        <div class="mb-3">
          <label class="form-label">Full Name</label>
          <input v-model="fullname" type="text" class="form-control" placeholder="Enter your full name" required />
        </div>

        <!-- Username -->
        <div class="mb-3">
          <label class="form-label">Username</label>
          <input v-model="username" type="text" class="form-control" placeholder="Choose a username" required />
        </div>

        <!-- Email -->
        <div class="mb-3">
          <label class="form-label">Email</label>
          <input v-model="email" type="email" class="form-control" placeholder="Enter your email" required />
        </div>

        <!-- Password -->
        <div class="mb-3">
          <label class="form-label">Password</label>
          <input v-model="password" type="password" class="form-control" placeholder="Create a password" required />
        </div>

        <!-- Confirm Password -->
        <div class="mb-3">
          <label class="form-label">Confirm Password</label>
          <input v-model="confirmPassword" type="password" class="form-control" placeholder="Confirm your password" required />
        </div>

        <!-- Qualification -->
        <div class="mb-3">
          <label class="form-label">Qualification</label>
          <input v-model="qualification" type="text" class="form-control" placeholder="Enter your qualification" required />
        </div>

        <!-- Self Description -->
        <div class="mb-3">
          <label class="form-label">Self Description (Optional)</label>
          <textarea v-model="selfDescription" class="form-control" placeholder="Tell us about yourself"></textarea>
        </div>

        <!-- Error Message -->
        <p v-if="errorMessage" class="text-danger text-center">{{ errorMessage }}</p>

        <!-- Submit Button -->
        <button type="submit" class="btn btn-primary w-100">Register</button>
      </form>

      <!-- Login Link -->
      <div class="mt-4 text-center">
        <p>Already have an account?</p>
        <router-link to="/login" class="btn btn-outline-secondary w-100">Login</router-link>
      </div>
    </div>
  </div>
</template>

<script>
import axios from '@/axios.js';

export default {
  data() {
    return {
      fullname: '',
      username: '',
      email: '',
      password: '',
      confirmPassword: '',
      qualification: '',
      selfDescription: '',
      errorMessage: '',
    };
  },
  methods: {
    async registerUser() {
      // Reset error message
      this.errorMessage = '';

      // Validate form
      if (!this.fullname || !this.username || !this.email || !this.password || !this.qualification) {
        this.errorMessage = 'All fields except Self Description are required';
        return;
      }

      // Validate password match
      if (this.password !== this.confirmPassword) {
        this.errorMessage = 'Passwords do not match';
        return;
      }

      try {
        // Make API request to register user
        const response = await axios.post('/api/register', {
          fullname: this.fullname,
          username: this.username,
          email: this.email,
          password: this.password,
          qualification: this.qualification,
          self_description: this.selfDescription || '',
        });

        // Show success message
        alert(response.data.message || 'Registration successful!');
        
        // Redirect to login page
        this.$router.push('/login');
      } catch (error) {
        console.error('Registration error:', error);
        this.errorMessage = error.response?.data?.message || 'Registration failed. Please try again.';
      }
    },
  },
};
</script>

<style scoped>
.register-box {
  max-width: 500px;
  width: 100%;
  border-radius: 10px;
  background: #fff;
  padding: 25px;
}
</style>
