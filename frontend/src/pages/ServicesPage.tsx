
import { useEffect, useState, type FormEvent } from "react";
import {
  CalendarDays,
  Plus,
  Clock,
  MapPin,
  X,
  Pencil,
  Search,
  QrCode,
  CheckCircle,
  Lock,
  Ban,
  RefreshCw,
} from "lucide-react";

import Button from "../components/common/Button";
import BackButton from "../components/common/BackButton";
import {
  getServices,
  createService,
  updateService,
  openService,
  closeService,
  cancelService,
  generateServiceQR,
  revokeServiceQR,
} from "../api/services";

import type {
  ChurchService,
  ServiceFormData,
  GeneratedQRCode,
} from "../types/service";

import "../styles/services.css";

const emptyForm: ServiceFormData = {
  name: "",
  date: "",
  start_time: "",
  end_time: "",
  venue: "",
  attendance_start: "",
  attendance_end: "",
};

function getErrorMessage(error: unknown): string {
  const err = error as {
    response?: { data?: unknown };
    message?: string;
  };

  const data = err.response?.data;

  if (data && typeof data === "object") {
    return Object.entries(data)
      .map(([field, value]) => {
        const message = Array.isArray(value)
          ? value.join(" ")
          : String(value);

        return `${field}: ${message}`;
      })
      .join(" ");
  }

  return err.message || "Something went wrong. Please try again.";
}

function toBackendDateTime(date: string, time: string): string {
  return new Date(`${date}T${time}:00`).toISOString();
}

function formatDate(date: string): string {
  return new Date(`${date}T00:00:00`).toLocaleDateString("en-GH", {
    weekday: "short",
    day: "numeric",
    month: "short",
    year: "numeric",
  });
}

function formatTime(time: string): string {
  const [hours, minutes] = time.split(":").map(Number);
  const date = new Date();

  date.setHours(hours, minutes, 0, 0);

  return date.toLocaleTimeString("en-GH", {
    hour: "numeric",
    minute: "2-digit",
    hour12: true,
  });
}

function getStatusLabel(status: ChurchService["status"]) {
  const labels = {
    scheduled: "Scheduled",
    open: "Open",
    closed: "Closed",
    cancelled: "Cancelled",
  };

  return labels[status];
}

