import axios from 'axios';

const API_URL = 'http://localhost:8000/api/v1';

export const client = axios.create({
    baseURL: API_URL,
    headers: {
        'Content-Type': 'application/json',
    },
});

export const api = {
    // Emails
    getEmails: async (limit = 100) => {
        const response = await client.get('/emails/with-scores', { params: { limit } });
        return response.data;
    },

    // Tasks
    getTasks: async (limit = 100) => {
        const response = await client.get('/tasks', { params: { limit, status: 'pending' } });
        return response.data;
    },

    // Follow-ups
    getWaitingFollowups: async (limit = 100) => {
        const response = await client.get('/followups/waiting', { params: { limit } });
        return response.data;
    },

    getOverdueFollowups: async (limit = 100) => {
        const response = await client.get('/followups/overdue', { params: { limit } });
        return response.data;
    },

    getStats: async () => {
        const response = await client.get('/followups/stats');
        return response.data;
    },

    // Status Updates
    updateStatus: async (id, status) => {
        const response = await client.patch(`/emails/${id}/status`, null, { params: { status } });
        return response.data;
    },

    snoozeEmail: async (id, hours = 24) => {
        const response = await client.patch(`/emails/${id}/snooze`, null, { params: { hours } });
        return response.data;
    }
};
