/**
 * Admin login page.
 */

import { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { useAuth } from '../hooks/useAuth';
import { Input, Button } from '../components/ui';

export function AdminLogin() {
  const [username, setUsername] = useState('');
  const [password, setPassword] = useState('');
  const [error, setError] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const { login } = useAuth();
  const navigate = useNavigate();

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError('');
    setIsLoading(true);

    try {
      const success = await login(username, password);
      if (success) {
        navigate('/admin');
      } else {
        setError('Invalid username or password');
      }
    } catch {
      setError('An error occurred. Please try again.');
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="min-h-screen bg-dark-bg flex items-center justify-center px-4">
      <div className="w-full max-w-md">
        <div className="card">
          {/* Header */}
          <div className="text-center mb-8">
            <div className="w-16 h-16 mx-auto mb-4 bg-primary-900 rounded-xl flex items-center justify-center">
              <svg
                className="w-8 h-8 text-primary-500"
                fill="none"
                stroke="currentColor"
                viewBox="0 0 24 24"
              >
                <path
                  strokeLinecap="round"
                  strokeLinejoin="round"
                  strokeWidth={2}
                  d="M12 15v2m-6 4h12a2 2 0 002-2v-6a2 2 0 00-2-2H6a2 2 0 00-2 2v6a2 2 0 002 2zm10-10V7a4 4 0 00-8 0v4h8z"
                />
              </svg>
            </div>
            <h1 className="text-2xl font-bold text-dark-text">Admin Login</h1>
            <p className="text-sm text-dark-text-secondary mt-2">
              Sign in to access the admin dashboard
            </p>
          </div>

          {/* Login form */}
          <form onSubmit={handleSubmit} className="space-y-4">
            {error && (
              <div className="p-3 bg-error/10 border border-error rounded-lg">
                <p className="text-error text-sm">{error}</p>
              </div>
            )}

            <Input
              label="Username"
              value={username}
              onChange={(e) => setUsername(e.target.value)}
              placeholder="Enter username"
              required
              autoComplete="username"
            />

            <Input
              type="password"
              label="Password"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              placeholder="Enter password"
              required
              autoComplete="current-password"
            />

            <Button
              type="submit"
              variant="primary"
              className="w-full"
              isLoading={isLoading}
            >
              Sign In
            </Button>
          </form>

          {/* Back link */}
          <div className="mt-6 text-center">
            <a
              href="/"
              className="text-sm text-primary-500 hover:text-primary-400 transition-colors"
            >
              &larr; Back to subscription form
            </a>
          </div>
        </div>
      </div>
    </div>
  );
}
