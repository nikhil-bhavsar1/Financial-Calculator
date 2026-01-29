import React, { useRef, useState } from 'react';
import { Upload, X, FileText, File, Loader2, CheckCircle, AlertCircle } from 'lucide-react';
import { open } from '@tauri-apps/plugin-dialog';

interface UploadModalProps {
  isOpen: boolean;
  onClose: () => void;
  onUploadSuccess: (filePath: string, type: string, fileName: string, content?: string) => void;
}

export const UploadModal: React.FC<UploadModalProps> = ({ isOpen, onClose, onUploadSuccess }) => {
  const [isDragging, setIsDragging] = useState(false);
  const [isProcessing, setIsProcessing] = useState(false);
  const [selectedFiles, setSelectedFiles] = useState<{ name: string; path: string; type: string; content?: string }[]>([]);
  const [error, setError] = useState<string | null>(null);
  const [useFallback, setUseFallback] = useState(false);
  const fileInputRef = useRef<HTMLInputElement>(null);

  if (!isOpen) return null;

  const handleNativeFileSelect = async () => {
    fileInputRef.current?.click();
  };

  const processFiles = (fileList: FileList | File[]) => {
    const newFiles = Array.from(fileList);
    const processedFiles: { name: string; path: string; type: string; content?: string }[] = [];

    let processedCount = 0;

    newFiles.forEach(file => {
      const fileName = file.name;
      const ext = fileName.split('.').pop()?.toLowerCase() || '';

      const reader = new FileReader();
      reader.onload = () => {
        const result = reader.result as string;
        const base64Content = result.includes(',') ? result.split(',')[1] : result;

        processedFiles.push({
          name: fileName,
          path: file.name, // Use name as path for display/reference
          type: ext,
          content: base64Content
        });

        processedCount++;
        if (processedCount === newFiles.length) {
          setSelectedFiles(prev => [...prev, ...processedFiles]);
          setError(null);
        }
      };
      reader.readAsDataURL(file);
    });
  };

  const handleUpload = async () => {
    if (selectedFiles.length === 0) return;

    // Close immediately to show processing state in main UI
    onClose();

    try {
      // Process files one by one
      for (const file of selectedFiles) {
        await onUploadSuccess(file.path, file.type, file.name, file.content);
      }
    } catch (e) {
      console.error('Upload failed:', e);
      // In a real app, you might want to show a global toast notification here
    }
  };

  const removeFile = (index: number) => {
    setSelectedFiles(prev => prev.filter((_, i) => i !== index));
  };

  const getFileIcon = (type: string) => {
    if (type === 'pdf') return <FileText className="w-8 h-8 text-error" />;
    return <File className="w-8 h-8 text-info" />;
  };

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center p-4">
      {/* Backdrop */}
      <div
        className="absolute inset-0 bg-black/40 backdrop-blur-sm animate-fadeIn"
        onClick={onClose}
      />

      {/* Modal */}
      <div className="relative w-full max-w-lg glass-modal p-6 animate-fadeInScale flex flex-col max-h-[90vh]">
        {/* Header */}
        <div className="flex items-center justify-between mb-6 shrink-0">
          <div>
            <h2 className="text-lg font-semibold text-primary">Upload Document</h2>
            <p className="text-sm text-tertiary mt-0.5">Select financial documents to analyze</p>
          </div>
          <button onClick={onClose} className="btn-icon">
            <X className="w-5 h-5" />
          </button>
        </div>

        {/* Drop Zone */}
        <div
          onClick={handleNativeFileSelect}
          onDragOver={(e) => { e.preventDefault(); setIsDragging(true); }}
          onDragLeave={() => setIsDragging(false)}
          onDrop={(e) => {
            e.preventDefault();
            setIsDragging(false);
            if (e.dataTransfer.files && e.dataTransfer.files.length > 0) {
              processFiles(e.dataTransfer.files);
            }
          }}
          className={`relative border-2 border-dashed rounded-2xl p-8 text-center cursor-pointer transition-all shrink-0 ${isDragging
            ? 'border-[var(--accent-primary)] bg-[var(--accent-primary)]/5'
            : 'border-[var(--border-default)] hover:border-[var(--border-strong)] hover:bg-[var(--bg-hover)]'
            }`}
        >
          <div className="flex flex-col items-center">
            <div className="w-16 h-16 rounded-2xl bg-[var(--accent-primary)]/10 flex items-center justify-center mb-4">
              <Upload className="w-7 h-7 text-accent" />
            </div>
            <p className="text-sm font-medium text-primary">Click to select files</p>
            <p className="text-xs text-tertiary mt-1">PDF, CSV, TXT, XLSX, XBRL, MD supported</p>
          </div>
        </div>

        {/* Selected Files List */}
        {selectedFiles.length > 0 && (
          <div className="mt-4 flex-1 overflow-y-auto custom-scrollbar min-h-0 border-t border-[var(--border-default)] pt-4">
            <h3 className="text-xs font-semibold text-tertiary uppercase tracking-wider mb-2">Selected Files ({selectedFiles.length})</h3>
            <div className="space-y-2">
              {selectedFiles.map((file, idx) => (
                <div key={idx} className="flex items-center justify-between p-3 rounded-lg bg-[var(--bg-surface)] border border-[var(--border-default)] animate-fadeIn">
                  <div className="flex items-center gap-3 overflow-hidden">
                    {getFileIcon(file.type)}
                    <div className="min-w-0">
                      <p className="text-sm font-medium text-primary truncate">{file.name}</p>
                      <p className="text-xs text-tertiary">{Math.round((file.content?.length || 0) * 0.75 / 1024)} KB</p>
                    </div>
                  </div>
                  <button
                    onClick={(e) => { e.stopPropagation(); removeFile(idx); }}
                    className="p-1 text-tertiary hover:text-error hover:bg-red-50 dark:hover:bg-red-900/20 rounded transition-colors"
                  >
                    <X className="w-4 h-4" />
                  </button>
                </div>
              ))}
            </div>
          </div>
        )}

        {/* Hidden File Input for Browser Fallback */}
        <input
          type="file"
          ref={fileInputRef}
          className="hidden"
          multiple
          accept=".pdf,.txt,.csv,.xbrl,.xml,.xlsx,.md"
          onChange={(e) => {
            if (e.target.files && e.target.files.length > 0) {
              processFiles(e.target.files);
            }
          }}
        />

        {/* Error */}
        {error && (
          <div className="flex items-center gap-2 mt-4 p-3 rounded-xl bg-[var(--color-error-bg)] border border-[var(--color-error-border)] animate-fadeIn shrink-0">
            <AlertCircle className="w-4 h-4 text-error flex-shrink-0" />
            <p className="text-sm text-error">{error}</p>
          </div>
        )}

        {/* Actions */}
        <div className="flex items-center justify-end gap-3 mt-6 shrink-0">
          <button onClick={onClose} className="btn-secondary">
            Cancel
          </button>
          <button
            onClick={handleUpload}
            disabled={selectedFiles.length === 0 || isProcessing}
            className="btn-primary"
          >
            {isProcessing ? (
              <>
                <Loader2 className="w-4 h-4 animate-spin" />
                <span>Processing {selectedFiles.length} files...</span>
              </>
            ) : (
              <>
                <CheckCircle className="w-4 h-4" />
                <span>Upload & Analyze</span>
              </>
            )}
          </button>
        </div>
      </div>
    </div>
  );
};

export default UploadModal;
