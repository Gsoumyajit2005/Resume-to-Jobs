/**
 * JobList Component - True Glassmorphism Design - PREMIUM
 *
 * Design Philosophy:
 * - Premium glass material with enhanced realism
 * - Subtle light falloff, stronger top highlight
 * - Embedded feel with proper hierarchy
 */
import { useState, useEffect, useRef } from 'react';
import { searchJobs, matchJobs, applyToJob } from '../api';

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
      // Success, warning, danger - all teal-based variants
      success: '#14B8A6',
      successSoft: 'rgba(20, 184, 166, 0.12)',
      warning: '#0D9488',
      warningSoft: 'rgba(13, 148, 136, 0.12)',
      danger: '#E11D48',
      dangerSoft: 'rgba(225, 29, 72, 0.12)',
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
      success: '#14B8A6',
      successSoft: 'rgba(20, 184, 166, 0.15)',
      warning: '#0D9488',
      warningSoft: 'rgba(13, 148, 136, 0.15)',
      danger: '#F43F5E',
      dangerSoft: 'rgba(244, 63, 94, 0.15)',
      lightGradient: 'linear-gradient(to bottom, rgba(255,255,255,0.12), rgba(255,255,255,0.03))',
    },
  },
  spacing: {
    xs: '4px',
    sm: '8px',
    md: '12px',
    lg: '16px',
    xl: '24px',
    '2xl': '32px',
  },
  radius: {
    sm: '8px',
    md: '10px',
    lg: '12px',
    xl: '16px',
    '2xl': '20px',
    full: '50%',
  },
  shadow: {
    float: '0 25px 80px rgba(0, 0, 0, 0.35)',
    soft: '0 4px 16px rgba(0, 0, 0, 0.04)',
    md: '0 8px 32px rgba(0, 0, 0, 0.10)',
    lg: '0 16px 48px rgba(0, 0, 0, 0.18)',
    // Light mode shadow - elevated, not blended (increased for lifted feel)
    lightMd: '0 12px 36px rgba(0, 0, 0, 0.10)',
    // Refined inner highlights - stronger for top edge
    innerLight: 'inset 0 1px rgba(255, 255, 255, 0.16)',
    innerDark: 'inset 0 1px rgba(0, 0, 0, 0.05)',
  },
  transition: 'all 200ms cubic-bezier(0.4, 0, 0.2, 1)',
};

// Score thresholds and labels - will be computed dynamically based on theme
const getScoreLevels = (colors) => ({
  excellent: { min: 80, color: colors.success, soft: colors.successSoft, label: 'Excellent Match' },
  good: { min: 60, color: colors.warning, soft: colors.warningSoft, label: 'Good Match' },
  fair: { min: 40, color: colors.warning, soft: colors.warningSoft, label: 'Fair Match' },
  poor: { min: 0, color: colors.danger, soft: colors.dangerSoft, label: 'Low Match' },
});

/**
 * Score Badge - Circular progress with color-coded status
 */
const ScoreBadge = ({ score, colors }) => {
  const currentColors = colors || DS.colors.light;
  if (!score) return null;

  const getLevel = (s) => {
    if (s >= 80) return 'excellent';
    if (s >= 60) return 'good';
    if (s >= 40) return 'fair';
    return 'poor';
  };

  const level = getLevel(score);
  const config = getScoreLevels(currentColors)[level];

  return (
    <div
      className="ds-score-badge"
      role="img"
      aria-label={`Match score: ${score}%. ${config.label}`}
    >
      <div className="ds-score-circle" style={{ '--score-color': config.color }}>
        <svg className="ds-score-ring" viewBox="0 0 36 36">
          <path
            className="ds-score-bg"
            d="M18 2.0845 a 15.9155 15.9155 0 0 1 0 31.831 a 15.9155 15.9155 0 0 1 0 -31.831"
            fill="none"
            stroke={currentColors.border}
            strokeWidth="3"
          />
          <path
            className="ds-score-progress"
            d="M18 2.0845 a 15.9155 15.9155 0 0 1 0 31.831 a 15.9155 15.9155 0 0 1 0 -31.831"
            fill="none"
            stroke="var(--score-color)"
            strokeWidth="3"
            strokeDasharray={`${score}, 100`}
          />
        </svg>
        <span className="ds-score-value">{score}%</span>
      </div>
      <span className="ds-score-label">{config.label}</span>
    </div>
  );
};

/**
 * Tag Component - Reusable tag pill for skills
 */
const Tag = ({ children, variant = 'default', onClick, className = '' }) => {
  const variants = {
    default: 'ds-tag-default',
    success: 'ds-tag-success',
    warning: 'ds-tag-warning',
    muted: 'ds-tag-muted',
  };

  return (
    <span
      className={`ds-tag ${variants[variant]} ${className}`}
      onClick={onClick}
      role={onClick ? 'button' : 'span'}
      tabIndex={onClick ? 0 : undefined}
    >
      {children}
    </span>
  );
};

/**
 * Button Component - Reusable button with variants
 */
const Button = ({ children, variant = 'primary', size = 'md', onClick, disabled, icon: Icon, className = '' }) => {
  const base = 'ds-btn';
  const variants = {
    primary: 'ds-btn-primary',
    secondary: 'ds-btn-secondary',
    ghost: 'ds-btn-ghost',
    icon: 'ds-btn-icon',
  };
  const sizes = {
    sm: 'ds-btn-sm',
    md: 'ds-btn-md',
    lg: 'ds-btn-lg',
  };

  return (
    <button
      className={`${base} ${variants[variant]} ${sizes[size]} ${className}`}
      onClick={onClick}
      disabled={disabled}
      type="button"
    >
      {Icon && <Icon className="ds-btn-icon" />}
      <span className="ds-btn-text">{children}</span>
    </button>
  );
};

/**
 * Card Component - Base card wrapper
 */
const Card = ({ children, className = '', ...props }) => (
  <div className={`ds-card ${className}`} {...props}>
    {children}
  </div>
);

/**
 * Skills Section Component
 */
