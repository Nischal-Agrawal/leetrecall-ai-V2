import { lazy, Suspense, useEffect, useState } from 'react';
import { BrowserRouter, Navigate, Route, Routes, useLocation, useNavigate } from 'react-router-dom';
import {
  Activity,
  BrainCircuit,
  CalendarDays,
  ChartNoAxesCombined,
  CircleAlert,
  ClipboardList,
  CodeXml,
  Database,
  LayoutDashboard,
  ListChecks,
  RotateCcw,
  Users,
} from 'lucide-react';

const DecayChart = lazy(() => import('./AnalyticsCharts.jsx').then((module) => ({ default: module.DecayChart })));
const TopicCoverageChart = lazy(() => import('./AnalyticsCharts.jsx').then((module) => ({ default: module.TopicCoverageChart })));

const tokenKey = 'leetrecall-token';

const navItems = [
  'Dashboard',
  'Question Library',
  'Revision Queue',
  'Decay Analysis',
  'Topic Mastery',
  'Pattern Coverage',
  'Weak Areas',
  'Contest Analyzer',
  'AI Coach',
  'Interview Planner',
];

const navPaths = {
  Dashboard: '/',
  'Question Library': '/questions',
  'Revision Queue': '/revisions',
  'Decay Analysis': '/decay',
  'Topic Mastery': '/topics',
  'Pattern Coverage': '/patterns',
  'Weak Areas': '/weak-areas',
  'Contest Analyzer': '/contests',
  'AI Coach': '/coach',
  'Interview Planner': '/interview',
};

const navIcons = {
  Dashboard: LayoutDashboard,
  'Question Library': CodeXml,
  'Revision Queue': ListChecks,
  'Decay Analysis': Activity,
  'Topic Mastery': ChartNoAxesCombined,
  'Pattern Coverage': ChartNoAxesCombined,
  'Weak Areas': CircleAlert,
  'Contest Analyzer': ClipboardList,
  'AI Coach': BrainCircuit,
  'Interview Planner': CalendarDays,
};

const fallbackDashboard = {
  totalUsers: 0,
  totalQuestions: 0,
  totalSolved: 0,
  totalRevisions: 0,
  streak: 0,
  mastery: 0,
  weakTopics: [],
  confidenceScore: 0,
};

const buttonStyle = {
  background: 'linear-gradient(135deg, rgba(59,130,246,0.12), rgba(168,85,247,0.12))',
  border: '1px solid rgba(96,165,250,0.3)',
};

const formatPercent = (value) => `${Math.round(Number(value || 0) * 100)}%`;

async function apiFetch(path, options = {}) {
  const headers = { Accept: 'application/json', ...(options.headers || {}) };
  const token = localStorage.getItem(tokenKey);

  if (token) headers.Authorization = `Bearer ${token}`;
  if (options.body && typeof options.body !== 'string') {
    headers['Content-Type'] = 'application/json';
    options.body = JSON.stringify(options.body);
  }

  const response = await fetch(`/api${path}`, { cache: 'no-store', ...options, headers });
  const payload = await response.json().catch(() => ({}));

  if (!response.ok) throw new Error(payload.message || 'Request failed');
  if (Array.isArray(payload) && (path === '/recommendations' || path === '/knowledge-decay')) {
    payload.modelSource = response.headers.get('X-ML-Source') || 'unknown';
    payload.modelWarning = response.headers.get('X-ML-Warning') || '';
  }
  return payload;
}

