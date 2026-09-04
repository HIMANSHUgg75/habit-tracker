import { useEffect, useState } from "react";
import "@/App.css";
import axios from "axios";
import { Check, Flame, LoaderCircle, Plus, Trophy } from "lucide-react";

const BACKEND_URL = process.env.REACT_APP_BACKEND_URL || "http://localhost:8000";
const API = `${BACKEND_URL}/api`;

const Home = () => {
  const [summary, setSummary] = useState(null);
  const [habitName, setHabitName] = useState("");
  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);
  const [message, setMessage] = useState("");

  const loadSummary = async () => {
    try {
      const response = await axios.get(`${API}/habits/summary`);
      setSummary(response.data);
    } catch (error) {
      setMessage("Backend unavailable. Start FastAPI on port 8000.");
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadSummary();
  }, []);

  const logHabit = async (event) => {
    event.preventDefault();
    if (!habitName.trim()) return;
    setSaving(true);
    setMessage("");
    try {
      const response = await axios.post(`${API}/habits/log`, { name: habitName });
      setMessage(response.data.already_logged_today ? "Already counted today." : `${response.data.habit} logged for today.`);
      setHabitName("");
      await loadSummary();
    } catch (error) {
      setMessage(error.response?.data?.detail || "Could not log that habit.");
    } finally {
      setSaving(false);
    }
  };

  return (
    <main className="app-shell">
      <section className="hero">
        <div className="eyebrow"><span className="eyebrow-dot" /> DAILY PRACTICE</div>
        <h1>Small promises,<br /><em>kept daily.</em></h1>
        <p className="hero-copy">A calm place to notice your progress and keep the rhythm going.</p>
        <form className="log-form" onSubmit={logHabit}>
          <input value={habitName} onChange={(event) => setHabitName(event.target.value)} placeholder="What did you do today?" aria-label="Habit name" />
          <button type="submit" disabled={saving || !habitName.trim()}>{saving ? <LoaderCircle className="spin" size={18} /> : <Plus size={18} />} Log habit</button>
        </form>
        {message && <p className="message" role="status">{message}</p>}
      </section>

      <section className="dashboard">
        <div className="section-heading"><div><span className="eyebrow">YOUR RHYTHM</span><h2>Keep showing up.</h2></div><div className="today"><Check size={15} /> {new Date().toLocaleDateString(undefined, { weekday: "short", month: "short", day: "numeric" })}</div></div>
        {loading ? <div className="loading"><LoaderCircle className="spin" /> Loading your habits...</div> : !summary?.habits?.length ? <div className="empty">No habits yet. Log your first one above.</div> : <div className="habit-grid">{summary.habits.map((habit) => <article className={`habit-card ${habit.habit === summary.best ? "featured" : ""}`} key={habit.habit}><div className="card-top"><span className="habit-icon"><Flame size={18} /></span>{habit.habit === summary.best && <span className="best"><Trophy size={13} /> TOP STREAK</span>}</div><h3>{habit.habit}</h3><div className="streak-number">{habit.streak}<span> days</span></div><div className="card-bottom"><span>{habit.streak ? "Active now" : "Ready to restart"}</span><span>best {habit.longest_streak}d</span></div></article>)}</div>}
        {summary?.best && <div className="summary-line"><Trophy size={18} /> <strong>{summary.best}</strong> is your most consistent habit with a {summary.streak}-day streak.</div>}
      </section>
    </main>
  );
};

function App() { return <Home />; }

export default App;
