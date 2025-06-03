import React from 'react';
import ReactMarkdown from 'react-markdown';
import remarkGfm from 'remark-gfm';
import { useLocation, useNavigate } from 'react-router-dom';
import './custom.css';
import { motion } from 'framer-motion'; // Import motion for animations
import { FaArrowLeft } from 'react-icons/fa'; // Import the arrow icon

export default function ReviewResult() {
  const location = useLocation();
  const navigate = useNavigate();
  const { prUrl } = location.state || {};

  // Static markdown content
  const staticMarkdown = `# 📋 Pull Request Review\n\n**Title:** Pull Request Review  \n**Repository:** python/cpython  \n**Author:** Aadarsha  \n**PR Number:** #135037  \n\n---\n\n## 🧮 Review Summary\n\n| Category        | Count | Severity |\n|----------------|-------|----------|\n| Code Quality    |   4   | Medium   |\n| Security        |   2   | High     |\n| Documentation   |   1   | Low      |\n\n---\n\n## 🧾 Code Changes\n\n\`\`\`js\nfunction login(user, pass) {\n  // TODO: add input validation\n  authenticate(user, pass);\n  // Removed legacy logging\n  return true;\n}\n\`\`\`\n\n## Agent Feedback\n\n### Code Quality\n- Consider using async/await for authentication. *(Medium)*\n- Remove commented-out code before merging. *(Low)*\n\n### Security\n- Missing input validation for user credentials. *(High)*\n- Consider rate limiting login attempts. *(Medium)*\n\n### Documentation\n- Add JSDoc comments for the login function. *(Low)*\n`;

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
    <div className="gradient-bg full-screen-container" style={{ position: 'relative', overflowY: 'auto', padding: '2rem 1rem' }}> {/* Apply gradient and full screen, add padding and overflow */}
      {/* Back arrow button */}
      <motion.div
        style={{
          position: 'fixed',
          top: '2rem',
          left: '2rem',
          zIndex: 20,
          cursor: 'pointer',
          color: '#e0e7ff', /* Light color for visibility */
          fontSize: '1.5rem', /* Increased size */
          padding: '0.5rem',
        }}
        whileHover={{ scale: 1.1 }}
        whileTap={{ scale: 0.9 }}
        onClick={() => navigate('/')}
      >
        <FaArrowLeft />
      </motion.div>

      <motion.div
        className="glass-card" /* Wrap markdown in glass card */
        style={{
          width: '100%',
          maxWidth: '1000px', /* Match max width in CSS */
          // margin: '2rem auto', /* Center the card */
        }}
        variants={containerVariants}
        initial="hidden"
        animate="visible"
      >
        <div className="markdown-preview" style={{ background: 'none', boxShadow: 'none', padding: '0' }}> {/* Remove conflicting styles */}
          <ReactMarkdown remarkPlugins={[remarkGfm]}>
            {staticMarkdown}
          </ReactMarkdown>
        </div>
      </motion.div>
    </div>
  );
}