function LoginPage({ onLogin }) {
  const [mode, setMode] = useState('login');
  const [form, setForm] = useState({ name: '', email: '', password: '' });
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(false);

  async function handleSubmit(event) {
    event.preventDefault();
    setLoading(true);
    setError('');

    try {
      const payload = await apiFetch(`/auth/${mode === 'signup' ? 'signup' : 'login'}`, { method: 'POST', body: form });
      localStorage.setItem(tokenKey, payload.token);
      onLogin(payload.user);
    } catch (err) {
      if (mode === 'signup' && err.message === 'User already exists.') {
        setMode('login');
        setError('This email already has an account. Sign in, or use the local password recovery command described in README.md.');
      } else {
        setError(err.message || 'Login failed');
      }
    } finally {
      setLoading(false);
    }
  }

  return (
    <div className="login-shell">
      <div className="login-card">
        <div className="brand-lockup small-brand">
          <div className="brain-icon">🧠</div>
          <div className="logo-copy" style={{ fontSize: '2.6rem' }}>LeetRecall AI</div>
        </div>

        <form onSubmit={handleSubmit} className="login-form">
          {mode === 'signup' && <label>
            <span>Name</span>
            <input required value={form.name} onChange={(e) => setForm({ ...form, name: e.target.value })} />
          </label>}
          <label>
            <span>Email</span>
            <input type="email" value={form.email} onChange={(e) => setForm({ ...form, email: e.target.value })} />
          </label>
          <label>
            <span>Password</span>
            <input type="password" minLength={8} required value={form.password} onChange={(e) => setForm({ ...form, password: e.target.value })} />
          </label>
          {error && <p className="error-text">{error}</p>}
          <button type="submit" disabled={loading}>{loading ? 'Please wait...' : mode === 'signup' ? 'Create account' : 'Sign in'}</button>
        </form>
        <button className="auth-mode-toggle" type="button" onClick={() => { setMode(mode === 'login' ? 'signup' : 'login'); setError(''); }}>
          {mode === 'login' ? 'Create an account' : 'Already registered? Sign in'}
        </button>
      </div>
    </div>
  );
}

function MetricCard({ item }) {
  const Icon = item.icon;
  return (
    <div className={`metric-card ${item.accent}`}>
      <div className="metric-icon"><Icon aria-hidden="true" /></div>
      <div className="metric-number">{item.value}</div>
      <div className="metric-label">{item.label}</div>
    </div>
  );
}

function ModelSource({ recommendations }) {
  const source = recommendations[0]?.source || recommendations.modelSource;
  if (!source) return null;

  const isTrainedModel = source === 'trained-xgboost' || source === 'trained-random-forest';
  const isUnavailable = source === 'unavailable';
  return (
    <p className={`model-source ${isTrainedModel ? 'trained' : 'fallback'}`}>
      {isTrainedModel
        ? 'AI model predictions'
        : isUnavailable
          ? 'AI model unavailable'
          : `Non-model response (${recommendations[0]?.model || source})`}
      {recommendations.modelWarning ? ` · ${recommendations.modelWarning}` : ''}
    </p>
  );
}

function recommendationsEmptyMessage(recommendations) {
  return recommendations.modelSource === 'unavailable'
    ? 'The trained model did not return predictions.'
    : 'No solve history is available for recommendations yet.';
}

function DashboardView({ dashboard, recommendations }) {
  const metrics = [
    { label: 'Total Users', value: dashboard.totalUsers ?? 0, icon: Users, accent: 'indigo' },
    { label: 'Questions', value: dashboard.totalQuestions ?? 0, icon: Database, accent: 'purple' },
    { label: 'Total Solves', value: dashboard.totalSolved ?? 0, icon: CodeXml, accent: 'teal' },
    { label: 'Revisions', value: dashboard.totalRevisions ?? 0, icon: RotateCcw, accent: 'amber' },
  ];

  return (
    <>
      <div className="page-header">
        <h1>Dashboard</h1>
        <p>Your intelligent DSA revision &amp; retention overview</p>
      </div>

      <div className="metrics-grid">
        {metrics.map((item) => (
          <MetricCard key={item.label} item={item} />
        ))}
      </div>

      <div className="panel-block">
        <h2>Questions To Revise</h2>
        <ModelSource recommendations={recommendations} />
        <table className="leet-table">
          <thead>
            <tr>
              <th>ID</th>
              <th>Title</th>
              <th>Topic</th>
              <th>Pattern</th>
              <th>Difficulty</th>
              <th>Risk</th>
              <th>Link</th>
            </tr>
          </thead>
          <tbody>
            {recommendations.map((row) => (
              <tr key={row.questionId || row.id || row.question_id || row.title}>
                <td>{row.questionId || row.id || row.question_id || '—'}</td>
                <td>{row.title}</td>
                <td>{row.topic}</td>
                <td>{row.pattern}</td>
                <td>{row.difficulty}</td>
                <td>{formatPercent(row.forgetProbability ?? row.forget_probability ?? 0)}</td>
                <td>
                  <a href={row.url || row.link} target="_blank" rel="noreferrer">leetcode</a>
                </td>
              </tr>
            ))}
            {recommendations.length === 0 && (
              <tr><td colSpan="7">{recommendationsEmptyMessage(recommendations)}</td></tr>
            )}
          </tbody>
        </table>
      </div>
    </>
  );
}

