import { useState, useEffect } from 'react';
import Upload from './components/Upload';
import JobList from './components/JobList';
import { useTheme } from './contexts/ThemeContext';

// TRUE GLASSMORPHISM DESIGN SYSTEM - SLATE + TEAL
// Cool, modern, calm SaaS interface with teal as primary accent
const DS = {
  colors: {
    light: {
      // COOL NEUTRAL BACKGROUND - slate-based, no warmth
      base: '#F8FAFC',          // Cool neutral slate
      baseCenter: '#F1F5F9',    // Slightly lighter for depth
      baseEdge: '#E2E8F0',      // Subtle edge transition
      // NEUTRAL GLASS - no tint, pure transparency
      surface: 'rgba(255, 255, 255, 0.70)',
      surfaceElevated: 'rgba(255, 255, 255, 0.80)',
      surfaceSolid: '#FFFFFF',
      surfaceAlt: 'rgba(255, 255, 255, 0.60)',
      // Micro-contrast layers
      surfaceToggle: 'rgba(255, 255, 255, 0.55)',
      surfaceUpload: 'rgba(255, 255, 255, 0.65)',
      text: '#0F172A',
      textMuted: '#64748B',
      textDim: '#94A3B8',
      // Edge lighting - clean slate tones
      border: 'rgba(255, 255, 255, 0.20)',
      borderElevated: 'rgba(255, 255, 255, 0.30)',
      borderLight: 'rgba(255, 255, 255, 0.45)',
      borderDark: 'rgba(15, 23, 42, 0.05)',
      // TEAL AS PRIMARY ACCENT - only color used
      accent: '#14B8A6',        // Teal 500
      accentSoft: 'rgba(20, 184, 166, 0.12)',
      accentHover: '#0D9488',   // Teal 600
      lightGradient: 'linear-gradient(to bottom, rgba(255,255,255,0.22), rgba(255,255,255,0.06))',
    },
    dark: {
      // DEEP SLATE BACKGROUND - cool, modern, no pure black
      base: '#0B1220',          // Deep slate
      baseCenter: '#131C2F',    // Slightly lighter for depth
      baseEdge: '#080D18',      // Darker edge
      // NEUTRAL GLASS - no tint, pure transparency
      surface: 'rgba(255, 255, 255, 0.08)',
      surfaceElevated: 'rgba(255, 255, 255, 0.10)',
      surfaceSolid: '#1E293B',  // Slate 800
      surfaceAlt: 'rgba(255, 255, 255, 0.05)',
      surfaceToggle: 'rgba(255, 255, 255, 0.06)',
      surfaceUpload: 'rgba(255, 255, 255, 0.08)',
      text: '#E2E8F0',
      textMuted: '#94A3B8',
      textDim: '#64748B',
      border: 'rgba(255, 255, 255, 0.08)',
      borderElevated: 'rgba(255, 255, 255, 0.12)',
      borderLight: 'rgba(255, 255, 255, 0.20)',
      borderDark: 'rgba(15, 23, 42, 0.30)',
      // TEAL AS PRIMARY ACCENT - only color used
      accent: '#14B8A6',        // Teal 500
      accentSoft: 'rgba(20, 184, 166, 0.15)',
      accentHover: '#0D9488',   // Teal 600
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
    sm: '10px',
    md: '12px',
    lg: '14px',
    xl: '18px',
    '2xl': '22px',
    full: '50%',
  },
  shadow: {
    // SOFT floating effect - depth without heaviness
    float: '0 25px 80px rgba(0, 0, 0, 0.35)',
    md: '0 16px 48px rgba(0, 0, 0, 0.25)',
    lg: '0 24px 64px rgba(0, 0, 0, 0.30)',
    // Light mode elevation - increased shadow for lifted feel
    lightMd: '0 12px 36px rgba(0, 0, 0, 0.10)',
    lightFloat: '0 20px 60px rgba(0, 0, 0, 0.12)',
    // Inner highlights for top edge (glass catching light)
    innerLight: 'inset 0 1px rgba(255, 255, 255, 0.16)',
    innerLightSubtle: 'inset 0 1px rgba(255, 255, 255, 0.08)',
    innerDark: 'inset 0 1px rgba(0, 0, 0, 0.06)',
    innerSubtle: 'inset 0 0 16px rgba(0, 0, 0, 0.10)',
  },
  transition: 'all 200ms cubic-bezier(0.4, 0, 0.2, 1)',
};

const App = () => {
  const { theme, toggleTheme } = useTheme();
  const [parsedResume, setParsedResume] = useState(null);
  const [resumeId, setResumeId] = useState(null);
  const [activeTab, setActiveTab] = useState('upload');

  // Apply dark mode class and update CSS custom properties
  useEffect(() => {
    if (theme === 'dark') {
      document.documentElement.classList.add('dark-mode');
    } else {
      document.documentElement.classList.remove('dark-mode');
    }
  }, [theme]);

  const colors = theme === 'dark' ? DS.colors.dark : DS.colors.light;

  // Update CSS custom properties when colors change
  useEffect(() => {
    const root = document.documentElement;
    root.style.setProperty('--ds-accent', colors.accent);
    root.style.setProperty('--ds-accent-soft', colors.accentSoft);
    root.style.setProperty('--ds-accent-hover', colors.accentHover);
    root.style.setProperty('--ds-text', colors.text);
    root.style.setProperty('--ds-text-muted', colors.textMuted);
    root.style.setProperty('--ds-text-light', colors.textDim || colors.textMuted);
    root.style.setProperty('--ds-border', colors.border);
    root.style.setProperty('--ds-border-elevated', colors.borderElevated);
    root.style.setProperty('--ds-border-light', colors.borderLight);
    root.style.setProperty('--ds-border-dark', colors.borderDark);
    root.style.setProperty('--ds-surface', colors.surface);
    root.style.setProperty('--ds-surface-elevated', colors.surfaceElevated);
    root.style.setProperty('--ds-surface-solid', colors.surfaceSolid);
    root.style.setProperty('--ds-surface-alt', colors.surfaceAlt);
    root.style.setProperty('--ds-surface-gradient', colors.lightGradient);
    root.style.setProperty('--ds-shadow-soft', colors.shadow?.soft || DS.shadow.soft);
    root.style.setProperty('--ds-shadow-md', colors.shadow?.md || DS.shadow.md);
    root.style.setProperty('--ds-shadow-lg', colors.shadow?.lg || DS.shadow.lg);
    root.style.setProperty('--ds-shadow-float', colors.shadow?.float || DS.shadow.float);
    root.style.setProperty('--ds-shadow-inner-light', colors.shadow?.innerLight || DS.shadow.innerLight);
    root.style.setProperty('--ds-shadow-inner-dark', colors.shadow?.innerDark || DS.shadow.innerDark);
    root.style.setProperty('--ds-shadow-inner-subtle', colors.shadow?.innerSubtle || DS.shadow.innerSubtle);
  }, [colors]);

  const handleUploadComplete = (id, data) => {
    setResumeId(id);
    setParsedResume(data);
    setActiveTab('jobs');
  };

  const handleClearResume = () => {
    setResumeId(null);
    setParsedResume(null);
    setActiveTab('upload');
  };

  return (
    <div className="ds-app" style={{ '--ds-color-base': colors.base }}>
      {/* Navigation - Weak secondary glass layer */}
      <nav className="ds-app-nav" role="navigation" aria-label="Main navigation">
        <div className="ds-nav-content">
          <div className="ds-nav-logo" role="link" aria-label="ResumeMatch Home">
            <div className="ds-logo-icon" style={{ color: colors.accent }}>
              <svg viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
                <path d="M12 2L2 7V20C2 20.5304 2.21071 21.0391 2.58579 21.4142C2.96086 21.7893 3.46957 22 4 22H20C20.5304 22 21.0391 21.7893 21.4142 21.4142C21.7893 21.0391 22 20.5304 22 20V7L12 2Z" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"/>
              </svg>
            </div>
            <span className="ds-logo-text">ResumeMatch</span>
          </div>
          <div className="ds-nav-tabs" role="tablist" aria-label="Main tabs">
            <button
              className={`ds-nav-tab ${activeTab === 'upload' ? 'ds-nav-tab-active' : ''}`}
              onClick={() => setActiveTab('upload')}
              disabled={!!parsedResume}
              role="tab"
              aria-selected={activeTab === 'upload'}
              aria-controls="upload-panel"
            >
              Upload Resume
            </button>
            <button
              className={`ds-nav-tab ${activeTab === 'jobs' ? 'ds-nav-tab-active' : ''}`}
              onClick={() => setActiveTab('jobs')}
              disabled={!parsedResume}
              role="tab"
              aria-selected={activeTab === 'jobs'}
              aria-controls="jobs-panel"
            >
              Job Search
            </button>
          </div>
          <button
            className="ds-theme-toggle"
            onClick={toggleTheme}
            aria-label={`Switch to ${theme === 'light' ? 'dark' : 'light'} mode`}
            title={theme === 'light' ? 'Dark mode' : 'Light mode'}
          >
            {theme === 'light' ? (
              <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke={colors.textMuted} strokeWidth="2">
                <circle cx="12" cy="12" r="5" />
                <path d="M12 1v2M12 21v2M4.22 4.22l1.42 1.42M18.36 18.36l1.42 1.42M1 12h2M21 12h2M4.22 19.78l1.42-1.42M18.36 5.64l1.42-1.42" />
              </svg>
            ) : (
              <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke={colors.textMuted} strokeWidth="2">
                <path d="M21 12.79A9 9 0 1 1 11.21 3 7 7 0 0 0 21 12.79z" />
              </svg>
            )}
          </button>
          <button
            className="ds-clear-btn"
            onClick={handleClearResume}
            aria-label="Clear resume and start over"
          >
            <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke={colors.textMuted} strokeWidth="2">
              <line x1="18" y1="6" x2="6" y2="18" />
              <line x1="6" y1="6" x2="18" y2="18" />
            </svg>
            <span>Clear</span>
          </button>
        </div>
      </nav>

      {/* Main Content */}
      <main className="ds-app-main" id="main-content">
        {activeTab === 'upload' && (
          <div className="ds-upload-container">
            <Upload onUploadComplete={handleUploadComplete} colors={colors} />
          </div>
        )}

        {activeTab === 'jobs' && parsedResume && (
          <div className="ds-jobs-container">
            {/* Resume Summary Card - Strong glass */}
            <Card className="ds-resume-summary" colors={colors}>
              <h2 className="ds-summary-title">Your Profile</h2>
              <div className="ds-summary-card">
                <div className="ds-summary-content">
                  <div className="ds-profile-section">
                    <div className="ds-profile-name">{parsedResume.name}</div>
                    <div className="ds-profile-info">
                      {parsedResume.email && <span className="ds-info-item" title={parsedResume.email} style={{ borderColor: colors.border }}>
                        <svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke={colors.accent} strokeWidth="2">
                          <path d="M4 4h16c1.1 0 2 .9 2 2v12c0 1.1-.9 2-2 2H4c-1.1 0-2-.9-2-2V6c0-1.1.9-2 2-2z" />
                          <polyline points="22 6 12 13 2 6" />
                        </svg>
                        <span>{parsedResume.email}</span>
                      </span>}
                      {parsedResume.location && <span className="ds-info-item" title={parsedResume.location} style={{ borderColor: colors.border }}>
                        <svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke={colors.accent} strokeWidth="2">
                          <path d="M21 10c0 7-9 13-9 13s-9-6-9-13a9 9 0 0 1 18 0z" />
                          <circle cx="12" cy="10" r="3" />
                        </svg>
                        <span>{parsedResume.location}</span>
                      </span>}
                      {parsedResume.total_experience_years && (
                        <span className="ds-info-item" title={`${parsedResume.total_experience_years} years experience`} style={{ borderColor: colors.border }}>
                          <svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke={colors.accent} strokeWidth="2">
                            <circle cx="12" cy="12" r="10" />
                            <polyline points="12 6 12 12 16 14" />
                          </svg>
                          <span>{parsedResume.total_experience_years} years experience</span>
                        </span>
                      )}
                    </div>
                  </div>
                  <div className="ds-skills-section">
                    <h4 className="ds-skills-title">Key Skills</h4>
                    <div className="ds-skills-grid">
                      {parsedResume.skills.slice(0, 10).map((skill, idx) => (
                        <span key={idx} className="ds-skill-tag" title={skill} style={{ borderColor: colors.border }}>
                          {skill}
                        </span>
                      ))}
                      {parsedResume.skills.length > 10 && (
                        <span className="ds-skill-tag ds-skill-tag-ghost" style={{ borderColor: colors.accent }}>
                          +{parsedResume.skills.length - 10} more
                        </span>
                      )}
                    </div>
                  </div>
                </div>
              </div>
            </Card>

            {/* Stats Grid - Secondary glass layer */}
            <div className="ds-job-stats">
              <StatCard value={parsedResume.skills.length} label="Skills" colors={colors} />
              <StatCard value={parsedResume.preferred_roles.length} label="Potential Roles" colors={colors} />
              <StatCard value={parsedResume.experience.length} label="Experience Items" colors={colors} />
            </div>

            <JobList resumeId={resumeId} resumeData={parsedResume} colors={colors} theme={theme} />
          </div>
        )}
      </main>

      {/* Footer */}
      <footer className="ds-app-footer" role="contentinfo">
        <div className="ds-footer-content">
          <p>© 2026 ResumeMatch • Powered by FastAPI & LangChain</p>
          <p className="ds-footer-sub">AI-powered job matching platform</p>
        </div>
      </footer>

      <style>{`
        * {
          margin: 0;
          padding: 0;
          box-sizing: border-box;
        }

        body {
          font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Inter, Roboto, Oxygen, Ubuntu, Cantarell, sans-serif;
          background: var(--ds-color-base);
          /* SUBTLE WARM GRADIENT - creates atmosphere without clutter */
          /* Top: slightly warmer (#F3F1EC), Bottom: slightly cooler (#FAFAF8) */
          background-image: radial-gradient(circle at center, ${colors.baseCenter} 0%, ${colors.base} 40%, ${colors.baseEdge} 100%);
          background-size: 100% 100%;
          min-height: 100vh;
          color: ${colors.text};
          -webkit-font-smoothing: antialiased;
          -moz-osx-font-smoothing: grayscale;
        }

        /* Light mode specific - subtle radial highlight behind main card */
        :not(.dark-mode) body::after {
          content: '';
          position: fixed;
          top: 50%;
          left: 50%;
          transform: translate(-50%, -50%);
          width: 120%;
          height: 80%;
          pointer-events: none;
          z-index: -1;
          background: radial-gradient(circle, rgba(255, 248, 240, 0.08) 0%, rgba(255, 248, 240, 0.02) 40%, transparent 70%);
        }

        .dark-mode body {
          /* STRONGER radial glow behind cards in dark mode */
          background-image: radial-gradient(circle at center, ${colors.baseCenter} 0%, ${colors.base} 45%, ${colors.baseEdge} 100%);
        }

        /* Subtle noise texture - reduced visibility (~25%) */
        body::before {
          content: '';
          position: fixed;
          top: 0;
          left: 0;
          right: 0;
          bottom: 0;
          pointer-events: none;
          z-index: -1;
          background-image: url("data:image/svg+xml,%3Csvg viewBox='0 0 200 200' xmlns='http://www.w3.org/2000/svg'%3E%3Cfilter id='noiseFilter'%3E%3CfeTurbulence type='fractalNoise' baseFrequency='0.85' numOctaves='3' stitchTiles='stitch'/%3E%3C/filter%3E%3Crect width='100%25' height='100%25' filter='url(%23noiseFilter)' opacity='0.022'/%3E%3C/svg%3E");
        }

        .ds-app {
          display: flex;
          flex-direction: column;
          min-height: 100vh;
          position: relative;
          z-index: 1;
        }

        /* ==================== NAVIGATION - Compact Glass ==================== */
        .ds-app-nav {
          position: sticky;
          top: 0;
          z-index: 50;
          backdrop-filter: blur(20px);
          -webkit-backdrop-filter: blur(20px);
          background: ${colors.surface};
          /* Subtle directional lighting for navbar */
          background-image: ${colors.lightGradient};
          border-bottom: 1px solid ${colors.borderElevated};
          padding: 4px ${DS.spacing.xl};
          /* Very tight, compact navbar */
        }

        .dark-mode .ds-app-nav {
          background: ${colors.surface};
          background-image: ${colors.lightGradient};
          border-bottom-color: ${colors.borderElevated};
        }

        .ds-nav-content {
          display: flex;
          justify-content: space-between;
          align-items: center;
          max-width: 1000px;
          margin: 0 auto;
          gap: 12px;
        }

        .ds-nav-logo {
          display: flex;
          align-items: center;
          gap: 8px;
          font-weight: 600;
          font-size: 1rem;
          letter-spacing: -0.01em;
        }

        .ds-logo-icon {
          width: 22px;
          height: 22px;
          flex-shrink: 0;
        }

        .ds-logo-text {
          font-weight: 600;
          letter-spacing: -0.02em;
        }

        .ds-nav-tabs {
          display: flex;
          gap: 4px;
          padding: 4px;
          background: transparent;
          border-radius: ${DS.radius.md};
        }

        .dark-mode .ds-nav-tabs {
          background: transparent;
        }

        .ds-nav-tab {
          padding: 8px 16px;
          border: none;
          background: transparent;
          border-radius: ${DS.radius.sm};
          cursor: pointer;
          font-size: 0.85rem;
          font-weight: 500;
          color: ${colors.textMuted};
          transition: all 250ms cubic-bezier(0.4, 0, 0.2, 1);
        }

        .dark-mode .ds-nav-tab {
          color: ${colors.textMuted};
        }

        .ds-nav-tab:hover:not(:disabled) {
          color: ${colors.text};
          background: ${colors.surfaceAlt};
        }

        .dark-mode .ds-nav-tab:hover:not(:disabled) {
          color: ${colors.text};
          background: ${colors.surfaceAlt};
        }

        .ds-nav-tab-active {
          background: ${colors.accent};
          color: white;
          box-shadow: 0 4px 16px rgba(0, 0, 0, 0.25);
        }

        .dark-mode .ds-nav-tab-active {
          background: ${colors.accent};
          color: white;
          box-shadow: 0 4px 16px rgba(0, 0, 0, 0.25);
        }

        .ds-nav-tab:disabled {
          opacity: 0.4;
          cursor: not-allowed;
        }

        .ds-clear-btn {
          display: flex;
          align-items: center;
          gap: 4px;
          padding: 4px 10px;
          border: 1px solid ${colors.border};
          border-radius: ${DS.radius.sm};
          cursor: pointer;
          font-size: 0.7rem;
          font-weight: 500;
          color: ${colors.textMuted};
          transition: all 250ms cubic-bezier(0.4, 0, 0.2, 1);
          background: transparent;
        }

        .dark-mode .ds-clear-btn {
          border-color: ${colors.border};
          color: ${colors.textMuted};
          background: transparent;
        }

        .ds-clear-btn:hover {
          border-color: ${colors.accent};
          color: ${colors.accent};
          background: transparent;
        }

        .dark-mode .ds-clear-btn:hover {
          border-color: ${colors.accent};
          color: ${colors.accent};
          background: transparent;
        }

        /* ==================== MAIN CONTENT ==================== */
        .ds-app-main {
          flex: 1;
          padding: 60px 20px;
          max-width: 1000px;
          margin: 0 auto;
          width: 100%;
          position: relative;
          z-index: 1;
        }

        .ds-upload-container {
          max-width: 600px;
          margin: 0 auto;
          padding: 0;
        }

        .ds-jobs-container {
          display: flex;
          flex-direction: column;
          gap: ${DS.spacing.lg};
          max-width: 1000px;
          margin: 0 auto;
        }

        /* ==================== GLASS CARD - Premium Glass with Warmth ==================== */
        .ds-card {
          backdrop-filter: blur(28px);
          -webkit-backdrop-filter: blur(28px);
          background: ${colors.surfaceElevated};
          /* Soft directional gradient - gentle light falloff */
          background-image: ${colors.lightGradient};
          border-radius: ${DS.radius['2xl']};
          border: 1px solid ${colors.borderElevated};
          /* GENTLE floating effect - card feels gently lifted */
          box-shadow: ${colors.shadow?.lightFloat || DS.shadow.lightFloat}, ${DS.shadow.innerLight};
          transition: all 250ms cubic-bezier(0.4, 0, 0.2, 1);
          position: relative;
        }

        .dark-mode .ds-card {
          background: ${colors.surfaceElevated};
          background-image: ${colors.lightGradient};
          border-color: ${colors.borderElevated};
          box-shadow: ${colors.shadow?.float || DS.shadow.float}, ${DS.shadow.innerLight};
        }

        /* Light mode - optimized elevation for lifted feel */
        :not(.dark-mode) .ds-card {
          border-color: ${colors.borderLight};
          box-shadow: 0 12px 35px rgba(0, 0, 0, 0.08), ${DS.shadow.innerLight};
        }

        .ds-card:hover {
          transform: translateY(-4px);
          box-shadow: ${colors.shadow?.md || DS.shadow.md}, ${DS.shadow.innerLight};
        }

        .dark-mode .ds-card:hover {
          transform: translateY(-4px);
        }

        .ds-resume-summary {
          padding: ${DS.spacing['2xl']};
        }

        .ds-summary-title {
          font-size: 1.6rem;
          font-weight: 600;
          color: ${colors.text};
          margin-bottom: ${DS.spacing.lg};
          display: flex;
          align-items: center;
          gap: 12px;
          letter-spacing: -0.02em;
          /* Top edge highlight for title */
        }

        .ds-summary-title::before {
          content: '';
          width: 5px;
          height: 32px;
          background: linear-gradient(to bottom, ${colors.borderLight}, ${colors.accent});
          border-radius: ${DS.radius.sm};
          box-shadow: 0 0 12px ${colors.accentSoft};
        }

        .ds-summary-card {
          background: ${colors.surfaceSolid};
          /* Subtle directional light for inner card */
          background-image: linear-gradient(to bottom, rgba(255,255,255,0.12), rgba(255,255,255,0.04));
          border-radius: ${DS.radius.xl};
          padding: ${DS.spacing['2xl']};
          border: 1px solid ${colors.border};
          box-shadow: ${DS.shadow.innerSubtle};
        }

        .dark-mode .ds-summary-card {
          background: ${colors.surfaceSolid};
          background-image: linear-gradient(to bottom, rgba(255,255,255,0.08), rgba(255,255,255,0.03));
          border-color: ${colors.border};
        }

        .ds-summary-content {
          display: flex;
          justify-content: space-between;
          align-items: flex-start;
          gap: 40px;
        }

        .ds-profile-section {
          flex: 1;
        }

        .ds-profile-name {
          font-size: 1.85rem;
          font-weight: 600;
          color: ${colors.text};
          margin-bottom: 18px;
          letter-spacing: -0.02em;
        }

        .ds-profile-info {
          display: flex;
          flex-wrap: wrap;
          gap: 10px;
        }

        .ds-info-item {
          display: inline-flex;
          align-items: center;
          gap: 8px;
          padding: 9px 13px;
          background: ${colors.surface};
          border-radius: ${DS.radius.sm};
          font-size: 0.85rem;
          color: ${colors.textMuted};
          transition: all 250ms cubic-bezier(0.4, 0, 0.2, 1);
          border: 1px solid ${colors.borderElevated};
          /* Glass embedded feel */
        }

        .dark-mode .ds-info-item {
          background: ${colors.surface};
          color: ${colors.textMuted};
          border-color: ${colors.borderElevated};
        }

        .ds-info-item:hover {
          color: ${colors.accent};
          background: ${colors.accentSoft};
          border-color: ${colors.accent};
          transform: translateY(-1px);
        }

        .ds-skills-section {
          flex: 1;
        }

        .ds-skills-title {
          font-weight: 500;
          color: ${colors.textMuted};
          margin-bottom: 12px;
          font-size: 0.7rem;
          text-transform: uppercase;
          letter-spacing: 0.1em;
        }

        .ds-skills-grid {
          display: flex;
          flex-wrap: wrap;
          gap: 8px;
        }

        .ds-skill-tag {
          display: inline-flex;
          align-items: center;
          padding: 9px 13px;
          background: ${colors.surface};
          color: ${colors.textMuted};
          border-radius: ${DS.radius.sm};
          font-size: 0.85rem;
          font-weight: 500;
          transition: all 250ms cubic-bezier(0.4, 0, 0.2, 1);
          border: 1px solid ${colors.borderElevated};
        }

        .dark-mode .ds-skill-tag {
          background: ${colors.surface};
          color: ${colors.textMuted};
          border-color: ${colors.borderElevated};
        }

        .ds-skill-tag:hover {
          color: ${colors.accent};
          background: ${colors.accentSoft};
          border-color: ${colors.accent};
          transform: translateY(-1px);
        }

        .ds-skill-tag-ghost {
          background: transparent;
          color: ${colors.accent};
        }

        /* ==================== STAT CARDS - Premium Glass with Micro-Contrast ==================== */
        .ds-job-stats {
          display: grid;
          grid-template-columns: repeat(3, 1fr);
          gap: 24px;
        }

        .ds-stat-card {
          backdrop-filter: blur(24px);
          -webkit-backdrop-filter: blur(24px);
          background: ${colors.surfaceElevated};
          /* Slightly stronger than main card for hierarchy */
          background-image: ${colors.lightGradient};
          border-radius: ${DS.radius.xl};
          padding: 32px;
          text-align: center;
          border: 1px solid ${colors.borderElevated};
          /* Lighter shadow for secondary element */
          box-shadow: ${colors.shadow?.lightMd || DS.shadow.lightMd}, ${DS.shadow.innerLightSubtle};
          transition: all 250ms cubic-bezier(0.4, 0, 0.2, 1);
        }

        .dark-mode .ds-stat-card {
          background: ${colors.surfaceElevated};
          background-image: ${colors.lightGradient};
          border-color: ${colors.borderElevated};
          box-shadow: ${colors.shadow?.md || DS.shadow.md}, ${DS.shadow.innerLightSubtle};
        }

        .ds-stat-card:hover {
          transform: translateY(-4px);
          box-shadow: ${colors.shadow?.md || DS.shadow.md}, ${DS.shadow.innerLight};
        }

        .dark-mode .ds-stat-card:hover {
          transform: translateY(-4px);
        }

        /* Light mode stat cards - optimized elevation */
        :not(.dark-mode) .ds-stat-card:hover {
          box-shadow: 0 16px 40px rgba(0, 0, 0, 0.08), ${DS.shadow.innerLight};
        }

        .ds-stat-value {
          font-size: 2.25rem;
          font-weight: 600;
          color: ${colors.accent};
          margin-bottom: 8px;
          line-height: 1.1;
          /* Light source effect */
        }

        .dark-mode .ds-stat-value {
          color: ${colors.accent};
        }

        .ds-stat-label {
          font-size: 0.8rem;
          color: ${colors.textMuted};
          font-weight: 500;
        }

        .dark-mode .ds-stat-label {
          color: ${colors.textMuted};
        }

        /* ==================== FOOTER - Premium Glass ==================== */
        .ds-app-footer {
          /* Slightly different surface for footer micro-contrast */
          background: ${colors.surfaceAlt};
          padding: ${DS.spacing.md} ${DS.spacing.xl};
          text-align: center;
          border-top: 1px solid ${colors.border};
          backdrop-filter: blur(16px);
          -webkit-backdrop-filter: blur(16px);
        }

        .dark-mode .ds-app-footer {
          background: ${colors.surfaceAlt};
          border-top-color: ${colors.border};
        }

        .ds-footer-content {
          display: flex;
          flex-direction: column;
          gap: 8px;
        }

        .ds-footer-sub {
          color: ${colors.textDim};
          font-size: 0.8rem;
        }

        /* ==================== RESPONSIVE ==================== */
        @media (max-width: 900px) {
          .ds-nav-content {
            flex-direction: column;
            gap: 12px;
          }

          .ds-summary-content {
            flex-direction: column;
          }

          .ds-job-stats {
            grid-template-columns: 1fr;
          }

          .ds-app-main {
            padding: 48px 16px;
          }
        }

        @media (max-width: 600px) {
          .ds-stat-card {
            padding: 24px;
          }

          .ds-stat-value {
            font-size: 1.75rem;
          }

          .ds-summary-title {
            font-size: 1.3rem;
          }

          .ds-profile-name {
            font-size: 1.4rem;
          }

          .ds-resume-summary {
            padding: 24px;
          }

          .ds-app-main {
            padding: 32px 12px;
          }
        }

        /* ==================== THEME TOGGLE ==================== */
        .ds-theme-toggle {
          border: 1px solid ${colors.border};
          cursor: pointer;
          padding: 8px;
          border-radius: ${DS.radius.sm};
          color: ${colors.textMuted};
          transition: all 250ms cubic-bezier(0.4, 0, 0.2, 1);
          display: flex;
          align-items: center;
          justify-content: center;
          backdrop-filter: blur(12px);
          -webkit-backdrop-filter: blur(12px);
          background: transparent;
        }

        .dark-mode .ds-theme-toggle {
          border-color: ${colors.border};
          color: ${colors.textMuted};
          background: transparent;
        }

        .ds-theme-toggle:hover {
          background: ${colors.accentSoft};
          color: ${colors.accent};
          transform: rotate(5deg);
        }

        .dark-mode .ds-theme-toggle:hover {
          background: ${colors.accentSoft};
          color: ${colors.accent};
        }
      `}</style>
    </div>
  );
};

// Sub-components for cleaner structure
const Card = ({ children, className = '', colors }) => (
  <div className={`ds-card ${className}`} style={{
    background: colors.surfaceElevated,
    border: `1px solid ${colors.borderElevated}`,
    boxShadow: `${colors.shadow?.float || DS.shadow.float}, ${colors.shadow?.innerLight || DS.shadow.innerLight}`,
  }}>
    {children}
  </div>
);

const StatCard = ({ value, label, colors }) => (
  <Card className="ds-stat-card" colors={colors}>
    <div className="ds-stat-value" style={{ color: colors.accent }}>{value}</div>
    <div className="ds-stat-label">{label}</div>
  </Card>
);

export default App;
