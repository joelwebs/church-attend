
import {
  useEffect,
  useState,
  type FormEvent,
  type ChangeEvent,
} from "react";

import {
  Users,
  UserPlus,
  Search,
  RefreshCw,
  UserCheck,
  UserX,
  ChevronLeft,
  ChevronRight,
  X,
  Pencil,
  Archive,
  RotateCcw,
} from "lucide-react";

import {
  getMembers,
  getArchivedMembers,
  createMember,
  updateMember,
  deleteMember,
  restoreMember,
  activateMember,
  deactivateMember,
} from "../api/members";

import type {
  Member,
  MemberFormData,
  PaginatedMembers,
} from "../types/member";

import BackButton from "../components/common/BackButton";
import "../styles/members.css";

function getTodayDate(): string {
  const today = new Date();

  return [
    today.getFullYear(),
    String(today.getMonth() + 1).padStart(2, "0"),
    String(today.getDate()).padStart(2, "0"),
  ].join("-");
}

const initialFormData: MemberFormData = {
  membership_number: "",
  first_name: "",
  last_name: "",
  other_names: "",
  phone_number: "",
  email: "",
  date_joined: getTodayDate(),
  is_active: true,
};

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

  return "Something went wrong. Please try again.";
}

export default function MembersPage() {
  const [members, setMembers] = useState<Member[]>([]);
  const [search, setSearch] = useState("");
  const [activeSearch, setActiveSearch] = useState("");
  const [page, setPage] = useState(1);
  const [pagination, setPagination] =
    useState<PaginatedMembers | null>(null);

  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");
  const [actionLoading, setActionLoading] = useState<string | null>(null);

  // Active members or archived members
  const [showArchived, setShowArchived] = useState(false);

  // Registration and editing modal
  const [showModal, setShowModal] = useState(false);
  const [editingMember, setEditingMember] = useState<Member | null>(null);
  const [formData, setFormData] =
    useState<MemberFormData>(initialFormData);
  const [registering, setRegistering] = useState(false);
  const [formError, setFormError] = useState("");

  async function loadMembers(
    searchTerm = activeSearch,
    currentPage = page,
    archived = showArchived
  ) {
    setLoading(true);
    setError("");

    try {
      const data = archived
        ? await getArchivedMembers(searchTerm, currentPage)
        : await getMembers(searchTerm, currentPage);

      setMembers(data.results);
      setPagination(data);
    } catch {
      setError("Unable to load members. Please try again.");
    } finally {
      setLoading(false);
    }
  }

  useEffect(() => {
    loadMembers(activeSearch, page, showArchived);
  }, [activeSearch, page, showArchived]);

  function handleSearch(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    setPage(1);
    setActiveSearch(search.trim());
  }

  function openCreateModal() {
    setEditingMember(null);
    setFormData({
      ...initialFormData,
      date_joined: getTodayDate(),
    });
    setFormError("");
    setShowModal(true);
  }

  function openEditModal(member: Member) {
    setEditingMember(member);

    setFormData({
      membership_number: member.membership_number || "",
      first_name: member.first_name,
      last_name: member.last_name,
      other_names: member.other_names || "",
      phone_number: member.phone_number || "",
      email: member.email || "",
      date_joined: member.date_joined,
    });

    setFormError("");
    setShowModal(true);
  }

  function closeModal() {
    if (registering) return;

    setShowModal(false);
    setEditingMember(null);
    setFormError("");
  }

  function handleFormChange(event: ChangeEvent<HTMLInputElement>) {
    const { name, value } = event.target;

    setFormData((previous) => ({
      ...previous,
      [name]: value,
    }));
  }

  async function handleSubmit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();

    if (registering) return;

    const firstName = formData.first_name.trim();
    const lastName = formData.last_name.trim();

    if (!firstName || !lastName) {
      setFormError("First name and last name are required.");
      return;
    }

    setRegistering(true);
    setFormError("");

    const payload: MemberFormData = {
      ...formData,
      membership_number: formData.membership_number?.trim() || "",
      first_name: firstName,
      last_name: lastName,
      other_names: formData.other_names?.trim() || "",
      phone_number: formData.phone_number?.trim() || "",
      email: formData.email?.trim() || "",
      is_active: editingMember ? undefined : true,
    };

    try {
      if (editingMember) {
        await updateMember(editingMember.id, payload);
      } else {
        await createMember(payload);
      }

      setShowModal(false);
      setEditingMember(null);
      setSearch("");
      setActiveSearch("");
      setPage(1);

      await loadMembers("", 1, showArchived);
    } catch (err: unknown) {
      setFormError(getErrorMessage(err));
    } finally {
      setRegistering(false);
    }
  }

  async function handleStatusChange(member: Member) {
    const action = member.is_active ? "deactivate" : "activate";

    const confirmed = window.confirm(
      `Are you sure you want to ${action} ${member.full_name}?`
    );

    if (!confirmed) return;

    setActionLoading(member.id);
    setError("");

    try {
      if (member.is_active) {
        await deactivateMember(member.id);
      } else {
        await activateMember(member.id);
      }

      await loadMembers();
    } catch {
      setError(`Could not ${action} this member.`);
    } finally {
      setActionLoading(null);
    }
  }

  async function handleArchive(member: Member) {
    const confirmed = window.confirm(
      `Archive ${member.full_name}?\n\nTheir historical records will be preserved.`
    );

    if (!confirmed) return;

    setActionLoading(member.id);
    setError("");

    try {
      await deleteMember(member.id);
      await loadMembers();
    } catch {
      setError("Unable to archive this member. Please try again.");
    } finally {
      setActionLoading(null);
    }
  }

  async function handleRestore(member: Member) {
    const confirmed = window.confirm(
      `Restore ${member.full_name} to the members list?`
    );

    if (!confirmed) return;

    setActionLoading(member.id);
    setError("");

    try {
      await restoreMember(member.id);
      await loadMembers();
    } catch {
      setError("Unable to restore this member. Please try again.");
    } finally {
      setActionLoading(null);
    }
  }

  function changeView(archived: boolean) {
    setShowArchived(archived);
    setPage(1);
    setSearch("");
    setActiveSearch("");
    setError("");
  }

  const activeCount = members.filter(
    (member) => member.is_active
  ).length;

  const inactiveCount = members.filter(
    (member) => !member.is_active
  ).length;

  return (
    <div className="members-page">
      {/* Header */}
      <div className="members-header">
        <div>
          <BackButton fallback="/dashboard" />
          <p className="members-eyebrow">CHURCHATTEND</p>

          <h1>
            {showArchived ? "Archived Members" : "Church Members"}
          </h1>

          <p>
            {showArchived
              ? "View and restore archived church members."
              : "View and manage registered church members."}
          </p>
        </div>

        {!showArchived && (
          <button
            type="button"
            className="members-add-button"
            onClick={openCreateModal}
          >
            <UserPlus size={18} />
            Register Member
          </button>
        )}
      </div>

      {/* View switcher */}
      <div className="members-view-tabs">
        <button
          type="button"
          className={!showArchived ? "active" : ""}
          onClick={() => changeView(false)}
        >
          <Users size={17} />
          All Members
        </button>

        <button
          type="button"
          className={showArchived ? "active" : ""}
          onClick={() => changeView(true)}
        >
          <Archive size={17} />
          Archived Members
        </button>
      </div>

      {/* Statistics */}
      {!showArchived && (
        <div className="members-stats">
          <div className="member-stat-card">
            <div className="member-stat-icon">
              <Users size={22} />
            </div>
            <div>
              <span>Members on this page</span>
              <h2>{members.length}</h2>
            </div>
          </div>

          <div className="member-stat-card">
            <div className="member-stat-icon active">
              <UserCheck size={22} />
            </div>
            <div>
              <span>Active on this page</span>
              <h2>{activeCount}</h2>
            </div>
          </div>

          <div className="member-stat-card">
            <div className="member-stat-icon inactive">
              <UserX size={22} />
            </div>
            <div>
              <span>Inactive on this page</span>
              <h2>{inactiveCount}</h2>
            </div>
          </div>
        </div>
      )}

      {/* Members content */}
      <div className="members-content">
        <form className="members-search" onSubmit={handleSearch}>
          <div className="members-search-input">
            <Search size={19} />

            <input
              type="search"
              placeholder={
                showArchived
                  ? "Search archived members..."
                  : "Search members..."
              }
              value={search}
              onChange={(event) => setSearch(event.target.value)}
            />
          </div>

          <button type="submit">Search</button>

          <button
            type="button"
            className="members-refresh-button"
            onClick={() => loadMembers()}
            title="Refresh members"
          >
            <RefreshCw size={18} />
          </button>
        </form>

        {error && <div className="members-error">{error}</div>}

        {loading ? (
          <div className="members-loading">
            <RefreshCw className="members-spinner" size={24} />
            <p>Loading members...</p>
          </div>
        ) : members.length === 0 ? (
          <div className="members-empty">
            {showArchived ? (
              <Archive size={40} />
            ) : (
              <Users size={40} />
            )}

            <h3>
              {showArchived ? "No archived members" : "No members found"}
            </h3>

            <p>
              {activeSearch
                ? "Try another search term."
                : showArchived
                  ? "Archived members will appear here."
                  : "Register your first church member to get started."}
            </p>

            {!showArchived && !activeSearch && (
              <button
                type="button"
                className="members-add-button"
                onClick={openCreateModal}
              >
                <UserPlus size={18} />
                Register Member
              </button>
            )}
          </div>
        ) : (
          <>
            <div className="members-table-wrapper">
              <table className="members-table">
                <thead>
                  <tr>
                    <th>Member</th>
                    <th>Membership No.</th>
                    <th>Phone Number</th>
                    <th>Date Joined</th>
                    {!showArchived && <th>Status</th>}
                    {showArchived && <th>Archived On</th>}
                    <th>Actions</th>
                  </tr>
                </thead>

                <tbody>
                  {members.map((member) => (
                    <tr key={member.id}>
                      <td>
                        <div className="member-name">
                          <div className="member-avatar">
                            {member.first_name.charAt(0).toUpperCase()}
                          </div>

                          <div>
                            <strong>{member.full_name}</strong>
                            <span>{member.email || "No email"}</span>
                          </div>
                        </div>
                      </td>

                      <td>{member.membership_number || "—"}</td>
                      <td>{member.phone_number || "—"}</td>
                      <td>{member.date_joined || "—"}</td>

                      {!showArchived && (
                        <td>
                          <span
                            className={`member-status ${
                              member.is_active
                                ? "status-active"
                                : "status-inactive"
                            }`}
                          >
                            {member.is_active ? "Active" : "Inactive"}
                          </span>
                        </td>
                      )}

                      {showArchived && (
                        <td>
                          {member.deleted_at
                            ? new Date(member.deleted_at).toLocaleDateString()
                            : "—"}
                        </td>
                      )}

                      <td>
                        <div className="member-row-actions">
                          {showArchived ? (
                            <button
                              type="button"
                              className="member-action-button restore"
                              disabled={actionLoading === member.id}
                              onClick={() => handleRestore(member)}
                            >
                              <RotateCcw size={15} />
                              {actionLoading === member.id
                                ? "Please wait..."
                                : "Restore"}
                            </button>
                          ) : (
                            <>
                              <button
                                type="button"
                                className="member-action-button edit"
                                onClick={() => openEditModal(member)}
                              >
                                <Pencil size={15} />
                                Edit
                              </button>

                              <button
                                type="button"
                                className={`member-action-button ${
                                  member.is_active
                                    ? "deactivate"
                                    : "activate"
                                }`}
                                disabled={actionLoading === member.id}
                                onClick={() => handleStatusChange(member)}
                              >
                                {member.is_active ? "Deactivate" : "Activate"}
                              </button>

                              <button
                                type="button"
                                className="member-action-button archive"
                                disabled={actionLoading === member.id}
                                onClick={() => handleArchive(member)}
                              >
                                <Archive size={15} />
                                Archive
                              </button>
                            </>
                          )}
                        </div>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>

            {/* Pagination */}
            <div className="members-pagination">
              <span>
                {pagination?.count ?? members.length} total members
              </span>

              <div>
                <button
                  type="button"
                  disabled={!pagination?.previous}
                  onClick={() => setPage((current) => current - 1)}
                >
                  <ChevronLeft size={18} />
                  Previous
                </button>

                <span>Page {page}</span>

                <button
                  type="button"
                  disabled={!pagination?.next}
                  onClick={() => setPage((current) => current + 1)}
                >
                  Next
                  <ChevronRight size={18} />
                </button>
              </div>
            </div>
          </>
        )}
      </div>

      {/* Create / Edit Modal */}
      {showModal && (
        <div
          className="member-modal-overlay"
          onMouseDown={(event) => {
            if (event.target === event.currentTarget) {
              closeModal();
            }
          }}
        >
          <div
            className="member-modal"
            role="dialog"
            aria-modal="true"
            aria-labelledby="member-modal-title"
          >
            <div className="member-modal-header">
              <div>
                <div className="member-modal-icon">
                  {editingMember ? (
                    <Pencil size={22} />
                  ) : (
                    <UserPlus size={22} />
                  )}
                </div>

                <h2 id="member-modal-title">
                  {editingMember ? "Edit Member" : "Register New Member"}
                </h2>

                <p>
                  {editingMember
                    ? "Update this member's information."
                    : "Add a member to your church records."}
                </p>
              </div>

              <button
                type="button"
                className="member-modal-close"
                onClick={closeModal}
                disabled={registering}
                aria-label="Close modal"
              >
                <X size={22} />
              </button>
            </div>

            {formError && (
              <div className="form-error" role="alert">
                {formError}
              </div>
            )}

            <form onSubmit={handleSubmit}>
              <div className="member-modal-grid">
                <div className="form-group">
                  <label htmlFor="first_name">First Name *</label>
                  <input
                    id="first_name"
                    name="first_name"
                    value={formData.first_name}
                    onChange={handleFormChange}
                    placeholder="Enter first name"
                    required
                  />
                </div>

                <div className="form-group">
                  <label htmlFor="last_name">Last Name *</label>
                  <input
                    id="last_name"
                    name="last_name"
                    value={formData.last_name}
                    onChange={handleFormChange}
                    placeholder="Enter last name"
                    required
                  />
                </div>

                <div className="form-group">
                  <label htmlFor="other_names">Other Names</label>
                  <input
                    id="other_names"
                    name="other_names"
                    value={formData.other_names || ""}
                    onChange={handleFormChange}
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
                    value={formData.membership_number || ""}
                    onChange={handleFormChange}
                    placeholder="Optional"
                  />
                </div>

                <div className="form-group">
                  <label htmlFor="phone_number">Phone Number</label>
                  <input
                    id="phone_number"
                    name="phone_number"
                    type="tel"
                    value={formData.phone_number || ""}
                    onChange={handleFormChange}
                    placeholder="e.g. 0241234567"
                  />
                </div>

                <div className="form-group">
                  <label htmlFor="email">Email Address</label>
                  <input
                    id="email"
                    name="email"
                    type="email"
                    value={formData.email || ""}
                    onChange={handleFormChange}
                    placeholder="Optional"
                  />
                </div>

                <div className="form-group">
                  <label htmlFor="date_joined">Date Joined</label>
                  <input
                    id="date_joined"
                    name="date_joined"
                    type="date"
                    value={formData.date_joined || ""}
                    onChange={handleFormChange}
                  />
                </div>
              </div>

              <div className="member-modal-actions">
                <button
                  type="button"
                  className="member-modal-cancel"
                  onClick={closeModal}
                  disabled={registering}
                >
                  Cancel
                </button>

                <button
                  type="submit"
                  className="members-add-button"
                  disabled={registering}
                >
                  {registering
                    ? "Please wait..."
                    : editingMember
                      ? "Save Changes"
                      : "Register Member"}
                </button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  );
}