function RevisionQueueView({ recommendations }) {
  const [savingId, setSavingId] = useState(null);
  const [error, setError] = useState('');
  const rows = recommendations;

  async function recordRevision(item) {
    setSavingId(item.question_id);
    setError('');
    try {
      await apiFetch('/revisions', {
        method: 'POST',
        body: { questionId: item.question_id, revisionQuality: 0.8 },
      });
      window.dispatchEvent(new Event('leetrecall:data-changed'));
    } catch (requestError) {
      setError(requestError.message || 'Could not record revision.');
    } finally {
      setSavingId(null);
    }
  }

  return (
    <>
      <div className="page-header">
        <h1>Revision Queue</h1>
        <p>Questions sorted by forgetting probability</p>
      </div>
      <div className="panel-block">
        <ModelSource recommendations={rows} />
        {error && <div className="api-error" role="alert">{error}</div>}
        <table className="leet-table">
          <thead>
            <tr>
              <th>ID</th>
              <th>Title</th>
              <th>Topic</th>
              <th>Pattern</th>
              <th>Difficulty</th>
              <th>Forget Risk</th>
              <th>Link</th>
              <th>Action</th>
            </tr>
          </thead>
          <tbody>
            {rows.map((row) => (
              <tr key={row.question_id || row.id || row.title}>
                <td>{row.question_id || row.id || '—'}</td>
                <td>{row.title}</td>
                <td>{row.topic}</td>
                <td>{row.pattern}</td>
                <td>{row.difficulty}</td>
                <td>{formatPercent(row.forget_probability ?? row.forgetProbability ?? 0)}</td>
                <td><a href={row.url || row.link} target="_blank" rel="noreferrer">leetcode</a></td>
                <td><button className="table-action" onClick={() => recordRevision(row)} disabled={savingId === row.question_id}>
                  {savingId === row.question_id ? 'Saving…' : 'Revised'}
                </button></td>
              </tr>
            ))}
            {rows.length === 0 && <tr><td colSpan="8">{recommendationsEmptyMessage(rows)}</td></tr>}
          </tbody>
        </table>
      </div>
    </>
  );
}

