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
  const [selectedFile, setSelectedFile] = useState<{ name: string; path: string; type: string; content?: string } | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [useFallback, setUseFallback] = useState(false);
  const fileInputRef = useRef<HTMLInputElement>(null);

  if (!isOpen) return null;

  const handleNativeFileSelect = async () => {
    // Check if running in Tauri (Desktop)
    // @ts-ignore
    const isTauri = !!(window.__TAURI__ || window.__TAURI_INTERNALS__);

    if (!isTauri || useFallback) {
      // Browser or Fallback: Click hidden input immediately (sync) to avoid popup blocker
      fileInputRef.current?.click();
      return;
    }

    // Desktop: Try native dialog
    try {
      const result = await open({
        multiple: false,
        filters: [{
          name: 'Financial Documents',
          extensions: ['pdf', 'txt', 'csv', 'xbrl', 'xml', 'xlsx']
        }]
      });

      if (result && typeof result === 'string') {
        const fileName = result.split('/').pop() || result.split('\\').pop() || 'document';
        const ext = fileName.split('.').pop()?.toLowerCase() || '';

        setSelectedFile({
          name: fileName,
          path: result,
          type: ext
        });
        setError(null);
      } else if (result === null) {
        // User cancelled, do nothing
      }
    } catch (e) {
      console.warn('Native file dialog failed. Enabling fallback.', e);
      setUseFallback(true);
      // We cannot trigger click() reliably in async catch on some platforms. 
      // Ask user to retry which will hit the sync path.
      setError("System picker failed. Click this area again to use the browser selector.");
    }
  };

  const handleUpload = async () => {
    if (!selectedFile) return;

    setIsProcessing(true);
    setError(null);

    try {
      await new Promise(resolve => setTimeout(resolve, 500));
      onUploadSuccess(selectedFile.path, selectedFile.type, selectedFile.name, selectedFile.content);
      onClose();
    } catch (e) {
      setError('Failed to process file');
    } finally {
      setIsProcessing(false);
    }
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
      <div className="relative w-full max-w-lg glass-modal p-6 animate-fadeInScale">
        {/* Header */}
        <div className="flex items-center justify-between mb-6">
          <div>
            <h2 className="text-lg font-semibold text-primary">Upload Document</h2>
            <p className="text-sm text-tertiary mt-0.5">Select a financial document to analyze</p>
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
          onDrop={(e) => { e.preventDefault(); setIsDragging(false); }}
          className={`relative border-2 border-dashed rounded-2xl p-8 text-center cursor-pointer transition-all ${isDragging
            ? 'border-[var(--accent-primary)] bg-[var(--accent-primary)]/5'
            : selectedFile
              ? 'border-[var(--color-success)] bg-[var(--color-success-bg)]'
              : 'border-[var(--border-default)] hover:border-[var(--border-strong)] hover:bg-[var(--bg-hover)]'
            }`}
        >
          {selectedFile ? (
            <div className="flex flex-col items-center animate-fadeIn">
              {getFileIcon(selectedFile.type)}
              <p className="text-sm font-medium text-primary mt-3">{selectedFile.name}</p>
              <p className="text-xs text-tertiary mt-1">Click to change file</p>
            </div>
          ) : (
            <div className="flex flex-col items-center">
              <div className="w-16 h-16 rounded-2xl bg-[var(--accent-primary)]/10 flex items-center justify-center mb-4">
                <Upload className="w-7 h-7 text-accent" />
              </div>
              <p className="text-sm font-medium text-primary">Click to select a file</p>
              <p className="text-xs text-tertiary mt-1">PDF, CSV, TXT, XLSX, XBRL supported</p>
            </div>
          )}
        </div>

        {/* Hidden File Input for Browser Fallback */}
        <input
          type="file"
          ref={fileInputRef}
          className="hidden"
          accept=".pdf,.txt,.csv,.xbrl,.xml,.xlsx"
          onChange={(e) => {
            const file = e.target.files?.[0];
            if (file) {
              const fileName = file.name;
              const ext = fileName.split('.').pop()?.toLowerCase() || '';

              const reader = new FileReader();
              reader.onload = () => {
                const result = reader.result as string;
                const base64Content = result.includes(',') ? result.split(',')[1] : result;

                setSelectedFile({
                  name: fileName,
                  path: file.name,
                  type: ext,
                  content: base64Content
                });
              };
              reader.readAsDataURL(file);

              setError(null);
            }
          }}
        />

        {/* Error */}
        {error && (
          <div className="flex items-center gap-2 mt-4 p-3 rounded-xl bg-[var(--color-error-bg)] border border-[var(--color-error-border)] animate-fadeIn">
            <AlertCircle className="w-4 h-4 text-error flex-shrink-0" />
            <p className="text-sm text-error">{error}</p>
          </div>
        )}

        {/* Actions */}
        <div className="flex items-center justify-end gap-3 mt-6">
          <button onClick={onClose} className="btn-secondary">
            Cancel
          </button>
          <button
            onClick={handleUpload}
            disabled={!selectedFile || isProcessing}
            className="btn-primary"
          >
            {isProcessing ? (
              <>
                <Loader2 className="w-4 h-4 animate-spin" />
                <span>Processing...</span>
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
