
import {
  House,
  Info,
  LayoutGrid,
  CirclePlus,
  Search
} from 'lucide-react'
import ThemeToggle from '../components/ThemeToggle'
import '../App.css'

function App() {
  return (
    <div className="app">

      <aside className="sidebar">
        <div className="brand">
          <span className="brand-icon">C</span>
          <span>CivicTrack</span>
        </div>

        <p className="sidebar-label">MAIN MENU</p>

        <nav className="sidebar-nav">
          <a href="#home" className="active">
            <House size={20} />
            <span>Home</span>
          </a>

          <a href="#about">
            <Info size={20} />
            <span>About</span>
          </a>

          <a href="#services">
            <LayoutGrid size={20} />
            <span>Services</span>
          </a>

          <a href="#report">
            <CirclePlus size={20} />
            <span>Report an Issue</span>
          </a>

          <a href="#track">
            <Search size={20} />
            <span>Track Complaint</span>
          </a>
        </nav>

       <div className="sidebar-bottom">
  <ThemeToggle />

  <a href="/login" className="sidebar-login">Login</a>
  <a href="#register" className="sidebar-register">Register</a>
</div>
      </aside>

      <main className="main-content">

        <section className="hero-section" id="home">
          <div className="hero-content">
            <span className="hero-tag">
              SMART PUBLIC SERVICE PLATFORM
            </span>

            <h1>
              Building Better Communities,
              <span> Together.</span>
            </h1>

            <p>
              Report civic issues, track complaints and stay informed.
              Join us in making your community cleaner, safer and better.
            </p>

            <div className="hero-actions">
              <a href="#services" className="primary-btn">
                Explore Services
              </a>

              <a href="#about" className="secondary-btn">
                Learn More
              </a>
            </div>
          </div>
        </section>

        <section className="services-section" id="services">
          <div className="section-heading">
            <h2>Our Public Services</h2>
            <p>
              A simple platform to report and track public infrastructure issues.
            </p>
          </div>

          <div className="service-grid">
            <div className="service-card">
              <h3>Report an Issue</h3>
              <p>
                Submit complaints about roads, water supply, garbage and more.
              </p>
            </div>

            <div className="service-card">
              <h3>Track Complaints</h3>
              <p>
                Follow the progress of your submitted public service requests.
              </p>
            </div>

            <div className="service-card">
              <h3>Public Transparency</h3>
              <p>
                Stay informed about complaint resolution and service performance.
              </p>
            </div>
          </div>
        </section>

        <section className="about-section" id="about">
          <h2>About CivicTrack</h2>
          <p>
            CivicTrack connects citizens and public service departments
            through a transparent complaint management platform.
          </p>
        </section>

        <footer className="footer">
            <p>© 2026 CivicTrack. Smart Public Service Platform.</p>        </footer>

      </main>
    </div>
  )
}

export default App
