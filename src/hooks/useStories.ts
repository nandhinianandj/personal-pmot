import { useState, useEffect } from 'react';
import axios from 'axios';
import { Story } from '../types';
import toast from 'react-hot-toast';

const API_URL = '/api';

export function useStories() {
  const [stories, setStories] = useState<Story[]>([]);
  const [isLoading, setIsLoading] = useState(false);

  const fetchStories = async () => {
    try {
      const response = await axios.get(`${API_URL}/stories/`);
      setStories(response.data);
    } catch (error) {
      toast.error('Failed to fetch stories');
    }
  };

  const createStory = async (data: Omit<Story, 'id'>) => {
    setIsLoading(true);
    try {
      await axios.post(`${API_URL}/stories/`, data);
      toast.success('Story created successfully');
      await fetchStories();
      return true;
    } catch (error) {
      toast.error('Failed to create story');
      return false;
    } finally {
      setIsLoading(false);
    }
  };

  const updateStory = async (id: number, data: Omit<Story, 'id'>) => {
    setIsLoading(true);
    try {
      await axios.put(`${API_URL}/stories/${id}`, data);
      toast.success('Story updated successfully');
      await fetchStories();
      return true;
    } catch (error) {
      toast.error('Failed to update story');
      return false;
    } finally {
      setIsLoading(false);
    }
  };

  const deleteStory = async (id: number) => {
    try {
      await axios.delete(`${API_URL}/stories/${id}`);
      toast.success('Story deleted successfully');
      await fetchStories();
    } catch (error) {
      toast.error('Failed to delete story');
    }
  };

  useEffect(() => {
    fetchStories();
  }, []);

  return {
    stories,
    isLoading,
    createStory,
    updateStory,
    deleteStory,
  };
}