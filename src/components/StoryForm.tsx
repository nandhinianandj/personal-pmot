import React, { useState, useRef } from 'react';
import { Plus, Minus, Upload } from 'lucide-react';
import { Story, MediaLink } from '../types';
import axios from 'axios';
import toast from 'react-hot-toast';

interface StoryFormProps {
  initialData?: Story;
  onSubmit: (data: Omit<Story, 'id'>) => void;
  isLoading?: boolean;
}

export default function StoryForm({ initialData, onSubmit, isLoading }: StoryFormProps) {
  const fileInputRef = useRef<HTMLInputElement>(null);
  const [formData, setFormData] = useState<Omit<Story, 'id'>>({
    title: initialData?.title || '',
    takeoff: initialData?.takeoff || '',
    turbulence: initialData?.turbulence || '',
    touchdown: initialData?.touchdown || '',
    media_links: initialData?.media_links || [],
  });
  const [uploading, setUploading] = useState(false);

  const handleAddMediaLink = () => {
    setFormData(prev => ({
      ...prev,
      media_links: [...prev.media_links, { media_type: 'youtube', url: '' }],
    }));
  };

  const handleRemoveMediaLink = (index: number) => {
    setFormData(prev => ({
      ...prev,
      media_links: prev.media_links.filter((_, i) => i !== index),
    }));
  };

  const handleMediaLinkChange = (index: number, field: keyof MediaLink, value: string) => {
    setFormData(prev => ({
      ...prev,
      media_links: prev.media_links.map((link, i) =>
        i === index ? { ...link, [field]: value } : link
      ),
    }));
  };

  const handleFileUpload = async (event: React.ChangeEvent<HTMLInputElement>) => {
    const file = event.target.files?.[0];
    if (!file) return;

    const formData = new FormData();
    formData.append('file', file);

    setUploading(true);
    try {
      const response = await axios.post('/api/upload/', formData, {
        headers: {
          'Content-Type': 'multipart/form-data',
        },
      });

      const fileType = file.type.split('/')[0];
      setFormData(prev => ({
        ...prev,
        media_links: [...prev.media_links, {
          media_type: fileType === 'video' ? 'youtube' : fileType,
          url: response.data.url,
        }],
      }));
      toast.success('File uploaded successfully');
    } catch (error) {
      toast.error('Failed to upload file');
    } finally {
      setUploading(false);
      if (fileInputRef.current) {
        fileInputRef.current.value = '';
      }
    }
  };

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    onSubmit(formData);
  };

  return (
    <form onSubmit={handleSubmit} className="space-y-6">
      <div>
        <label className="block text-sm font-medium text-gray-700">Title</label>
        <input
          type="text"
          value={formData.title}
          onChange={e => setFormData(prev => ({ ...prev, title: e.target.value }))}
          className="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-indigo-500 focus:ring-indigo-500"
          required
        />
      </div>

      <div>
        <label className="block text-sm font-medium text-gray-700">Takeoff</label>
        <textarea
          value={formData.takeoff}
          onChange={e => setFormData(prev => ({ ...prev, takeoff: e.target.value }))}
          className="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-indigo-500 focus:ring-indigo-500"
          rows={3}
          required
        />
      </div>

      <div>
        <label className="block text-sm font-medium text-gray-700">Turbulence</label>
        <textarea
          value={formData.turbulence}
          onChange={e => setFormData(prev => ({ ...prev, turbulence: e.target.value }))}
          className="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-indigo-500 focus:ring-indigo-500"
          rows={3}
          required
        />
      </div>

      <div>
        <label className="block text-sm font-medium text-gray-700">Touchdown</label>
        <textarea
          value={formData.touchdown}
          onChange={e => setFormData(prev => ({ ...prev, touchdown: e.target.value }))}
          className="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-indigo-500 focus:ring-indigo-500"
          rows={3}
          required
        />
      </div>

      <div>
        <div className="flex items-center justify-between mb-4">
          <label className="block text-sm font-medium text-gray-700">Media</label>
          <div className="flex space-x-2">
            <input
              type="file"
              ref={fileInputRef}
              onChange={handleFileUpload}
              className="hidden"
              accept="image/*,video/*,audio/*"
            />
            <button
              type="button"
              onClick={() => fileInputRef.current?.click()}
              disabled={uploading}
              className="inline-flex items-center px-3 py-1 border border-transparent text-sm font-medium rounded-md text-white bg-green-600 hover:bg-green-700"
            >
              <Upload className="h-4 w-4 mr-1" />
              {uploading ? 'Uploading...' : 'Upload File'}
            </button>
            <button
              type="button"
              onClick={handleAddMediaLink}
              className="inline-flex items-center px-3 py-1 border border-transparent text-sm font-medium rounded-md text-white bg-indigo-600 hover:bg-indigo-700"
            >
              <Plus className="h-4 w-4 mr-1" /> Add Link
            </button>
          </div>
        </div>

        <div className="space-y-4">
          {formData.media_links.map((link, index) => (
            <div key={index} className="flex items-center gap-4">
              <select
                value={link.media_type}
                onChange={e => handleMediaLinkChange(index, 'media_type', e.target.value)}
                className="block w-1/4 rounded-md border-gray-300 shadow-sm focus:border-indigo-500 focus:ring-indigo-500"
              >
                <option value="youtube">YouTube</option>
                <option value="image">Image</option>
                <option value="video">Video</option>
                <option value="audio">Audio</option>
                <option value="text">Text</option>
              </select>
              <input
                type="text"
                value={link.url}
                onChange={e => handleMediaLinkChange(index, 'url', e.target.value)}
                placeholder="Enter URL"
                className="block w-2/3 rounded-md border-gray-300 shadow-sm focus:border-indigo-500 focus:ring-indigo-500"
              />
              <button
                type="button"
                onClick={() => handleRemoveMediaLink(index)}
                className="p-2 text-red-600 hover:text-red-800"
              >
                <Minus className="h-5 w-5" />
              </button>
            </div>
          ))}
        </div>
      </div>

      <div className="flex justify-end">
        <button
          type="submit"
          disabled={isLoading || uploading}
          className="inline-flex items-center px-4 py-2 border border-transparent text-sm font-medium rounded-md shadow-sm text-white bg-indigo-600 hover:bg-indigo-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-indigo-500"
        >
          {isLoading ? 'Saving...' : 'Save Story'}
        </button>
      </div>
    </form>
  );
}