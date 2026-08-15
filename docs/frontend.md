# Frontend Documentation (`src/`)

This document provides a detailed breakdown of the React frontend codebase, consisting primarily of a single entry component (`App.jsx`).

---

## 1. `src/App.jsx` (Main Component)

This file contains the entirety of the frontend logic. It defines the main application shell, handles routing via local state, manages the theme, and defines the views for signing in, signing up, and classifying emails.

### Code Sections:

#### **`App` Component (The Shell)**
- **State Hooks:**
  - `const [view, setView] = useState("signin")`: Manages the currently active view instead of using a traditional routing library like `react-router-dom`.
  - `const [theme, setTheme] = useState("light")`: Stores the current visual theme.
- **Effect Hooks:**
  - `useEffect` (Initialization): Runs once on component mount. Checks `localStorage` for a saved theme preference. If absent, it queries the browser's system preference using `window.matchMedia("(prefers-color-scheme: dark)")`. It sets the local state and applies the theme string to `document.documentElement.dataset.theme`.
  - `useEffect` (Update): Runs whenever the `theme` state changes. It updates the DOM dataset attribute to immediately reflect the visual change via CSS, and persists the choice to `localStorage`.
- **Functions:**
  - `toggleTheme()`: A simple toggler function that swaps "dark" for "light" and vice-versa.
- **Render Output:**
  - Renders a container div (`className="app-root"`).
  - Renders the `<header>` with a `<nav>` bar containing buttons. Clicking these buttons updates the `view` state, driving navigation.
  - Renders the `<main>` area, conditionally displaying `<SigninView />`, `<SignupView />`, or `<ClassifyView />` depending on the current `view`.

#### **`SigninView` Component**
- **State Hooks:**
  - `email`, `password`: Controlled string states for the input fields.
  - `message`: Stores status messages (e.g., loading or error).
- **Functions:**
  - `handleSubmit(event)`:
    - Prevents the default browser form submission.
    - Constructs a `FormData` object containing the email and password.
    - Uses the `fetch` API to send a `POST` request to the backend `/signin` endpoint.
    - Handles redirects: If the Flask backend responds with a redirect (indicating successful login), it forces the browser to follow it (`window.location.href = response.url`).
    - Catches and displays network errors.
- **Render Output:**
  - A `<form>` containing standard `<input>` fields wired to the React state (`value={email}`, `onChange={...}`).

#### **`SignupView` Component**
- **State Hooks:**
  - `form`: A complex object state storing all registration fields (`full_name`, `username`, `email`, `phone`, `password`, `confirm_password`).
  - `message`: Stores status messages.
- **Functions:**
  - `handleChange(e)`: A generic handler that updates the specific property within the `form` object corresponding to the input's `name` attribute.
  - `handleSubmit(event)`:
    - Prevents default submission.
    - Iterates over the `form` state object, appending each key-value pair to a `FormData` object.
    - Uses `fetch` to `POST` to the backend `/signup` endpoint.
    - Follows any redirect issued by the backend upon successful registration.
    - Catches and displays errors.
- **Render Output:**
  - A comprehensive registration `<form>` where each `<input>` is bound to the corresponding key in the `form` state object via `name` and `onChange`.

#### **`ClassifyView` Component**
- **State Hooks:**
  - `text`: Stores the contents of the textarea.
  - `result`: Stores the JSON object returned from the API containing the prediction details.
  - `loading`: A boolean flag used to disable the submit button while a request is pending.
- **Functions:**
  - `handleSubmit(event)`:
    - Prevents default submission.
    - Checks for empty input (`!text.trim()`).
    - Sets `loading(true)` and clears previous results.
    - Makes a `POST` request to the backend JSON endpoint (`/api/predict`). Unlike the authentication forms, it sends a JSON payload (`JSON.stringify({ text })`) and sets the `Content-Type` header to `application/json`.
    - Awaits the JSON response, stores it in `result`, and disables the loading state.
    - Catches and displays errors.
- **Render Output:**
  - A `<form>` containing a `<textarea>` bound to the `text` state.
  - A submit button whose text and disabled state react to the `loading` variable.
  - Conditional rendering logic that displays the prediction, probability, and model version if the `result` state contains valid data without errors.
  - Conditional rendering to display any error string returned by the API or the fetch block.
