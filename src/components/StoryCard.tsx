import React from 'react';
import { Story } from '../types';
import { Edit, Trash2 } from 'lucide-react';

interface StoryCardProps {
  story: Story;
  onEdit: (story: Story) => void;
  onDelete: (id: number) => void;
}

export default function StoryCard({ story, onEdit, onDelete }: StoryCardProps) {
  const renderMedia = (mediaLink: Story['media_links'][0]) => {
    switch (mediaLink.media_type) {
      case 'youtube':
        return (
          <iframe
            width="100%"
            height="200"
            src={mediaLink.url}
            frameBorder="0"
            allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture"
            allowFullScreen
          />
        );
      case 'image':
        return (
          <img
            src={mediaLink.url}
            alt="Story media"
            className="w-full h-48 object-cover rounded-md"
          />
        );
      case 'video':
        return (
          <video controls className="w-full">
            <source src={mediaLink.url} />
            Your browser does not support the video element.
          </video>
        );
      case 'audio':
        return (
          <audio controls className="w-full">
            <source src={mediaLink.url} />
            Your browser does not support the audio element.
          </audio>
        );
      case 'text':
        return (
          <div className="p-4 bg-gray-50 rounded-md">
            <p className="text-sm text-gray-600">{mediaLink.url}</p>
          </div>
        );
      default:
        return null;
    }
  };

  return (
    <div className="bg-white rounded-lg shadow-md overflow-hidden">
      <div className="p-6">
        <div className="flex justify-between items-start mb-4">
          <h2 className="text-xl font-bold text-gray-900">{story.title}</h2>
          <div className="flex space-x-2">
            <button
              onClick={() => onEdit(story)}
              className="p-2 text-blue-600 hover:text-blue-800"
            >
              <Edit className="h-5 w-5" />
            </button>
            <button
              onClick={() => story.id && onDelete(story.id)}
              className="p-2 text-red-600 hover:text-red-800"
            >
              <Trash2 className="h-5 w-5" />
            </button>
          </div>
        </div>

        <div className="space-y-4">
          <div>
            <h3 className="text-lg font-semibold text-gray-700">Takeoff</h3>
            <p className="mt-1 text-gray-600">{story.takeoff}</p>
          </div>

          <div>
            <h3 className="text-lg font-semibold text-gray-700">Turbulence</h3>
            <p className="mt-1 text-gray-600">{story.turbulence}</p>
          </div>

          <div>
            <h3 className="text-lg font-semibold text-gray-700">Touchdown</h3>
            <p className="mt-1 text-gray-600">{story.touchdown}</p>
          </div>

          {story.media_links.length > 0 && (
            <div>
              <h3 className="text-lg font-semibold text-gray-700 mb-2">Media</h3>
              <div className="grid grid-cols-1 gap-4">
                {story.media_links.map((link, index) => (
                  <div key={index} className="border rounded-md p-2">
                    {renderMedia(link)}
                  </div>
                ))}
              </div>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}