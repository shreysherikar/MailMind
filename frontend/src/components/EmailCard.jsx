import React from 'react';
import { Clock, Calendar, AlertCircle } from 'lucide-react';
import { clsx } from 'clsx';
import { twMerge } from 'tailwind-merge';

export function cn(...inputs) {
    return twMerge(clsx(inputs));
}

const PriorityBadge = ({ label, color, badge }) => {
    const colorClasses = {
        red: 'bg-red-100 text-red-800 border-red-200',
        orange: 'bg-orange-100 text-orange-800 border-orange-200',
        yellow: 'bg-yellow-100 text-yellow-800 border-yellow-200',
        green: 'bg-green-100 text-green-800 border-green-200',
        gray: 'bg-gray-100 text-gray-800 border-gray-200',
    };

    return (
        <span className={cn(
            "inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium border",
            colorClasses[color] || colorClasses.gray
        )}>
            <span className="mr-1">{badge}</span>
            {label}
        </span>
    );
};

export const EmailCard = ({ email, type = 'email', onAction }) => {
    // Handle difference between Email model and FollowUp model
    const isFollowUp = type === 'followup';

    const subject = email.subject || email.source_email_subject;
    const sender = email.sender || email.recipient_email; // For sent emails, show recipient
    const snippet = email.snippet;
    const timestamp = new Date(email.timestamp || email.sent_at).toLocaleString();

    return (
        <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-4 hover:shadow-md transition-shadow group">
            <div className="flex justify-between items-start mb-2">
                <div className="flex-1">
                    <h3 className="text-lg font-semibold text-gray-900 truncate pr-4">{subject}</h3>
                    <p className="text-sm text-gray-600 flex items-center mt-1">
                        <span className="font-medium mr-2">{isFollowUp ? 'To:' : 'From:'} {sender}</span>
                        <span className="text-gray-400 text-xs">• {timestamp}</span>
                    </p>
                </div>

                {/* Actions for regular emails */}
                {!isFollowUp && onAction && (
                    <div className="flex space-x-1 opacity-100 sm:opacity-0 group-hover:opacity-100 transition-opacity">
                        <button
                            onClick={(e) => { e.stopPropagation(); onAction(email.id, 'done'); }}
                            className="p-1.5 text-gray-400 hover:text-green-600 hover:bg-green-50 rounded-full"
                            title="Mark Done"
                        >
                            <svg className="w-5 h-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 13l4 4L19 7" />
                            </svg>
                        </button>
                        <button
                            onClick={(e) => { e.stopPropagation(); onAction(email.id, 'snooze'); }}
                            className="p-1.5 text-gray-400 hover:text-orange-600 hover:bg-orange-50 rounded-full"
                            title="Snooze"
                        >
                            <svg className="w-5 h-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z" />
                            </svg>
                        </button>
                        <button
                            onClick={(e) => { e.stopPropagation(); onAction(email.id, 'archive'); }}
                            className="p-1.5 text-gray-400 hover:text-gray-700 hover:bg-gray-100 rounded-full"
                            title="Archive"
                        >
                            <svg className="w-5 h-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 8h14M5 8a2 2 0 110-4h14a2 2 0 110 4M5 8v10a2 2 0 002 2h10a2 2 0 002-2V8m-9 4h4" />
                            </svg>
                        </button>
                    </div>
                )}

                {/* Priority Badge */}
                {!isFollowUp && (
                    <div className="ml-2">
                        <PriorityBadge
                            label={email.priority_label || 'Unknown'}
                            color={email.priority_color || 'gray'}
                            badge={email.priority_badge || '⚪'}
                        />
                    </div>
                )}

                {/* Follow-up Status Badge */}
                {isFollowUp && (
                    <span className={cn(
                        "inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium border",
                        email.status === 'overdue' ? "bg-red-100 text-red-800 border-red-200" : "bg-blue-100 text-blue-800 border-blue-200"
                    )}>
                        {email.status === 'overdue' ? '⚠️ Overdue' : '⏳ Waiting'}
                        {email.days_waiting > 0 && ` (${email.days_waiting}d)`}
                    </span>
                )}
            </div>

            <p className="text-gray-600 text-sm line-clamp-2 mb-3">
                {snippet}
            </p>

            <div className="flex items-center space-x-4 text-xs text-gray-500">
                {isFollowUp && email.expected_reply_by && (
                    <div className="flex items-center">
                        <Calendar className="w-3 h-3 mr-1" />
                        Expect by: {new Date(email.expected_reply_by).toLocaleDateString()}
                    </div>
                )}

                {!isFollowUp && (
                    <div className="flex items-center">
                        {/* Placeholder for task count if we link tasks to emails later */}
                    </div>
                )}
            </div>
        </div>
    );
};
