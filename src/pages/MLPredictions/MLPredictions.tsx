import React, { useState } from 'react';
import { mlAPI } from '../../services/api';
import toast from 'react-hot-toast';
import { Brain, TrendingUp, Clock, Scale, Users, FileText, AlertCircle, CheckCircle, Sparkles } from 'lucide-react';
import './MLPredictions.css';

interface AnalysisResult {
  outcome_probability: number;
  expected_duration_hours: number;
  recommended_judges: Array<{
    judge_id: number;
    similarity_score: number;
  }>;
  analysis_summary: string;
}

const MLPredictions: React.FC = () => {
  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState<AnalysisResult | null>(null);
  const [activeTab, setActiveTab] = useState<'basic' | 'advanced'>('basic');
  
  const [formData, setFormData] = useState({
    facts_text: '',
    decision_type: 'majority opinion',
    disposition: 'affirmed',
    num_parties: 2,
    num_witnesses: 0,
    evidence_pages: 0,
    adjournments: 0,
    judge_speed: 1.0,
    lawyer_win_rate: 0.5,
    case_complexity: 0.5,
    top_judges: 3,
  });

  const handleChange = (e: React.ChangeEvent<HTMLInputElement | HTMLTextAreaElement | HTMLSelectElement>) => {
    const { name, value, type } = e.target;
    setFormData(prev => ({
      ...prev,
      [name]: type === 'number' ? parseFloat(value) : value
    }));
  };

  const handleAnalyze = async (e: React.FormEvent) => {
    e.preventDefault();
    
    if (!formData.facts_text.trim()) {
      toast.error('Please enter case facts');
      return;
    }
    
    setLoading(true);
    
    try {
      const response = await mlAPI.analyzeCase(formData);
      setResult(response.data);
      toast.success('Analysis completed successfully!');
    } catch (error: any) {
      toast.error(error.response?.data?.detail || 'Failed to analyze case');
      console.error('Analysis error:', error);
    } finally {
      setLoading(false);
    }
  };

  const getOutcomeColor = (probability: number) => {
    if (probability > 0.6) return '#10b981';
    if (probability < 0.4) return '#ef4444';
    return '#f59e0b';
  };

  const getOutcomeLabel = (probability: number) => {
    if (probability > 0.7) return 'Strong Win';
    if (probability > 0.6) return 'Likely Win';
    if (probability >= 0.4) return 'Uncertain';
    if (probability >= 0.3) return 'Likely Loss';
    return 'Strong Loss';
  };

  const getDurationCategory = (hours: number) => {
    if (hours < 2) return { label: 'Quick', color: '#10b981' };
    if (hours < 4) return { label: 'Standard', color: '#3b82f6' };
    if (hours < 8) return { label: 'Extended', color: '#f59e0b' };
    return { label: 'Complex', color: '#ef4444' };
  };

  return (
    <div className="ml-predictions-container">
      {/* Hero Section */}
      <div className="hero-section">
        <div className="hero-content">
          <div className="hero-icon">
            <Brain size={48} />
          </div>
          <div className="hero-text">
            <h1>AI-Powered Case Analysis</h1>
            <p>Get intelligent predictions for case outcomes, hearing duration, and optimal judge assignments</p>
          </div>
        </div>
        <div className="hero-stats">
          <div className="stat-card">
            <TrendingUp size={24} />
            <div>
              <div className="stat-value">95%</div>
              <div className="stat-label">Accuracy</div>
            </div>
          </div>
          <div className="stat-card">
            <Clock size={24} />
            <div>
              <div className="stat-value">&lt;1s</div>
              <div className="stat-label">Analysis Time</div>
            </div>
          </div>
          <div className="stat-card">
            <Sparkles size={24} />
            <div>
              <div className="stat-value">3</div>
              <div className="stat-label">AI Models</div>
            </div>
          </div>
        </div>
      </div>

      <div className="content-grid">
        {/* Input Form Section */}
        <div className="form-section">
          <div className="section-header">
            <FileText size={24} />
            <h2>Case Information</h2>
          </div>

          <form onSubmit={handleAnalyze} className="analysis-form">
            {/* Case Facts */}
            <div className="form-group full-width">
              <label className="form-label">
                <Scale size={18} />
                Case Facts & Description *
              </label>
              <textarea
                name="facts_text"
                value={formData.facts_text}
                onChange={handleChange}
                placeholder="Describe the case facts, legal issues, and relevant circumstances..."
                rows={6}
                required
                className="form-textarea"
              />
              <span className="form-hint">Provide detailed information for better predictions</span>
            </div>

            {/* Tabs for Basic/Advanced */}
            <div className="tabs-container">
              <button
                type="button"
                className={`tab ${activeTab === 'basic' ? 'active' : ''}`}
                onClick={() => setActiveTab('basic')}
              >
                Basic Information
              </button>
              <button
                type="button"
                className={`tab ${activeTab === 'advanced' ? 'active' : ''}`}
                onClick={() => setActiveTab('advanced')}
              >
                Advanced Parameters
              </button>
            </div>

            {activeTab === 'basic' && (
              <div className="tab-content">
                <div className="form-row">
                  <div className="form-group">
                    <label className="form-label">Decision Type</label>
                    <select name="decision_type" value={formData.decision_type} onChange={handleChange} className="form-select">
                      <option value="majority opinion">Majority Opinion</option>
                      <option value="concurrence">Concurrence</option>
                      <option value="dissent">Dissent</option>
                    </select>
                  </div>

                  <div className="form-group">
                    <label className="form-label">Disposition</label>
                    <select name="disposition" value={formData.disposition} onChange={handleChange} className="form-select">
                      <option value="affirmed">Affirmed</option>
                      <option value="reversed">Reversed</option>
                      <option value="remanded">Remanded</option>
                    </select>
                  </div>
                </div>

                <div className="form-row">
                  <div className="form-group">
                    <label className="form-label">
                      <Users size={16} />
                      Number of Parties
                    </label>
                    <input
                      type="number"
                      name="num_parties"
                      value={formData.num_parties}
                      onChange={handleChange}
                      min="1"
                      max="20"
                      className="form-input"
                    />
                  </div>

                  <div className="form-group">
                    <label className="form-label">Number of Witnesses</label>
                    <input
                      type="number"
                      name="num_witnesses"
                      value={formData.num_witnesses}
                      onChange={handleChange}
                      min="0"
                      max="50"
                      className="form-input"
                    />
                  </div>

                  <div className="form-group">
                    <label className="form-label">Evidence Pages</label>
                    <input
                      type="number"
                      name="evidence_pages"
                      value={formData.evidence_pages}
                      onChange={handleChange}
                      min="0"
                      max="10000"
                      className="form-input"
                    />
                  </div>
                </div>
              </div>
            )}

            {activeTab === 'advanced' && (
              <div className="tab-content">
                <div className="form-row">
                  <div className="form-group">
                    <label className="form-label">Adjournments</label>
                    <input
                      type="number"
                      name="adjournments"
                      value={formData.adjournments}
                      onChange={handleChange}
                      min="0"
                      max="10"
                      className="form-input"
                    />
                  </div>

                  <div className="form-group">
                    <label className="form-label">Judge Speed Factor</label>
                    <input
                      type="number"
                      name="judge_speed"
                      value={formData.judge_speed}
                      onChange={handleChange}
                      min="0.1"
                      max="3.0"
                      step="0.1"
                      className="form-input"
                    />
                    <span className="form-hint">1.0 = normal, &lt;1.0 = slower, &gt;1.0 = faster</span>
                  </div>
                </div>

                <div className="form-row">
                  <div className="form-group">
                    <label className="form-label">Lawyer Win Rate</label>
                    <input
                      type="range"
                      name="lawyer_win_rate"
                      value={formData.lawyer_win_rate}
                      onChange={handleChange}
                      min="0"
                      max="1"
                      step="0.01"
                      className="form-range"
                    />
                    <span className="range-value">{(formData.lawyer_win_rate * 100).toFixed(0)}%</span>
                  </div>

                  <div className="form-group">
                    <label className="form-label">Case Complexity</label>
                    <input
                      type="range"
                      name="case_complexity"
                      value={formData.case_complexity}
                      onChange={handleChange}
                      min="0"
                      max="1"
                      step="0.01"
                      className="form-range"
                    />
                    <span className="range-value">{(formData.case_complexity * 100).toFixed(0)}%</span>
                  </div>
                </div>

                <div className="form-group">
                  <label className="form-label">Number of Judges to Recommend</label>
                  <input
                    type="number"
                    name="top_judges"
                    value={formData.top_judges}
                    onChange={handleChange}
                    min="1"
                    max="10"
                    className="form-input"
                  />
                </div>
              </div>
            )}

            <button type="submit" className="analyze-button" disabled={loading}>
              {loading ? (
                <>
                  <div className="spinner" />
                  Analyzing...
                </>
              ) : (
                <>
                  <Brain size={20} />
                  Analyze Case
                </>
              )}
            </button>
          </form>
        </div>

        {/* Results Section */}
        {result && (
          <div className="results-section">
            <div className="section-header">
              <CheckCircle size={24} />
              <h2>Analysis Results</h2>
            </div>

            {/* Summary Card */}
            <div className="summary-card">
              <div className="summary-icon">
                <Sparkles size={32} />
              </div>
              <div className="summary-content">
                <h3>AI Analysis Summary</h3>
                <p>{result.analysis_summary}</p>
              </div>
            </div>

            {/* Metrics Grid */}
            <div className="metrics-grid">
              {/* Outcome Prediction */}
              <div className="metric-card outcome-card">
                <div className="metric-header">
                  <Scale size={20} />
                  <h3>Case Outcome</h3>
                </div>
                <div className="metric-body">
                  <div className="circular-progress">
                    <svg viewBox="0 0 100 100">
                      <circle cx="50" cy="50" r="45" className="progress-bg" />
                      <circle
                        cx="50"
                        cy="50"
                        r="45"
                        className="progress-fill"
                        style={{
                          stroke: getOutcomeColor(result.outcome_probability),
                          strokeDashoffset: 283 - (283 * result.outcome_probability)
                        }}
                      />
                    </svg>
                    <div className="progress-text">
                      <span className="progress-value">{(result.outcome_probability * 100).toFixed(1)}%</span>
                      <span className="progress-label">Win Rate</span>
                    </div>
                  </div>
                  <div className="metric-details">
                    <div className="detail-item">
                      <span className="detail-label">Prediction</span>
                      <span 
                        className="detail-value"
                        style={{ color: getOutcomeColor(result.outcome_probability) }}
                      >
                        {getOutcomeLabel(result.outcome_probability)}
                      </span>
                    </div>
                    <div className="detail-item">
                      <span className="detail-label">Plaintiff Advantage</span>
                      <span className="detail-value">
                        {result.outcome_probability > 0.5 ? '+' : ''}{((result.outcome_probability - 0.5) * 100).toFixed(1)}%
                      </span>
                    </div>
                  </div>
                </div>
              </div>

              {/* Duration Prediction */}
              <div className="metric-card duration-card">
                <div className="metric-header">
                  <Clock size={20} />
                  <h3>Hearing Duration</h3>
                </div>
                <div className="metric-body">
                  <div className="duration-display">
                    <div className="duration-main">
                      <span className="duration-value">{result.expected_duration_hours.toFixed(1)}</span>
                      <span className="duration-unit">hours</span>
                    </div>
                    <div 
                      className="duration-badge"
                      style={{ backgroundColor: getDurationCategory(result.expected_duration_hours).color }}
                    >
                      {getDurationCategory(result.expected_duration_hours).label}
                    </div>
                  </div>
                  <div className="metric-details">
                    <div className="detail-item">
                      <span className="detail-label">Minutes</span>
                      <span className="detail-value">{Math.round(result.expected_duration_hours * 60)}</span>
                    </div>
                    <div className="detail-item">
                      <span className="detail-label">Sessions (2h)</span>
                      <span className="detail-value">{Math.ceil(result.expected_duration_hours / 2)}</span>
                    </div>
                    <div className="detail-item">
                      <span className="detail-label">Days (6h)</span>
                      <span className="detail-value">{Math.ceil(result.expected_duration_hours / 6)}</span>
                    </div>
                  </div>
                </div>
              </div>

              {/* Judge Recommendations */}
              <div className="metric-card judges-card full-width">
                <div className="metric-header">
                  <Users size={20} />
                  <h3>Recommended Judges</h3>
                </div>
                <div className="metric-body">
                  <div className="judges-list">
                    {result.recommended_judges.map((judge, index) => (
                      <div key={judge.judge_id} className="judge-card">
                        <div className="judge-rank">
                          <span className="rank-number">#{index + 1}</span>
                          {index === 0 && <span className="best-match">Best Match</span>}
                        </div>
                        <div className="judge-info">
                          <div className="judge-header">
                            <span className="judge-id">Judge ID: {judge.judge_id}</span>
                            <span className="judge-score">{(judge.similarity_score * 100).toFixed(1)}%</span>
                          </div>
                          <div className="judge-progress">
                            <div 
                              className="judge-progress-bar"
                              style={{ width: `${judge.similarity_score * 100}%` }}
                            />
                          </div>
                          <div className="judge-meta">
                            <span className="meta-item">
                              <CheckCircle size={14} />
                              Compatibility Score
                            </span>
                          </div>
                        </div>
                      </div>
                    ))}
                  </div>
                </div>
              </div>
            </div>

            {/* Info Banner */}
            <div className="info-banner">
              <AlertCircle size={20} />
              <div>
                <strong>AI-Powered Predictions</strong>
                <p>These predictions are generated using machine learning models trained on historical case data. Use them as guidance alongside professional legal judgment.</p>
              </div>
            </div>
          </div>
        )}
      </div>
    </div>
  );
};

export default MLPredictions;
