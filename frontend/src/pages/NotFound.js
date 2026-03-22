import { Link } from "react-router-dom";

function NotFound() {
  return (
    <div className="loginPageWrapper">
      <div className="loginBox">
        <h2>404</h2>
        <p>Oops! The page you're looking for doesn't exist.</p>
        <Link to="/">
          <button className="loginBtn" style={{ marginTop: "16px" }}>
            Go Back Home
          </button>
        </Link>
      </div>
    </div>
  );
}

export default NotFound;
