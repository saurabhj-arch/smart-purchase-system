import { Link, useNavigate, useSearchParams } from "react-router-dom";
import { useState, useEffect } from "react";

function Navbar() {
  const navigate = useNavigate();
  const [searchParams] = useSearchParams();
  const [searchText, setSearchText] = useState(searchParams.get("q") || "");

  useEffect(() => {
    setSearchText(searchParams.get("q") || "");
  }, [searchParams]);

  const handleSearch = (e) => {
    e.preventDefault();
    navigate(`/?q=${encodeURIComponent(searchText)}`);
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
        <Link to="/login">Login</Link>
      </div>
    </div>
  );
}

export default Navbar;