function QuestionRow({ question }) {
  const [isOpen, setIsOpen] = useState(false);
  const [saving, setSaving] = useState(false);
  const [error, setError] = useState('');
  const [form, setForm] = useState({ timeTakenMinutes: 30, wrongAttempts: 0, hintsUsed: 0, confidenceScore: 0.7 });

  async function submitSolve(event) {
    event.preventDefault();
    setSaving(true);
    setError('');
    try {
      await apiFetch('/solves', { method: 'POST', body: { ...form, questionId: question.id } });
      setIsOpen(false);
      window.dispatchEvent(new Event('leetrecall:data-changed'));
    } catch (requestError) {
      setError(requestError.message || 'Could not record solve.');
    } finally {
      setSaving(false);
    }
  }

  return (
    <>
      <tr>
        <td>{question.id}</td>
        <td>{question.title}</td>
        <td>{question.topic}</td>
        <td>{question.pattern}</td>
        <td>{question.difficulty}</td>
        <td>{question.solved ? 'Solved' : 'Not solved'}</td>
        <td><a href={question.url} target="_blank" rel="noreferrer">leetcode</a></td>
        <td><button className="table-action" onClick={() => setIsOpen(!isOpen)}>{question.solved ? 'Log another solve' : 'Log solve'}</button></td>
      </tr>
      {isOpen && <tr><td colSpan="8">
        <form className="solve-entry-form" onSubmit={submitSolve}>
          <label>Minutes <input type="number" min="1" required value={form.timeTakenMinutes} onChange={(event) => setForm({ ...form, timeTakenMinutes: Number(event.target.value) })} /></label>
          <label>Wrong attempts <input type="number" min="0" required value={form.wrongAttempts} onChange={(event) => setForm({ ...form, wrongAttempts: Number(event.target.value) })} /></label>
          <label>Hints used <input type="number" min="0" required value={form.hintsUsed} onChange={(event) => setForm({ ...form, hintsUsed: Number(event.target.value) })} /></label>
          <label>Confidence (0-1) <input type="number" min="0" max="1" step="0.05" required value={form.confidenceScore} onChange={(event) => setForm({ ...form, confidenceScore: Number(event.target.value) })} /></label>
          <button type="submit" disabled={saving}>{saving ? 'Saving…' : 'Save solve'}</button>
          {error && <span className="error-text">{error}</span>}
        </form>
      </td></tr>}
    </>
  );
}

function QuestionsPage({ dataVersion }) {
  const [questions, setQuestions] = useState([]);
  const [search, setSearch] = useState('');
  const [difficulty, setDifficulty] = useState('All');
  const [error, setError] = useState('');

  useEffect(() => {
    let active = true;
    apiFetch('/questions')
      .then((data) => { if (active) setQuestions(data); })
      .catch((requestError) => { if (active) setError(requestError.message); });
    return () => { active = false; };
  }, [dataVersion]);

  const filteredQuestions = questions.filter((question) => (
    (difficulty === 'All' || question.difficulty === difficulty)
    && `${question.title} ${question.topic} ${question.pattern}`.toLowerCase().includes(search.toLowerCase())
  ));

  return (
    <>
      <div className="page-header">
        <h1>Question Library</h1>
        <p>{questions.length.toLocaleString()} questions in your PostgreSQL database</p>
      </div>
      <div className="table-toolbar">
        <input aria-label="Search questions" placeholder="Search title, topic, or pattern" value={search} onChange={(event) => setSearch(event.target.value)} />
        <select aria-label="Filter difficulty" value={difficulty} onChange={(event) => setDifficulty(event.target.value)}>
          {['All', 'Easy', 'Medium', 'Hard'].map((value) => <option key={value}>{value}</option>)}
        </select>
        <span>{filteredQuestions.length.toLocaleString()} shown</span>
      </div>
      {error && <div className="api-error" role="alert">{error}</div>}
      <div className="panel-block table-scroll">
        <table className="leet-table">
          <thead><tr><th>ID</th><th>Title</th><th>Topic</th><th>Pattern</th><th>Difficulty</th><th>Status</th><th>Link</th><th>Action</th></tr></thead>
          <tbody>
            {filteredQuestions.map((question) => <QuestionRow key={question.id} question={question} />)}
            {filteredQuestions.length === 0 && <tr><td colSpan="8">No questions match this search.</td></tr>}
          </tbody>
        </table>
      </div>
    </>
  );
}

function DecayAnalysisView({ recommendations }) {
  const decayData = recommendations.map((item) => ({
    label: item.title,
    value: Math.round((item.forgetProbability ?? item.forget_probability ?? 0) * 100),
  }));

  return (
    <>
      <div className="page-header">
        <h1>Decay Analysis</h1>
        <p>Visualize which problems you're most likely to forget</p>
      </div>
      <div className="panel-block charts-block">
        {decayData.length > 0
          ? <DecayChart data={decayData} />
          : <p className="empty-state">No prediction data is available yet.</p>}
      </div>
    </>
  );
}

