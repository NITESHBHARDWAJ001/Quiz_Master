import axios from '@/axios.js';

/**
 * Notification service to handle sending notification emails 
 * for new content creation (quizzes, subjects , chapters)
 */
const notificationService = {
  /**
   * Check if notification endpoint is available
   * @returns {Promise<boolean>} - Whether the notification system is available
   */
  async checkNotificationSystem() {
    try {
      const response = await axios.get('/api/notification-status');
      console.log('Notification system status:', response.data);
      return response.data?.available || false;
    } catch (error) {
      console.warn('Notification system may not be available:', error.message);
      return false;
    }
  },

  /**
   * Send notification emails about a new quiz
   * @param {number} quizId - ID of the newly created quiz
   * @returns {Promise} - The axios response
   */
  async notifyNewQuiz(quizId) {
    if (!quizId) {
      console.error('Cannot send quiz notification: No quiz ID provided');
      return Promise.resolve({ error: 'No quiz ID provided' });
    }

    console.log(`Sending notifications for quiz ID: ${quizId}`);
    
    // Try the primary endpoint first
    try {
      const response = await axios.post(`/api/admin/notify-quiz/${quizId}`);
      console.log(`Quiz notification sent successfully:`, response.data);
      return response;
    } catch (primaryError) {
      console.warn(`Primary notification endpoint failed:`, primaryError.message);
      
      // Try the fallback endpoint
      try {
        const fallbackResponse = await axios.post('/api/notifications/send-all', {
          subject: 'New Quiz Available',
          message: 'A new quiz has been added to the system. Login to take it!',
          include_quizzes: true,
          days_ahead: 30,
          highlight_quiz_id: quizId
        });
        console.log(`Quiz notification sent via fallback:`, fallbackResponse.data);
        return fallbackResponse;
      } catch (fallbackError) {
        console.error('All notification attempts failed:', fallbackError.message);
        return { error: fallbackError };
      }
    }
  },

  /**
   * Send notification emails to all users about all available quizzes
   * @param {Object} options - Optional configuration parameters
   * @returns {Promise} - The axios response
   */
  async notifyAllUsersAboutQuizzes(options = {}) {
    try {
      console.log('Notifying all users about quizzes', options);
      
      // Try multiple possible endpoints to accommodate different backend implementations
      const endpoints = [
        '/api/admin/notify-all-quizzes',
        '/api/admin/notify-all',
        '/api/notifications/send-all'
      ];
      
      const payload = {
        type: 'quizzes',
        adminTriggered: true,
        subject: options.subject || 'New Quizzes Available',
        message: options.message || 'There are new quizzes available for you to attempt!',
        include_quizzes: options.includeQuizzes !== false, // Default to true
        days_ahead: options.daysAhead || 30,
        highlight_quiz_id: options.highlightQuizId
      };
      
      for (const endpoint of endpoints) {
        try {
          const response = await axios.post(endpoint, payload);
          console.log(`Notification to all users successful via ${endpoint}:`, response.data);
          return {
            data: {
              sentCount: response.data.users_notified || 'all',
              message: response.data.message || 'Notifications sent successfully'
            }
          };
        } catch (endpointError) {
          console.warn(`Failed to notify via ${endpoint}:`, endpointError.message);
          // Continue to next endpoint
        }
      }
      
      // If we reach here, all endpoints failed
      throw new Error('All notification endpoints failed');
    } catch (error) {
      console.error('Error sending notifications to all users:', error);
      return { error };
    }
  },

  /**
   * Send notification emails about a new subject
   * @param {number} subjectId - ID of the newly created subject
   * @param {string} subjectName - Name of the subject
   * @returns {Promise} - The axios response
   */
  async notifyNewSubject(subjectId, subjectName) {
    if (!subjectId) {
      console.error('Cannot send subject notification: No subject ID provided');
      return Promise.resolve({ error: 'No subject ID provided' });
    }

    // Try multiple endpoint patterns
    const endpoints = [
      '/api/admin/notify-subject',
      '/api/notify/subject',
      '/api/subjects/notify'
    ];
    
    for (const endpoint of endpoints) {
      try {
        const response = await axios.post(endpoint, {
          subjectId,
          subjectName,
          autoTriggered: true
        });
        console.log(`Subject notification sent successfully via ${endpoint}:`, response.data);
        return response;
      } catch (error) {
        console.warn(`Failed to send subject notification via ${endpoint}:`, error.message);
      }
    }
    
    console.error('All subject notification attempts failed');
    return Promise.resolve({ error: 'All notification endpoints failed' });
  },

  /**
   * Send notification emails about a new chapter
   * @param {number} chapterId - ID of the newly created chapter
   * @param {string} chapterName - Name of the chapter
   * @param {number} subjectId - ID of the parent subject
   * @returns {Promise} - The axios response
   */
  async notifyNewChapter(chapterId, chapterName, subjectId) {
    if (!chapterId) {
      console.error('Cannot send chapter notification: No chapter ID provided');
      return Promise.resolve({ error: 'No chapter ID provided' });
    }

    // Try multiple endpoint patterns
    const endpoints = [
      '/api/admin/notify-chapter',
      '/api/notify/chapter',
      '/api/chapters/notify'
    ];
    
    for (const endpoint of endpoints) {
      try {
        const response = await axios.post(endpoint, {
          chapterId,
          chapterName,
          subjectId,
          autoTriggered: true
        });
        console.log(`Chapter notification sent successfully via ${endpoint}:`, response.data);
        return response;
      } catch (error) {
        console.warn(`Failed to send chapter notification via ${endpoint}:`, error.message);
      }
    }
    
    console.error('All chapter notification attempts failed');
    return Promise.resolve({ error: 'All notification endpoints failed' });
  }
};

export default notificationService;
