import React, { useState } from 'react';
import { useNavigate, Link } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';

export const RegisterPage: React.FC = () => {
  const [fullName, setFullName] = useState('');
  const [email, setEmail] = useState('');
  const [organization, setOrganization] = useState('');
  const [password, setPassword] = useState('');
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(false);
  const { register } = useAuth();
  const navigate = useNavigate();

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError('');
    setLoading(true);
    try {
      await register({ full_name: fullName, email, password, organization });
      navigate('/dashboard');
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Registration failed. Please check inputs.');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="bg-background text-on-background min-h-screen flex flex-col md:flex-row antialiased">
      {/* Left Illustration */}
      <div className="md:w-1/2 lg:w-3/5 relative h-64 md:h-screen flex-shrink-0 bg-surface-container overflow-hidden rounded-b-3xl md:rounded-none md:rounded-r-[2rem] z-10 shadow-lg">
        <div
          className="absolute inset-0 bg-cover bg-center"
          style={{
            backgroundImage: `url('https://images.unsplash.com/photo-1625246333195-78d9c38ad449?q=80&w=1600&auto=format&fit=crop')`,
          }}
        />
        <div className="absolute inset-0 bg-gradient-to-t md:bg-gradient-to-r from-black/70 via-black/40 to-transparent flex flex-col justify-end p-8 md:p-16">
          <h1 className="font-display-lg text-display-lg text-white mb-4">Join AgriNova Today</h1>
          <p className="font-body-lg text-body-lg text-white/90 max-w-lg">
            Start monitoring crop health, predicting moisture stress, and optimizing irrigation with satellite AI.
          </p>
        </div>
      </div>

      {/* Right Form */}
      <div className="md:w-1/2 lg:w-2/5 flex flex-col justify-center items-center p-6 md:p-12 relative z-20">
        <div className="w-full max-w-md bg-surface rounded-[16px] p-8 soft-shadow border border-outline-variant/30 backdrop-blur-sm relative -mt-16 md:mt-0 z-30">
          <div className="text-center mb-8">
            <div className="inline-flex items-center justify-center w-12 h-12 rounded-xl bg-primary-container text-on-primary-container mb-4 shadow-sm">
              <span className="material-symbols-outlined text-[28px]">person_add</span>
            </div>
            <h2 className="font-headline-lg text-headline-lg text-on-surface mb-2">Create Account</h2>
            <p className="font-body-md text-body-md text-on-surface-variant">Get started with precision agriculture</p>
          </div>

          {error && (
            <div className="mb-4 p-3 rounded-lg bg-error-container text-on-error-container text-sm flex items-center gap-2">
              <span className="material-symbols-outlined text-sm">error</span>
              <span>{error}</span>
            </div>
          )}

          <form onSubmit={handleSubmit} className="space-y-4">
            <div>
              <label className="block font-label-md text-label-md text-on-surface mb-1">Full Name</label>
              <input
                type="text"
                value={fullName}
                onChange={(e) => setFullName(e.target.value)}
                placeholder="John Doe"
                required
                className="input-field"
              />
            </div>

            <div>
              <label className="block font-label-md text-label-md text-on-surface mb-1">Email Address</label>
              <input
                type="email"
                value={email}
                onChange={(e) => setEmail(e.target.value)}
                placeholder="john@farm.com"
                required
                className="input-field"
              />
            </div>

            <div>
              <label className="block font-label-md text-label-md text-on-surface mb-1">Farm / Organization</label>
              <input
                type="text"
                value={organization}
                onChange={(e) => setOrganization(e.target.value)}
                placeholder="Green Valley Farms"
                className="input-field"
              />
            </div>

            <div>
              <label className="block font-label-md text-label-md text-on-surface mb-1">Password</label>
              <input
                type="password"
                value={password}
                onChange={(e) => setPassword(e.target.value)}
                placeholder="Min 8 chars, 1 uppercase, 1 digit"
                required
                className="input-field"
              />
            </div>

            <button
              type="submit"
              disabled={loading}
              className="w-full mt-4 flex justify-center py-3 px-4 rounded-[12px] shadow-sm font-label-md text-label-md text-white bg-primary hover:bg-primary-container transition-all active:scale-[0.98] items-center gap-2"
            >
              {loading ? 'Creating Account...' : 'Register & Get Started'}
              <span className="material-symbols-outlined text-[18px]">arrow_forward</span>
            </button>
          </form>

          <p className="mt-6 text-center font-body-md text-sm text-on-surface-variant">
            Already have an account?{' '}
            <Link to="/login" className="font-label-md text-primary hover:text-primary-container font-semibold">
              Sign in
            </Link>
          </p>
        </div>
      </div>
    </div>
  );
};
