<template>
    <div>
      <h4>User Performance</h4>
      <ul>
        <li v-for="user in users" :key="user.id">
          {{ user.username }}
          <button @click="viewPerformance(user.id)">View Performance</button>
        </li>
      </ul>
    </div>
  </template>
  
  <script>
  import apiClient from '@/axios';
  
  export default {
    data() {
      return {
        users: [],
      };
    },
    methods: {
      async fetchUsers() {
        try {
          const response = await apiClient.get('/users');
          this.users = response.data;
        } catch (error) {
          console.error('Error fetching users:', error);
        }
      },
      async viewPerformance(userId) {
        try {
          const response = await apiClient.get(`/performance/${userId}`);
          console.log('User performance:', response.data);
          // You can display the performance data here.
        } catch (error) {
          console.error('Error fetching performance:', error);
        }
      },
    },
    created() {
      this.fetchUsers();
    },
  };
  </script>
  