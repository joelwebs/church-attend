import { useState } from "react";
import { motion } from "framer-motion";
import { LockKeyhole, Mail, Church, Eye, EyeOff } from "lucide-react";
import "../styles/auth.css";

export default function LoginPage() {
  const [showPassword, setShowPassword] = useState(false);

  return (
    <main className="login-page">
      <motion.section
        className="login-card"
        initial={{ opacity: 0, y: 25 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.5 }}
      >
        <div className="login-brand">
          <div className="brand-icon"><Church size={30} /></div>
          <h1>ChurchAttend</h1>
          <p>Church Attendance Management</p>
        </div>

        <div className="login-heading">
          <h2>Welcome back</h2>
          <p>Sign in to access your staff dashboard.</p>
        </div>

        <form onSubmit={(e) => e.preventDefault()}>
          <label htmlFor="username">Username</label>
          <div className="login-input">
            <Mail size={19} />
            <input id="username" type="text" placeholder="Enter your username" required />
          </div>

          <label htmlFor="password">Password</label>
          <div className="login-input">
            <LockKeyhole size={19} />
            <input
              id="password"
              type={showPassword ? "text" : "password"}
              placeholder="Enter your password"
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

          <button className="login-button" type="submit">
            Sign in
          </button>
        </form>

        <p className="login-footer">
          ChurchAttend © 2027
        </p>
      </motion.section>
    </main>
  );
}
