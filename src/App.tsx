import React, { useState } from 'react';
import { PlusCircle } from 'lucide-react';
import { Story } from './types';
import StoryForm from './components/StoryForm';
import StoryCard from './components/StoryCard';
import Layout from './components/Layout';
import Modal from './components/Modal';
import { useStories } from './hooks/useStories';
import { Toaster } from 'react-hot-toast';

function App() {
  const { stories, isLoading, createStory, updateStory, deleteStory } = useStories();
  const [isFormOpen, setIsFormOpen] = useState(false);
  const [editingStory, setEditingStory] = useState<Story | null>(null);

  const handleSubmit = async (data: Omit<Story, 'id'>) => {
    const success = editingStory?.id
      ? await updateStory(editingStory.id, data)
      : await createStory(data);

    if (success) {
      setIsFormOpen(false);
      setEditingStory(null);
    }
  };

  const handleEdit = (story: Story) => {
    setEditingStory(story);
    setIsFormOpen(true);
  };

  const handleDelete = async (id: number) => {
    if (window.confirm('Are you sure you want to delete this story?')) {
      await deleteStory(id);
    }
  };

  return (
    <Layout>
      <Toaster position="top-right" />
      
      <div className="flex justify-end mb-8">
        <button
          onClick={() => {
            setIsFormOpen(true);
            setEditingStory(null);
          }}
          className="inline-flex items-center px-4 py-2 border border-transparent text-sm font-medium rounded-md shadow-sm text-white bg-indigo-600 hover:bg-indigo-700"
        >
          <PlusCircle className="h-5 w-5 mr-2" />
          New Story
        </button>
      </div>

      <Modal
        isOpen={isFormOpen}
        onClose={() => {
          setIsFormOpen(false);
          setEditingStory(null);
        }}
        title={editingStory ? 'Edit Story' : 'New Story'}
      >
        <StoryForm
          initialData={editingStory || undefined}
          onSubmit={handleSubmit}
          isLoading={isLoading}
        />
      </Modal>

      <div className="grid grid-cols-1 gap-6 sm:grid-cols-2 lg:grid-cols-3">
        {stories.map(story => (
          <StoryCard
            key={story.id}
            story={story}
            onEdit={handleEdit}
            onDelete={handleDelete}
          />
        ))}
      </div>

      {stories.length === 0 && (
        <div className="text-center py-12">
          <p className="text-gray-500">No stories yet. Create your first story!</p>
        </div>
      )}
    </Layout>
  );
}

export default App;