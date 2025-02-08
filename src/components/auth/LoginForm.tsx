import React from 'react';
import { useAuth } from '../../contexts/AuthContext';
import { Github, ToggleLeft as Google, Twitter } from 'lucide-react';

export default function LoginForm() {
  const { login } = useAuth();

  const handleLogin = async () => {
    try {
      await login();
    } catch (error) {
      console.error('Login error:', error);
    }
  };

  return (
    <div className="space-y-6">
      <div className="grid grid-cols-1 gap-4">
        <button
          onClick={handleLogin}
          className="flex items-center justify-center px-4 py-2 border border-transparent rounded-md shadow-sm text-sm font-medium text-white bg-indigo-600 hover:bg-indigo-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-indigo-500"
        >
          <Google className="h-5 w-5 mr-2" />
          Continue with Google
        </button>

        <button
          onClick={handleLogin}
          className="flex items-center justify-center px-4 py-2 border border-transparent rounded-md shadow-sm text-sm font-medium text-white bg-gray-800 hover:bg-gray-900 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-gray-500"
        >
          <Github className="h-5 w-5 mr-2" />
          Continue with GitHub
        </button>

        <button
          onClick={handleLogin}
          className="flex items-center justify-center px-4 py-2 border border-transparent rounded-md shadow-sm text-sm font-medium text-white bg-blue-400 hover:bg-blue-500 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-300"
        >
          <Twitter className="h-5 w-5 mr-2" />
          Continue with Twitter
        </button>
      </div>
    </div>
  );
}