function TopicAndPatternView({ type, topicMastery, patternCoverage }) {
  const data = type === 'Topic Mastery' ? topicMastery : patternCoverage;
  const labelKey = type === 'Topic Mastery' ? 'topic' : 'pattern';
  const valueKey = type === 'Topic Mastery' ? 'mastery' : 'coverage';
  const title = type === 'Topic Mastery' ? 'Topic Mastery' : 'Pattern Coverage';
  const average = data.length
    ? Math.round(data.reduce((sum, item) => sum + Number(item[valueKey] || 0), 0) / data.length)
    : 0;
  const focusCount = data.filter((item) => Number(item[valueKey] || 0) < 60).length;

  return (
    <>
      <div className="page-header">
        <h1>{title}</h1>
        <p>{type === 'Topic Mastery' ? 'Track proficiency across all DSA topics' : 'See how well you have covered each pattern'}</p>
      </div>

      <div className="two-col-charts">
        <div className="panel-block chart-panel">
          <div className="panel-title">{type === 'Topic Mastery' ? 'Mastery' : 'Coverage'}</div>
          {data.length > 0
            ? <TopicCoverageChart data={data} labelKey={labelKey} valueKey={valueKey} title={title} />
            : <p className="empty-state">No {type.toLowerCase()} data is available yet.</p>}
        </div>

        <div className="panel-block chart-panel">
          <div className="panel-title">Coverage Summary</div>
          <div className="summary-stat"><span>Average {type === 'Topic Mastery' ? 'mastery' : 'coverage'}</span><strong>{average}%</strong></div>
          <div className="summary-stat"><span>{type === 'Topic Mastery' ? 'Topics' : 'Patterns'} tracked</span><strong>{data.length}</strong></div>
          <div className="summary-stat"><span>Below 60%</span><strong>{focusCount}</strong></div>
        </div>
      </div>
    </>
  );
}

function WeakAreasView({ weakTopics, weakPatterns }) {
  const topicRows = weakTopics;
  const patternRows = weakPatterns;

  return (
    <>
      <div className="page-header">
        <h1>Weak Areas</h1>
        <p>Identify your weakest topics and patterns</p>
      </div>
      <div className="two-col-charts">
        <div className="panel-block chart-panel">
          <div className="panel-title">Weak Topics</div>
          <div className="mini-bars">
            {topicRows.map((item) => (
              <div className="mini-row" key={`weak-${item.topic}`}>
                <span>{item.topic}</span>
                <div className="mini-track"><div className="mini-fill" style={{ width: `${Math.max(25, item.weakness ?? item.mastery ?? 50)}%` }} /></div>
              </div>
            ))}
          </div>
        </div>
        <div className="panel-block chart-panel">
          <div className="panel-title">Weak Patterns</div>
          <div className="mini-bars alt">
            {patternRows.map((item) => (
              <div className="mini-row" key={`weak-pattern-${item.pattern}`}>
                <span>{item.pattern}</span>
                <div className="mini-track"><div className="mini-fill danger" style={{ width: `${Math.max(25, item.weakness ?? item.coverage ?? 50)}%` }} /></div>
              </div>
            ))}
          </div>
        </div>
      </div>
    </>
  );
}

