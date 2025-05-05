import { createRouter, createWebHistory } from 'vue-router';
import HomePage from '../components/HomePage.vue';
import QuizSummaryPage from '@/components/QuizSummaryPage.vue';
import UserReportsPage from '@/components/UserReportsPage.vue';

const routes = [
  { path: '/', component: HomePage },
  { path: '/quiz1', component: () => import('../components/QuizPage.vue') },
  { path: '/search', component: () => import('../components/SearchPage.vue') },
  {
    path: '/search-results',
    name: 'search-results',
    component: () => import('../components/SearchResults.vue')
  },
  { path: '/progress', component: () => import('../components/UserProgress.vue') },
  { path: '/register', component: () => import('../views/Register.vue') },
  { path: '/login', component: () => import('../views/login.vue') },
  { path: '/logout', component: () => import('../components/Logout.vue') },
  
  // ADMIN ROUTES - prefix with /admin
  { 
    path: '/AdminDashboard', 
    component: () => import('../components/AdminDashboard.vue'),
    beforeEnter: (to, from, next) => {
      const userType = localStorage.getItem("user_type");
      console.log("Checking access to AdminDashboard, user type:", userType);
      if (userType === "admin") {
        next();
      } else {
        alert("Access denied! Admins only.");
        next('/');
      }
    }
  },
  { path: '/FormSubject', component: () => import('../components/FormSubject.vue') },
  {
    path: '/update-subject/:id',
    component: () => import('../components/UpdateSubject.vue'),
    props: true
  },
  {
    path: '/admin/chapters/:chapterId',  // CHANGED: Added admin prefix
    name: 'AdminChapterPage',           // CHANGED: New name
    component: () => import('../components/UpdateChapter.vue'),
    props: true, 
  },
  {
    path: '/admin/quizzes/:subjectId/:chapterId', // CHANGED: Added admin prefix
    name: 'AdminQuizzes',                        // CHANGED: New name
    component: () => import('../components/QuizzesPage.vue'),
    props: true
  },
  {
    path: '/quizzes/:quizId/questions',
    name: 'QuizQuestions',
    component: () => import('../components/QuestionsPage.vue'),
    props: true
  },
  {
    path: '/update-question/:id',
    component: () => import('../components/UpdateQuestion.vue'),
  },
  {
    path: '/update-chapter/:id',
    name: 'UpdateChapter',
    component: () => import('../components/UpdateChapter.vue'),
    props: true
  },
  {
    path: '/update-quiz-basic/:id',
    component: () => import('../components/UpdateQuizBasic.vue'),
    props: true,
  },
  {
    path: '/update-quiz-advanced/:id',
    component: () => import('../components/UpdateQuizAdvanced.vue'),
    props: true,
  },
  {
    path: '/user-profile/:id',
    component: () => import('../components/UserProfile.vue'),
  },
  {
    path: '/manage-subjects',
    component: () => import('../components/SubjectCRUD.vue'),
  },
  {
    path: '/manage-users',
    component: () => import('../components/UserManage.vue'),
  },
  {
    path: '/subjects/:subjectId/add-chapter',
    name: 'AddChapter',
    component: () => import('../components/AddChapter.vue'),
    props: true
  },
  
  // USER QUIZ FLOW ROUTES - Keep these separate and with distinct names
  {
    path: '/quiz',
    name: 'quiz',
    component: () => import('../components/SubjectsPage.vue')
  },
  {
    path: '/chapters/:subjectId',
    name: 'chapters',
    component: () => import('../components/ChaptersPage.vue'),
    props: true
  },
  {
    path: '/user/quizzes/:chapterId',  // CHANGED: Added user/ prefix
    name: 'user-quizzes',             // CHANGED: New distinct name
    component: () => import('../components/UserQuizzesPage.vue'),
    props: true
  },
  {
    path: '/quiz-attempt/:quizId',
    name: 'quiz-attempt',
    component: () => import('../components/QuizAttempt.vue'),
    props: true
  },
  {
    path: '/quiz-summary',
    name: 'QuizSummary',
    component: QuizSummaryPage,
    meta: {
      requiresAuth: true,
      requiresAdmin: true
    }
  },
  {
    path: '/user-reports',
    name: 'UserReports',
    component: UserReportsPage,
    meta: {
      requiresAuth: true,
      requiresAdmin: true
    }
  }
];

const router = createRouter({
  history: createWebHistory(),
  routes
});

router.beforeEach((to, from, next) => {
  const isLoggedIn = !!localStorage.getItem("auth_token");
  const userType = localStorage.getItem("user_type");

  // Define public routes that don't require authentication
  const publicRoutes = ['/login', '/register'];

  if (to.path === '/login' && isLoggedIn) {
    next(userType === 'admin' ? '/AdminDashboard' : '/'); // Redirect based on role
  } else if (!isLoggedIn && !publicRoutes.includes(to.path)) {
    alert('Please log in first'); // Notify unauthenticated users
    next('/login'); // Redirect unauthenticated users to login
  } else {
    next(); // Allow navigation
  }
});

export default router;
