import React, { useEffect, useState } from "react";

function App() {
  const [view, setView] = useState("signin");
  const [theme, setTheme] = useState("light");

  useEffect(() => {
    const stored = window.localStorage.getItem("theme");
    const prefersDark = window.matchMedia && window.matchMedia("(prefers-color-scheme: dark)").matches;
    const initial = stored || (prefersDark ? "dark" : "light");
    setTheme(initial);
    document.documentElement.dataset.theme = initial;
  }, []);

  useEffect(() => {
    document.documentElement.dataset.theme = theme;
    window.localStorage.setItem("theme", theme);
  }, [theme]);

  const toggleTheme = () => {
    setTheme((prev) => (prev === "dark" ? "light" : "dark"));
  };

  return (
    <div className="app-root">
      <header className="app-header">
        <h1>Spam Email Classifier</h1>
        <nav>
          <button onClick={() => setView("signin")}>Sign in</button>
          <button onClick={() => setView("signup")}>Sign up</button>
          <button onClick={() => setView("classify")}>Classify</button>
          <button type="button" onClick={toggleTheme}>
            Theme: {theme === "dark" ? "Dark" : "Light"}
          </button>
        </nav>
      </header>
      <main>
        {view === "signin" && <SigninView />}
        {view === "signup" && <SignupView />}
        {view === "classify" && <ClassifyView />}
      </main>
    </div>
  );
}

function SigninView() {
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [message, setMessage] = useState("");

  const handleSubmit = async (event) => {
    event.preventDefault();
    setMessage("");

    const formData = new FormData();
    formData.append("email", email);
    formData.append("password", password);

    try {
      const response = await fetch("/signin", {
        method: "POST",
        body: formData,
      });

      if (response.redirected) {
        window.location.href = response.url;
        return;
      }

      setMessage("Sign-in response received.");
    } catch (error) {
      setMessage("Sign-in failed: network error.");
    }
  };

  return (
    <section>
      <h2>Sign in</h2>
      <form onSubmit={handleSubmit}>
        <label>
          Email
          <input
            type="email"
            value={email}
            onChange={(e) => setEmail(e.target.value)}
            required
            autoComplete="email"
          />
        </label>
        <label>
          Password
          <input
            type="password"
            value={password}
            onChange={(e) => setPassword(e.target.value)}
            required
            autoComplete="current-password"
          />
        </label>
        <button type="submit">Sign in</button>
      </form>
      {message && <p>{message}</p>}
    </section>
  );
}

function SignupView() {
  const [form, setForm] = useState({
    full_name: "",
    username: "",
    email: "",
    phone: "",
    password: "",
    confirm_password: "",
  });
  const [message, setMessage] = useState("");

  const handleChange = (e) => {
    setForm({ ...form, [e.target.name]: e.target.value });
  };

  const handleSubmit = async (event) => {
    event.preventDefault();
    setMessage("");

    const data = new FormData();
    Object.entries(form).forEach(([key, value]) => {
      data.append(key, value);
    });

    try {
      const response = await fetch("/signup", {
        method: "POST",
        body: data,
      });

      if (response.redirected) {
        window.location.href = response.url;
        return;
      }

      setMessage("Signup response received.");
    } catch (error) {
      setMessage("Signup failed: network error.");
    }
  };

  return (
    <section>
      <h2>Sign up</h2>
      <form onSubmit={handleSubmit}>
        <label>
          Full name
          <input
            name="full_name"
            value={form.full_name}
            onChange={handleChange}
            required
          />
        </label>
        <label>
          Username
          <input
            name="username"
            value={form.username}
            onChange={handleChange}
            required
          />
        </label>
        <label>
          Email
          <input
            type="email"
            name="email"
            value={form.email}
            onChange={handleChange}
            required
          />
        </label>
        <label>
          Phone
          <input
            name="phone"
            value={form.phone}
            onChange={handleChange}
            required
          />
        </label>
        <label>
          Password
          <input
            type="password"
            name="password"
            value={form.password}
            onChange={handleChange}
            required
          />
        </label>
        <label>
          Confirm password
          <input
            type="password"
            name="confirm_password"
            value={form.confirm_password}
            onChange={handleChange}
            required
          />
        </label>
        <button type="submit">Sign up</button>
      </form>
      {message && <p>{message}</p>}
    </section>
  );
}

function ClassifyView() {
  const [text, setText] = useState("");
  const [result, setResult] = useState(null);
  const [loading, setLoading] = useState(false);

  const handleSubmit = async (event) => {
    event.preventDefault();
    if (!text.trim()) return;

    setLoading(true);
    setResult(null);

    try {
      const response = await fetch("/api/predict", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ text }),
      });

      const data = await response.json();
      setResult(data);
    } catch (error) {
      setResult({ error: "Prediction failed" });
    } finally {
      setLoading(false);
    }
  };

  return (
    <section>
      <h2>Classify message</h2>
      <form onSubmit={handleSubmit}>
        <label>
          Message
          <textarea
            rows={5}
            value={text}
            onChange={(e) => setText(e.target.value)}
            required
          />
        </label>
        <button type="submit" disabled={loading}>
          {loading ? "Predicting..." : "Predict"}
        </button>
      </form>
      {result && !result.error && (
        <div>
          <p>Prediction: {result.prediction}</p>
          <p>Probability: {Math.round((result.probability || 0) * 100)}%</p>
          <p>Model version: {result.model_version}</p>
        </div>
      )}
      {result && result.error && <p>{result.error}</p>}
    </section>
  );
}

export default App;
