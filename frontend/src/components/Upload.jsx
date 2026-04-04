/**
 * Upload Component - True Glassmorphism Design - PREMIUM
 *
 * Design Philosophy:
 * - Premium glass material with enhanced realism
 * - Subtle light falloff, stronger top highlight
 * - Embedded feel with proper hierarchy
 */
import { useState, useEffect, useCallback, useRef } from 'react';
import { uploadResume, parseResumeText } from '../api';

// TRUE GLASSMORPHISM DESIGN SYSTEM - SLATE + TEAL
// Cool, modern SaaS interface with teal as primary accent
const DS = {
  colors: {
    light: {
      base: '#F8FAFC',
      baseCenter: '#F1F5F9',
      baseEdge: '#E2E8F0',
      surface: 'rgba(255, 255, 255, 0.70)',
      surfaceElevated: 'rgba(255, 255, 255, 0.80)',
      surfaceSolid: '#FFFFFF',
      surfaceAlt: 'rgba(255, 255, 255, 0.60)',
      text: '#0F172A',
      textMuted: '#64748B',
      textDim: '#94A3B8',
      border: 'rgba(255, 255, 255, 0.15)',
      borderElevated: 'rgba(255, 255, 255, 0.25)',
      borderLight: 'rgba(255, 255, 255, 0.40)',
      borderDark: 'rgba(15, 23, 42, 0.06)',
      accent: '#14B8A6',
      accentSoft: 'rgba(20, 184, 166, 0.12)',
      accentHover: '#0D9488',
      lightGradient: 'linear-gradient(to bottom, rgba(255,255,255,0.22), rgba(255,255,255,0.05))',
    },
    dark: {
      base: '#0B1220',
      baseCenter: '#131C2F',
      baseEdge: '#080D18',
      surface: 'rgba(255, 255, 255, 0.08)',
      surfaceElevated: 'rgba(255, 255, 255, 0.10)',
      surfaceSolid: '#1E293B',
      surfaceAlt: 'rgba(255, 255, 255, 0.05)',
      text: '#E2E8F0',
      textMuted: '#94A3B8',
      textDim: '#64748B',
      border: 'rgba(255, 255, 255, 0.08)',
      borderElevated: 'rgba(255, 255, 255, 0.12)',
      borderLight: 'rgba(255, 255, 255, 0.20)',
      borderDark: 'rgba(15, 23, 42, 0.25)',
      accent: '#14B8A6',
      accentSoft: 'rgba(20, 184, 166, 0.15)',
      accentHover: '#0D9488',
      lightGradient: 'linear-gradient(to bottom, rgba(255,255,255,0.12), rgba(255,255,255,0.03))',
    },
  },
  radius: {
    sm: '8px',
    md: '10px',
    lg: '12px',
    xl: '16px',
    '2xl': '20px',
  },
  spacing: {
    sm: '8px',
    md: '12px',
    lg: '16px',
  },
  shadow: {
    float: '0 25px 80px rgba(0, 0, 0, 0.35)',
    soft: '0 4px 16px rgba(0, 0, 0, 0.04)',
    // Light mode shadow - elevated, not blended
    lightMd: '0 12px 36px rgba(0, 0, 0, 0.10)',
    // Refined inner highlights - stronger for top edge
    innerLight: 'inset 0 1px rgba(255, 255, 255, 0.16)',
    innerDark: 'inset 0 1px rgba(0, 0, 0, 0.05)',
  },
  transition: 'all 200ms cubic-bezier(0.4, 0, 0.2, 1)',
};

