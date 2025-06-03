import { useState } from 'react';
import { BrowserRouter as Router, Routes, Route, useNavigate } from 'react-router-dom';
import './custom.css';
import { FaLock, FaGlobe } from 'react-icons/fa';
import CodeSenseLanding from './CodeSenseLanding';
import ReviewResult from './ReviewResult';

// Dummy PR metadata
// const prMeta = {
//   title: 'Refactor authentication flow',
//   repo: 'codesense/codebase',
//   author: 'octocat',
//   number: 42,
//   created: '2024-05-01',
//   branch: 'feature/auth-refactor',
// };

// Dummy summary data
// const summary = [
//   { agent: 'Code Quality', count: 4, severity: 'Medium' },
//   { agent: 'Security', count: 2, severity: 'High' },
//   { agent: 'Documentation', count: 1, severity: 'Low' },
// ];

// Dummy code diff (array of lines, with highlights)
// const codeDiff = [
//   { line: 1, content: 'function login(user, pass) {', type: 'context' },
//   { line: 2, content: '  // TODO: add input validation', type: 'added' },
//   { line: 3, content: '  authenticate(user, pass);', type: 'context' },
//   { line: 4, content: '  // Removed legacy logging', type: 'removed' },
//   { line: 5, content: '  return true;', type: 'context' },
//   { line: 6, content: '}', type: 'context' },
// ];

// Dummy agent feedback
// const agentFeedback = {
//   'Code Quality': [
//     { comment: 'Consider using async/await for authentication.', severity: 'Medium' },
//     { comment: 'Remove commented-out code before merging.', severity: 'Low' },
//   ],
//   Security: [
//     { comment: 'Missing input validation for user credentials.', severity: 'High' },
//     { comment: 'Consider rate limiting login attempts.', severity: 'Medium' },
//   ],
//   Documentation: [
//     { comment: 'Add JSDoc comments for the login function.', severity: 'Low' },
//   ],
// };

// function HomePage() {
//   const [mode, setMode] = useState('Public');
//   const [prUrl, setPrUrl] = useState('');
//   const [token, setToken] = useState('');
//   const [errors, setErrors] = useState({});
//   const navigate = useNavigate();

//   const validate = () => {
//     const errs = {};
//     const prPattern = /^https:\/\/github\.com\/[\w-]+\/[\w-]+\/pull\/\d+$/i;
//     if (!prPattern.test(prUrl)) {
//       errs.prUrl = 'Enter a valid GitHub PR URL.';
//     }
//     if (mode === 'Private' && token.trim().length === 0) {
//       errs.token = 'Token is required for Private mode.';
//     }
//     setErrors(errs);
//     return Object.keys(errs).length === 0;
//   };

//   const handleSubmit = (e) => {
//     e.preventDefault();
//     if (validate()) {
//       navigate('/review', {
//         state: {
//           mode,
//           prUrl,
//           token,
//         },
//       });
//     }
//   };

//   return (
//     <div
//       className="gradient-bg"
//     >
//       <div className="text-center mb-4" style={{ color: '#fff' }}>
//         <h1 style={{ fontWeight: 700, letterSpacing: 1 }}>CodeSense</h1>
//         <p className="lead mb-1" style={{ fontWeight: 400, opacity: 0.92 }}>
//           <span role="img" aria-label="AI">🤖</span> AI-Powered Code Review Intelligence
//         </p>
//         <p style={{ fontSize: 16, opacity: 0.7 }}>
//           Accelerate your PR reviews with multi-agent NLP insights.
//         </p>
//       </div>
//       <div className="container-fluid">
//         <div className="glass-card" style={{ width: '100%', maxWidth: '800px' }}>
//           <form onSubmit={handleSubmit} noValidate>
//             <div className="text-center mb-4">
//               <span className="badge bg-primary rounded-pill" style={{ fontSize: 14, letterSpacing: 1, padding: '0.5rem 1rem' }}>
//                 Start a PR Review
//               </span>
//             </div>
//             <div className="row">
//               <div className="col-12 col-md-6">
//                 <label className="form-label fw-semibold">Mode</label>
//                 <div className="d-flex gap-3">
//                   <div className="form-check">
//                     <input
//                       className="form-check-input"
//                       type="radio"
//                       name="mode"
//                       id="publicMode"
//                       value="Public"
//                       checked={mode === 'Public'}
//                       onChange={() => setMode('Public')}
//                     />
//                     <label className="form-check-label d-flex align-items-center gap-1" htmlFor="publicMode">
//                       <FaGlobe style={{ color: '#4fd1c5' }} /> Public
//                     </label>
//                   </div>
//                   <div className="form-check">
//                     <input
//                       className="form-check-input"
//                       type="radio"
//                       name="mode"
//                       id="privateMode"
//                       value="Private"
//                       checked={mode === 'Private'}
//                       onChange={() => setMode('Private')}
//                     />
//                     <label className="form-check-label d-flex align-items-center gap-1" htmlFor="privateMode">
//                       <FaLock style={{ color: '#f67280' }} /> Private
//                     </label>
//                   </div>
//                 </div>
//               </div>
//               <div className="col-12 col-md-6">
//                 <label htmlFor="prUrl" className="form-label fw-semibold">GitHub PR URL</label>
//                 <input
//                   type="url"
//                   className={`form-control${errors.prUrl ? ' is-invalid' : ''}`}
//                   id="prUrl"
//                   placeholder="https://github.com/owner/repo/pull/123"
//                   value={prUrl}
//                   onChange={e => setPrUrl(e.target.value)}
//                   required
//                   style={{ background: 'rgba(255,255,255,0.85)', borderRadius: 12 }}
//                 />
//                 {errors.prUrl && <div className="invalid-feedback">{errors.prUrl}</div>}
//               </div>
//               {mode === 'Private' && (
//                 <div className="col-12 col-md-6">
//                   <label htmlFor="token" className="form-label fw-semibold">Access Token</label>
//                   <input
//                     type="password"
//                     className={`form-control${errors.token ? ' is-invalid' : ''}`}
//                     id="token"
//                     placeholder="Enter your GitHub token"
//                     value={token}
//                     onChange={e => setToken(e.target.value)}
//                     required={mode === 'Private'}
//                     style={{ background: 'rgba(255,255,255,0.85)', borderRadius: 12 }}
//                   />
//                   {errors.token && <div className="invalid-feedback">{errors.token}</div>}
//                 </div>
//               )}
//             </div>
//             <button
//               type="submit"
//               className="btn btn-primary w-100 mt-4"
//               style={{ borderRadius: 12, fontWeight: 600, letterSpacing: 1 }}
//             >
//               Review Pull Request
//             </button>
//           </form>
//         </div>
//       </div>
//       <div className="text-center mt-4" style={{ color: '#b8c1ec', fontSize: 13, opacity: 0.7 }}>
//         &copy; {new Date().getFullYear()} CodeSense &mdash; Multi-Agent PR Review Assistant
//       </div>
//     </div>
//   );
// }

function App() {
  return (
    <Router>
      <div style={{
        display: 'flex',
        flexDirection: 'column', /* Stack children vertically */
        alignItems: 'center', /* Center items horizontally */
        justifyContent: 'center', /* Center items vertically */
        minHeight: '100vh',
        width: '100%',
      }}>
        <Routes>
          <Route path="/" element={<CodeSenseLanding />} />
          <Route path="/review" element={<ReviewResult />} />
        </Routes>
      </div>
    </Router>
  );
}

export default App;