function ContestAnalyzerView({ contestAnalysis }) {
  const contests = contestAnalysis?.contests || [];
  const [review, setReview] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');

  async function generateReview() {
    setLoading(true);
    setError('');
    try {
      setReview(await apiFetch('/contest-ai'));
    } catch (requestError) {
      setError(requestError.message || 'Could not generate contest review.');
    } finally {
      setLoading(false);
    }
  }

  return (
    <>
      <div className="page-header">
        <h1>Contest Analyzer</h1>
        <p>Contest questions matched to your weak patterns</p>
      </div>
      <div className="contest-actions">
        <span>{contests.length} matching sample questions</span>
        <button type="button" onClick={generateReview} disabled={loading}>
          {loading ? 'Reviewing…' : 'Generate AI review'}
        </button>
      </div>
      {error && <div className="api-error" role="alert">{error}</div>}
      {review?.review && <div className="panel-block contest-review">
        <p>{review.review}</p>
        {review.provider && <p className="ai-source">{review.provider} · {review.source}</p>}
        {review.warning && <p className="error-text">{review.warning}</p>}
        {(review.advice || []).map((item) => <p key={item}>{item}</p>)}
      </div>}
      <div className="panel-block">
        <table className="leet-table">
          <thead>
            <tr>
              <th>Question</th>
              <th>Pattern</th>
              <th>Difficulty</th>
              <th>Why it is recommended</th>
            </tr>
          </thead>
          <tbody>
            {contests.map((contest) => (
              <tr key={`${contest.question}-${contest.pattern}`}>
                <td>{contest.question}</td>
                <td>{contest.pattern}</td>
                <td>{contest.difficulty}</td>
                <td>{contest.reason}</td>
              </tr>
            ))}
            {contests.length === 0 && <tr><td colSpan="4">No contest questions currently match your weakest patterns.</td></tr>}
          </tbody>
        </table>
      </div>
    </>
  );
}

function AICoachView({ coachData }) {
  const isAIProvider = ['gemini', 'openai'].includes(coachData?.source);
  const sourceLabel = isAIProvider
    ? `Generated by ${coachData.provider} using your retention predictions`
    : coachData?.source === 'local-insights'
      ? 'Data-based guidance; configured AI providers are unavailable'
      : coachData?.source === 'unavailable'
        ? 'AI provider unavailable'
        : 'Coach insights have not loaded';

  return (
    <>
      <div className="page-header">
        <h1>AI Coach</h1>
        <p>Personalized revision advice based on your learning patterns</p>
      </div>
      <p className={`ai-source ${isAIProvider ? 'trained' : 'fallback'}`}>{sourceLabel}</p>
      {coachData?.warning && <div className="api-error" role="status">{coachData.warning}</div>}
      <div className="coach-grid">
        {coachData?.summary && (
          <div className="coach-card">
            <div className="coach-head">
              <div className="coach-title">Your next focus</div>
              <span className="coach-risk">PRIORITY</span>
            </div>
            <div className="coach-advice">
              <div className="coach-label">COACH ADVICE</div>
              <p>{coachData.summary}</p>
            </div>
          </div>
        )}
        {(coachData?.advice || []).map((item, index) => (
          <div key={`${index}-${item}`} className="coach-card">
            <div className="coach-head">
              <div className="coach-title">Revision action</div>
              <span className="coach-risk">NEXT STEP</span>
            </div>
            <div className="coach-advice">
              <div className="coach-label">COACH ADVICE</div>
              <p>{item}</p>
            </div>
          </div>
        ))}
        {!coachData && <p className="empty-state">Coach insights are loading from your retention data.</p>}
      </div>
    </>
  );
}

