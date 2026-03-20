import { useState } from "react";
import { useNavigate } from "react-router-dom";

function Login() {
  const navigate = useNavigate();
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");

  const handleLogin = (e) => {
    e.preventDefault();
    if (email && password) {
      navigate("/");
    }
  };

  return (
    <div className="loginPageWrapper">
      <div className="loginBox">
        <h2>Welcome Back</h2>
        <p>Login to continue exploring the best deals.</p>

        <form className="loginForm" onSubmit={handleLogin}>
          <input
            type="email"
            placeholder="Email address"
            value={email}
            onChange={(e) => setEmail(e.target.value)}
          />

          <input
            type="password"
            placeholder="Password"
            value={password}
            onChange={(e) => setPassword(e.target.value)}
          />

          <button type="submit" className="loginBtn">
            Login
          </button>
        </form>
      </div>
    </div>
  );
}

export default Login;