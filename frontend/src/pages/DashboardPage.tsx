import { motion } from "framer-motion";
import {
  Users, CalendarDays, ClipboardCheck,
  TrendingUp, Menu, Bell, Church
} from "lucide-react";
import "../styles/dashboard.css";

const stats = [
  { title: "Total Members", value: "250", icon: Users, color: "blue" },
  { title: "Today's Attendance", value: "186", icon: ClipboardCheck, color: "green" },
  { title: "Active Services", value: "2", icon: CalendarDays, color: "orange" },
  { title: "Attendance Rate", value: "74.4%", icon: TrendingUp, color: "purple" },
];

export default function DashboardPage() {
  return (
    <div className="dashboard">
      <aside className="sidebar">
        <div className="sidebar-brand">
          <Church size={27} />
          <h2>ChurchAttend</h2>
        </div>

        <p className="nav-label">MAIN MENU</p>
        <nav>
          <a className="nav-item active" href="/dashboard">Dashboard</a>
          <a className="nav-item" href="/members">Members</a>
          <a className="nav-item" href="/attendance">Attendance</a>
          <a className="nav-item" href="/services">Services</a>
        </nav>

        <div className="sidebar-bottom">
          <span>Church Administration</span>
        </div>
      </aside>

      <main className="dashboard-main">
        <header className="dashboard-header">
          <button className="mobile-menu" aria-label="Menu"><Menu /></button>
          <div>
            <h1>Dashboard</h1>
            <p>Welcome back! Here's your church overview.</p>
          </div>
          <button className="notification-button" aria-label="Notifications">
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
            <p className="empty-state">Attendance activity will appear here.</p>
          </div>

          <div className="content-card">
            <h2>Quick Actions</h2>
            <button className="action-button">+ Add Member</button>
            <button className="action-button">Create Service</button>
            <button className="action-button">View Attendance</button>
          </div>
        </section>
      </main>
    </div>
  );
}
