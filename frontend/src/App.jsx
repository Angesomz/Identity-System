import { BrowserRouter as Router, Routes, Route, Link } from 'react-router-dom';
import Layout from './components/Layout';
import Enrollment from './pages/Enrollment';
import Identification from './pages/Identification';
import Identities from './pages/Identities';
import IDScanner from './pages/IDScanner';
import { Shield, ArrowRight, UserPlus, ScanLine, Search } from 'lucide-react';
import { motion } from 'framer-motion';

function Home() {
  return (
    <div className="flex flex-col items-center justify-center min-h-[80vh] text-center">
      <motion.div
        initial={{ scale: 0.8, opacity: 0 }}
        animate={{ scale: 1, opacity: 1 }}
        transition={{ duration: 0.5 }}
        className="mb-8 p-6 bg-brand-500/10 rounded-full ring-4 ring-brand-500/20"
      >
        <Shield className="h-24 w-24 text-brand-400" />
      </motion.div>

      <motion.h1
        initial={{ y: 20, opacity: 0 }}
        animate={{ y: 0, opacity: 1 }}
        transition={{ delay: 0.2 }}
        className="text-5xl font-bold bg-clip-text text-transparent bg-gradient-to-r from-brand-300 to-indigo-400 mb-6"
      >
        INSA Identity System
      </motion.h1>

      <motion.p
        initial={{ y: 20, opacity: 0 }}
        animate={{ y: 0, opacity: 1 }}
        transition={{ delay: 0.3 }}
        className="text-xl text-gray-400 max-w-2xl mb-12"
      >
        Next-generation biometric identity resolution platform capable of million-scale identification with liveness detection.
      </motion.p>

      <motion.div
        initial={{ y: 20, opacity: 0 }}
        animate={{ y: 0, opacity: 1 }}
        transition={{ delay: 0.4 }}
        className="flex flex-col sm:flex-row gap-6 mb-8"
      >
        <Link
          to="/enroll"
          className="group px-8 py-4 bg-brand-600 hover:bg-brand-500 rounded-xl text-white font-bold text-lg transition-all shadow-lg hover:shadow-brand-500/30 flex items-center gap-2"
        >
          New Enrollment <ArrowRight className="h-5 w-5 group-hover:translate-x-1 transition-transform" />
        </Link>
        <Link
          to="/identify"
          className="group px-8 py-4 bg-dark-card hover:bg-white/10 border border-white/10 rounded-xl text-white font-bold text-lg transition-all flex items-center gap-2"
        >
          Live Identification <ArrowRight className="h-5 w-5 group-hover:translate-x-1 transition-transform" />
        </Link>
        <Link
          to="/scan-id"
          className="group px-8 py-4 bg-dark-card hover:bg-white/10 border border-brand-500/30 rounded-xl text-brand-300 font-bold text-lg transition-all flex items-center gap-2 hover:border-brand-500/60"
        >
          <ScanLine className="h-5 w-5" /> Scan Fayda ID
        </Link>
      </motion.div>

      <motion.div
        initial={{ y: 20, opacity: 0 }}
        animate={{ y: 0, opacity: 1 }}
        transition={{ delay: 0.5 }}
      >
        <Link
          to="/identities"
          className="text-gray-400 hover:text-white flex items-center gap-2 hover:underline"
        >
          <UserPlus className="h-4 w-4" /> View Enrolled Database
        </Link>
      </motion.div>
    </div>
  );
}

function App() {
  return (
    <Router>
      <Layout>
        <Routes>
          <Route path="/" element={<Home />} />
          <Route path="/enroll" element={<Enrollment />} />
          <Route path="/identify" element={<Identification />} />
          <Route path="/identities" element={<Identities />} />
          <Route path="/scan-id" element={<IDScanner />} />
        </Routes>
      </Layout>
    </Router>
  );
}

export default App;