const SkillsSection = ({ matched, missing, colors }) => {
  const currentColors = colors || DS.colors.light;
  const [showAll, setShowAll] = useState(false);

  const safeMatched = Array.isArray(matched) ? matched : [];
  const safeMissing = Array.isArray(missing) ? missing : [];

  const visibleMatched = showAll ? safeMatched : safeMatched.slice(0, 5);
  const hiddenMatched = safeMatched.length - visibleMatched.length;

  const visibleMissing = safeMissing.slice(0, 3);
  const hiddenMissing = safeMissing.length - visibleMissing.length;

  return (
    <div className="ds-skills-section">
      {/* Matched Skills */}
      {safeMatched.length > 0 && (
        <div className="ds-skills-group">
          <h4 className="ds-skills-title">
            <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke={currentColors.success} strokeWidth="2.5" strokeLinecap="round" strokeLinejoin="round">
              <path d="M22 11.08V12a10 10 0 1 1-5.93-9.14" />
              <polyline points="22 4 12 14.01 9 11.01" />
            </svg>
            <span>Skills Match</span>
          </h4>
          <div className="ds-skills-list">
            {visibleMatched.map((skill, idx) => (
              <Tag key={idx} variant="success">{skill}</Tag>
            ))}
            {hiddenMatched > 0 && (
              <button
                className="ds-tag ds-tag-ghost"
                onClick={() => setShowAll(true)}
                aria-label={`Show ${hiddenMatched} more skills`}
              >
                +{hiddenMatched} more
              </button>
            )}
          </div>
        </div>
      )}

      {/* Missing Skills */}
      {safeMissing.length > 0 && (
        <div className="ds-skills-group ds-skills-missing">
          <h4 className="ds-skills-title">
            <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke={currentColors.danger} strokeWidth="2.5" strokeLinecap="round" strokeLinejoin="round">
              <circle cx="12" cy="12" r="10" />
              <line x1="15" y1="9" x2="9" y2="15" />
              <line x1="9" y1="9" x2="15" y2="15" />
            </svg>
            <span>Missing</span>
          </h4>
          <div className="ds-skills-list">
            {visibleMissing.map((skill, idx) => (
              <Tag key={idx} variant="warning">{skill}</Tag>
            ))}
            {hiddenMissing > 0 && (
              <Tag variant="muted">+{hiddenMissing} more</Tag>
            )}
          </div>
        </div>
      )}
    </div>
  );
};

/**
 * Job Card Component
 */
const JobCard = ({ job, match, rank, onApply, onSave, colors }) => {
  const currentColors = colors || DS.colors.light;
  const score = match?.match_score;
  const reason = match?.reason;
  const matchedSkills = Array.isArray(match?.matched_skills) ? match.matched_skills : [];
  const missingSkills = Array.isArray(match?.missing_skills) ? match.missing_skills : [];
  const [isHovered, setIsHovered] = useState(false);
  const [isSaved, setIsSaved] = useState(match?.saved || false);

  const jobTitleRef = useRef(null);

  const handleSave = (e) => {
    e.stopPropagation();
    const newSaved = !isSaved;
    setIsSaved(newSaved);
    onSave?.({ ...job, saved: newSaved });
  };

  return (
    <Card
      className={`ds-job-card ${score !== undefined ? 'ds-job-card-matched' : ''} ${isHovered ? 'ds-job-card-hovered' : ''}`}
      onMouseEnter={() => setIsHovered(true)}
      onMouseLeave={() => setIsHovered(false)}
      tabIndex={0}
      aria-labelledby={`job-title-${job.id}`}
    >
      {/* Rank Badge (only for matched jobs) */}
      {score !== undefined && (
        <div className="ds-rank-badge" aria-label={`Rank #${rank}`}>
          <span>{rank}</span>
        </div>
      )}

      <div className="ds-job-content">
        {/* Header Row */}
        <div className="ds-job-header">
          <div className="ds-job-primary">
            <h3 className="ds-job-title" ref={jobTitleRef} title={job.title}>
              {job.title}
            </h3>
            <div className="ds-job-meta">
              <span className="ds-company-name">{job.company}</span>
              {job.location && (
                <span className="ds-job-location" title={job.location}>
                  <svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke={currentColors.textMuted} strokeWidth="2">
                    <path d="M21 10c0 7-9 13-9 13s-9-6-9-13a9 9 0 0 1 18 0z" />
                    <circle cx="12" cy="10" r="3" />
                  </svg>
                  {job.location}
                </span>
              )}
              {job.posted_date && (
                <time className="ds-job-date" dateTime={job.posted_date}>
                  {new Date(job.posted_date).toLocaleDateString('en-US', { month: 'short', day: 'numeric' })}
                </time>
              )}
            </div>
          </div>

          {score !== undefined && (
            <div className="ds-job-score">
              <ScoreBadge score={score} colors={currentColors} />
            </div>
          )}
        </div>

        {/* Match Reason (Insight) */}
        {reason && score !== undefined && (
          <div className="ds-job-insight" role="note">
            <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke={currentColors.primary} strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
              <circle cx="12" cy="12" r="10" />
              <path d="M9.09 9a3 3 0 0 1 5.83 1c0 2-3 3-3 3" />
              <path d="M12 17h.01" />
            </svg>
            <p className="ds-insight-text">{reason}</p>
          </div>
        )}

        {/* Skills */}
        {(matchedSkills.length > 0 || missingSkills.length > 0) && (
          <div className="ds-job-skills">
            <SkillsSection matched={matchedSkills} missing={missingSkills} colors={currentColors} />
          </div>
        )}

        {/* Footer */}
        <div className="ds-job-footer">
          <div className="ds-job-source">
            {job.source && <span className="ds-job-source-tag">{job.source}</span>}
            {job.source && job.location && <span className="ds-separator">•</span>}
            {job.job_type && <span className="ds-job-type-tag">{job.job_type}</span>}
          </div>

          <div className="ds-job-actions">
            <button
              className="ds-save-btn"
              onClick={handleSave}
              aria-label={isSaved ? 'Remove from saved jobs' : 'Save this job'}
              aria-pressed={isSaved}
              title={isSaved ? 'Remove from saved' : 'Save job'}
            >
              <svg
                width="18" height="18" viewBox="0 0 24 24"
                fill={isSaved ? currentColors.danger : 'none'}
                stroke={isSaved ? currentColors.danger : currentColors.textMuted}
                strokeWidth="2"
                strokeLinecap="round" strokeLinejoin="round"
              >
                <path d="M19 21l-7-5-7 5V5a2 2 0 0 1 2-2h10a2 2 0 0 1 2 2z" />
              </svg>
              <span className="ds-save-label">{isSaved ? 'Saved' : 'Save'}</span>
            </button>
            <Button
              variant="primary"
              size="sm"
              onClick={(e) => {
                e.stopPropagation();
                onApply(job.apply_url);
              }}
              icon={() => (
                <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
                  <path d="M4 4h16c1.1 0 2 .9 2 2v12c0 1.1-.9 2-2 2H4c-1.1 0-2-.9-2-2V6c0-1.1.9-2 2-2z" />
                  <polyline points="16 6 16 12 8 12 8 18" />
                </svg>
              )}
            >
              Apply Now
            </Button>
          </div>
        </div>
      </div>
    </Card>
  );
};

/**
 * Main JobList Component
 */
