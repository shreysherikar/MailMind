import React from 'react';
import { clsx } from 'clsx';
import { twMerge } from 'tailwind-merge';

export function cn(...inputs) {
    return twMerge(clsx(inputs));
}

export const TabBar = ({ activeTab, onTabChange, counts }) => {
    const tabs = [
        { id: 'do_now', label: '🔥 Do Now', color: 'text-red-600' },
        { id: 'waiting', label: '⏳ Waiting for Reply', color: 'text-blue-600' },
        { id: 'tasks', label: '🧠 Needs Decision', color: 'text-purple-600' },
        { id: 'low_priority', label: '😌 Low Priority', color: 'text-gray-500' },
    ];

    return (
        <div className="border-b border-gray-200 bg-white">
            <nav className="-mb-px flex space-x-8 px-6 overflow-x-auto" aria-label="Tabs">
                {tabs.map((tab) => {
                    const isActive = activeTab === tab.id;
                    const count = counts[tab.id] || 0;

                    return (
                        <button
                            key={tab.id}
                            onClick={() => onTabChange(tab.id)}
                            className={cn(
                                isActive
                                    ? 'border-indigo-500 text-indigo-600'
                                    : 'border-transparent text-gray-500 hover:border-gray-300 hover:text-gray-700',
                                'whitespace-nowrap border-b-2 py-4 px-1 text-sm font-medium flex items-center transition-colors'
                            )}
                        >
                            <span className={cn("mr-2", tab.color)}>{tab.label.split(' ')[0]}</span>
                            {tab.label.split(' ').slice(1).join(' ')}
                            <span
                                className={cn(
                                    isActive ? 'bg-indigo-100 text-indigo-600' : 'bg-gray-100 text-gray-900',
                                    'ml-3 hidden rounded-full py-0.5 px-2.5 text-xs font-medium md:inline-block'
                                )}
                            >
                                {count}
                            </span>
                        </button>
                    );
                })}
            </nav>
        </div>
    );
};
