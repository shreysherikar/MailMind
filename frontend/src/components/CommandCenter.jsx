import React, { useState, useEffect } from 'react';
import { TabBar } from './TabBar';
import { EmailCard } from './EmailCard';
import { api } from '../api/client';
import { Loader2 } from 'lucide-react';

export const CommandCenter = () => {
    const [activeTab, setActiveTab] = useState('do_now');
    const [loading, setLoading] = useState(true);

    // Data state
    const [emails, setEmails] = useState([]);
    const [followups, setFollowups] = useState([]);
    const [tasks, setTasks] = useState([]);

    // Filtered data
    const [filteredData, setFilteredData] = useState([]);

    // Counts
    const [counts, setCounts] = useState({
        do_now: 0,
        waiting: 0,
        tasks: 0,
        low_priority: 0
    });

    // Fetch data on mount
    useEffect(() => {
        const fetchData = async () => {
            setLoading(true);
            try {
                const [emailsData, followupsData, tasksData] = await Promise.all([
                    api.getEmails(),
                    api.getWaitingFollowups(),
                    api.getTasks()
                ]);

                setEmails(emailsData);
                setFollowups(followupsData);
                setTasks(tasksData);

                // Calculate counts
                const doNowCount = emailsData.filter(e => e.score >= 60).length;
                const lowPriorityCount = emailsData.filter(e => e.score < 40).length;
                const waitingCount = followupsData.length;
                // tasks tab can show emails that have tasks, or just tasks. 
                // For now, let's assume 'Needs Decision' tab shows emails with score 40-59 (Medium) OR have tasks.
                // Or simpler: follow logic in tabs.
                //  - Do Now: score >= 60
                //  - Waiting: followups
                //  - Needs Decision: score 40-59
                //  - Low Priority: score 0-39

                const needsDecisionCount = emailsData.filter(e => e.score >= 40 && e.score < 60).length;

                setCounts({
                    do_now: doNowCount,
                    waiting: waitingCount,
                    tasks: needsDecisionCount,
                    low_priority: lowPriorityCount
                });

            } catch (error) {
                console.error("Failed to fetch data:", error);
            } finally {
                setLoading(false);
            }
        };

        fetchData();
    }, []);

    // Filter data when tab or data changes
    useEffect(() => {
        if (loading) return;

        let result = [];

        switch (activeTab) {
            case 'do_now':
                result = emails.filter(e => e.score >= 60);
                break;
            case 'waiting':
                result = followups;
                break;
            case 'tasks': // Needs Decision
                result = emails.filter(e => e.score >= 40 && e.score < 60);
                break;
            case 'low_priority':
                result = emails.filter(e => e.score < 40);
                break;
            default:
                result = [];
        }

        setFilteredData(result);
    }, [activeTab, emails, followups, tasks, loading]);

    // Action handler
    const handleAction = async (id, action) => {
        // Optimistic update
        setEmails(prev => prev.filter(e => e.id !== id));

        // Also update counts locally for immediate feedback
        if (action === 'done' || action === 'archive' || action === 'snooze') {
            // Re-calculate counts would be complex without refetching, 
            // but simple decrement of current tab's count works visually.
        }

        try {
            if (action === 'snooze') {
                await api.snoozeEmail(id, 24); // Default 24h
            } else {
                await api.updateStatus(id, action);
            }
        } catch (error) {
            console.error("Action failed:", error);
            // Revert optimistic update if needed, but for prototype we can skip
        }
    };

    return (
        <div className="flex flex-col h-screen bg-gray-50">
            <header className="bg-white border-b border-gray-200 px-6 py-4 flex items-center justify-between">
                <div className="flex items-center">
                    <div className="bg-indigo-600 rounded-lg p-2 mr-3">
                        <svg className="w-5 h-5 text-white" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M3 8l7.89 5.26a2 2 0 002.22 0L21 8M5 19h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v10a2 2 0 002 2z" />
                        </svg>
                    </div>
                    <h1 className="text-xl font-bold text-gray-900">MailMind</h1>
                </div>
                <div className="flex items-center space-x-4">
                    <button className="p-2 text-gray-400 hover:text-gray-500">
                        <svg className="w-6 h-6" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z" />
                        </svg>
                    </button>
                    <button className="p-2 text-gray-400 hover:text-gray-500">
                        <svg className="w-6 h-6" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 17h5l-1.405-1.405A2.032 2.032 0 0118 14.158V11a6.002 6.002 0 00-4-5.659V5a2 2 0 10-4 0v.341C7.67 6.165 6 8.388 6 11v3.159c0 .538-.214 1.055-.595 1.436L4 17h5m6 0v1a3 3 0 11-6 0v-1m6 0H9" />
                        </svg>
                    </button>
                    <img
                        className="h-8 w-8 rounded-full"
                        src="https://images.unsplash.com/photo-1472099645785-5658abf4ff4e?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=facearea&facepad=2&w=256&h=256&q=80"
                        alt=""
                    />
                </div>
            </header>

            <TabBar activeTab={activeTab} onTabChange={setActiveTab} counts={counts} />

            <main className="flex-1 overflow-y-auto p-6">
                {loading ? (
                    <div className="flex justify-center items-center h-full">
                        <Loader2 className="w-8 h-8 text-indigo-600 animate-spin" />
                    </div>
                ) : filteredData.length === 0 ? (
                    <div className="text-center py-20">
                        <div className="bg-gray-100 rounded-full w-16 h-16 flex items-center justify-center mx-auto mb-4">
                            <svg className="w-8 h-8 text-gray-400" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M20 13V6a2 2 0 00-2-2H6a2 2 0 00-2 2v7m16 0v5a2 2 0 01-2 2H6a2 2 0 01-2-2v-5m16 0h-2.586a1 1 0 00-.707.293l-2.414 2.414a1 1 0 01-.707.293h-3.172a1 1 0 01-.707-.293l-2.414-2.414A1 1 0 006.586 13H4" />
                            </svg>
                        </div>
                        <h3 className="text-lg font-medium text-gray-900">No emails in this category</h3>
                        <p className="mt-1 text-gray-500">All caught up! Check other tabs or waiting for new emails.</p>
                    </div>
                ) : (
                    <div className="max-w-4xl mx-auto space-y-4">
                        {filteredData.map((item) => (
                            <EmailCard
                                key={item.id}
                                email={item}
                                type={activeTab === 'waiting' ? 'followup' : 'email'}
                                onAction={handleAction}
                            />
                        ))}
                    </div>
                )}
            </main>
        </div>
    );
};
