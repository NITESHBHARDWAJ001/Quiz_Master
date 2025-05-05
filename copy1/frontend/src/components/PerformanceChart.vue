<template>
  <div class="performance-chart-container">
    <div class="chart-controls mb-4">
      <div class="row">
        <div class="col-md-6">
          <div class="form-group">
            <label for="chartType">Chart Type</label>
            <select id="chartType" v-model="selectedChartType" class="form-select">
              <option value="bar">Bar Chart</option>
              <option value="radar">Radar Chart</option>
              <option value="line">Line Chart</option>
            </select>
          </div>
        </div>
        <div class="col-md-6">
          <div class="form-group">
            <label for="filterSubject">Filter by Subject</label>
            <select id="filterSubject" v-model="selectedSubject" class="form-select">
              <option value="">All Subjects</option>
              <option v-for="subject in subjects" :key="subject.id" :value="subject.id">
                {{ subject.name }}
              </option>
            </select>
          </div>
        </div>
      </div>
    </div>

    <div v-if="loading" class="text-center py-5">
      <div class="spinner-border text-primary" role="status">
        <span class="visually-hidden">Loading...</span>
      </div>
      <p class="mt-3">Loading performance data...</p>
    </div>

    <div v-else-if="error" class="alert alert-danger">
      {{ error }}
    </div>

    <div v-else-if="!hasData" class="alert alert-info">
      <p class="mb-0">No comparative data available. Try taking more quizzes!</p>
    </div>

    <div v-else>
      <div class="chart-container">
        <canvas ref="chartCanvas"></canvas>
      </div>

      <div class="performance-details mt-4">
        <h4 class="mb-3">Performance Details</h4>
        <div class="table-responsive">
          <table class="table table-striped">
            <thead>
              <tr>
                <th>Quiz</th>
                <th>Your Score</th>
                <th>Class Average</th>
                <th>Percentile</th>
              </tr>
            </thead>
            <tbody>
              <tr v-for="item in comparisonData" :key="item.quiz_id">
                <td>{{ item.quiz_name }}</td>
                <td>
                  <span 
                    class="badge" 
                    :class="getScoreClass(item.user_score, item.average_score)"
                  >
                    {{ item.user_score !== null ? `${item.user_score}%` : 'Not Attempted' }}
                  </span>
                </td>
                <td>{{ item.average_score }}%</td>
                <td>
                  <span v-if="item.percentile !== null">
                    {{ item.percentile }}% 
                    <span class="text-muted">(better than {{ item.percentile }}% of students)</span>
                  </span>
                  <span v-else>N/A</span>
                </td>
              </tr>
            </tbody>
          </table>
        </div>
      </div>

      <div class="insights-section mt-4">
        <h4 class="mb-3">Performance Insights</h4>
        <div class="row">
          <div class="col-md-4 mb-3">
            <div class="card h-100">
              <div class="card-body">
                <h5 class="card-title">Overall Standing</h5>
                <p class="card-text">
                  {{ overallPerformanceMessage }}
                </p>
              </div>
            </div>
          </div>
          <div class="col-md-4 mb-3">
            <div class="card h-100">
              <div class="card-body">
                <h5 class="card-title">Strongest Areas</h5>
                <p class="card-text" v-if="topPerformingQuiz">
                  Your highest performance was in <strong>{{ topPerformingQuiz.quiz_name }}</strong> with a score of <strong>{{ topPerformingQuiz.user_score }}%</strong>.
                </p>
                <p class="card-text" v-else>
                  Complete more quizzes to identify your strong areas.
                </p>
              </div>
            </div>
          </div>
          <div class="col-md-4 mb-3">
            <div class="card h-100">
              <div class="card-body">
                <h5 class="card-title">Areas for Improvement</h5>
                <p class="card-text" v-if="bottomPerformingQuiz">
                  You may want to focus more on <strong>{{ bottomPerformingQuiz.quiz_name }}</strong> where your score was <strong>{{ bottomPerformingQuiz.user_score }}%</strong>.
                </p>
                <p class="card-text" v-else>
                  Complete more quizzes to identify areas for improvement.
                </p>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import axios from '@/axios.js';
// Change the Chart.js import to use the standard format
import { Chart, registerables } from 'chart.js';
// Register all chart components
Chart.register(...registerables);

