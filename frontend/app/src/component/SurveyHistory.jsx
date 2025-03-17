import { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import axios from 'axios';
import './SurveyHistory.css';

const SurveyHistory = () => {
  const navigate = useNavigate();
  const [surveys, setSurveys] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    const fetchSurveys = async () => {
      try {
        const response = await axios.get('http://127.0.0.1:8000/api/history/');
        setSurveys(response.data.surveys);
        setLoading(false);
      } catch (err) {
        setError('Failed to fetch survey history');
        setLoading(false);
      }
    };

    fetchSurveys();
  }, []);

  if (loading) return <div>Loading...</div>;
  if (error) return <div>{error}</div>;

  return (
    <div className="history-container">
      <button onClick={() => navigate('/')} className="survey-button">Back to Survey</button>
      <h2>Survey History</h2>
      {surveys.map((survey) => (
        <div key={survey.id} className="survey-card">
          <h3>Industry: {survey.industry}</h3>
          <p>Target Audience: {survey.target_audience}</p>
          <p>Technologies: {survey.technology.join(', ')}</p>
          <p>Created: {new Date(survey.created_at).toLocaleString()}</p>
          <details>
            <summary>More Details</summary>
            <div className="details-content">
              <p>Frontend: {(survey.web_frontend || []).join(', ') || 'None'}</p>
              <p>Backend: {(survey.web_backend || []).join(', ') || 'None'}</p>
              <p>Hosting: {(survey.web_hosting || []).join(', ') || 'None'}</p>
              <p>Database: {(survey.web_database || []).join(', ') || 'None'}</p>
              <p>Security: {(survey.security_features || []).join(', ') || 'None'}</p>
            </div>
          </details>
        </div>
      ))}
    </div>
  );
};

export default SurveyHistory;