const JobList = ({ resumeId, resumeData, colors, theme }) => {
  const [searchQuery, setSearchQuery] = useState('');
  const [location, setLocation] = useState('');
  const [jobs, setJobs] = useState([]);
  const [matches, setMatches] = useState([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const [searchMode, setSearchMode] = useState('search');
  const [filter, setFilter] = useState('all');
  const [hasSearched, setHasSearched] = useState(false);

  // Use passed colors or fallback to light theme defaults
  const currentColors = colors || DS.colors.light;
  const currentTheme = theme || 'light';

  // Update CSS variables when theme changes
  useEffect(() => {
    const colors = currentTheme === 'dark' ? DS.colors.dark : DS.colors.light;
    const root = document.documentElement;
    root.style.setProperty('--ds-primary', colors.primary);
    root.style.setProperty('--ds-primary-hover', colors.primaryHover);
    root.style.setProperty('--ds-primary-soft', colors.primarySoft);
    root.style.setProperty('--ds-success', colors.success);
    root.style.setProperty('--ds-success-soft', colors.successSoft);
    root.style.setProperty('--ds-warning', colors.warning);
    root.style.setProperty('--ds-warning-soft', colors.warningSoft);
    root.style.setProperty('--ds-danger', colors.danger);
    root.style.setProperty('--ds-danger-soft', colors.dangerSoft);
    root.style.setProperty('--ds-text', colors.text);
    root.style.setProperty('--ds-text-muted', colors.textMuted);
    root.style.setProperty('--ds-text-light', colors.textDim || colors.textMuted);
    root.style.setProperty('--ds-border', colors.border);
    root.style.setProperty('--ds-border-soft', colors.borderSoft);
    root.style.setProperty('--ds-surface', colors.surface);
    root.style.setProperty('--ds-surface-alt', colors.surfaceAlt);
  }, [currentTheme]);

  useEffect(() => {
    if (resumeData?.preferred_roles?.length > 0) {
      setSearchQuery(resumeData.preferred_roles[0]);
    }
  }, [resumeData]);

  // Search Jobs Handler
  const handleSearch = async () => {
    if (!searchQuery.trim()) {
      setError('Please enter a job role to search');
      return;
    }

    setFilter('all');
    setHasSearched(true);
    setLoading(true);
    setError('');

    try {
      const response = await searchJobs({
        role: searchQuery,
        location: location || null,
        skills: resumeData?.skills || [],
        maxResults: 20,
      });
      setJobs(response.jobs || []);
      setMatches([]);
      setSearchMode('search');
    } catch (err) {
      setError(String(err.response?.data?.detail || err.message || 'Failed to search jobs'));
    } finally {
      setLoading(false);
    }
  };

  // Match Jobs Handler
  const handleMatch = async () => {
    if (!resumeId) {
      setError('Please upload a resume first');
      return;
    }

    setFilter('all');
    setHasSearched(true);
    setLoading(true);
    setError('');

    try {
      const response = await matchJobs({
        resumeId,
        role: searchQuery || resumeData?.preferred_roles?.[0] || null,
        location: location || null,
      });
      setMatches(response.matched_jobs || []);
      setJobs([]);
      setSearchMode('match');
    } catch (err) {
      setError(String(err.response?.data?.detail || err.message || 'Failed to match jobs'));
    } finally {
      setLoading(false);
    }
  };

  // Apply to job
  const handleApply = (url) => applyToJob(url);

  // Save job toggle
  const handleSaveJob = (updatedJob) => {
    setMatches((prev) =>
      prev.map((m) => (m.job.id === updatedJob.id ? { ...m, saved: updatedJob.saved } : m))
    );
  };

  // Filter matches
  const filteredMatches = matches.filter((match) => {
    if (filter === 'all') return true;
    if (filter === 'excellent') return match.match_score >= 80;
    if (filter === 'good') return match.match_score >= 60;
    if (filter === 'fair') return match.match_score >= 40;
    return match.match_score < 40;
  });

  // Filter counts for pill badges - calculated from FULL matches, not filtered
  const filterCounts = {
    all: matches.length,
    excellent: matches.filter((m) => m.match_score >= 80).length,
    good: matches.filter((m) => m.match_score >= 60 && m.match_score < 80).length,
    fair: matches.filter((m) => m.match_score >= 40 && m.match_score < 60).length,
    poor: matches.filter((m) => m.match_score < 40).length,
  };

  const totalJobs = searchMode === 'search' ? jobs.length : filteredMatches.length;

  // Filter options
  const filterOptions = [
    { id: 'all', label: 'All', count: filterCounts.all },
    { id: 'excellent', label: 'Excellent', count: filterCounts.excellent },
    { id: 'good', label: 'Good', count: filterCounts.good },
    { id: 'fair', label: 'Fair', count: filterCounts.fair },
    { id: 'poor', label: 'Low', count: filterCounts.poor },
  ];

  return (
    <div className="ds-job-list-section" role="main" aria-label="Job discovery and search">
      {/* Search Control Bar */}
      <div className="ds-search-bar">
        <div className="ds-search-inputs">
          <div className="ds-search-input-group">
            <svg className="ds-search-icon" width="18" height="18" viewBox="0 0 24 24" fill="none" stroke={currentColors.textMuted} strokeWidth="2">
              <path d="M21 21l-5.197-5.197m0 0A7.5 7.5 0 105.196 5.196a7.5 7.5 0 0010.607 10.607z" />
            </svg>
            <input
              type="text"
              className="ds-search-input"
              placeholder="Job title, skills, or keywords"
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              disabled={loading}
              aria-label="Job title or keywords"
              onKeyDown={(e) => e.key === 'Enter' && handleSearch()}
            />
          </div>
          <div className="ds-search-input-group ds-search-input-compact">
            <svg className="ds-search-icon" width="18" height="18" viewBox="0 0 24 24" fill="none" stroke={currentColors.textMuted} strokeWidth="2">
              <path d="M15 10l4.553-2.276A1 1 0 0121 8.618v6.764a1 1 0 01-1.447.894L15 14M5 18h8a2 2 0 002-2V8a2 2 0 00-2-2H5a2 2 0 00-2 2v8a2 2 0 002 2z" />
            </svg>
            <input
              type="text"
              className="ds-search-input"
              placeholder="Location (optional)"
              value={location}
              onChange={(e) => setLocation(e.target.value)}
              disabled={loading}
              aria-label="Job location"
            />
          </div>
        </div>
        <div className="ds-search-actions">
          <Button variant="primary" size="md" onClick={handleSearch} disabled={loading} icon={() => (
            <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
              <circle cx="11" cy="11" r="8" />
              <path d="m21 21-4.3-4.3" />
            </svg>
          )}>
            {loading ? 'Searching...' : 'Search Jobs'}
          </Button>
          {resumeId && (
            <Button variant="secondary" size="md" onClick={handleMatch} disabled={loading} icon={() => (
              <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                <path d="m9 11 3 3L22 4" />
                <path d="M21 12v7a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2h11" />
              </svg>
            )}>
              {loading ? 'Analyzing...' : 'AI Match Jobs'}
            </Button>
          )}
        </div>
      </div>

      {/* Error Banner */}
      {error && (
        <div className="ds-error-banner" role="alert" aria-live="assertive">
          <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke={currentColors.danger} strokeWidth="2">
            <circle cx="12" cy="12" r="10" />
            <line x1="12" y1="8" x2="12" y2="12" />
            <line x1="12" y1="16" x2="12.01" y2="16" />
          </svg>
          <span className="ds-error-text">{error}</span>
          <button className="ds-error-close" onClick={() => setError('')} aria-label="Close error">
            <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
              <line x1="18" y1="6" x2="6" y2="18" />
              <line x1="6" y1="6" x2="18" y2="18" />
            </svg>
          </button>
        </div>
      )}

      {/* Filter Bar */}
      {searchMode === 'match' && (
        <div className="ds-filter-bar" role="group" aria-label="Filter jobs by match score">
          <div className="ds-filter-content">
            <span className="ds-filter-label">Score:</span>
            <div className="ds-filter-pill-group">
              {filterOptions.map((f) => (
                <button
                  key={f.id}
                  className={`ds-filter-pill ${filter === f.id ? 'ds-filter-pill-active' : ''}`}
                  onClick={() => setFilter(f.id)}
                  aria-pressed={filter === f.id}
                  aria-label={`${f.label} matches (${f.count} jobs)`}
                >
                  <span className="ds-filter-pill-label">{f.label}</span>
                  <span className="ds-filter-pill-count">{f.count}</span>
                </button>
              ))}
            </div>
          </div>
          <div className="ds-filter-summary">
            <span className="ds-filter-count">{filteredMatches.length}</span>
            <span className="ds-filter-label">jobs found</span>
          </div>
        </div>
      )}

      {/* Results Container */}
      <div className="ds-jobs-container" role="list" aria-label="Job results">
        {(searchMode === 'search' ? jobs : filteredMatches).map((item, idx) => {
          const actualJob = searchMode === 'match' ? item.job : item;
          const actualMatch = searchMode === 'match' ? item : null;

          return (
            <JobCard
              key={actualJob.id}
              job={actualJob}
              match={actualMatch}
              rank={idx + 1}
              onApply={handleApply}
              onSave={handleSaveJob}
              colors={currentColors}
            />
          );
        })}

        {/* Empty State */}
        {(searchMode === 'search' ? jobs.length : filteredMatches.length) === 0 && hasSearched && !loading && (
          <div className="ds-empty-state">
            {searchMode === 'search' ? (
              <div className="ds-empty-icon">
                <svg width="64" height="64" viewBox="0 0 24 24" fill="none" stroke={currentColors.textMuted} strokeWidth="1.5">
                  <path d="M21 21l-5.197-5.197m0 0A7.5 7.5 0 105.196 5.196a7.5 7.5 0 0010.607 10.607z" />
                  <path d="M8.5 14.5A2.5 2.5 0 0011 17h2a2.5 2.5 0 002.5-2.5 2.5 2.5 0 00-2.5-2.5h-2A2.5 2.5 0 008.5 14.5z" />
                </svg>
              </div>
            ) : (
              <div className="ds-empty-icon">
                <svg width="64" height="64" viewBox="0 0 24 24" fill="none" stroke={currentColors.textMuted} strokeWidth="1.5">
                  <path d="m9 11 3 3L22 4" />
                  <path d="M21 12v7a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2h11" />
                  <path d="M8 12v5" />
                  <path d="M16 12v5" />
                </svg>
              </div>
            )}
            <h3 className="ds-empty-title">
              {searchMode === 'search' ? 'No jobs found' : 'No matching jobs'}
            </h3>
            <p className="ds-empty-desc">
              {searchMode === 'search'
                ? 'Try adjusting your search terms or location filters'
                : 'Try searching for more jobs or updating your resume'}
            </p>
            <div className="ds-empty-tips">
              <div className="ds-tip-card">
                <span className="ds-tip-icon">💡</span>
                <div className="ds-tip-content">
                  <span className="ds-tip-title">Pro Tip</span>
                  <p className="ds-tip-text">
                    {searchMode === 'search'
                      ? 'Use broader terms like "Developer" instead of "Senior Developer"'
                      : 'Add more skills to your resume for better AI matches'}
                  </p>
                </div>
              </div>
            </div>
          </div>
        )}

        {/* Loading Skeleton */}
        {loading && (
          <div className="ds-loading-skeleton">
            {[1, 2, 3].map((i) => (
              <div className="ds-skeleton-card" key={i}>
                <div className="ds-skeleton-header">
                  <div className="ds-skeleton-title" />
                  <div className="ds-skeleton-company" />
                </div>
                <div className="ds-skeleton-body">
                  <div className="ds-skeleton-skills" />
                  <div className="ds-skeleton-skills ds-skeleton-short" />
                </div>
                <div className="ds-skeleton-footer">
                  <div className="ds-skeleton-actions" />
                </div>
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  );
};

export default JobList;

/**
 * Modern SaaS Design System Styles
 * Inspired by Linear.app, Vercel, and Notion UI
 */

// Design tokens as CSS variables - SLATE + TEAL
const designTokensCSS = `
  :root {
    /* Colors - Cool slate + teal palette */
    --ds-primary: #14B8A6;
    --ds-primary-hover: #0D9488;
    --ds-primary-soft: rgba(20, 184, 166, 0.12);
    --ds-success: #14B8A6;
    --ds-success-soft: rgba(20, 184, 166, 0.12);
    --ds-warning: #0D9488;
    --ds-warning-soft: rgba(13, 148, 136, 0.12);
    --ds-danger: #E11D48;
    --ds-danger-soft: rgba(225, 29, 72, 0.12);
    --ds-text: #0F172A;
    --ds-text-muted: #64748B;
    --ds-text-light: #94A3B8;
    --ds-border: rgba(255, 255, 255, 0.20);
    --ds-border-soft: rgba(255, 255, 255, 0.10);
    --ds-surface: rgba(255, 255, 255, 0.70);
    --ds-surface-alt: rgba(255, 255, 255, 0.60);

    /* Spacing */
    --ds-xs: 4px;
    --ds-sm: 8px;
    --ds-md: 16px;
    --ds-lg: 24px;
    --ds-xl: 32px;
    --ds-2xl: 40px;
    --ds-3xl: 48px;

    /* Radius */
    --ds-radius-sm: 8px;
    --ds-radius-md: 10px;
    --ds-radius-lg: 14px;
    --ds-radius-xl: 18px;
    --ds-radius-2xl: 24px;

    /* Shadows */
    --ds-shadow-sm: 0 2px 12px rgba(0, 0, 0, 0.06);
    --ds-shadow-md: 0 4px 20px rgba(0, 0, 0, 0.08);
    --ds-shadow-lg: 0 8px 24px rgba(0, 0, 0, 0.1);
    --ds-shadow-xl: 0 12px 32px rgba(0, 0, 0, 0.12);
    --ds-shadow-2xl: 0 20px 48px rgba(0, 0, 0, 0.15);

    /* Transition */
    --ds-transition: all 200ms cubic-bezier(0.4, 0, 0.2, 1);
  }

  /* Dark mode overrides - Deep slate + teal */
  .dark-mode :root {
    --ds-primary: #14B8A6;
    --ds-primary-hover: #0D9488;
    --ds-primary-soft: rgba(20, 184, 166, 0.15);
    --ds-success: #14B8A6;
    --ds-success-soft: rgba(20, 184, 166, 0.15);
    --ds-warning: #0D9488;
    --ds-warning-soft: rgba(13, 148, 136, 0.15);
    --ds-danger: #F43F5E;
    --ds-danger-soft: rgba(244, 63, 94, 0.15);
    --ds-text: #E2E8F0;
    --ds-text-muted: #94A3B8;
    --ds-text-light: #64748B;
    --ds-border: rgba(255, 255, 255, 0.08);
    --ds-border-soft: rgba(255, 255, 255, 0.04);
    --ds-surface: rgba(255, 255, 255, 0.08);
    --ds-surface-alt: rgba(255, 255, 255, 0.05);
  }
`;

// Insert styles at module level (run once)
if (typeof window !== 'undefined' && !document.getElementById('ds-job-list-styles')) {
  const styleEl = document.createElement('style');
  styleEl.id = 'ds-job-list-styles';
  styleEl.textContent = designTokensCSS + `
    /* ==================== JOB LIST SECTION ==================== */
    .ds-job-list-section {
      max-width: 1000px;
      margin: 0 auto;
      padding: 20px;
    }

    /* ==================== SECTION HEADER ==================== */
    .ds-section-header {
      text-align: center;
      margin-bottom: 32px;
    }

    .ds-section-title {
      font-size: 2rem;
      font-weight: 700;
      line-height: 1.2;
      color: var(--ds-text);
      margin-bottom: 8px;
      letter-spacing: -0.02em;
    }

    .ds-section-subtitle {
      color: var(--ds-text-muted);
      font-size: 1rem;
      font-weight: 400;
    }

    /* ==================== SEARCH BAR ==================== */
    .ds-search-bar {
      display: flex;
      gap: 16px;
      margin-bottom: 24px;
      padding: 0;
      background: var(--ds-surface);
      border-radius: var(--ds-radius-xl);
      border: 1px solid var(--ds-border);
      box-shadow: var(--ds-shadow-sm);
      flex-wrap: wrap;
    }

    .ds-search-inputs {
      display: flex;
      gap: 12px;
      flex: 1;
      min-width: 280px;
    }

    .ds-search-input-group {
      flex: 1;
      display: flex;
      align-items: center;
      gap: 10px;
      padding: 10px 14px;
      /* Single clean glass surface - no inner background rectangle */
      border: 1px solid rgba(255, 255, 255, 0.12);
      border-radius: var(--ds-radius-sm);
      transition: var(--ds-transition);
      /* Input sits directly on the glass surface */
    }

    .ds-search-input-group:hover {
      border-color: rgba(255, 255, 255, 0.20);
    }

    .dark-mode .ds-search-input-group:hover {
      border-color: rgba(255, 255, 255, 0.25);
    }

    .ds-search-input-group:focus-within {
      border-color: var(--ds-primary);
      box-shadow: 0 0 0 3px var(--ds-primary-soft);
    }

    .dark-mode .ds-search-input-group:focus-within {
      border-color: var(--ds-primary);
      box-shadow: 0 0 0 3px var(--ds-primary-soft);
    }

    .ds-search-input-compact {
      flex: 0 0 180px;
    }

    .ds-search-icon {
      flex-shrink: 0;
      color: var(--ds-text-muted);
    }

    .ds-search-input {
      flex: 1;
      border: none;
      outline: none;
      font-size: 0.95rem;
      color: var(--ds-text);
      background: transparent;
      appearance: none;
      -webkit-appearance: none;
      -moz-appearance: none;
      box-shadow: none;
    }

    .ds-search-input::placeholder {
      color: var(--ds-text-light);
    }

    .ds-search-input::-webkit-input-placeholder {
      color: var(--ds-text-light);
    }

    .ds-search-input::-moz-placeholder {
      color: var(--ds-text-light);
    }

    .ds-search-actions {
      display: flex;
      gap: 10px;
      flex-shrink: 0;
    }

    /* ==================== BUTTONS ==================== */
    .ds-btn {
      display: inline-flex;
      align-items: center;
      justify-content: center;
      gap: 8px;
      border: none;
      border-radius: var(--ds-radius-sm);
      font-weight: 600;
      font-size: 0.95rem;
      line-height: 1.5;
      cursor: pointer;
      transition: var(--ds-transition);
      position: relative;
      overflow: hidden;
    }

    .ds-btn:hover:not(:disabled) {
      transform: translateY(-1px);
    }

    .ds-btn:active:not(:disabled) {
      transform: translateY(0);
    }

    .ds-btn:disabled {
      opacity: 0.5;
      cursor: not-allowed;
      transform: none;
    }

    .ds-btn-primary {
      padding: 10px 20px;
      background: var(--ds-primary);
      color: white;
      box-shadow: 0 2px 8px rgba(20, 184, 166, 0.25);
    }

    .ds-btn-primary:hover:not(:disabled) {
      background: var(--ds-primary-hover);
      box-shadow: 0 4px 12px rgba(20, 184, 166, 0.35);
    }

    .ds-btn-secondary {
      padding: 10px 20px;
      background: transparent;
      color: var(--ds-primary);
      border: 2px solid var(--ds-primary);
    }

    .ds-btn-secondary:hover:not(:disabled) {
      background: var(--ds-primary-soft);
      box-shadow: 0 2px 8px rgba(20, 184, 166, 0.25);
    }

    .ds-btn-ghost {
      padding: 8px 14px;
      background: transparent;
      color: var(--ds-text-muted);
      border: none;
    }

    .ds-btn-ghost:hover:not(:disabled) {
      background: var(--ds-surface-alt);
      color: var(--ds-text);
    }

    .ds-btn-icon {
      padding: 8px 12px;
      background: transparent;
      color: var(--ds-text);
      border: 1px solid var(--ds-border);
    }

    .ds-btn-icon:hover:not(:disabled) {
      border-color: var(--ds-text-muted);
    }

    .ds-btn-sm {
      padding: 8px 14px;
      font-size: 0.85rem;
      gap: 6px;
    }

    .ds-btn-md {
      padding: 10px 20px;
      font-size: 0.95rem;
    }

    .ds-btn-lg {
      padding: 12px 24px;
      font-size: 1rem;
      gap: 10px;
    }

    .ds-btn-text {
      pointer-events: none;
    }

    .ds-btn-icon .ds-btn-text {
      display: none;
    }

    .ds-btn-sm .ds-btn-text {
      display: inline;
    }

    /* ==================== ERROR BANNER ==================== */
    .ds-error-banner {
      display: flex;
      align-items: center;
      gap: 12px;
      padding: 12px 16px;
      background: #fef2f2;
      border: 1.5px solid #fecaca;
      border-radius: var(--ds-radius-md);
      margin-bottom: 24px;
      animation: ds-slideDown 0.3s ease-out;
    }

    @keyframes ds-slideDown {
      from { opacity: 0; transform: translateY(-8px); }
      to { opacity: 1; transform: translateY(0); }
    }

    .ds-error-text {
      flex: 1;
      font-size: 0.95rem;
      color: var(--ds-danger);
    }

    .ds-error-close {
      background: transparent;
      border: none;
      color: var(--ds-danger);
      cursor: pointer;
      padding: 4px;
      border-radius: var(--ds-radius-sm);
      display: flex;
      align-items: center;
      justify-content: center;
    }

    .ds-error-close:hover {
      background: rgba(239, 68, 68, 0.1);
    }

    /* ==================== FILTER BAR ==================== */
    .ds-filter-bar {
      display: flex;
      align-items: center;
      justify-content: space-between;
      padding: 14px 20px;
      background: var(--ds-surface);
      border-radius: var(--ds-radius-lg);
      border: 1px solid var(--ds-border);
      margin-bottom: 24px;
    }

    .ds-filter-content {
      display: flex;
      align-items: center;
      gap: 16px;
    }

    .ds-filter-label {
      color: var(--ds-text-muted);
      font-weight: 600;
      font-size: 0.85rem;
    }

    .ds-filter-pill-group {
      display: flex;
      gap: 8px;
    }

    .ds-filter-pill {
      display: flex;
      align-items: center;
      gap: 6px;
      padding: 6px 12px;
      border: 1.5px solid var(--ds-border);
      background: var(--ds-surface);
      border-radius: 20px;
      cursor: pointer;
      font-size: 0.85rem;
      font-weight: 600;
      color: var(--ds-text-muted);
      transition: var(--ds-transition);
    }

    .ds-filter-pill:hover {
      border-color: var(--ds-border-soft);
      background: var(--ds-surface-alt);
    }

    .ds-filter-pill-active {
      background: var(--ds-primary);
      border-color: var(--ds-primary);
      color: white;
      box-shadow: 0 2px 8px rgba(99, 102, 241, 0.3);
    }

    .ds-filter-pill-count {
      font-size: 0.75rem;
      opacity: 0.8;
      background: rgba(0, 0, 0, 0.1);
      padding: 2px 6px;
      border-radius: 10px;
    }

    .ds-filter-summary {
      display: flex;
      align-items: center;
      gap: 6px;
      padding-left: 16px;
      border-left: 1px solid var(--ds-border);
    }

    .ds-filter-count {
      font-weight: 700;
      color: var(--ds-primary);
      font-size: 1rem;
    }

    /* ==================== JOBS CONTAINER ==================== */
    .ds-jobs-container {
      display: flex;
      flex-direction: column;
      gap: 16px;
      min-height: 200px;
      padding: 0 14px;
    }

    /* ==================== JOB CARD - Premium Glass with Warm Light ==================== */
    .ds-job-card {
      background: var(--ds-surface);
      /* Soft light falloff for depth */
      background-image: var(--ds-surface-gradient);
      border-radius: var(--ds-radius-xl);
      padding: 0;
      position: relative;
      transition: var(--ds-transition);
      overflow: hidden;
      border: 1px solid var(--ds-border-elevated);
      box-shadow: var(--ds-shadow-md), var(--ds-shadow-inner-light);
    }

    .dark-mode .ds-job-card {
      border-color: var(--ds-border-elevated);
      box-shadow: var(--ds-shadow-md), var(--ds-shadow-inner-light);
    }

    /* Light mode - gentle elevation with warm tint */
    :not(.dark-mode) .ds-job-card {
      border-color: var(--ds-border-light);
      box-shadow: 0 12px 35px rgba(0, 0, 0, 0.08), var(--ds-shadow-inner-light);
    }

    .ds-job-card-matched {
      border-left: 4px solid var(--ds-primary);
    }

    .ds-job-card-hovered {
      box-shadow: var(--ds-shadow-xl), var(--ds-shadow-inner-light);
      border-color: var(--ds-primary);
      transform: translateY(-2px);
    }

    .ds-rank-badge {
      position: absolute;
      top: 20px;
      left: 20px;
      width: 32px;
      height: 32px;
      display: flex;
      align-items: center;
      justify-content: center;
      background: var(--ds-primary);
      color: white;
      border-radius: 50%;
      font-weight: 700;
      font-size: 0.85rem;
      box-shadow: var(--ds-shadow-md);
      z-index: var(--ds.zIndex.badge);
    }

    .ds-job-content {
      padding: 20px 20px 20px 50px;
    }

    /* ==================== JOB HEADER ==================== */
    .ds-job-header {
      display: flex;
      justify-content: space-between;
      align-items: flex-start;
      margin-bottom: 16px;
      gap: 16px;
      padding-left: 50px;
      position: relative;
    }

    .ds-job-primary {
      flex: 1;
      min-width: 0;
    }

    .ds-job-title {
      margin: 0;
      font-size: 1.25rem;
      font-weight: 600;
      line-height: 1.4;
      color: var(--ds-text);
      margin-bottom: 8px;
      cursor: default;
    }

    .ds-job-meta {
      display: flex;
      align-items: center;
      gap: 12px;
      flex-wrap: wrap;
    }

    .ds-company-name {
      font-weight: 600;
      color: var(--ds-text);
      font-size: 0.95rem;
      max-width: 250px;
      white-space: nowrap;
      overflow: hidden;
      text-overflow: ellipsis;
    }

    .ds-job-location {
      display: inline-flex;
      align-items: center;
      gap: 4px;
      color: var(--ds-text-muted);
      font-size: 0.85rem;
      background: var(--ds-surface-alt);
      padding: 4px 8px;
      border-radius: var(--ds-radius-sm);
    }

    .ds-job-date {
      color: var(--ds-text-light);
      font-size: 0.8rem;
      font-variant-numeric: tabular-nums;
    }

    .ds-job-score {
      flex-shrink: 0;
      display: flex;
      flex-direction: column;
      align-items: flex-end;
      min-width: 110px;
    }

    /* ==================== SCORE BADGE ==================== */
    .ds-score-badge {
      display: flex;
      flex-direction: column;
      align-items: center;
      gap: 8px;
    }

    .ds-score-circle {
      position: relative;
      width: 56px;
      height: 56px;
      display: flex;
      align-items: center;
      justify-content: center;
    }

    .ds-score-ring {
      position: absolute;
      top: 0;
      left: 0;
      width: 100%;
      height: 100%;
      transform: rotate(-90deg);
    }

    .ds-score-bg {
      stroke: var(--ds-border);
    }

    .ds-score-progress {
      stroke: var(--score-color);
      transition: stroke-dasharray 0.5s cubic-bezier(0.4, 0, 0.2, 1);
    }

    .ds-score-value {
      position: absolute;
      font-weight: 700;
      font-size: 1rem;
      color: var(--ds-text);
      line-height: 1.2;
    }

    .ds-score-label {
      font-size: 0.75rem;
      font-weight: 600;
      color: var(--ds-text-muted);
      white-space: nowrap;
    }

    /* ==================== JOB INSIGHT ==================== */
    .ds-job-insight {
      display: flex;
      align-items: flex-start;
      gap: 10px;
      padding: 12px 16px;
      background: var(--ds-surface-alt);
      border-radius: var(--ds-radius-md);
      margin-bottom: 16px;
      border-left: 3px solid var(--ds-primary);
    }

    .ds-insight-text {
      margin: 0;
      font-size: 0.95rem;
      font-weight: 400;
      line-height: 1.6;
      color: var(--ds-text-muted);
    }

    /* ==================== SKILLS SECTION ==================== */
    .ds-skills-section {
      margin-bottom: 16px;
    }

    .ds-skills-group {
      margin-bottom: 12px;
    }

    .ds-skills-group:last-child {
      margin-bottom: 0;
    }

    .ds-skills-missing {
      opacity: 0.65;
    }

    .ds-skills-title {
      display: flex;
      align-items: center;
      gap: 8px;
      margin-bottom: 8px;
      font-size: 0.8rem;
      font-weight: 600;
      color: var(--ds-text);
      text-transform: uppercase;
      letter-spacing: 0.05em;
    }

    .ds-skills-title svg {
      flex-shrink: 0;
    }

    .ds-skills-list {
      display: flex;
      flex-wrap: wrap;
      gap: 8px;
    }

    /* ==================== TAGS ==================== */
    .ds-tag {
      display: inline-flex;
      align-items: center;
      padding: 5px 10px;
      border-radius: var(--ds-radius-sm);
      font-size: 0.85rem;
      font-weight: 500;
      white-space: nowrap;
      cursor: default;
      border: 1px solid transparent;
    }

    .ds-tag-default {
      background: var(--ds-surface-alt);
      color: var(--ds-text-muted);
    }

    .ds-tag-success {
      background: var(--ds-success-soft);
      color: var(--ds-success);
      border-color: rgba(16, 185, 129, 0.2);
    }

    .ds-tag-warning {
      background: var(--ds-warning-soft);
      color: var(--ds-warning);
      border-color: rgba(245, 158, 11, 0.2);
    }

    .ds-tag-muted {
      background: var(--ds-surface-alt);
      color: var(--ds-text-light);
    }

    .ds-tag-ghost {
      background: transparent;
      color: var(--ds-primary);
      border: 1px dashed var(--ds-primary);
      cursor: pointer;
    }

    .ds-tag-ghost:hover {
      background: var(--ds-primary-soft);
    }

    /* ==================== JOB FOOTER ==================== */
    .ds-job-footer {
      display: flex;
      justify-content: space-between;
      align-items: center;
      margin-top: 16px;
      padding-top: 16px;
      border-top: 1px solid var(--ds-border);
    }

    .ds-job-source {
      display: flex;
      align-items: center;
      gap: 8px;
      font-size: 0.8rem;
      color: var(--ds-text-muted);
    }

    .ds-job-source-tag,
    .ds-job-type-tag {
      display: inline-flex;
      align-items: center;
      padding: 3px 10px;
      background: var(--ds-surface-alt);
      border-radius: var(--ds-radius-sm);
      font-weight: 500;
    }

    .ds-separator {
      color: var(--ds-border);
    }

    .ds-job-actions {
      display: flex;
      gap: 8px;
    }

    .ds-save-btn {
      display: flex;
      align-items: center;
      gap: 6px;
      padding: 8px 12px;
      border-radius: var(--ds-radius-sm);
      font-size: 0.85rem;
      font-weight: 500;
      cursor: pointer;
      transition: var(--ds-transition);
      background: transparent;
      border: 1px solid var(--ds-border);
      color: var(--ds-text-muted);
    }

    .ds-save-btn:hover {
      border-color: var(--ds-text-muted);
      color: var(--ds-text);
      background: var(--ds-surface-alt);
    }

    .ds-save-btn svg {
      flex-shrink: 0;
    }

    .ds-save-label {
      font-size: 0.85rem;
    }

    /* ==================== EMPTY STATE ==================== */
    .ds-empty-state {
      text-align: center;
      padding: 64px 32px;
      background: var(--ds-surface);
      border-radius: var(--ds-radius-xl);
      border: 2px dashed var(--ds-border);
    }

    .ds-empty-icon {
      margin-bottom: 24px;
      opacity: 0.5;
    }

    .ds-empty-title {
      font-size: 1.5rem;
      font-weight: 600;
      line-height: 1.3;
      color: var(--ds-text);
      margin-bottom: 12px;
    }

    .ds-empty-desc {
      color: var(--ds-text-muted);
      font-size: 1rem;
      margin-bottom: 24px;
      max-width: 400px;
      margin-left: auto;
      margin-right: auto;
    }

    .ds-empty-tips {
      display: flex;
      justify-content: center;
    }

    .ds-tip-card {
      display: flex;
      align-items: flex-start;
      gap: 12px;
      padding: 16px;
      background: var(--ds-surface-alt);
      border-radius: var(--ds-radius-md);
      max-width: 360px;
    }

    .ds-tip-icon {
      font-size: 1.5rem;
      flex-shrink: 0;
    }

    .ds-tip-content {
      text-align: left;
    }

    .ds-tip-title {
      display: block;
      font-weight: 600;
      color: var(--ds-text);
      margin-bottom: 2px;
    }

    .ds-tip-text {
      color: var(--ds-text-muted);
      font-size: 0.9rem;
      margin: 0;
    }

    /* ==================== LOADING SKELETON ==================== */
    .ds-loading-skeleton {
      display: flex;
      flex-direction: column;
      gap: 16px;
      padding: 24px 0;
    }

    .ds-skeleton-card {
      background: var(--ds-surface-alt);
      border-radius: var(--ds-radius-xl);
      padding: 20px;
      animation: ds-skeletonPulse 1.5s ease-in-out infinite;
    }

    @keyframes ds-skeletonPulse {
      0%, 100% { opacity: 1; }
      50% { opacity: 0.6; }
    }

    .ds-skeleton-header {
      display: flex;
      justify-content: space-between;
      margin-bottom: 16px;
    }

    .ds-skeleton-title {
      width: 60%;
      height: 24px;
      background: var(--ds-border);
      border-radius: 4px;
      margin-bottom: 8px;
    }

    .ds-skeleton-company {
      width: 40%;
      height: 16px;
      background: var(--ds-border);
      border-radius: 4px;
    }

    .ds-skeleton-body {
      margin-bottom: 16px;
    }

    .ds-skeleton-skills {
      width: 100%;
      height: 28px;
      background: var(--ds-border);
      border-radius: var(--ds-radius.sm);
      margin-bottom: 8px;
    }

    .ds-skeleton-short {
      width: 60%;
    }

    .ds-skeleton-footer {
      display: flex;
      justify-content: space-between;
    }

    .ds-skeleton-actions {
      width: 120px;
      height: 36px;
      background: var(--ds-border);
      border-radius: var(--ds-radius.sm);
    }

    /* ==================== RESPONSIVE ==================== */
    @media (max-width: 768px) {
      .ds-job-list-section {
        padding: 16px;
      }

      .ds-search-bar {
        flex-direction: column;
        padding: 0;
      }

      .ds-jobs-container {
        padding: 0 14px;
      }

      .ds-search-inputs {
        flex-direction: column;
        width: 100%;
        min-width: auto;
      }

      .ds-search-actions {
        width: 100%;
        justify-content: stretch;
      }

      .ds-search-bar .ds-btn {
        width: 100%;
        justify-content: center;
      }

      .ds-filter-bar {
        flex-direction: column;
        gap: 16px;
        text-align: center;
        padding: 16px;
      }

      .ds-filter-content {
        flex-direction: column;
        width: 100%;
      }

      .ds-filter-pill-group {
        width: 100%;
        justify-content: center;
      }

      .ds-filter-summary {
        width: 100%;
        border-left: none;
        padding-left: 0;
        flex-direction: column;
        gap: 4px;
      }

      .ds-job-header {
        flex-direction: column;
        align-items: flex-start;
      }

      .ds-job-score {
        align-items: flex-start;
        width: 100%;
        margin-top: 12px;
      }

      .ds-rank-badge {
        position: static;
        width: auto;
        height: auto;
        border-radius: var(--ds-radius.sm);
        padding: 4px 10px;
        margin-bottom: 12px;
        order: -1;
      }

      .ds-job-footer {
        flex-direction: column;
        gap: 12px;
      }

      .ds-job-actions {
        width: 100%;
      }

      .ds-save-btn {
        justify-content: center;
      }
    }

    @media (max-width: 480px) {
      .ds-section-title {
        font-size: 1.5rem;
      }

      .ds-job-insight {
        flex-direction: column;
      }

      .ds-empty-tips {
        flex-direction: column;
      }

      .ds-tip-card {
        width: 100%;
      }
    }

    /* ==================== ACCESSIBILITY ==================== */
    *:focus-visible {
      outline: 2px solid var(--ds-primary);
      outline-offset: 2px;
      border-radius: var(--ds-radius.sm);
    }

    .ds-sr-only {
      position: absolute;
      width: 1px;
      height: 1px;
      padding: 0;
      margin: -1px;
      overflow: hidden;
      clip: rect(0, 0, 0, 0);
      white-space: nowrap;
      border: 0;
    }

    /* Reduced motion */
    @media (prefers-reduced-motion: reduce) {
      .ds-job-card,
      .ds-job-card-hovered,
      .ds-rank-badge,
      .ds-score-badge,
      .ds-filter-pill,
      .ds-btn,
      .ds-btn-primary,
      .ds-btn-secondary,
      .ds-save-btn {
        transition: none;
        animation: none;
      }
    }

    .dark-mode .ds-search-bar {
      background: var(--ds-surface);
      border-color: var(--ds-border);
    }

    .dark-mode .ds-search-input {
      background: transparent;
      border-color: transparent;
      color: var(--ds-text);
      appearance: none;
      -webkit-appearance: none;
      -moz-appearance: none;
      box-shadow: none;
    }

    .dark-mode .ds-search-input::placeholder {
      color: var(--ds-text-muted);
    }

    .dark-mode .ds-search-input::-webkit-input-placeholder {
      color: var(--ds-text-muted);
    }

    .dark-mode .ds-search-input::-moz-placeholder {
      color: var(--ds-text-muted);
    }

    .dark-mode .ds-filter-bar {
      background: var(--ds-surface);
      border-color: var(--ds-border);
    }

    .dark-mode .ds-filter-pill {
      background: var(--ds-surface-alt);
      border-color: var(--ds-border);
      color: var(--ds-text-muted);
    }

    .dark-mode .ds-filter-pill-active {
      background: var(--ds-primary);
      border-color: var(--ds-primary);
      color: white;
    }

    .dark-mode .ds-job-card {
      background: var(--ds-surface);
      border-color: var(--ds-border);
    }

    .dark-mode .ds-job-title {
      color: var(--ds-text);
    }

    .dark-mode .ds-job-meta {
      color: var(--ds-text-muted);
    }

    .dark-mode .ds-job-footer {
      border-top-color: var(--ds-border);
    }

    .dark-mode .ds-empty-state {
      color: var(--ds-text-muted);
    }

    .dark-mode .ds-empty-title {
      color: var(--ds-text);
    }

    .dark-mode .ds-empty-desc {
      color: var(--ds-text-muted);
    }

    .dark-mode .ds-tip-card {
      background: var(--ds-surface);
      border-color: var(--ds-border);
    }

    .dark-mode .ds-tip-title {
      color: var(--ds-text);
    }

    .dark-mode .ds-tip-text {
      color: var(--ds-text-muted);
    }

    .dark-mode .ds-btn-secondary {
      background: var(--ds-surface);
      color: var(--ds-text);
      border-color: var(--ds-border);
    }

    .dark-mode .ds-save-btn {
      color: var(--ds-text-muted);
    }

    .dark-mode .ds-save-btn:hover {
      color: var(--ds-primary);
      background: var(--ds-primary-soft);
    }

    .dark-mode .ds-save-btn.active {
      color: var(--ds-danger);
      background: var(--ds-danger-soft);
    }

    .dark-mode .ds-job-insight {
      background: var(--ds-surface-alt);
      border-color: var(--ds-primary);
    }

    .dark-mode .ds-skills-missing {
      opacity: 0.5;
    }
  `;

  document.head.appendChild(styleEl);
}

