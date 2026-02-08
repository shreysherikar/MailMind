/**
 * NLP & RAG API Client for MailMind Frontend
 * 
 * Provides easy-to-use functions for:
 * - Email analysis (NLP)
 * - Semantic search
 * - Company memory (question answering)
 * - Burnout detection
 */

import apiClient from './client';

// ============================================================================
// NLP ANALYSIS
// ============================================================================

/**
 * Analyze an email with NLP (summarization, entities, intent, sentiment)
 */
export const analyzeEmail = async (email) => {
  const response = await apiClient.post('/api/v1/nlp/analyze', email);
  return response.data;
};

/**
 * Get a summary of an email
 */
export const summarizeEmail = async (email) => {
  const response = await apiClient.post('/api/v1/nlp/summarize', email);
  return response.data;
};

/**
 * Extract named entities from an email
 */
export const extractEntities = async (email) => {
  const response = await apiClient.post('/api/v1/nlp/entities', email);
  return response.data;
};

/**
 * Detect the intent of an email
 */
export const detectIntent = async (email) => {
  const response = await apiClient.post('/api/v1/nlp/intent', email);
  return response.data;
};

// ============================================================================
// SEMANTIC SEARCH & COMPANY MEMORY (RAG)
// ============================================================================

/**
 * Search emails semantically (by meaning, not keywords)
 * 
 * @param {string} query - Natural language search query
 * @param {number} limit - Max results (default: 10)
 * @param {number} minSimilarity - Minimum similarity score 0-1 (default: 0.7)
 * @param {string} senderFilter - Optional sender email filter
 * @param {Date} dateFrom - Optional start date filter
 * @param {Date} dateTo - Optional end date filter
 */
export const searchEmails = async ({
  query,
  limit = 10,
  minSimilarity = 0.7,
  senderFilter = null,
  dateFrom = null,
  dateTo = null
}) => {
  const response = await apiClient.post('/api/v1/rag/search', {
    query,
    limit,
    min_similarity: minSimilarity,
    sender_filter: senderFilter,
    date_from: dateFrom?.toISOString(),
    date_to: dateTo?.toISOString()
  });
  return response.data;
};

/**
 * Ask a question about email history (Company Memory)
 * 
 * @param {string} question - Natural language question
 * @param {number} limit - Max source emails to consider (default: 5)
 */
export const askQuestion = async (question, limit = 5) => {
  const response = await apiClient.post('/api/v1/rag/ask', {
    question,
    limit
  });
  return response.data;
};

/**
 * Index an email for semantic search
 */
export const indexEmail = async (email) => {
  const response = await apiClient.post('/api/v1/rag/index', email);
  return response.data;
};

/**
 * Index multiple emails at once (more efficient)
 */
export const indexEmailsBatch = async (emails) => {
  const response = await apiClient.post('/api/v1/rag/index/batch', emails);
  return response.data;
};

/**
 * Remove an email from the search index
 */
export const deleteFromIndex = async (emailId) => {
  const response = await apiClient.delete(`/api/v1/rag/index/${emailId}`);
  return response.data;
};

/**
 * Get RAG system statistics
 */
export const getRagStats = async () => {
  const response = await apiClient.get('/api/v1/rag/stats');
  return response.data;
};

// ============================================================================
// BURNOUT DETECTION
// ============================================================================

/**
 * Analyze email patterns for burnout signals
 * 
 * @param {string} userEmail - User's email address
 * @param {Array} emails - Array of email objects with: id, subject, body, date, sender, is_sent
 * @param {number} periodDays - Analysis period in days (default: 30)
 */
export const analyzeBurnout = async (userEmail, emails, periodDays = 30) => {
  const response = await apiClient.post('/api/v1/burnout/analyze', {
    user_email: userEmail,
    emails,
    period_days: periodDays
  });
  return response.data;
};

/**
 * Quick burnout check (simplified response)
 */
export const quickBurnoutCheck = async (userEmail, emails, periodDays = 30) => {
  const response = await apiClient.post('/api/v1/burnout/quick-check', {
    user_email: userEmail,
    emails,
    period_days: periodDays
  });
  return response.data;
};

/**
 * Get information about burnout detection feature
 */
export const getBurnoutInfo = async () => {
  const response = await apiClient.get('/api/v1/burnout/info');
  return response.data;
};

// ============================================================================
// HELPER FUNCTIONS
// ============================================================================

/**
 * Format email for API calls
 */
export const formatEmailForAPI = (email) => {
  return {
    id: email.id,
    subject: email.subject || '',
    body: email.body || '',
    sender_email: email.sender_email || email.from || '',
    sender_name: email.sender_name || '',
    date: email.date || new Date().toISOString()
  };
};

/**
 * Get risk level color for burnout detection
 */
export const getBurnoutRiskColor = (riskLevel) => {
  const colors = {
    low: 'green',
    moderate: 'yellow',
    high: 'orange',
    critical: 'red'
  };
  return colors[riskLevel] || 'gray';
};

/**
 * Get risk level emoji
 */
export const getBurnoutRiskEmoji = (riskLevel) => {
  const emojis = {
    low: '😊',
    moderate: '😐',
    high: '😰',
    critical: '🚨'
  };
  return emojis[riskLevel] || '❓';
};

/**
 * Format similarity score as percentage
 */
export const formatSimilarity = (score) => {
  return `${(score * 100).toFixed(0)}%`;
};

// ============================================================================
// EXAMPLE USAGE
// ============================================================================

/*

// 1. Analyze an email
const analysis = await analyzeEmail({
  id: '123',
  subject: 'Project Update',
  body: 'The project is on track...',
  sender_email: 'john@company.com',
  sender_name: 'John Doe',
  date: new Date().toISOString()
});

console.log('Summary:', analysis.summary.short_summary);
console.log('Intent:', analysis.intent);
console.log('Entities:', analysis.entities);

// 2. Search emails
const searchResults = await searchEmails({
  query: 'budget approval',
  limit: 10,
  minSimilarity: 0.7
});

searchResults.results.forEach(result => {
  console.log(`${result.subject} (${formatSimilarity(result.similarity_score)})`);
});

// 3. Ask a question
const answer = await askQuestion('What did legal say about the AWS contract?');
console.log('Answer:', answer.answer);
console.log('Sources:', answer.sources.length);

// 4. Check burnout
const burnoutMetrics = await analyzeBurnout(
  'user@company.com',
  emails,
  30
);

console.log('Risk Level:', burnoutMetrics.risk_level);
console.log('Risk Score:', burnoutMetrics.risk_score);
console.log('Signals:', burnoutMetrics.signals);
console.log('Recommendations:', burnoutMetrics.recommendations);

*/

export default {
  // NLP
  analyzeEmail,
  summarizeEmail,
  extractEntities,
  detectIntent,
  
  // RAG
  searchEmails,
  askQuestion,
  indexEmail,
  indexEmailsBatch,
  deleteFromIndex,
  getRagStats,
  
  // Burnout
  analyzeBurnout,
  quickBurnoutCheck,
  getBurnoutInfo,
  
  // Helpers
  formatEmailForAPI,
  getBurnoutRiskColor,
  getBurnoutRiskEmoji,
  formatSimilarity
};
