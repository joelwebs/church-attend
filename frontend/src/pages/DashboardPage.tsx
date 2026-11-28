
import { useState } from "react";
import { motion } from "framer-motion";
import {
  Users,
  CalendarDays,
  ClipboardCheck,
  TrendingUp,
  Menu,
  X,
  Bell,
  Church,
  UserPlus,
  CalendarPlus,
  BarChart3,
} from "lucide-react";
import { Link, NavLink } from "react-router-dom";
import "../styles/dashboard.css";

const stats = [
  { title: "Total Members", value: "250", icon: Users, color: "blue" },
  {
    title: "Today's Attendance",
    value: "186",
    icon: ClipboardCheck,
    color: "green",
  },
  { title: "Active Services", value: "2", icon: CalendarDays, color: "orange" },
  {
    title: "Attendance Rate",
    value: "74.4%",
    icon: TrendingUp,
    color: "purple",
  },
];

const navigation = [
  { label: "Dashboard", path: "/dashboard" },
  { label: "Members", path: "/members" },
  { label: "Attendance", path: "/attendance" },
  { label: "Services", path: "/services" },
];

export default function DashboardPage() {
  const [menuOpen, setMenuOpen] = useState(false);

  function closeMenu() {
    setMenuOpen(false);
  }

  return (
    <div className="dashboard">
      {menuOpen && (
        <button
          className="sidebar-overlay"
          aria-label="Close navigation menu"
          onClick={closeMenu}
        />
      )}

      <aside className={`sidebar ${menuOpen ? "sidebar-open" : ""}`}>
        <div className="sidebar-brand">
          <Church size={27} />
          <h2>ChurchAttend</h2>

          <button
            className="sidebar-close"
            onClick={closeMenu}
            aria-label="Close menu"
          >
            <X size={22} />
          </button>
        </div>

        <p className="nav-label">MAIN MENU</p>

        <nav>
          {navigation.map((item) => (
            <NavLink
              key={item.path}
              to={item.path}
              onClick={closeMenu}
              className={({ isActive }) =>
                `nav-item ${isActive ? "active" : ""}`
              }
            >
              {item.label}
            </NavLink>
          ))}
        </nav>

        <div className="sidebar-bottom">
          <span>Church Administration</span>
        </div>
      </aside>

      <main className="dashboard-main">
        <header className="dashboard-header">
          <button
            className="mobile-menu"
            aria-label="Open navigation menu"
            aria-expanded={menuOpen}
            onClick={() => setMenuOpen(true)}
          >
            <Menu size={24} />
          </button>

          <div>
            <h1>Dashboard</h1>
            <p>Welcome back! Here's your church overview.</p>
          </div>

          <button
            className="notification-button"
            aria-label="Notifications"
          >
            <Bell />
          </button>
        </header>

        <section className="stats-grid">
          {stats.map((stat, index) => {
            const Icon = stat.icon;

            return (
              <motion.div
                key={stat.title}
                className="stat-card"
                initial={{ opacity: 0, y: 15 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ delay: index * 0.1 }}
              >
                <div className={`stat-icon ${stat.color}`}>
                  <Icon size={23} />
                </div>

                <p>{stat.title}</p>
                <h2>{stat.value}</h2>
              </motion.div>
            );
          })}
        </section>

        <section className="dashboard-content">
          <div className="content-card">
            <h2>Recent Activity</h2>

            <p className="empty-state">
              Attendance activity will appear here.
            </p>
          </div>

          <div className="content-card">
            <h2>Quick Actions</h2>

            <div className="quick-actions">
              <Link to="/members" className="action-button">
                <UserPlus size={18} />
                Register Member
              </Link>

              <Link
                to="/services"
                className="action-button"
                onClick={closeMenu}
              >
                <CalendarPlus size={18} />
                Manage Services
              </Link>

              <Link
                to="/attendance"
                className="action-button"
                onClick={closeMenu}
              >
                <BarChart3 size={18} />
                View Attendance
              </Link>

              <Link
                to="/members"
                className="action-button"
                onClick={closeMenu}
              >
                <Users size={18} />
                View Members
              </Link>
            </div>
          </div>
        </section>
      </main>
    </div>
  );
}
