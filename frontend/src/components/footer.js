import { Link } from "react-router-dom";

function Footer() {
  return (
    <footer className="footer">
      <div className="footerGrid">

        {/* Brand */}
        <div className="footerBrand">
          <h3 className="footerLogo"><i><b>Smart Purchase</b></i></h3>
          <p className="footerTagline">Compare prices across the web and make smarter buying decisions.</p>
        </div>

        {/* Quick Links */}
        <div className="footerSection">
          <h4>Quick Links</h4>
          <ul>
            <li><Link to="/">Home</Link></li>
            <li><Link to="/login">Login</Link></li>
            <li><Link to="/register">Register</Link></li>
            <li><Link to="/profile">Profile</Link></li>
          </ul>
        </div>

        {/* About the Project */}
        <div className="footerSection">
          <h4>About the Project</h4>
          <p>A smart shopping platform that scrapes Amazon, Flipkart, Croma, Reliance Digital and TataCliq to find you the best deal in real time.</p>
          <p style={{ marginTop: "8px" }}>
            <span className="footerBadge">SDG 12</span>
            <span className="footerBadge">SDG 16</span>
          </p>
        </div>

        {/* Team */}
        <div className="footerSection">
          <h4>Team — Div A</h4>
          <ul>
            <li>Suyash Gokarankar <span className="rollNo">#21</span></li>
            <li>Saurabh Jagdale <span className="rollNo">#24</span></li>
            <li>Yash Shedge <span className="rollNo">#54</span></li>
            <li>Heet Shah <span className="rollNo">#51</span></li>
          </ul>
          <p style={{ marginTop: "10px", fontSize: "13px", color: "#6e6e73" }}>
            Guide: Prof. Ashvini Gaikwad
          </p>
        </div>

      </div>

      <div className="footerBottom">
        <p>© 2025 Smart Purchase · Dept. of Computer Engineering</p>
      </div>
    </footer>
  );
}

export default Footer;
