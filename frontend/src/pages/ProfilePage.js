import { useState, useEffect } from "react";
import { useNavigate } from "react-router-dom";
import "../styles/ProfilePage.css";

// ─── Auth helper ───────────────────────────────────────────────────────────
function authHeaders() {
  return {
    "Content-Type": "application/json",
    Authorization: `Bearer ${localStorage.getItem("access")}`,
  };
}

// ─── Avatar initials helper ────────────────────────────────────────────────
function getInitials(name) {
  if (!name) return "?";
  return name
    .split(" ")
    .map((n) => n[0])
    .join("")
    .toUpperCase()
    .slice(0, 2);
}

// ─── Editable field row ────────────────────────────────────────────────────
function EditableField({ label, value, type = "text", editing, onChange }) {
  return (
    <div className="profileField">
      <span className="fieldLabel">{label}</span>
      {editing ? (
        <input
          className="fieldInput"
          type={type}
          value={value}
          onChange={(e) => onChange(e.target.value)}
        />
      ) : (
        <span className="fieldValue">{value || "—"}</span>
      )}
    </div>
  );
}

// ─── Main ProfilePage component ────────────────────────────────────────────
export default function ProfilePage() {
  const navigate = useNavigate();

  const [user, setUser] = useState(null);
  const [draft, setDraft] = useState({});
  const [editing, setEditing] = useState(false);
  const [activeTab, setActiveTab] = useState("profile");
  const [saveMsg, setSaveMsg] = useState("");
  const [history, setHistory] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");

  // ── Fetch user profile on mount ──────────────────────────────────────────
  useEffect(() => {
    const token = localStorage.getItem("access");
    if (!token) {
      navigate("/login");
      return;
    }

    fetch("http://localhost:8000/api/accounts/profile/", {
      headers: authHeaders(),
    })
      .then((res) => {
        if (res.status === 401) { navigate("/login"); return null; }
        return res.json();
      })
      .then((data) => {
        if (data) {
          setUser(data);
          setDraft(data);
        }
      })
      .catch(() => setError("Failed to load profile."))
      .finally(() => setLoading(false));
  }, [navigate]);

  // ── Fetch recently viewed when tab opens ─────────────────────────────────
  useEffect(() => {
    if (activeTab !== "history") return;

    fetch("http://localhost:8000/api/accounts/recently-viewed/", {
      headers: authHeaders(),
    })
      .then((res) => res.json())
      .then((data) => setHistory(Array.isArray(data) ? data : []))
      .catch(() => {});
  }, [activeTab]);

  // ── Save profile changes ─────────────────────────────────────────────────
  function handleSave() {
    fetch("http://localhost:8000/api/accounts/profile/", {
      method: "PATCH",
      headers: authHeaders(),
      body: JSON.stringify({
        first_name: draft.first_name,
        last_name: draft.last_name,
        email: draft.email,
      }),
    })
      .then((res) => res.json())
      .then((data) => {
        setUser(data);
        setDraft(data);
        setEditing(false);
        setSaveMsg("Changes saved!");
        setTimeout(() => setSaveMsg(""), 2500);
      })
      .catch(() => setError("Failed to save changes."));
  }

  function handleCancel() {
    setDraft(user);
    setEditing(false);
  }

  function handleLogout() {
    localStorage.removeItem("access");
    localStorage.removeItem("refresh");
    localStorage.removeItem("user");
    navigate("/login");
  }

  if (loading) {
    return (
      <div className="profilePageContent">
        <div className="profilePageHeader">
          <p style={{ color: "#6e6e73" }}>Loading profile...</p>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="profilePageContent">
        <div className="profilePageHeader">
          <p style={{ color: "#ff3b30" }}>{error}</p>
        </div>
      </div>
    );
  }

  const displayName = `${user?.first_name || ""} ${user?.last_name || ""}`.trim() || user?.username;
  const joinedDate = user?.date_joined
    ? new Date(user.date_joined).toLocaleDateString("en-US", { month: "long", year: "numeric" })
    : "—";

  return (
    <div className="profilePageContent">
      {/* Header */}
      <div className="profilePageHeader">
        <h1>My Profile</h1>
        <p>Manage your account and view your search history</p>
      </div>

      {/* Tab switcher */}
      <div className="profileTabs">
        <button
          className={`profileTab ${activeTab === "profile" ? "activeTab" : ""}`}
          onClick={() => setActiveTab("profile")}
        >
          Account Info
        </button>
        <button
          className={`profileTab ${activeTab === "history" ? "activeTab" : ""}`}
          onClick={() => setActiveTab("history")}
        >
          Recently Viewed
        </button>
      </div>

      {/* ── TAB: Profile ─────────────────────────────────── */}
      {activeTab === "profile" && (
        <div className="profileGrid">
          {/* Avatar card */}
          <div className="profileCard avatarCard">
            <div className="avatarCircle">
              <span className="avatarInitials">{getInitials(displayName)}</span>
            </div>
            <h2 className="avatarName">{displayName}</h2>
            <p className="avatarSub">Member since {joinedDate}</p>
            <div className="statRow">
              <div className="statBox">
                <span className="statNum">{history.length}</span>
                <span className="statLabel">Searches</span>
              </div>
              <div className="statBox">
                <span className="statNum">3</span>
                <span className="statLabel">Platforms</span>
              </div>
            </div>
          </div>

          {/* Info card */}
          <div className="profileCard infoCard">
            <div className="infoCardHeader">
              <h3>Personal Details</h3>
              {!editing ? (
                <button className="editBtn" onClick={() => setEditing(true)}>
                  ✏️ Edit
                </button>
              ) : (
                <div className="editActions">
                  <button className="saveBtn" onClick={handleSave}>Save</button>
                  <button className="cancelBtn" onClick={handleCancel}>Cancel</button>
                </div>
              )}
            </div>

            {saveMsg && <div className="saveMsg">✅ {saveMsg}</div>}

            <div className="fieldsGrid">
              <EditableField
                label="First Name"
                value={editing ? draft.first_name : user.first_name}
                editing={editing}
                onChange={(v) => setDraft({ ...draft, first_name: v })}
              />
              <EditableField
                label="Last Name"
                value={editing ? draft.last_name : user.last_name}
                editing={editing}
                onChange={(v) => setDraft({ ...draft, last_name: v })}
              />
              <EditableField
                label="Username"
                value={user.username}
                editing={false}
                onChange={() => {}}
              />
              <EditableField
                label="Email Address"
                type="email"
                value={editing ? draft.email : user.email}
                editing={editing}
                onChange={(v) => setDraft({ ...draft, email: v })}
              />
            </div>

            {/* Account actions */}
            <div className="accountActions">
              <h4>Account</h4>
              <button className="actionLink">🔒 Change Password</button>
              <button className="actionLink danger" onClick={handleLogout}>
                🚪 Logout
              </button>
              <button className="actionLink danger">🗑️ Delete Account</button>
            </div>
          </div>
        </div>
      )}

      {/* ── TAB: Recently Viewed ──────────────────────────── */}
      {activeTab === "history" && (
        <div className="historySection">
          {history.length === 0 ? (
            <div className="emptyState">
              <p>No recent searches yet. Start comparing prices!</p>
            </div>
          ) : (
            <div className="historyList">
              {history.map((item) => (
                <div className="historyCard" key={item.id}>
                  <div className="historyInfo">
                    <p className="historyProductName">{item.product.name}</p>
                    <p className="historyMeta">
                      Viewed on {new Date(item.viewed_at).toLocaleDateString()}
                    </p>
                  </div>
                  <button className="primaryBtn historyBtn">View Again</button>
                </div>
              ))}
            </div>
          )}
        </div>
      )}
    </div>
  );
}