const Upload = ({ onUploadComplete, colors }) => {
  const [file, setFile] = useState(null);
  const [isDragging, setIsDragging] = useState(false);
  const [isProcessing, setIsProcessing] = useState(false);
  const [parseMode, setParseMode] = useState('file');
  const [parseText, setParseText] = useState('');
  const [error, setError] = useState('');
  const [success, setSuccess] = useState(false);

  const fileInputRef = useRef(null);

  const currentColors = colors || DS.colors.light;

  // Update CSS custom properties when colors change
  useEffect(() => {
    const root = document.documentElement;
    root.style.setProperty('--ds-primary', currentColors.accent);
    root.style.setProperty('--ds-primary-soft', currentColors.accentSoft);
    root.style.setProperty('--ds-text', currentColors.text);
    root.style.setProperty('--ds-text-muted', currentColors.textMuted);
    root.style.setProperty('--ds-text-light', currentColors.textDim || currentColors.textMuted);
    root.style.setProperty('--ds-border', currentColors.border);
    root.style.setProperty('--ds-border-elevated', currentColors.borderElevated);
    root.style.setProperty('--ds-border-light', currentColors.borderLight);
    root.style.setProperty('--ds-border-dark', currentColors.borderDark || currentColors.border);
    root.style.setProperty('--ds-surface', currentColors.surface);
    root.style.setProperty('--ds-surface-elevated', currentColors.surfaceElevated);
    root.style.setProperty('--ds-surface-alt', currentColors.surfaceAlt);
    root.style.setProperty('--ds-surface-gradient', currentColors.lightGradient);
    root.style.setProperty('--ds-shadow-float', DS.shadow.float);
    root.style.setProperty('--ds-shadow-inner-light', DS.shadow.innerLight);
    root.style.setProperty('--ds-shadow-inner-dark', DS.shadow.innerDark);
  }, [currentColors]);

  const handleDragOver = useCallback((e) => {
    e.preventDefault();
    setIsDragging(true);
  }, []);

  const handleDragLeave = useCallback((e) => {
    e.preventDefault();
    setIsDragging(false);
  }, []);

  const handleDrop = useCallback((e) => {
    e.preventDefault();
    setIsDragging(false);

    const droppedFile = e.dataTransfer.files[0];
    if (droppedFile && (droppedFile.type === 'application/pdf' || droppedFile.name.endsWith('.pdf') || droppedFile.name.endsWith('.docx'))) {
      setFile(droppedFile);
      setError('');
    } else {
      setError('Please upload a PDF or DOCX file');
    }
  }, []);

  const handleFileSelect = (e) => {
    const selectedFile = e.target.files[0];
    e.target.value = '';
    if (selectedFile && (selectedFile.type === 'application/pdf' || selectedFile.name.endsWith('.pdf') || selectedFile.name.endsWith('.docx'))) {
      setFile(selectedFile);
      setError('');
    } else {
      setError('Please upload a PDF or DOCX file');
    }
  };

  const handleRemoveFile = () => {
    setFile(null);
    setError('');
  };

  const handleProcessResume = async () => {
    if (parseMode === 'file') {
      if (!file) {
        setError('Please select a file first');
        return;
      }

      setIsProcessing(true);
      setError('');

      try {
        const result = await uploadResume(file);
        setSuccess(true);
        if (onUploadComplete) {
          onUploadComplete(result.resume_id, result.extracted_data);
        }
      } catch (err) {
        setError(err.response?.data?.detail || 'Failed to parse resume');
      } finally {
        setIsProcessing(false);
      }
    } else {
      if (!parseText.trim()) {
        setError('Please enter resume text');
        return;
      }

      setIsProcessing(true);
      setError('');

      try {
        const result = await parseResumeText(parseText);
        setSuccess(true);
        if (onUploadComplete) {
          onUploadComplete(result.resume_id, result.extracted_data);
        }
      } catch (err) {
        setError(err.response?.data?.detail || 'Failed to parse resume text');
      } finally {
        setIsProcessing(false);
      }
    }
  };

  const handleReset = () => {
    setFile(null);
    setParseText('');
    setError('');
    setSuccess(false);
    setIsProcessing(false);
  };

  return (
    <div className="ds-upload-section">
      {/* Header */}
      <div className="ds-upload-header">
        <div className="ds-upload-title-group">
          <h2 className="ds-upload-title">Upload Your Resume</h2>
          <p className="ds-upload-subtitle">Get matched with the best jobs for your skills</p>
        </div>

        {/* Parse mode toggle */}
        <div className="ds-parse-mode-toggle" role="tablist" aria-label="Upload mode">
          <button
            className={`ds-parse-mode-btn ${parseMode === 'file' ? 'ds-parse-mode-btn-active' : ''}`}
            onClick={() => setParseMode('file')}
            disabled={isProcessing}
            role="tab"
            aria-selected={parseMode === 'file'}
          >
            <svg className="ds-btn-icon" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke={currentColors.textMuted} strokeWidth="2">
              <path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z" />
              <polyline points="14 2 14 8 20 8" />
              <line x1="16" y1="13" x2="8" y2="13" />
              <line x1="16" y1="17" x2="8" y2="17" />
              <polyline points="10 9 9 9 8 9" />
            </svg>
            <span>Upload File</span>
          </button>
          <button
            className={`ds-parse-mode-btn ${parseMode === 'text' ? 'ds-parse-mode-btn-active' : ''}`}
            onClick={() => setParseMode('text')}
            disabled={isProcessing}
            role="tab"
            aria-selected={parseMode === 'text'}
          >
            <svg className="ds-btn-icon" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke={currentColors.textMuted} strokeWidth="2">
              <path d="M21.6 13.6L13.6 21.6M14 10L2 22" />
              <path d="M7.6 2.4L16.4 11.2" />
              <line x1="2" y1="2" x2="22" y2="22" />
            </svg>
            <span>Paste Text</span>
          </button>
        </div>
      </div>

      {/* Main upload area - Embedded glass */}
      <div className="ds-upload-content">
        {parseMode === 'file' ? (
          <div
            className={`ds-file-drop-zone ${isDragging ? 'ds-file-drop-zone-active' : ''}`}
            onDragOver={handleDragOver}
            onDragLeave={handleDragLeave}
            onDrop={handleDrop}
            role="button"
            tabIndex={0}
            aria-label="Drag and drop resume file here"
            style={{ borderColor: currentColors.borderElevated }}
            onKeyDown={(e) => {
              if (e.key === 'Enter' || e.key === ' ') {
                e.preventDefault();
                fileInputRef.current?.click();
              }
            }}
          >
            <input
              type="file"
              id="file-input"
              ref={fileInputRef}
              accept=".pdf,.docx"
              onChange={handleFileSelect}
              style={{ display: 'none' }}
            />
            <label htmlFor="file-input" className="ds-file-label" role="button" tabIndex={0}>
              {file ? (
                <div className="ds-file-selected" style={{ borderColor: currentColors.accent }}>
                  <div className="ds-file-info">
                    <div className="ds-file-icon-circle" style={{ background: currentColors.accentSoft }}>
                      <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke={currentColors.accent} strokeWidth="2">
                        <path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z" />
                        <polyline points="14 2 14 8 20 8" />
                        <line x1="16" y1="13" x2="8" y2="13" />
                        <line x1="16" y1="17" x2="8" y2="17" />
                        <polyline points="10 9 9 9 8 9" />
                      </svg>
                    </div>
                    <div className="ds-file-details">
                      <span className="ds-file-name">{file.name}</span>
                      <span className="ds-file-size">{(file.size / 1024).toFixed(1)} KB</span>
                    </div>
                  </div>
                  <button
                    onClick={handleRemoveFile}
                    className="ds-remove-btn"
                    title="Remove file"
                    aria-label="Remove file"
                  >
                    <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke={currentColors.textMuted} strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
                      <path d="M18 6L6 18M6 6l12 12" />
                    </svg>
                  </button>
                </div>
              ) : (
                <div className="ds-drop-content" role="button" tabIndex={0} onKeyDown={(e) => {
                  if (e.key === 'Enter' || e.key === ' ') {
                    e.preventDefault();
                    fileInputRef.current?.click();
                  }
                }}>
                  <div className="ds-upload-icon-circle">
                    <span className="ds-upload-icon">📂</span>
                  </div>
                  <p className="ds-drop-title">Drag & drop your resume here</p>
                  <p className="ds-or-text">or</p>
                  <button
                    type="button"
                    onClick={() => fileInputRef.current?.click()}
                    className="ds-browse-btn"
                    style={{ background: currentColors.accent }}
                  >
                    Browse Files
                  </button>
                  <p className="ds-file-hint">Supported: PDF, DOCX (max 10MB)</p>
                </div>
              )}
            </label>
          </div>
        ) : (
          <div className="ds-text-paste-zone">
            <textarea
              value={parseText}
              onChange={(e) => setParseText(e.target.value)}
              placeholder="Paste your resume text here..."
              disabled={isProcessing}
              rows={8}
              className="ds-text-input"
              aria-label="Paste resume text"
              style={{
                borderColor: currentColors.borderElevated,
                color: currentColors.text,
              }}
            />
          </div>
        )}
      </div>

      {/* Error and success messages */}
      {error && (
        <div className="ds-error-banner" role="alert" aria-live="assertive" style={{ borderColor: currentColors.accent, color: currentColors.accent }}>
          <svg className="ds-error-icon" width="18" height="18" viewBox="0 0 24 24" fill="none" stroke={currentColors.accent} strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
            <circle cx="12" cy="12" r="10" />
            <line x1="12" y1="8" x2="12" y2="12" />
            <line x1="12" y1="16" x2="12.01" y2="16" />
          </svg>
          <span className="ds-error-text">{error}</span>
          <button className="ds-error-close" onClick={() => setError('')} aria-label="Close error" style={{ color: currentColors.textMuted }}>
            <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
              <line x1="18" y1="6" x2="6" y2="18" />
              <line x1="6" y1="6" x2="18" y2="18" />
            </svg>
          </button>
        </div>
      )}
      {success && (
        <div className="ds-success-banner" role="status" aria-live="polite" style={{ borderColor: currentColors.accent, color: currentColors.accent }}>
          <svg className="ds-success-icon" width="18" height="18" viewBox="0 0 24 24" fill="none" stroke={currentColors.accent} strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
            <path d="M22 11.08V12a10 10 0 1 1-5.93-9.14" />
            <polyline points="22 4 12 14.01 9 11.01" />
          </svg>
          <span className="ds-success-text">Resume processed successfully!</span>
        </div>
      )}

      {/* Action buttons */}
      <div className="ds-upload-actions">
        <button
          className="ds-process-btn"
          onClick={handleProcessResume}
          disabled={isProcessing || (!file && parseMode === 'file') || (!parseText && parseMode === 'text')}
          style={{
            background: currentColors.accent,
            color: 'white',
          }}
        >
          {isProcessing ? (
            <span className="ds-loading-spinner" aria-label="Processing">
              <span></span>
              <span></span>
              <span></span>
            </span>
          ) : (
            <>
              <svg className="ds-btn-icon" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" style={{ marginRight: '8px' }}>
                <path d="M21 12a9 9 0 0 1-9 9m9-9a9 9 0 0 0-9-9m9 9H3m9 9a9 9 0 0 1-9-9m9 9c1.657 0 3-4.03 3-9s-1.343-9-3-9m0 18c-1.657 0-3-4.03-3-9s1.343-9 3-9m-9 9a9 9 0 0 1 9-9" />
              </svg>
              Process Resume
            </>
          )}
        </button>

        {/* Reset button (only show after success) */}
        {success && (
          <button className="ds-reset-btn" onClick={handleReset}>
            Upload Another Resume
          </button>
        )}
      </div>

      <style>{`
        .ds-upload-section {
          max-width: 560px;
          margin: 0 auto;
          padding: 28px;
          background: var(--ds-surface-elevated);
          /* Soft light falloff */
          background-image: var(--ds-surface-gradient);
          border-radius: ${DS.radius['2xl']};
          backdrop-filter: blur(28px);
          -webkit-backdrop-filter: blur(28px);
          /* Soft integration - barely visible border, inset shadow for depth */
          border: 1px solid rgba(255, 248, 240, 0.12);
          box-shadow: ${DS.shadow.float}, var(--ds-shadow-inner-light);
        }

        .dark-mode .ds-upload-section {
          background: var(--ds-surface-elevated);
          background-image: var(--ds-surface-gradient);
          border-color: rgba(255, 255, 255, 0.10);
          box-shadow: ${DS.shadow.float}, var(--ds-shadow-inner-light);
        }

        /* Light mode - very subtle elevation */
        :not(.dark-mode) .ds-upload-section {
          border-color: rgba(255, 248, 240, 0.15);
          box-shadow: 0 8px 24px rgba(0, 0, 0, 0.06), var(--ds-shadow-inner-light);
        }

        .ds-upload-header {
          margin-bottom: ${DS.spacing.lg};
        }

        .ds-upload-title-group h2 {
          text-align: center;
          color: var(--ds-text);
          margin-bottom: 6px;
          font-weight: 600;
          font-size: 1.5rem;
          letter-spacing: -0.02em;
        }

        .dark-mode .ds-upload-title-group h2 {
          color: var(--ds-text);
        }

        .ds-upload-subtitle {
          text-align: center;
          color: var(--ds-text-muted);
          margin: 0;
          font-size: 0.9rem;
          font-weight: 400;
        }

        .dark-mode .ds-upload-subtitle {
          color: var(--ds-text-muted);
        }

        .ds-parse-mode-toggle {
          display: flex;
          gap: 4px;
          margin-top: ${DS.spacing.lg};
          padding: 5px;
          background: var(--ds-surface);
          border-radius: ${DS.radius.lg};
          border: 1px solid var(--ds-border-elevated);
        }

        .dark-mode .ds-parse-mode-toggle {
          background: var(--ds-surface);
          border-color: var(--ds-border-elevated);
        }

        .ds-parse-mode-btn {
          flex: 1;
          display: flex;
          align-items: center;
          justify-content: center;
          gap: 6px;
          padding: 10px 14px;
          border: none;
          background: transparent;
          border-radius: ${DS.radius.sm};
          cursor: pointer;
          font-size: 0.85rem;
          font-weight: 500;
          color: var(--ds-text-muted);
          transition: all 220ms cubic-bezier(0.4, 0, 0.2, 1);
        }

        .dark-mode .ds-parse-mode-btn {
          color: var(--ds-text-muted);
        }

        .ds-parse-mode-btn:hover:not(:disabled) {
          color: var(--ds-text);
          background: var(--ds-surface-alt);
        }

        .dark-mode .ds-parse-mode-btn:hover:not(:disabled) {
          color: var(--ds-text);
          background: var(--ds-surface-alt);
        }

        .ds-parse-mode-btn-active {
          background: var(--ds-primary);
          color: white;
        }

        .dark-mode .ds-parse-mode-btn-active {
          background: var(--ds-primary);
          color: white;
        }

        .ds-parse-mode-btn:disabled {
          opacity: 0.4;
          cursor: not-allowed;
        }

        .ds-btn-icon {
          flex-shrink: 0;
        }

        .ds-upload-content {
          margin-bottom: ${DS.spacing.lg};
        }

        /* Fully integrated embedded glass drop zone - no nested box feel */
        .ds-file-drop-zone {
          /* Subtle warm border for warm light mode integration */
          border: 1px solid rgba(255, 248, 240, 0.08);
          border-radius: ${DS.radius.xl};
          padding: 30px 24px;
          text-align: center;
          transition: all 200ms cubic-bezier(0.4, 0, 0.2, 1);
          cursor: pointer;
          position: relative;
          margin-bottom: 20px;
          box-shadow: inset 0 1px 2px rgba(0, 0, 0, 0.02);
        }

        .dark-mode .ds-file-drop-zone {
          border: 1px solid rgba(255, 255, 255, 0.04);
          box-shadow: inset 0 1px 2px rgba(0, 0, 0, 0.05);
        }

        .ds-file-drop-zone:hover {
          border: 1px solid rgba(255, 248, 240, 0.10);
          box-shadow: inset 0 1px 3px rgba(0, 0, 0, 0.03);
        }

        .dark-mode .ds-file-drop-zone:hover {
          border: 1px solid rgba(255, 255, 255, 0.06);
        }

        .ds-file-drop-zone-active {
          border: 1px solid rgba(255, 248, 240, 0.12);
          box-shadow: inset 0 1px 4px rgba(0, 0, 0, 0.04);
          transform: scale(1.005);
        }

        .dark-mode .ds-file-drop-zone-active {
          border: 1px solid rgba(255, 255, 255, 0.07);
        }

        .ds-file-label {
          display: block;
          cursor: pointer;
        }

        .ds-file-selected {
          display: flex;
          align-items: center;
          justify-content: space-between;
          padding: 16px;
          /* Subtle warm tint background */
          background: rgba(255, 248, 240, 0.06);
          border-radius: ${DS.radius.lg};
          border: 1px solid rgba(255, 248, 240, 0.08);
          margin: 16px 0;
          box-shadow: inset 0 1px 2px rgba(0, 0, 0, 0.03);
        }

        .dark-mode .ds-file-selected {
          background: rgba(255, 255, 255, 0.03);
          border: 1px solid rgba(255, 255, 255, 0.04);
          box-shadow: inset 0 1px 2px rgba(0, 0, 0, 0.05);
        }

        .ds-file-info {
          display: flex;
          align-items: center;
          gap: 12px;
        }

        .ds-file-icon-circle {
          width: 40px;
          height: 40px;
          display: flex;
          align-items: center;
          justify-content: center;
          border-radius: ${DS.radius.sm};
        }

        .ds-file-details {
          display: flex;
          flex-direction: column;
        }

        .ds-file-name {
          font-weight: 500;
          color: var(--ds-text);
          font-size: 0.9rem;
        }

        .dark-mode .ds-file-name {
          color: var(--ds-text);
        }

        .ds-file-size {
          color: var(--ds-text-muted);
          font-size: 0.8rem;
        }

        .dark-mode .ds-file-size {
          color: var(--ds-text-muted);
        }

        .ds-remove-btn {
          background: none;
          border: none;
          color: var(--ds-text-muted);
          cursor: pointer;
          padding: 6px;
          border-radius: ${DS.radius.sm};
          transition: all 220ms cubic-bezier(0.4, 0, 0.2, 1);
          display: flex;
          align-items: center;
          justify-content: center;
        }

        .dark-mode .ds-remove-btn {
          color: var(--ds-text-muted);
        }

        .ds-remove-btn:hover {
          background: rgba(0, 0, 0, 0.05);
          color: var(--ds-text-light);
        }

        .dark-mode .ds-remove-btn:hover {
          background: rgba(255, 255, 255, 0.05);
          color: var(--ds-text-light);
        }

        .ds-drop-content {
          display: flex;
          flex-direction: column;
          align-items: center;
          gap: 16px;
        }

        .ds-upload-icon-circle {
          width: 64px;
          height: 64px;
          display: flex;
          align-items: center;
          justify-content: center;
          background: rgba(255, 255, 255, 0.06);
          border-radius: 50%;
          margin-bottom: 20px;
        }

        .dark-mode .ds-upload-icon-circle {
          background: rgba(255, 255, 255, 0.04);
        }

        .ds-upload-icon {
          font-size: 3rem;
        }

        .ds-drop-title {
          margin: 0;
          color: var(--ds-text-muted);
          font-size: 1rem;
          font-weight: 500;
        }

        .dark-mode .ds-drop-title {
          color: var(--ds-text-muted);
        }

        .ds-or-text {
          font-weight: 500;
          color: var(--ds-text-light);
          font-size: 0.85rem;
        }

        .dark-mode .ds-or-text {
          color: var(--ds-text-light);
        }

        .ds-browse-btn {
          padding: 10px 28px;
          color: white;
          border: none;
          border-radius: ${DS.radius.sm};
          cursor: pointer;
          font-size: 0.95rem;
          font-weight: 500;
          transition: all 200ms cubic-bezier(0.4, 0, 0.2, 1);
        }

        .dark-mode .ds-browse-btn {
          color: white;
        }

        .ds-browse-btn:hover {
          transform: translateY(-2px);
          filter: brightness(1.1);
        }

        .ds-file-hint {
          font-size: 0.8rem;
          color: var(--ds-text-light);
          margin-top: 6px;
        }

        .dark-mode .ds-file-hint {
          color: var(--ds-text-light);
        }

        .ds-text-paste-zone {
          margin-bottom: 16px;
        }

        .ds-text-input {
          width: 100%;
          padding: 14px;
          border-radius: ${DS.radius.xl};
          font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Inter, sans-serif;
          font-size: 0.95rem;
          resize: vertical;
          box-sizing: border-box;
          transition: all 200ms cubic-bezier(0.4, 0, 0.2, 1);
          /* Subtle warm background */
          background: rgba(255, 248, 240, 0.05);
          min-height: 140px;
          border: 1px solid rgba(255, 248, 240, 0.08);
          box-shadow: inset 0 1px 2px rgba(0, 0, 0, 0.02);
        }

        .dark-mode .ds-text-input {
          background: rgba(255, 255, 255, 0.03);
          border: 1px solid rgba(255, 255, 255, 0.04);
        }

        .ds-text-input:focus {
          outline: none;
          background: rgba(255, 255, 255, 0.06);
          border-color: var(--ds-primary);
          box-shadow: inset 0 1px 3px rgba(0, 0, 0, 0.04), 0 0 0 3px rgba(255, 255, 255, 0.08);
        }

        .dark-mode .ds-text-input:focus {
          background: rgba(255, 255, 255, 0.04);
        }

        .ds-text-input::placeholder {
          color: var(--ds-text-light);
        }

        .dark-mode .ds-text-input::placeholder {
          color: var(--ds-text-light);
        }

        .ds-error-banner, .ds-success-banner {
          display: flex;
          align-items: center;
          gap: 12px;
          padding: 12px 16px;
          border-radius: ${DS.radius.lg};
          margin-bottom: ${DS.spacing.lg};
          font-size: 0.9rem;
          border: 1px solid rgba(255, 255, 255, 0.08);
          background: rgba(255, 255, 255, 0.06);
        }

        .dark-mode .ds-error-banner, .dark-mode .ds-success-banner {
          background: rgba(255, 255, 255, 0.04);
          border: 1px solid rgba(255, 255, 255, 0.06);
        }

        .ds-error-icon, .ds-success-icon {
          flex-shrink: 0;
        }

        .ds-error-text, .ds-success-text {
          flex: 1;
          font-weight: 500;
        }

        .ds-error-close {
          background: transparent;
          border: none;
          cursor: pointer;
          padding: 4px;
          border-radius: ${DS.radius.sm};
          display: flex;
          align-items: center;
          justify-content: center;
          transition: all 220ms cubic-bezier(0.4, 0, 0.2, 1);
        }

        .ds-error-close:hover {
          background: rgba(0, 0, 0, 0.1);
          transform: scale(1.1);
        }

        .dark-mode .ds-error-close:hover {
          background: rgba(255, 255, 255, 0.1);
        }

        .ds-upload-actions {
          display: flex;
          flex-direction: column;
          gap: 12px;
        }

        .ds-process-btn, .ds-reset-btn {
          width: 100%;
          padding: 12px 20px;
          border: none;
          border-radius: ${DS.radius.lg};
          font-size: 0.95rem;
          font-weight: 500;
          cursor: pointer;
          transition: all 220ms cubic-bezier(0.4, 0, 0.2, 1);
          display: flex;
          align-items: center;
          justify-content: center;
          letter-spacing: 0.01em;
        }

        .ds-process-btn {
          box-shadow: 0 4px 16px rgba(0, 0, 0, 0.12);
        }

        .dark-mode .ds-process-btn {
          box-shadow: 0 4px 16px rgba(0, 0, 0, 0.08);
        }

        .ds-process-btn:hover:not(:disabled) {
          transform: translateY(-2px);
          box-shadow: 0 6px 20px rgba(0, 0, 0, 0.15);
        }

        .dark-mode .ds-process-btn:hover:not(:disabled) {
          box-shadow: 0 6px 20px rgba(0, 0, 0, 0.10);
        }

        .ds-process-btn:disabled {
          opacity: 0.5;
          cursor: not-allowed;
          transform: none;
          box-shadow: none;
        }

        .ds-reset-btn {
          background: rgba(255, 255, 255, 0.06);
          color: var(--ds-text-muted);
          border: 1px solid rgba(255, 255, 255, 0.08);
          padding: 12px 20px;
          border-radius: ${DS.radius.lg};
          font-size: 0.95rem;
          font-weight: 500;
          cursor: pointer;
          transition: all 200ms cubic-bezier(0.4, 0, 0.2, 1);
          display: flex;
          align-items: center;
          justify-content: center;
        }

        .dark-mode .ds-reset-btn {
          background: rgba(255, 255, 255, 0.04);
          border: 1px solid rgba(255, 255, 255, 0.06);
        }

        .ds-reset-btn:hover {
          background: rgba(217, 119, 6, 0.12);
          color: var(--ds-primary);
          border-color: var(--ds-primary);
          transform: translateY(-2px);
        }

        .dark-mode .ds-reset-btn:hover {
          background: rgba(245, 158, 11, 0.10);
          color: var(--ds-primary);
        }

        .ds-loading-spinner {
          display: inline-flex;
          gap: 6px;
          vertical-align: middle;
        }

        .ds-loading-spinner span {
          width: 8px;
          height: 8px;
          background: white;
          border-radius: 50%;
          animation: ds-bounce 0.6s infinite;
        }

        .ds-loading-spinner span:nth-child(1) { animation-delay: 0s; }
        .ds-loading-spinner span:nth-child(2) { animation-delay: 0.15s; }
        .ds-loading-spinner span:nth-child(3) { animation-delay: 0.3s; }

        @keyframes ds-bounce {
          0%, 60%, 100% { transform: translateY(0); }
          30% { transform: translateY(-4px); }
        }

        @media (max-width: 600px) {
          .ds-upload-section {
            padding: 20px 16px;
          }

          .ds-parse-mode-toggle {
            flex-direction: column;
          }

          .ds-file-selected {
            flex-direction: column;
            text-align: center;
            gap: 12px;
          }

          .ds-upload-actions .ds-reset-btn {
            order: -1;
            margin-bottom: 10px;
          }

          .ds-upload-title-group h2 {
            font-size: 1.25rem;
          }

          .ds-file-drop-zone {
            padding: 32px 16px;
          }

          .ds-upload-icon-circle {
            width: 56px;
            height: 56px;
          }

          .ds-upload-icon {
            font-size: 2.5rem;
          }
        }
      `}</style>
    </div>
  );
};

export default Upload;
