<template>
  <div>
    <h3>Logging Out...</h3>
  </div>
</template>

<script>
export default {
  created() {
    // Clear all authentication data
    localStorage.removeItem('auth_token'); 
    localStorage.removeItem('user_id');
    localStorage.removeItem('username');
    localStorage.removeItem('user_type');
    
    // Redirect to the login page
    this.$router.push('/login');
  }
};
</script>