export default {
  name: 'PerformanceChart',
  props: {
    userId: {
      type: [Number, String],
      required: true
    }
  },
  data() {
    return {
      comparisonData: [],
      subjects: [],
      selectedSubject: '',
      selectedChartType: 'bar',
      chart: null,
      loading: true,
      error: null
    };
  },
  computed: {
    hasData() {
      return this.comparisonData && this.comparisonData.length > 0;
    },
    topPerformingQuiz() {
      if (!this.hasData) return null;
      
      const attemptedQuizzes = this.comparisonData.filter(quiz => quiz.user_score !== null);
      if (attemptedQuizzes.length === 0) return null;
      
      return attemptedQuizzes.reduce((best, current) => 
        current.user_score > best.user_score ? current : best, attemptedQuizzes[0]);
    },
    bottomPerformingQuiz() {
      if (!this.hasData) return null;
      
      const attemptedQuizzes = this.comparisonData.filter(quiz => quiz.user_score !== null);
      if (attemptedQuizzes.length === 0) return null;
      
      return attemptedQuizzes.reduce((worst, current) => 
        current.user_score < worst.user_score ? current : worst, attemptedQuizzes[0]);
    },
    overallPerformanceMessage() {
      if (!this.hasData) return "Take more quizzes to see your overall standing.";
      
      const attemptedQuizzes = this.comparisonData.filter(quiz => quiz.user_score !== null);
      if (attemptedQuizzes.length === 0) return "You haven't attempted any of these quizzes yet.";
      
      // Calculate average percentile across all quizzes
      const percentiles = attemptedQuizzes
        .filter(quiz => quiz.percentile !== null)
        .map(quiz => quiz.percentile);
      
      if (percentiles.length === 0) return "Not enough data to determine your standing.";
      
      const avgPercentile = percentiles.reduce((sum, val) => sum + val, 0) / percentiles.length;
      
      if (avgPercentile >= 90) {
        return "Excellent! You're outperforming 90% or more of your peers.";
      } else if (avgPercentile >= 75) {
        return "Great job! You're performing better than most of your peers.";
      } else if (avgPercentile >= 50) {
        return "Good job! You're performing above average compared to your peers.";
      } else if (avgPercentile >= 25) {
        return "You're on the right track, but there's room for improvement.";
      } else {
        return "You may want to focus on improving your quiz performance.";
      }
    }
  },
  watch: {
    selectedChartType() {
      this.$nextTick(() => {
        this.renderChart();
      });
    },
    selectedSubject() {
      this.fetchComparisonData();
    }
  },
  async created() {
    try {
      // Fetch all subjects for the filter
      const subjectsResponse = await axios.get('/api/subjects');
      this.subjects = subjectsResponse.data;
      
      // Fetch initial comparison data
      await this.fetchComparisonData();
    } catch (error) {
      console.error('Error in performance chart setup:', error);
      this.error = 'Failed to initialize performance chart.';
      this.loading = false;
    }
  },
  mounted() {
    // Ensure the initial chart is rendered once the component is mounted
    this.$nextTick(() => {
      if (this.hasData && !this.loading) {
        this.renderChart();
      }
    });
  },
  methods: {
    async fetchComparisonData() {
      try {
        this.loading = true;
        
        let url = `/api/user-performance-comparison/${this.userId}`;
        
        // Add subject filter if selected
        if (this.selectedSubject) {
          url += `?subject_id=${this.selectedSubject}`;
        }
        
        const response = await axios.get(url);
        this.comparisonData = response.data.comparison_data;
        
        this.loading = false;
        
        // Only render chart after data is loaded and component is mounted
        this.$nextTick(() => {
          this.renderChart();
        });
      } catch (error) {
        console.error('Error fetching comparison data:', error);
        this.error = 'Failed to load performance comparison data.';
        this.loading = false;
      }
    },
    renderChart() {
      if (!this.hasData) return;
      
      // Check if canvas element exists in the DOM
      if (!this.$refs.chartCanvas) {
        console.warn('Canvas element not found in the DOM');
        return;
      }
      
      // Destroy previous chart if it exists
      if (this.chart) {
        this.chart.destroy();
      }
      
      try {
        const ctx = this.$refs.chartCanvas.getContext('2d');
        
        // Prepare chart data
        const labels = this.comparisonData.map(item => item.quiz_name);
        
        const userData = this.comparisonData.map(item => item.user_score || 0);
        const averageData = this.comparisonData.map(item => item.average_score);
        
        // Chart configuration
        const chartConfig = {
          type: this.selectedChartType,
          data: {
            labels: labels,
            datasets: [
              {
                label: 'Your Score',
                data: userData,
                backgroundColor: 'rgba(75, 192, 192, 0.2)',
                borderColor: 'rgba(75, 192, 192, 1)',
                borderWidth: 2,
                pointBackgroundColor: 'rgba(75, 192, 192, 1)'
              },
              {
                label: 'Class Average',
                data: averageData,
                backgroundColor: 'rgba(153, 102, 255, 0.2)',
                borderColor: 'rgba(153, 102, 255, 1)',
                borderWidth: 2,
                pointBackgroundColor: 'rgba(153, 102, 255, 1)'
              }
            ]
          },
          options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
              legend: {
                position: 'top',
              },
              tooltip: {
                callbacks: {
                  label: function(context) {
                    return `${context.dataset.label}: ${context.raw}%`;
                  }
                }
              }
            },
            scales: this.selectedChartType !== 'radar' ? {
              y: {
                beginAtZero: true,
                max: 100,
                title: {
                  display: true,
                  text: 'Score (%)'
                }
              }
            } : {}
          }
        };
        
        // Create the chart
        this.chart = new Chart(ctx, chartConfig);
      } catch (error) {
        console.error('Error rendering chart:', error);
        this.error = 'Failed to render chart. Please try again later.';
      }
    },
    getScoreClass(userScore, avgScore) {
      if (userScore === null) return 'bg-secondary';
      if (userScore >= avgScore + 10) return 'bg-success';
      if (userScore >= avgScore) return 'bg-info';
      if (userScore >= avgScore - 10) return 'bg-warning';
      return 'bg-danger';
    }
  }
};
</script>

<style scoped>
.performance-chart-container {
  padding: 20px 0;
}

.chart-container {
  position: relative;
  height: 400px;
  margin-bottom: 30px;
}

.chart-controls {
  background-color: #f8f9fa;
  padding: 15px;
  border-radius: 8px;
  margin-bottom: 20px;
}

.insights-section .card {
  border-radius: 8px;
  box-shadow: 0 2px 4px rgba(0,0,0,0.1);
  transition: transform 0.3s ease;
}

.insights-section .card:hover {
  transform: translateY(-5px);
}
</style>
