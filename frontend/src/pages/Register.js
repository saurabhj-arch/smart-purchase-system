import { useState } from "react";
import { useNavigate, Link } from "react-router-dom";

function Register() {
  const navigate = useNavigate();
  const [form, setForm] = useState({
    name: "",
    email: "",
    phone: "",
    username: "",
    password: "",
    confirmPassword: "",
  });
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(false);

  const handleChange = (e) => {
    setForm({ ...form, [e.target.name]: e.target.value });
  };

  const handleRegister = async (e) => {
    e.preventDefault();
    setError("");

    if (!form.name || !form.email || !form.username || !form.phone || !form.password || !form.confirmPassword) {
      setError("Please fill in all fields.");
      return;
    }

    if (form.password !== form.confirmPassword) {
      setError("Passwords do not match.");
      return;
    }

    if (form.password.length < 6) {
      setError("Password: Must be at least 6 characters.");
      return;
    }

    setLoading(true);
    try {
      const res = await fetch("http://localhost:8000/api/accounts/register/", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          first_name: form.name,
          email: form.email,
          username: form.username,
          phone: form.phone,
          password: form.password,
        }),
      });

      const data = await res.json();

      if (res.ok) {
        localStorage.setItem("access", data.access);
        localStorage.setItem("refresh", data.refresh);
        localStorage.setItem("user", JSON.stringify(data.user));
        navigate("/");
      } else {
        // Build readable error messages with field names
        const fieldLabels = {
          first_name: "Full Name",
          email: "Email",
          username: "Username",
          phone: "Phone",
          password: "Password",
        };
        const messages = Object.entries(data).map(([field, errors]) => {
          const label = fieldLabels[field] || field;
          const msg = Array.isArray(errors) ? errors[0] : errors;
          return `${label}: ${msg}`;
        });
        setError(messages.join(" · "));
      }
    } catch (err) {
      setError("Cannot connect to server. Please try again.");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="loginPageWrapper">
      <div className="loginBox">
        <h2>Create Account</h2>
        <p>Sign up to start finding the best deals.</p>

        <form className="loginForm" onSubmit={handleRegister}>
          <input
            type="text"
            name="name"
            placeholder="Full name"
            value={form.name}
            onChange={handleChange}
          />

          <input
            type="text"
            name="username"
            placeholder="Username"
            value={form.username}
            onChange={handleChange}
          />

          <input
            type="email"
            name="email"
            placeholder="Email address"
            value={form.email}
            onChange={handleChange}
          />

          <input
            type="tel"
            name="phone"
            placeholder="Phone number"
            value={form.phone}
            onChange={handleChange}
          />

          <input
            type="password"
            name="password"
            placeholder="Password (min. 6 characters)"
            value={form.password}
            onChange={handleChange}
          />

          <input
            type="password"
            name="confirmPassword"
            placeholder="Confirm password"
            value={form.confirmPassword}
            onChange={handleChange}
          />

          {error && (
            <p style={{ color: "#ff3b30", fontSize: "14px", margin: 0 }}>
              {error}
            </p>
          )}

          <button type="submit" className="loginBtn" disabled={loading}>
            {loading ? "Creating account..." : "Register"}
          </button>
        </form>

        <p style={{ marginTop: "16px", fontSize: "14px", color: "#6e6e73" }}>
          Already have an account?{" "}
          <Link to="/login" style={{ color: "#0071e3", fontWeight: 600 }}>
            Login
          </Link>
        </p>
      </div>
    </div>
  );
}

export default Register;