
import { useState, type FormEvent } from "react";
import { motion } from "framer-motion";
import {
  LockKeyhole,
  Mail,
  Church,
  Eye,
  EyeOff,
  Loader2,
} from "lucide-react";
import { useNavigate } from "react-router-dom";
import { useAuth } from "../context/AuthContext";
import "../styles/auth.css";

export default function LoginPage() {
  const [username, setUsername] = useState("");
  const [password, setPassword] = useState("");
  const [showPassword, setShowPassword] = useState(false);
  const [error, setError] = useState("");

  const { login, isLoading } = useAuth();
  const navigate = useNavigate();

  const handleSubmit = async (e: FormEvent<HTMLFormElement>) => {
    e.preventDefault();
    setError("");

    try {
      await login({ username, password });
      navigate("/dashboard", { replace: true });
    } catch (err: unknown) {
      const apiError = err as {
        response?: {
          data?: {
            detail?: string;
          };
        };
      };

      setError(
        apiError.response?.data?.detail ||
          "Unable to sign in. Please check your connection and try again."
      );
    }
  };

  return (
    <main className="login-page">
      <motion.section
        className="login-card"
        initial={{ opacity: 0, y: 25 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.5 }}
      >
        <div className="login-brand">
          <div className="brand-icon">
            <Church size={30} />
          </div>
          <h1>ChurchAttend</h1>
          <p>Church Attendance Management</p>
        </div>

        <div className="login-heading">
          <h2>Welcome back</h2>
          <p>Sign in to access your staff dashboard.</p>
        </div>

        <form onSubmit={handleSubmit}>
          {error && (
            <div className="login-error" role="alert">
              {error}
            </div>
          )}

          <label htmlFor="username">Username</label>
          <div className="login-input">
            <Mail size={19} />
            <input
              id="username"
              type="text"
              placeholder="Enter your username"
              value={username}
              onChange={(e) => setUsername(e.target.value)}
              autoComplete="username"
              required
            />
          </div>

          <label htmlFor="password">Password</label>
          <div className="login-input">
            <LockKeyhole size={19} />
            <input
              id="password"
              type={showPassword ? "text" : "password"}
              placeholder="Enter your password"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              autoComplete="current-password"
              required
            />
            <button
              type="button"
              className="password-toggle"
              onClick={() => setShowPassword(!showPassword)}
              aria-label={showPassword ? "Hide password" : "Show password"}
            >
              {showPassword ? <EyeOff size={19} /> : <Eye size={19} />}
            </button>
          </div>

          <button
            className="login-button"
            type="submit"
            disabled={isLoading}
          >
            {isLoading ? (
              <>
                <Loader2 size={18} className="loading-spinner" />
                Signing in...
              </>
            ) : (
              "Sign in"
            )}
          </button>
        </form>

        <p className="login-footer">
          ChurchAttend © 2027
        </p>
      </motion.section>
    </main>
  );
}
