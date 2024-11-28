import React, { useState } from 'react';
import axios from 'axios';
import { toast } from 'react-hot-toast';
import { CreditCard } from 'lucide-react';

declare global {
  interface Window {
    Razorpay: any;
  }
}

export default function PremiumUpgrade() {
  const [isLoading, setIsLoading] = useState(false);

  const handleUpgrade = async () => {
    try {
      setIsLoading(true);
      const { data: order } = await axios.post('/api/premium/order');
      
      const options = {
        key: process.env.RAZORPAY_KEY_ID,
        amount: order.amount,
        currency: order.currency,
        name: 'PMOT Premium',
        description: 'Upgrade to Premium Membership',
        order_id: order.id,
        handler: async (response: any) => {
          try {
            await axios.post('/api/premium/verify', {
              payment_id: response.razorpay_payment_id,
              order_id: response.razorpay_order_id,
              signature: response.razorpay_signature,
            });
            toast.success('Upgrade successful!');
          } catch (error) {
            toast.error('Payment verification failed');
          }
        },
        prefill: {
          name: 'User Name',
          email: 'user@example.com',
        },
        theme: {
          color: '#4F46E5',
        },
      };

      const razorpay = new window.Razorpay(options);
      razorpay.open();
    } catch (error) {
      toast.error('Failed to initiate payment');
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="bg-white p-6 rounded-lg shadow-md">
      <div className="text-center">
        <CreditCard className="mx-auto h-12 w-12 text-indigo-600" />
        <h2 className="mt-4 text-2xl font-bold text-gray-900">Upgrade to Premium</h2>
        <p className="mt-2 text-gray-600">
          Get unlimited stories and exclusive features
        </p>
      </div>
      <div className="mt-6">
        <ul className="space-y-3">
          <li className="flex items-center">
            <svg className="h-5 w-5 text-green-500" fill="none" strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" viewBox="0 0 24 24" stroke="currentColor">
              <path d="M5 13l4 4L19 7"></path>
            </svg>
            <span className="ml-2">Unlimited stories</span>
          </li>
          <li className="flex items-center">
            <svg className="h-5 w-5 text-green-500" fill="none" strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" viewBox="0 0 24 24" stroke="currentColor">
              <path d="M5 13l4 4L19 7"></path>
            </svg>
            <span className="ml-2">Priority support</span>
          </li>
          <li className="flex items-center">
            <svg className="h-5 w-5 text-green-500" fill="none" strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" viewBox="0 0 24 24" stroke="currentColor">
              <path d="M5 13l4 4L19 7"></path>
            </svg>
            <span className="ml-2">Advanced features</span>
          </li>
        </ul>
      </div>
      <button
        onClick={handleUpgrade}
        disabled={isLoading}
        className="mt-6 w-full flex justify-center py-2 px-4 border border-transparent rounded-md shadow-sm text-sm font-medium text-white bg-indigo-600 hover:bg-indigo-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-indigo-500"
      >
        {isLoading ? 'Processing...' : 'Upgrade Now - ₹999'}
      </button>
    </div>
  );
}