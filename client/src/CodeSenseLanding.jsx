import React, { useState } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { TypeAnimation } from 'react-type-animation';
import { Globe, Lock, Sun, Moon, Bot } from 'lucide-react';
import { useNavigate } from 'react-router-dom';
import './custom.css';
import api from './api'; // Import the API instance

export default function CodeSenseLanding() {
  const [mode, setMode] = useState('Public');
  const [prUrl, setPrUrl] = useState('');
  const [token, setToken] = useState('');
  const [dark, setDark] = useState(true);
  const [errors, setErrors] = useState({});
  const [showForm, setShowForm] = useState(false);
  const [loading, setLoading] = useState(false); // Add loading state
  const navigate = useNavigate();

  // Validate PR URL and token
  const validate = () => {
    const errs = {};
    const prPattern = /^https:\/\/github\.com\/[\w-]+\/[\w-]+\/pull\/\d+$/i;
    if (!prPattern.test(prUrl)) {
      errs.prUrl = 'Enter a valid GitHub PR URL.';
    }
    if (mode === 'Private' && token.trim().length === 0) {
      errs.token = 'Token is required for Private mode.';
    }
    setErrors(errs);
    return Object.keys(errs).length === 0;
  };

  // Handle form submit: make API call and navigate to review page
  const handleSubmit = async (e) => {
    e.preventDefault();
    if (!validate()) return;
    
    setLoading(true); // Start loading
    
    try {
      // Make POST request to your backend
      const response = await api.post('/review-pr', {
        pr_url: prUrl  // Change from prUrl to pr_url to match backend
      });
      
      // Navigate to review page with the response data and form data
      navigate('/review', {
        state: {
          mode,
          prUrl,
          token,
          reviewData: response.data // Pass the response data
        }
      });
    } catch (error) {
      console.error('Error reviewing PR:', error);
      setErrors({ 
        submit: error.response?.data?.message || 'Failed to review PR. Please try again.'
      });
    } finally {
      setLoading(false); // End loading regardless of outcome
    }
  };

  // Toggle dark mode
  React.useEffect(() => {
    if (dark) {
      document.documentElement.classList.add('dark');
    } else {
      document.documentElement.classList.remove('dark');
    }
  }, [dark]);

  // Animation variants for the main card
  const cardVariants = {
    hidden: { opacity: 0, y: 50 },
    visible: { opacity: 1, y: 0, transition: { duration: 0.8, ease: "easeOut" } },
  };

  // Animation variants for staggered children
  const containerVariants = {
    hidden: { opacity: 0 },
    visible: {
      opacity: 1,
      transition: {
        staggerChildren: 0.1,
      },
    },
  };

  // Animation variants for individual items
  const itemVariants = {
    hidden: { opacity: 0, y: 20 },
    visible: { opacity: 1, y: 0, transition: { duration: 0.5, ease: "easeOut" } },
  };

  // Animation variants for the form section
  const formVariants = {
    hidden: { opacity: 0, height: 0, padding: 0, marginTop: 0, marginBottom: 0 },
    visible: { opacity: 1, height: 'auto', padding: '0', marginTop: '1rem', marginBottom: '0' },
  };

  return (
    <div className="gradient-bg full-screen-container" style={{ position: 'relative', overflow: 'hidden' }}>
      {/* Animated background elements */}
      <motion.div
        className="background-element"
        style={{
          top: '10%',
          left: '5%',
          width: '200px',
          height: '200px',
          background: 'rgba(129, 140, 248, 0.1)',
          borderRadius: '50%',
          filter: 'blur(60px)',
          zIndex: 0
        }}
        animate={{ y: [0, 50, 0], rotate: [0, 180, 0] }}
        transition={{ duration: 12, repeat: Infinity, repeatType: 'mirror', ease: 'easeInOut' }}
      />
      <motion.div
        className="background-element"
        style={{
          bottom: '5%',
          right: '10%',
          width: '250px',
          height: '250px',
          background: 'rgba(165, 180, 252, 0.15)',
          borderRadius: '50%',
          filter: 'blur(60px)',
          zIndex: 0
        }}
        animate={{ y: [0, -60, 0], rotate: [0, -180, 0] }}
        transition={{ duration: 15, repeat: Infinity, repeatType: 'mirror', ease: 'easeInOut' }}
      />
      <motion.div
        className="background-element"
        style={{
          top: '40%',
          right: '5%',
          width: '150px',
          height: '150px',
          background: 'rgba(199, 210, 254, 0.08)',
          borderRadius: '50%',
          filter: 'blur(60px)',
          zIndex: 0
        }}
        animate={{ x: [0, 40, 0], rotate: [0, 360, 0] }}
        transition={{ duration: 10, repeat: Infinity, repeatType: 'mirror', ease: 'easeInOut' }}
      />
      {/* <motion.div
        className="background-element"
        style={{
          bottom: '20%',
          left: '20%',
          width: '180px',
          height: '180px',
          background: 'rgba(129, 140, 248, 0.12)',
          borderRadius: '50%',
          filter: 'blur(60px)',
          zIndex: 0
        }}
        animate={{ x: [0, -50, 0], rotate: [0, 270, 0] }}
        transition={{ duration: 13, repeat: Infinity, repeatType: 'mirror', ease: 'easeInOut' }}
      /> */}
      {/* Glowing dots */}
      {/* <motion.div
        className="absolute"
        style={{
          left: '25%',
          top: '33%',
          width: '24px',
          height: '24px',
          background: 'rgba(99, 102, 241, 0.3)',
          borderRadius: '50%',
          filter: 'blur(8px)',
          zIndex: 0
        }}
        animate={{ scale: [1, 1.3, 1] }}
        transition={{ duration: 2, repeat: Infinity }}
      /> */}
      {/* <motion.div
        className="absolute"
        style={{
          right: '33%',
          bottom: '25%',
          width: '16px',
          height: '16px',
          background: 'rgba(99, 102, 241, 0.2)',
          borderRadius: '50%',
          filter: 'blur(8px)',
          zIndex: 0
        }}
        animate={{ scale: [1, 1.5, 1] }}
        transition={{ duration: 2.5, repeat: Infinity }}
      /> */}
      {/* Bot avatar illustration (centered vertically, larger) */}
      <motion.div
        className="absolute"
        style={{
          left: '5%',
          top: '50%', /* Positioned vertically in the middle */
          transform: 'translateY(-50%)', /* Adjust for the element's height */
          zIndex: 10,
          opacity: 0.5, /* Slightly increased opacity */
          marginTop: '-40%'
        }}
        initial={{ y: 0 }}
        animate={{ y: [0, 20, 0] }}
        transition={{ duration: 6, repeat: Infinity, repeatType: 'mirror' }}
      >
        <Bot size={100} strokeWidth={1.5} style={{ color: '#c0c7ff' }} /> {/* Increased size and slightly adjusted color */}
      </motion.div>
      {/* Dark mode toggle */}
      {/* <button
        className="absolute"
        style={{
          top: '24px',
          right: '32px',
          zIndex: 20,
          background: dark ? 'rgba(255,255,255,0.1)' : 'rgba(15, 23, 42, 0.4)',
          borderRadius: '50%',
          padding: '8px',
          border: '1px solid rgba(255,255,255,0.2)',
          cursor: 'pointer',
          transition: 'transform 0.2s'
        }}
        onClick={() => setDark(d => !d)}
        type="button"
      >
        {dark ? <Sun size={22} style={{ color: '#fbbf24' }} /> : <Moon size={22} style={{ color: '#1e293b' }} />}
      </button> */}
      {/* Main glassmorphism card */}
      <motion.div
        className="glass-card"
        style={{
          position: 'relative',
          zIndex: 10,
          maxWidth: '90%', /* Increased max width */
          width: '600px', /* Set a fixed width for larger screens */
          margin: '0 auto', /* Centering the card */
          display: 'flex',
          flexDirection: 'column',
          alignItems: 'center',
          gap: '1rem', /* Adjusted gap for elements inside the card */
          padding: '2.5rem', /* Increased padding */
        }}
        variants={cardVariants}
        initial="hidden"
        animate="visible"
      >
        {/* Content within the card with staggered animation */}
        <motion.div
          style={{
            width: '100%',
            display: 'flex',
            flexDirection: 'column',
            alignItems: 'center',
            gap: '0.75rem', /* Reduced gap between form elements */
          }}
          variants={containerVariants}
          initial="hidden"
          animate="visible"
        >
          {/* App name with animation */}
          <motion.h1
            style={{
              fontSize: '3rem', /* Increased font size */
              fontWeight: 800,
              color: '#fff',
              letterSpacing: '-0.025em',
              textAlign: 'center',
            }}
            variants={itemVariants}
          >
            <span style={{
              display: 'inline-block',
              background: 'linear-gradient(to right, #818cf8, #e0e7ff, #818cf8)',
              WebkitBackgroundClip: 'text',
              WebkitTextFillColor: 'transparent',
              filter: 'drop-shadow(0 4px 6px rgba(0, 0, 0, 0.1))'
            }}>
              CodeSense
            </span>
          </motion.h1>
          {/* Tagline with typing effect */}
          <motion.div variants={itemVariants}>
            <TypeAnimation
              sequence={['🤖 PR Review Assistant', 2000, '🤖 PR Review Assistant', 2000]}
              wrapper="span"
              speed={50}
              style={{
                display: 'block',
                fontSize: '1.25rem', /* Increased font size */
                fontWeight: 500,
                color: '#e0e7ff',
                textAlign: 'center',
                minHeight: '2.5rem',
              }}
              repeat={Infinity}
              cursor={true}
            />
          </motion.div>
          {/* Subtitle */}
          <motion.div
            style={{
              color: '#cbd5e1',
              fontSize: '1.125rem', /* Increased font size */
              textAlign: 'center',
              opacity: 0.8,
              marginBottom: showForm ? '0.5rem' : '1rem', /* Adjusted bottom margin */
            }}
            variants={itemVariants}
          >
            Accelerate your PR reviews with multi-agent NLP insights.
          </motion.div>
          {/* Animated CTA button */}
          {!showForm && (
            <motion.button
              style={{
                padding: '0.8rem 2rem', /* Increased padding */
                borderRadius: '0.75rem',
                background: '#4f46e5',
                color: '#fff',
                fontWeight: 600,
                fontSize: '1.125rem', /* Increased font size */
                boxShadow: '0 4px 6px rgba(0, 0, 0, 0.1)',
                cursor: 'pointer',
                border: 'none',
                outline: 'none',
              }}
              whileHover={{ scale: 1.07 }}
              whileTap={{ scale: 0.97 }}
              onClick={() => {
                setShowForm(true);
                setTimeout(() => {
                  document.getElementById('pr-form')?.scrollIntoView({ behavior: 'smooth' });
                }, 0);
              }}
              variants={itemVariants}
            >
              Start a PR Review
            </motion.button>
          )}

          {/* Form layout - Conditionally rendered and animated */}
          <AnimatePresence>
            {showForm && (
              <motion.form
                id="pr-form"
                style={{
                  width: '100%',
                  display: 'flex',
                  flexDirection: 'column',
                  gap: '1rem',
                  marginTop: '1rem', /* Adjusted margin top */
                }}
                onSubmit={(e) => e.preventDefault()}
                autoComplete="off"
                variants={formVariants}
                initial="hidden"
                animate="visible"
                exit="hidden"
              >
                {/* Mode radio buttons */}
                <div style={{
                  display: 'flex',
                  alignItems: 'center',
                  justifyContent: 'center',
                  gap: '1.5rem'
                }}>
                  <label style={{
                    display: 'flex',
                    alignItems: 'center',
                    gap: '0.5rem',
                    cursor: 'pointer',
                    padding: '0.6rem 1rem',
                    borderRadius: '0.5rem',
                    transition: 'background-color 0.2s',
                    background: mode === 'Public' ? 'rgba(79, 70, 229, 0.2)' : 'transparent',
                    border: mode === 'Public' ? '1px solid #818cf8' : 'none'
                  }}>
                    <input
                      type="radio"
                      name="mode"
                      value="Public"
                      checked={mode === 'Public'}
                      onChange={() => setMode('Public')}
                      style={{ accentColor: '#4f46e5' }}
                    />
                    <Globe size={20} style={{ color: '#818cf8' }} />
                    <span style={{ color: '#e0e7ff', fontSize: '1rem', fontWeight: 500 }}>Public</span>
                  </label>
                  <label style={{
                    display: 'flex',
                    alignItems: 'center',
                    gap: '0.5rem',
                    cursor: 'pointer',
                    padding: '0.6rem 1rem',
                    borderRadius: '0.5rem',
                    transition: 'background-color 0.2s',
                    background: mode === 'Private' ? 'rgba(79, 70, 229, 0.2)' : 'transparent',
                    border: mode === 'Private' ? '1px solid #818cf8' : 'none'
                  }}>
                    <input
                      type="radio"
                      name="mode"
                      value="Private"
                      checked={mode === 'Private'}
                      onChange={() => setMode('Private')}
                      style={{ accentColor: '#4f46e5' }}
                    />
                    <Lock size={20} style={{ color: '#818cf8' }} />
                    <span style={{ color: '#e0e7ff', fontSize: '1rem', fontWeight: 500 }}>Private</span>
                  </label>
                </div>
                {/* PR URL input */}
                <div>
                  <input
                    type="url"
                    style={{
                      width: '100%',
                      padding: '0.6rem 1rem',
                      borderRadius: '0.5rem',
                      background: dark ? 'rgba(15, 23, 42, 0.6)' : 'rgba(255, 255, 255, 0.8)',
                      color: dark ? '#e0e7ff' : '#1e293b',
                      border: errors.prUrl ? '1px solid #ef4444' : '1px solid rgba(255, 255, 255, 0.2)',
                      outline: 'none'
                    }}
                    placeholder="GitHub PR URL (e.g. https://github.com/owner/repo/pull/123)"
                    value={prUrl}
                    onChange={e => setPrUrl(e.target.value)}
                    required
                  />
                  {errors.prUrl && <div style={{ color: '#ef4444', fontSize: '0.875rem', marginTop: '0.25rem' }}>{errors.prUrl}</div>}
                </div>
                {/* Token input (only if Private) */}
                {mode === 'Private' && (
                  <div>
                    <input
                      type="password"
                      style={{
                        width: '100%',
                        padding: '0.6rem 1rem',
                        borderRadius: '0.5rem',
                        background: dark ? 'rgba(15, 23, 42, 0.6)' : 'rgba(255, 255, 255, 0.8)',
                        color: dark ? '#e0e7ff' : '#1e293b',
                        border: errors.token ? '1px solid #ef4444' : '1px solid rgba(255, 255, 255, 0.2)',
                        outline: 'none'
                      }}
                      placeholder="GitHub Access Token"
                      value={token}
                      onChange={e => setToken(e.target.value)}
                      required={mode === 'Private'}
                    />
                    {errors.token && <div style={{ color: '#ef4444', fontSize: '0.875rem', marginTop: '0.25rem' }}>{errors.token}</div>}
                  </div>
                )}
                {/* Submit button - Update to show loading state */}
                <motion.button
                  type="button"
                  style={{
                    width: '100%',
                    padding: '0.75rem',
                    borderRadius: '0.5rem',
                    background: '#4f46e5',
                    color: '#fff',
                    fontWeight: 600,
                    fontSize: '1.125rem',
                    boxShadow: '0 2px 4px rgba(0, 0, 0, 0.1)',
                    cursor: loading ? 'not-allowed' : 'pointer', // Change cursor when loading
                    border: 'none',
                    outline: 'none',
                    marginTop: '0.5rem',
                    opacity: loading ? 0.7 : 1 // Dim the button when loading
                  }}
                  whileHover={{ scale: loading ? 1 : 1.03 }} // Disable hover effect when loading
                  whileTap={{ scale: loading ? 1 : 0.98 }} // Disable tap effect when loading
                  onClick={loading ? null : handleSubmit} // Prevent multiple submissions
                >
                  {loading ? 'Processing...' : 'Review Pull Request'}
                </motion.button>
                
                {/* Error message for submission errors */}
                {errors.submit && (
                  <div style={{ 
                    color: '#ef4444', 
                    fontSize: '0.875rem', 
                    marginTop: '0.5rem',
                    textAlign: 'center' 
                  }}>
                    {errors.submit}
                  </div>
                )}
              </motion.form>
            )}
          </AnimatePresence>
        </motion.div>
      </motion.div>
      {/* Footer */}
      <div style={{
        position: 'absolute',
        bottom: '1rem',
        left: 0,
        width: '100%',
        textAlign: 'center',
        fontSize: '0.75rem',
        color: '#818cf8',
        opacity: 0.7,
        zIndex: 10,
        userSelect: 'none'
      }}>
        &copy; {new Date().getFullYear()} CodeSense &mdash; Multi-Agent PR Review Assistant
      </div>
    </div>
  );
}