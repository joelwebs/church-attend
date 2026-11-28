import { useState, type FormEvent, type ChangeEvent } from "react";
import { useNavigate, Link } from "react-router-dom";
import { UserPlus } from "lucide-react";

import { createMember } from "../api/members";
import type { MemberFormData } from "../types/member";

import BackButton from "../components/common/BackButton";

import "../styles/membersRegisterationPage.css";
import "../styles/forms.css";

function getTodayDate(): string {
  const today = new Date();

  const year = today.getFullYear();
  const month = String(today.getMonth() + 1).padStart(2, "0");
  const day = String(today.getDate()).padStart(2, "0");

  return `${year}-${month}-${day}`;
}

function getErrorMessage(error: unknown): string {
  const err = error as {
    response?: {
      data?: Record<string, unknown>;
    };
  };

  const data = err.response?.data;

  if (data && typeof data === "object") {
    return Object.entries(data)
      .map(([field, value]) => {
        const message = Array.isArray(value)
          ? value.join(" ")
          : String(value);

        return `${field.replaceAll("_", " ")}: ${message}`;
      })
      .join(" ");
  }

  return "Unable to connect to the server. Please try again.";
}

export default function MemberRegistrationPage() {
  const navigate = useNavigate();

  const [formData, setFormData] = useState<MemberFormData>({
    membership_number: "",
    first_name: "",
    last_name: "",
    other_names: "",
    phone_number: "",
    email: "",
    date_joined: getTodayDate(),
    is_active: true,
  });

  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");
  const [success, setSuccess] = useState("");

  function handleChange(event: ChangeEvent<HTMLInputElement>) {
    const { name, value } = event.target;

    setFormData((previous) => ({
      ...previous,
      [name]: value,
    }));
  }

  async function handleSubmit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();

    if (loading) return;

    setError("");
    setSuccess("");

    const firstName = formData.first_name.trim();
    const lastName = formData.last_name.trim();

    if (!firstName || !lastName) {
      setError("First name and last name are required.");
      return;
    }

    setLoading(true);

    try {
      const newMember = await createMember({
        ...formData,
        membership_number: formData.membership_number?.trim() || "",
        first_name: firstName,
        last_name: lastName,
        other_names: formData.other_names?.trim() || "",
        phone_number: formData.phone_number?.trim() || "",
        email: formData.email?.trim() || "",
        is_active: true,
      });

      setSuccess(`${newMember.full_name} was registered successfully.`);

      window.setTimeout(() => {
        navigate("/members");
      }, 1200);
    } catch (err: unknown) {
      setError(getErrorMessage(err));
    } finally {
      setLoading(false);
    }
  }

  return (
    <div className="form-page">
      <div className="form-container">

        {/* Header */}
        <div className="form-header">
          <BackButton fallback="/members" />

          <p className="form-eyebrow">CHURCHATTEND</p>

          <div className="form-title-icon">
            <UserPlus size={26} />
          </div>

          <h1>Register New Member</h1>

          <p>Add a member to your church records.</p>
        </div>

        {/* Feedback */}
        {error && (
          <div className="form-error" role="alert">
            {error}
          </div>
        )}

        {success && (
          <div className="form-success" role="status">
            {success}
          </div>
        )}

        {/* Registration Form */}
        <form onSubmit={handleSubmit}>
          <div className="form-grid">

            <div className="form-group">
              <label htmlFor="first_name">First Name *</label>
              <input
                id="first_name"
                name="first_name"
                value={formData.first_name}
                onChange={handleChange}
                placeholder="Enter first name"
                autoComplete="given-name"
                required
              />
            </div>

            <div className="form-group">
              <label htmlFor="last_name">Last Name *</label>
              <input
                id="last_name"
                name="last_name"
                value={formData.last_name}
                onChange={handleChange}
                placeholder="Enter last name"
                autoComplete="family-name"
                required
              />
            </div>

            <div className="form-group">
              <label htmlFor="other_names">Other Names</label>
              <input
                id="other_names"
                name="other_names"
                value={formData.other_names}
                onChange={handleChange}
                placeholder="Optional"
              />
            </div>

            <div className="form-group">
              <label htmlFor="membership_number">
                Membership Number
              </label>
              <input
                id="membership_number"
                name="membership_number"
                value={formData.membership_number}
                onChange={handleChange}
                placeholder="Optional"
              />
            </div>

            <div className="form-group">
              <label htmlFor="phone_number">Phone Number</label>
              <input
                id="phone_number"
                name="phone_number"
                type="tel"
                value={formData.phone_number}
                onChange={handleChange}
                placeholder="e.g. 0241234567"
                autoComplete="tel"
              />
            </div>

            <div className="form-group">
              <label htmlFor="email">Email Address</label>
              <input
                id="email"
                name="email"
                type="email"
                value={formData.email}
                onChange={handleChange}
                placeholder="Optional"
                autoComplete="email"
              />
            </div>

            <div className="form-group">
              <label htmlFor="date_joined">Date Joined</label>
              <input
                id="date_joined"
                name="date_joined"
                type="date"
                value={formData.date_joined}
                onChange={handleChange}
              />
            </div>

          </div>

          {/* Actions */}
          <div className="form-actions">
            <Link
              to="/members"
              className="button-secondary"
              aria-disabled={loading}
              onClick={(event) => {
                if (loading) event.preventDefault();
              }}
            >
              Cancel
            </Link>

            <button type="submit" disabled={loading}>
              {loading ? (
                "Registering..."
              ) : (
                <>
                  <UserPlus size={17} />
                  Register Member
                </>
              )}
            </button>
          </div>
        </form>
      </div>
    </div>
  );
}
