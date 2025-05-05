<template>
    <div class="container my-4">
      <!-- Chapter Name -->
      <div class="text-center mb-5">
        <h2 class="text-success">{{ chapter.name }}</h2>
        <p class="text-muted">{{ chapter.description }}</p>
      </div>
  
      <!-- Quizzes List -->
      <div v-if="quizzes.length > 0">
        <h4 class="mb-4 text-primary">Quizzes in this Chapter:</h4>
        <div v-for="quiz in quizzes" :key="quiz.id" class="mb-4 border rounded p-4 shadow-sm">
          <div class="d-flex justify-content-between">
            <h5 class="text-info">{{ quiz.title }}</h5>
            <div>
              <button @click="editQuiz(quiz.id)" class="btn btn-warning me-2">Edit Quiz</button>
              <button @click="deleteQuiz(quiz.id)" class="btn btn-danger">Delete Quiz</button>
            </div>
          </div>
          <p class="text-muted">{{ quiz.description }}</p>
          <p><strong>Number of Questions: </strong>{{ quiz.numberOfQuestions }}</p>
          <p><strong>Quiz Duration: </strong>{{ quiz.duration }} minutes</p>
        </div>
      </div>
      <div v-else>
        <p class="text-center text-warning">No quizzes available for this chapter.</p>
      </div>
  
      <!-- Add New Quiz Button -->
      <div class="text-center mt-4">
        <button @click="addNewQuiz" class="btn btn-success">Add New Quiz</button>
      </div>
  
      <!-- Go Back Button -->
      <div class="text-center mt-3">
        <button @click="goBack" class="btn btn-secondary">Go Back</button>
      </div>
    </div>
  </template>
  
  <script>
  export default {
    data() {
      return {
        chapter: {
          id: 1, // Example chapter ID
          name: 'Introduction to Data Structures',
          description: 'This chapter covers basic data structures and algorithms.',
        },
        quizzes: [
          { id: 1, title: 'Quiz 1', description: 'Basic Data Structures', numberOfQuestions: 10, duration: 20 },
          { id: 2, title: 'Quiz 2', description: 'Arrays and Lists', numberOfQuestions: 15, duration: 25 },
          { id: 3, title: 'Quiz 3', description: 'Stacks and Queues', numberOfQuestions: 12, duration: 20 },
        ],
      };
    },
    methods: {
      // Edit Quiz Function (Redirect to edit page)
      editQuiz(quizId) {
        this.$router.push(`/edit-quiz/${quizId}`);
      },
      // Delete Quiz Function
      deleteQuiz(quizId) {
        // Ideally you would call an API to delete the quiz
        if (confirm('Are you sure you want to delete this quiz?')) {
          this.quizzes = this.quizzes.filter(quiz => quiz.id !== quizId);
          alert('Quiz deleted successfully!');
        }
      },
      // Go back function
      goBack() {
        this.$router.push('/admin-dashboard'); // Redirect to dashboard or previous page
      },
      // Add new quiz function
      addNewQuiz() {
        this.$router.push(`/add-quiz/${this.chapter.id}`);
      },
    },
  };
  </script>
  
  <style scoped>
  /* Styling for the page */
  .container {
    background-color: #f4f7fa; /* Light grey background */
    border-radius: 10px;
    box-shadow: 0 4px 8px rgba(0, 0, 0, 0.1);
  }
  
  h2 {
    color: #4CAF50; /* Green color for the chapter name */
    font-weight: bold;
  }
  
  h5 {
    color: #007bff; /* Vibrant blue for quiz titles */
  }
  
  p {
    color: #555; /* Dark gray for text */
  }
  
  .text-center {
    text-align: center;
  }
  
  /* Button styling */
  .btn {
    font-weight: bold;
  }
  
  .btn-warning {
    background-color: #ffcc00; /* Yellow color for edit button */
    border-color: #ffcc00;
  }
  
  .btn-danger {
    background-color: #f44336; /* Red color for delete button */
    border-color: #f44336;
  }
  
  .btn-success {
    background-color: #4caf50; /* Green color for adding new quiz */
    border-color: #4caf50;
  }
  
  .btn-secondary {
    background-color: #6c757d; /* Grey color for go back button */
    border-color: #6c757d;
  }
  
  /* Add some padding for quizzes */
  .mb-4 {
    margin-bottom: 1.5rem;
  }
  
  .border {
    border: 1px solid #ddd; /* Light border for each quiz */
  }
  </style>
  