function InterviewPlannerView() {
  const [interviewDate, setInterviewDate] = useState(() => (
    new Date(Date.now() + 30 * 86400000).toISOString().slice(0, 10)
  ));
  const [plan, setPlan] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');

  async function handleGenerate() {
    setLoading(true);
    setError('');
    try {
      setPlan(await apiFetch('/interview-mode', { method: 'POST', body: { interviewDate } }));
    } catch (requestError) {
      setError(requestError.message || 'Could not generate an interview plan.');
    } finally {
      setLoading(false);
    }
  }

  return (
    <>
      <div className="page-header">
        <h1>Interview Planner</h1>
        <p>Get a personalized AI revision plan before your interview</p>
      </div>

      <div className="panel-block interview-box">
        <div className="interview-row">
          <div className="label">Select Interview Date</div>
          <input className="date-box" type="date" value={interviewDate} onChange={(event) => setInterviewDate(event.target.value)} />
        </div>

        {error && <div className="api-error" role="alert">{error}</div>}
        {plan?.warning && <div className="api-error" role="status">{plan.warning}</div>}
        {plan && <p className={`ai-source ${['gemini', 'openai'].includes(plan.source) ? 'trained' : 'fallback'}`}>
          {['gemini', 'openai'].includes(plan.source) ? `Generated by ${plan.provider} using your retention predictions` : 'Data-based plan; AI providers are unavailable'}
        </p>}
        {plan && <>
          <div className="panel-block">
            <div className="panel-title">Focus areas</div>
            <ul>{plan.focus.map((item) => <li key={item}>{item}</li>)}</ul>
          </div>
          <div className="panel-block">
            <div className="panel-title">Plan</div>
            <ol>{plan.plan.map((item) => <li key={item}>{item}</li>)}</ol>
          </div>
        </>}

        <button className="plan-button" style={buttonStyle} onClick={handleGenerate} disabled={loading || !interviewDate}>
          {loading ? 'Generating plan...' : '🚀 Generate Interview Plan'}
        </button>
      </div>
    </>
  );
}

