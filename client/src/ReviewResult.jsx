import React from 'react';
import ReactMarkdown from 'react-markdown';
import remarkGfm from 'remark-gfm';
import { useLocation, useNavigate } from 'react-router-dom';
import './custom.css';
import { motion } from 'framer-motion';
import { FaArrowLeft } from 'react-icons/fa';

export default function ReviewResult() {
  const location = useLocation();
  const navigate = useNavigate();
  
  // Extract data passed from CodeSenseLanding
  const { prUrl, reviewData } = location.state || {};
  
  // Use the review data from API response, or fallback to empty string
  const markdownContent = reviewData?.report || '';
  
  React.useEffect(() => {
    if (!prUrl) {
      navigate('/');
    }
  }, [prUrl, navigate]);

  // Animation variants for the content container
  const containerVariants = {
    hidden: { opacity: 0, y: 20 },
    visible: { opacity: 1, y: 0, transition: { duration: 0.6, ease: "easeOut" } },
  };

  return (
    <div className="gradient-bg full-screen-container" style={{ position: 'relative', overflowY: 'auto', padding: '2rem 1rem' }}>
      {/* Back arrow button */}
      <motion.div
        style={{
          position: 'fixed',
          top: '2rem',
          left: '2rem',
          zIndex: 20,
          cursor: 'pointer',
          color: '#e0e7ff',
          fontSize: '1.5rem',
          padding: '0.5rem',
        }}
        whileHover={{ scale: 1.1 }}
        whileTap={{ scale: 0.9 }}
        onClick={() => navigate('/')}
      >
        <FaArrowLeft />
      </motion.div>

      <motion.div
        className="glass-card"
        style={{
          width: '100%',
          maxWidth: '1000px',
          margin: '2rem auto',
        }}
        variants={containerVariants}
        initial="hidden"
        animate="visible"
      >
        <div className="markdown-preview" style={{ background: 'none', boxShadow: 'none', padding: '0' }}>
          <ReactMarkdown remarkPlugins={[remarkGfm]}>
            {markdownContent}
          </ReactMarkdown>
        </div>
      </motion.div>
    </div>
  );
}
