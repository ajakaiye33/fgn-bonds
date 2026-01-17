/**
 * Document Upload Component
 *
 * Handles file upload for payment evidence documents.
 */

import { useState, useRef } from 'react';
import { adminApi } from '../../services/api';

interface DocumentUploadProps {
  paymentId: number;
  onUploaded: () => void;
}

const ALLOWED_TYPES = ['application/pdf', 'image/jpeg', 'image/jpg', 'image/png'];
const MAX_SIZE = 5 * 1024 * 1024; // 5MB

export function DocumentUpload({ paymentId, onUploaded }: DocumentUploadProps) {
  const [isUploading, setIsUploading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [dragActive, setDragActive] = useState(false);
  const fileInputRef = useRef<HTMLInputElement>(null);

  const handleFile = async (file: File) => {
    setError(null);

    // Validate file type
    if (!ALLOWED_TYPES.includes(file.type)) {
      setError('Invalid file type. Please upload PDF, JPG, or PNG files.');
      return;
    }

    // Validate file size
    if (file.size > MAX_SIZE) {
      setError('File too large. Maximum size is 5MB.');
      return;
    }

    setIsUploading(true);
    try {
      await adminApi.uploadDocument(paymentId, file);
      onUploaded();
    } catch (err) {
      console.error('Upload failed:', err);
      setError('Failed to upload document. Please try again.');
    } finally {
      setIsUploading(false);
    }
  };

  const handleDrag = (e: React.DragEvent) => {
    e.preventDefault();
    e.stopPropagation();
    if (e.type === 'dragenter' || e.type === 'dragover') {
      setDragActive(true);
    } else if (e.type === 'dragleave') {
      setDragActive(false);
    }
  };

  const handleDrop = (e: React.DragEvent) => {
    e.preventDefault();
    e.stopPropagation();
    setDragActive(false);

    if (e.dataTransfer.files && e.dataTransfer.files[0]) {
      handleFile(e.dataTransfer.files[0]);
    }
  };

  const handleChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    if (e.target.files && e.target.files[0]) {
      handleFile(e.target.files[0]);
    }
  };

  const handleClick = () => {
    fileInputRef.current?.click();
  };

  return (
    <div>
      <input
        ref={fileInputRef}
        type="file"
        accept=".pdf,.jpg,.jpeg,.png"
        onChange={handleChange}
        className="hidden"
      />

      <div
        className={`border-2 border-dashed rounded-lg p-4 text-center transition-colors cursor-pointer ${
          dragActive
            ? 'border-primary-500 bg-primary-500/10'
            : 'border-dark-border hover:border-dark-text-secondary'
        }`}
        onDragEnter={handleDrag}
        onDragLeave={handleDrag}
        onDragOver={handleDrag}
        onDrop={handleDrop}
        onClick={handleClick}
      >
        {isUploading ? (
          <div className="flex items-center justify-center gap-2">
            <div className="animate-spin w-5 h-5 border-2 border-primary-500 border-t-transparent rounded-full" />
            <span className="text-sm text-dark-text-secondary">Uploading...</span>
          </div>
        ) : (
          <>
            <svg
              className="w-8 h-8 mx-auto text-dark-text-secondary mb-2"
              fill="none"
              viewBox="0 0 24 24"
              stroke="currentColor"
            >
              <path
                strokeLinecap="round"
                strokeLinejoin="round"
                strokeWidth={2}
                d="M7 16a4 4 0 01-.88-7.903A5 5 0 1115.9 6L16 6a5 5 0 011 9.9M15 13l-3-3m0 0l-3 3m3-3v12"
              />
            </svg>
            <p className="text-sm text-dark-text-secondary">
              Drag and drop or{' '}
              <span className="text-primary-500">click to browse</span>
            </p>
            <p className="text-xs text-dark-text-secondary mt-1">
              PDF, JPG, PNG (max 5MB)
            </p>
          </>
        )}
      </div>

      {error && <p className="text-sm text-error mt-2">{error}</p>}
    </div>
  );
}
