import { Link, useNavigate, useSearchParams } from "react-router-dom";
import { useState, useEffect } from "react";

function Navbar() {
  const navigate = useNavigate();
  const [searchParams] = useSearchParams();
  const [searchText, setSearchText] = useState(searchParams.get("q") || "");
  const [isLoggedIn, setIsLoggedIn] = useState(!!localStorage.getItem("access"));

  // Re-check auth state whenever the component re-renders or storage changes
  useEffect(() => {
    const checkAuth = () => setIsLoggedIn(!!localStorage.getItem("access"));

    // Listen for storage changes (e.g. login/logout in another tab)
    window.addEventListener("storage", checkAuth);

    // Also check on every navigation by polling — simple and reliable
    const interval = setInterval(checkAuth, 500);

    return () => {
      window.removeEventListener("storage", checkAuth);
      clearInterval(interval);
    };
  }, []);

  useEffect(() => {
    setSearchText(searchParams.get("q") || "");
  }, [searchParams]);

  const handleSearch = (e) => {
    e.preventDefault();
    navigate(`/?q=${encodeURIComponent(searchText)}`);
  };

  const handleLogout = () => {
    localStorage.removeItem("access");
    localStorage.removeItem("refresh");
    localStorage.removeItem("user");
    setIsLoggedIn(false);
    navigate("/login");
  };

  return (
    <div className="navbar">
      <div className="logo"><i><b>Smart Purchase</b></i></div>

      <form className="searchForm" onSubmit={handleSearch}>
        <input
          className="search"
          placeholder="Search products..."
          value={searchText}
          onChange={(e) => setSearchText(e.target.value)}
        />
      </form>

      <div className="navLinks">
        <Link to="/">Home</Link>
        {isLoggedIn ? (
          <>
            <Link to="/profile">Profile</Link>
            <button
              onClick={handleLogout}
              className="navLogoutBtn"
            >
              Logout
            </button>
          </>
        ) : (
          <>
            <Link to="/login">Login</Link>
            <Link to="/register">Register</Link>
          </>
        )}
      </div>
    </div>
  );
}

export default Navbar;