export default function ServicesPage() {
  const [services, setServices] = useState<ChurchService[]>([]);
  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);
  const [actionLoading, setActionLoading] = useState<string | null>(null);

  const [showForm, setShowForm] = useState(false);
  const [editingId, setEditingId] = useState<string | null>(null);

  const [search, setSearch] = useState("");
  const [formData, setFormData] = useState<ServiceFormData>(emptyForm);

  const [error, setError] = useState("");
  const [success, setSuccess] = useState("");

  const [qrData, setQrData] = useState<GeneratedQRCode | null>(null);
  const [qrServiceName, setQrServiceName] = useState("");

  async function loadServices() {
    setLoading(true);
    setError("");

    try {
      const response = await getServices("", 1);
      setServices(response.results);
    } catch (err) {
      setError(getErrorMessage(err));
    } finally {
      setLoading(false);
    }
  }

  useEffect(() => {
    void loadServices();
  }, []);

  const filteredServices = services.filter((service) => {
    const term = search.trim().toLowerCase();

    return (
      service.name.toLowerCase().includes(term) ||
      service.venue.toLowerCase().includes(term)
    );
  });

  function openCreateForm() {
    setEditingId(null);
    setFormData(emptyForm);
    setError("");
    setSuccess("");
    setShowForm(true);
  }

  function openEditForm(service: ChurchService) {
    setEditingId(service.id);

    setFormData({
      name: service.name,
      date: service.date,
      start_time: service.start_time.slice(0, 5),
      end_time: service.end_time.slice(0, 5),
      venue: service.venue,
      attendance_start: new Date(service.attendance_start)
        .toLocaleTimeString("en-GB", {
          hour: "2-digit",
          minute: "2-digit",
          hour12: false,
        }),
      attendance_end: new Date(service.attendance_end)
        .toLocaleTimeString("en-GB", {
          hour: "2-digit",
          minute: "2-digit",
          hour12: false,
        }),
    });

    setError("");
    setShowForm(true);
  }

  function closeForm() {
    setShowForm(false);
    setEditingId(null);
    setFormData(emptyForm);
  }

  async function handleSubmit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();

    setError("");
    setSuccess("");

    if (formData.end_time <= formData.start_time) {
      setError("End time must be after start time.");
      return;
    }

    if (formData.attendance_end <= formData.attendance_start) {
      setError("Attendance end must be after attendance start.");
      return;
    }

    if (
      formData.attendance_start < formData.start_time ||
      formData.attendance_end > formData.end_time
    ) {
      setError("The attendance window must fall within the service time.");
      return;
    }

    const payload: ServiceFormData = {
      name: formData.name.trim(),
      date: formData.date,
      start_time: formData.start_time,
      end_time: formData.end_time,
      venue: formData.venue.trim(),
      attendance_start: toBackendDateTime(
        formData.date,
        formData.attendance_start
      ),
      attendance_end: toBackendDateTime(
        formData.date,
        formData.attendance_end
      ),
    };

    setSaving(true);

    try {
      if (editingId) {
        await updateService(editingId, payload);
        setSuccess("Service updated successfully.");
      } else {
        await createService(payload);
        setSuccess("Service created successfully.");
      }

      closeForm();
      await loadServices();
    } catch (err) {
      setError(getErrorMessage(err));
    } finally {
      setSaving(false);
    }
  }

  async function handleServiceAction(
    id: string,
    action: "open" | "close" | "cancel"
  ) {
    setActionLoading(id);
    setError("");
    setSuccess("");

    try {
      if (action === "open") {
        await openService(id);
        setSuccess("Service opened successfully.");
      } else if (action === "close") {
        await closeService(id);
        setSuccess("Service closed successfully.");
      } else {
        if (!window.confirm("Are you sure you want to cancel this service?")) {
          return;
        }

        await cancelService(id);
        setSuccess("Service cancelled successfully.");
      }

      await loadServices();
    } catch (err) {
      setError(getErrorMessage(err));
    } finally {
      setActionLoading(null);
    }
  }

  async function handleGenerateQR(service: ChurchService) {
    setActionLoading(service.id);
    setError("");
    setSuccess("");

    try {
      const result = await generateServiceQR(service.id);

      setQrData(result);
      setQrServiceName(service.name);
    } catch (err) {
      setError(getErrorMessage(err));
    } finally {
      setActionLoading(null);
    }
  }

  async function handleRevokeQR() {
    if (!qrData) return;

    if (!window.confirm("Revoke this QR code? It will no longer work.")) {
      return;
    }

    setActionLoading(qrData.service_id);

    try {
      await revokeServiceQR(qrData.service_id);
      setQrData(null);
      setSuccess("QR code revoked successfully.");
    } catch (err) {
      setError(getErrorMessage(err));
    } finally {
      setActionLoading(null);
    }
  }

  const upcomingCount = services.filter(
    (service) =>
      service.date >= new Date().toLocaleDateString("en-CA")
  ).length;

  const openCount = services.filter(
    (service) => service.status === "open"
  ).length;

  return (
    <div className="page-container services-page">
      <BackButton fallback="/dashboard" />

      <div className="page-header services-page-header">
        <div>
          <span className="page-eyebrow">CHURCH MANAGEMENT</span>
          <h1>Church Services</h1>
          <p>Schedule services and manage attendance QR codes.</p>
        </div>

        <Button
          leftIcon={<Plus size={18} />}
          onClick={openCreateForm}
        >
          Create Service
        </Button>
      </div>

      {error && <div className="form-error">{error}</div>}
      {success && <div className="form-success">{success}</div>}

      <div className="service-summary">
        <div className="service-summary-card">
          <div className="summary-icon blue">
            <CalendarDays size={21} />
          </div>
          <div>
            <span>Total Services</span>
            <h2>{services.length}</h2>
          </div>
        </div>

        <div className="service-summary-card">
          <div className="summary-icon green">
            <CalendarCheckIcon />
          </div>
          <div>
            <span>Upcoming Services</span>
            <h2>{upcomingCount}</h2>
          </div>
        </div>

        <div className="service-summary-card">
          <div className="summary-icon grey">
            <CheckCircle size={21} />
          </div>
          <div>
            <span>Open Services</span>
            <h2>{openCount}</h2>
          </div>
        </div>
      </div>

      {showForm && (
        <div className="service-form-card">
          <div className="service-form-header">
            <div>
              <h2>{editingId ? "Edit Service" : "Create New Service"}</h2>
              <p>Enter the service and attendance details.</p>
            </div>

            <button
              type="button"
              className="close-form-button"
              onClick={closeForm}
              aria-label="Close form"
            >
              <X size={20} />
            </button>
          </div>

          <form onSubmit={handleSubmit}>
            <div className="service-form-grid">
              <div className="form-group">
                <label htmlFor="service-name">Service Name *</label>
                <input
                  id="service-name"
                  value={formData.name}
                  onChange={(e) =>
                    setFormData({ ...formData, name: e.target.value })
                  }
                  placeholder="e.g. Sunday Worship Service"
                  required
                />
              </div>

              <div className="form-group">
                <label htmlFor="service-date">Service Date *</label>
                <input
                  id="service-date"
                  type="date"
                  value={formData.date}
                  onChange={(e) =>
                    setFormData({ ...formData, date: e.target.value })
                  }
                  required
                />
              </div>

              <div className="form-group">
                <label htmlFor="service-start">Start Time *</label>
                <input
                  id="service-start"
                  type="time"
                  value={formData.start_time}
                  onChange={(e) =>
                    setFormData({ ...formData, start_time: e.target.value })
                  }
                  required
                />
              </div>

              <div className="form-group">
                <label htmlFor="service-end">End Time *</label>
                <input
                  id="service-end"
                  type="time"
                  value={formData.end_time}
                  onChange={(e) =>
                    setFormData({ ...formData, end_time: e.target.value })
                  }
                  required
                />
              </div>

              <div className="form-group">
                <label htmlFor="service-venue">Venue</label>
                <input
                  id="service-venue"
                  value={formData.venue}
                  onChange={(e) =>
                    setFormData({ ...formData, venue: e.target.value })
                  }
                  placeholder="e.g. Main Auditorium"
                />
              </div>

              <div className="form-group">
                <label htmlFor="attendance-start">Attendance Opens *</label>
                <input
                  id="attendance-start"
                  type="time"
                  value={formData.attendance_start}
                  onChange={(e) =>
                    setFormData({
                      ...formData,
                      attendance_start: e.target.value,
                    })
                  }
                  required
                />
              </div>

              <div className="form-group">
                <label htmlFor="attendance-end">Attendance Closes *</label>
                <input
                  id="attendance-end"
                  type="time"
                  value={formData.attendance_end}
                  onChange={(e) =>
                    setFormData({
                      ...formData,
                      attendance_end: e.target.value,
                    })
                  }
                  required
                />
              </div>
            </div>

            <div className="form-actions">
              <Button variant="secondary" onClick={closeForm}>
                Cancel
              </Button>

              <Button type="submit" loading={saving}>
                {editingId ? "Save Changes" : "Create Service"}
              </Button>
            </div>
          </form>
        </div>
      )}

      <div className="services-section">
        <div className="services-section-header">
          <div>
            <h2>All Services</h2>
            <p>Manage your scheduled church services.</p>
          </div>

          <Button
            variant="outline"
            size="small"
            leftIcon={<RefreshCw size={15} />}
            onClick={loadServices}
          >
            Refresh
          </Button>
        </div>

        <div className="service-search">
          <Search size={19} />
          <input
            type="search"
            placeholder="Search service or venue..."
            value={search}
            onChange={(e) => setSearch(e.target.value)}
          />
        </div>

        {loading ? (
          <div className="page-card service-empty">
            <RefreshCw size={30} />
            <p>Loading services...</p>
          </div>
        ) : filteredServices.length === 0 ? (
          <div className="page-card service-empty">
            <CalendarDays size={42} />
            <h2>No Services Found</h2>
            <p>
              {search
                ? "Try searching with another name or venue."
                : "Create your first church service to get started."}
            </p>

            {!search && (
              <Button
                leftIcon={<Plus size={17} />}
                onClick={openCreateForm}
              >
                Create First Service
              </Button>
            )}
          </div>
        ) : (
          <div className="services-grid">
            {filteredServices.map((service) => (
              <div className="service-card" key={service.id}>
                <div className="service-card-top">
                  <div className="service-icon">
                    <CalendarDays size={22} />
                  </div>

                  <span className={`service-status ${service.status}`}>
                    {getStatusLabel(service.status)}
                  </span>
                </div>

                <h3>{service.name}</h3>

                <div className="service-details">
                  <p>
                    <CalendarDays size={17} />
                    <span>{formatDate(service.date)}</span>
                  </p>

                  <p>
                    <Clock size={17} />
                    <span>
                      {formatTime(service.start_time)} – {formatTime(service.end_time)}
                    </span>
                  </p>

                  <p>
                    <MapPin size={17} />
                    <span>{service.venue || "Venue not specified"}</span>
                  </p>

                  <p>
                    <Clock size={17} />
                    <span>
                      Attendance: {new Date(service.attendance_start).toLocaleTimeString("en-GH", { hour: "numeric", minute: "2-digit" })} – {new Date(service.attendance_end).toLocaleTimeString("en-GH", { hour: "numeric", minute: "2-digit" })}
                    </span>
                  </p>
                </div>

                <div className="service-card-footer">
                  {service.status === "scheduled" && (
                    <>
                      <Button
                        size="small"
                        onClick={() => handleServiceAction(service.id, "open")}
                        loading={actionLoading === service.id}
                      >
                        Open Service
                      </Button>

                      <Button
                        size="small"
                        variant="outline"
                        leftIcon={<Pencil size={15} />}
                        onClick={() => openEditForm(service)}
                      >
                        Edit
                      </Button>
                    </>
                  )}

                  {service.status === "open" && (
                    <>
                      <Button
                        size="small"
                        leftIcon={<QrCode size={15} />}
                        onClick={() => handleGenerateQR(service)}
                        loading={actionLoading === service.id}
                      >
                        Generate QR
                      </Button>

                      <Button
                        size="small"
                        variant="secondary"
                        leftIcon={<Lock size={15} />}
                        onClick={() => handleServiceAction(service.id, "close")}
                        loading={actionLoading === service.id}
                      >
                        Close
                      </Button>
                    </>
                  )}

                  {service.status === "scheduled" && (
                    <Button
                      size="small"
                      variant="danger"
                      leftIcon={<Ban size={15} />}
                      onClick={() => handleServiceAction(service.id, "cancel")}
                      loading={actionLoading === service.id}
                    >
                      Cancel
                    </Button>
                  )}
                </div>
              </div>
            ))}
          </div>
        )}
      </div>

      {qrData && (
        <div className="qr-modal-overlay">
          <div className="qr-modal">
            <button
              className="close-form-button qr-close"
              onClick={() => setQrData(null)}
              aria-label="Close QR code"
            >
              <X size={20} />
            </button>

            <div className="qr-modal-content">
              <QrCode size={32} />
              <h2>Attendance QR Code</h2>
              <p>{qrServiceName}</p>

              <img
                src={qrData.qr_code}
                alt={`Attendance QR code for ${qrServiceName}`}
              />

              <p className="qr-expiry">
                Expires: {new Date(qrData.expires_at).toLocaleString("en-GH")}
              </p>

              <Button
                variant="danger"
                onClick={handleRevokeQR}
                loading={actionLoading === qrData.service_id}
              >
                Revoke QR Code
              </Button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}

function CalendarCheckIcon() {
  return <CalendarDays size={21} />;
}