function AppShell({ user, onLogout }) {
  const navigate = useNavigate();
  const location = useLocation();
  const activeView = Object.entries(navPaths).find(([, path]) => path === location.pathname)?.[0] || 'Dashboard';
  const [dataVersion, setDataVersion] = useState(0);
  const [dashboard, setDashboard] = useState(fallbackDashboard);
  const [recommendations, setRecommendations] = useState([]);
  const [topicMastery, setTopicMastery] = useState([]);
  const [patternCoverage, setPatternCoverage] = useState([]);
  const [weakTopics, setWeakTopics] = useState([]);
  const [weakPatterns, setWeakPatterns] = useState([]);
  const [contestAnalysis, setContestAnalysis] = useState({ contests: [] });
  const [coachData, setCoachData] = useState(null);
  const [loading, setLoading] = useState(false);
  const [loadError, setLoadError] = useState('');

  useEffect(() => {
    const refreshData = () => setDataVersion((current) => current + 1);
    window.addEventListener('leetrecall:data-changed', refreshData);
    return () => window.removeEventListener('leetrecall:data-changed', refreshData);
  }, []);

  useEffect(() => {
    let active = true;

    const loadData = async () => {
      setLoading(true);
      setLoadError('');
      try {
        const [dashboardData, recommendationData, topicData, patternData, weakTopicsData, weakPatternsData, contestData] = await Promise.all([
          apiFetch('/dashboard'),
          apiFetch('/recommendations'),
          apiFetch('/topic-mastery'),
          apiFetch('/pattern-coverage'),
          apiFetch('/weak-topics'),
          apiFetch('/weak-patterns'),
          apiFetch('/contest-analysis'),
        ]);

        if (!active) return;

        setDashboard({ ...fallbackDashboard, ...dashboardData });
        setRecommendations(Array.isArray(recommendationData) ? recommendationData : []);
        setTopicMastery(Array.isArray(topicData) ? topicData : []);
        setPatternCoverage(Array.isArray(patternData) ? patternData : []);
        setWeakTopics(Array.isArray(weakTopicsData) ? weakTopicsData : []);
        setWeakPatterns(Array.isArray(weakPatternsData) ? weakPatternsData : []);
        setContestAnalysis(contestData || { contests: [] });
      } catch (error) {
        if (!active) return;
        setLoadError(error.message || 'Could not load application data.');
        console.error('Failed to load app data:', error);
      } finally {
        if (active) setLoading(false);
      }
    };

    loadData();
    return () => {
      active = false;
    };
  }, [user.email, dataVersion]);

  useEffect(() => {
    if (activeView !== 'AI Coach') return undefined;
    let active = true;
    setCoachData(null);
    apiFetch('/ai-coach')
      .then((data) => { if (active) setCoachData(data); })
      .catch((error) => {
        if (active) setCoachData({ source: 'unavailable', summary: '', advice: [], warning: error.message });
      });
    return () => { active = false; };
  }, [activeView, user.email, dataVersion]);

  return (
    <div className="app-shell">
      <aside className="sidebar">
        <div className="brand-block">
          <div className="brand-icon">🧠</div>
          <div className="brand-name">LeetRecall AI</div>
          <div className="brand-meta">DSA REVISION SYSTEM</div>
        </div>

        <div className="user-box">
          <div className="user-tag">👤 Logged In</div>
          <div className="welcome-card">Welcome, {user.name}</div>
          <div className="email-text">{user.email}</div>
          <button className="logout-btn" onClick={onLogout}>🚪 Logout</button>
        </div>

        <div className="nav-title">NAVIGATION</div>
        <nav className="nav-list">
          {navItems.map((item) => (
            <button
              key={item}
              className={`nav-item ${activeView === item ? 'active' : ''}`}
              onClick={() => navigate(navPaths[item])}
            >
              {(() => { const Icon = navIcons[item]; return <Icon size={17} aria-hidden="true" />; })()}
              {item}
            </button>
          ))}
        </nav>
      </aside>

      <main className="content-panel">
        {loading && <div className="loading-banner">Syncing with backend…</div>}
        {loadError && <div className="api-error" role="alert">Backend connection failed: {loadError}</div>}
        <Suspense fallback={<div className="loading-banner">Loading analytics visualization…</div>}>
        <Routes>
          <Route path="/" element={<DashboardView dashboard={dashboard} recommendations={recommendations} />} />
          <Route path="/questions" element={<QuestionsPage dataVersion={dataVersion} />} />
          <Route path="/revisions" element={<RevisionQueueView recommendations={recommendations} />} />
          <Route path="/decay" element={<DecayAnalysisView recommendations={recommendations} />} />
          <Route path="/topics" element={<TopicAndPatternView type="Topic Mastery" topicMastery={topicMastery} patternCoverage={patternCoverage} />} />
          <Route path="/patterns" element={<TopicAndPatternView type="Pattern Coverage" topicMastery={topicMastery} patternCoverage={patternCoverage} />} />
          <Route path="/weak-areas" element={<WeakAreasView weakTopics={weakTopics} weakPatterns={weakPatterns} />} />
          <Route path="/contests" element={<ContestAnalyzerView contestAnalysis={contestAnalysis} />} />
          <Route path="/coach" element={<AICoachView coachData={coachData} />} />
          <Route path="/interview" element={<InterviewPlannerView />} />
          <Route path="*" element={<Navigate to="/" replace />} />
        </Routes>
        </Suspense>
      </main>
    </div>
  );
}

function Application() {
  const navigate = useNavigate();
  const location = useLocation();
  const [user, setUser] = useState(null);
  const [authLoading, setAuthLoading] = useState(Boolean(localStorage.getItem(tokenKey)));

  useEffect(() => {
    if (!localStorage.getItem(tokenKey)) return undefined;
    let active = true;
    apiFetch('/auth/me')
      .then((payload) => { if (active) setUser(payload.user); })
      .catch(() => { if (active) localStorage.removeItem(tokenKey); })
      .finally(() => { if (active) setAuthLoading(false); });
    return () => { active = false; };
  }, []);

  useEffect(() => {
    if (user && location.pathname === '/login') navigate('/', { replace: true });
  }, [user, location.pathname, navigate]);

  if (authLoading) return <div className="login-shell"><p className="loading-banner">Restoring your session…</p></div>;
  if (!user) return <LoginPage onLogin={(authenticatedUser) => { setUser(authenticatedUser); navigate('/', { replace: true }); }} />;

  return <AppShell user={user} onLogout={() => { localStorage.removeItem(tokenKey); setUser(null); navigate('/login', { replace: true }); }} />;
}

export default function App() {
  return (
    <BrowserRouter>
      <Application />
    </BrowserRouter>
  );
}
