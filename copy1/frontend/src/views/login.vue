<template>
  <div class="container d-flex justify-content-center align-items-center vh-100">
    <div class="card p-4 shadow-lg login-box">
      <h2 class="text-center mb-4">Login</h2>
      <form @submit.prevent="loginUser">
        <!-- Email Input -->
        <div class="mb-3">
          <label class="form-label">Username</label>
          <input v-model="username" type="text" class="form-control" placeholder="Username" required />
        </div>

        <!-- Password Input -->
        <div class="mb-3">
          <label class="form-label">Password</label>
          <input v-model="password" type="password" class="form-control" placeholder="Enter password" required />
        </div>

        <!-- User Type Dropdown -->
        <div class="mb-3">
          <label class="form-label">User Type</label>
          <select v-model="userType" class="form-control" required>
            <option value="" disabled>Select user type</option>
            <option value="admin">Admin</option>
            <option value="user">User</option>
          </select>
        </div>

        <!-- Error Message -->
        <p v-if="errorMessage" class="text-danger text-center">{{ errorMessage }}</p>

        <!-- Submit Button -->
        <button type="submit" class="btn btn-primary w-100">Login</button>
      </form>

      <!-- Sign-up Section -->
      <div class="mt-4 text-center">
        <p>Don't have an account?</p>
        <router-link to="/register" class="btn btn-success w-100">Create New Account</router-link>
      </div>
    </div>
  </div>
</template>

<script>
import axios from "@/axios.js";

export default {
  data() {
    return {
      username: "",
      password: "",
      userType: "",
      errorMessage: "",
    };
  },
  methods: {
    async loginUser() {
      this.errorMessage = "";

      if (!this.username || !this.password || !this.userType) {
        this.errorMessage = "All fields are required!";
        return;
      }

      try {
        console.log('Logging in with:', { username: this.username, userType: this.userType });
        
        const response = await axios.post("/api/login", {
          username: this.username,
          password: this.password,
          userType: this.userType,
        });

        if (response.data.access_token) {
          console.log('Login successful:', response.data);
          
          // Store authentication token and user details
          // Make sure token is stored correctly without 'Bearer ' prefix
          const token = response.data.access_token;
          localStorage.setItem("auth_token", token);
          localStorage.setItem("user_id", response.data.user_id);
          localStorage.setItem("username", response.data.username);
          localStorage.setItem("user_type", response.data.user_type);

          console.log('Token saved:', localStorage.getItem("auth_token"));
          console.log('User type saved:', localStorage.getItem("user_type"));

          alert("Login successful!");

          // Redirect based on user type
          if (response.data.user_type === "admin") {
            this.$router.push("/AdminDashboard");
          } else {
            this.$router.push("/");
          }
        }
      } catch (error) {
        console.error('Login error:', error);
        this.errorMessage = error.response?.data?.message || "Login failed";
      }
    },
  },
};
</script>

<style scoped>
.login-box {
  max-width: 400px;
  width: 100%;
  border-radius: 10px;
  background: #fff;
  padding: 25px;
}

.btn-success {
  background-color: #28a745;
  border-color: #28a745;
}

.btn-success:hover {
  background-color: #218838;
  border-color: #1e7e34;
}
</style>
