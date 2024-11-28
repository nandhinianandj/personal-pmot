import React from 'react';
import { Plane } from 'lucide-react';

interface LayoutProps {
  children: React.ReactNode;
}

export default function Layout({ children }: LayoutProps) {
  return (
    <div className="min-h-screen bg-gray-100">
      <div className="max-w-7xl mx-auto py-6 sm:px-6 lg:px-8">
        <div className="px-4 py-6 sm:px-0">
          <div className="flex items-center space-x-2 mb-8">
            <Plane className="h-8 w-8 text-indigo-600" />
            <h1 className="text-3xl font-bold text-gray-900">PMOT Stories</h1>
          </div>
          {children}
        </div>
      </div>
    </div>
  );
}