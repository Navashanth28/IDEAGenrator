import { useState } from "react";
import { useNavigate } from "react-router-dom";
import axios from "axios";
import "./SurveyForm.css";

const SurveyForm = () => {
  const [formData, setFormData] = useState({
    industry: "",
    industryOther: "",
    targetAudience: "",
    technology: [],
    subTechnology: "",
    platform: "",
    webFrontend: [],
    webBackend: [],
    webHosting: [],
    webDatabase: [],
    securityFeatures: []
  });

  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  const navigate = useNavigate();

  const handleChange = (e) => {
    const { name, value, type, checked } = e.target;
    setFormData((prev) => {
      if (type === "checkbox") {
        return {
          ...prev,
          [name]: checked ? [...prev[name], value] : prev[name].filter((item) => item !== value),
        };
      }
      return { ...prev, [name]: value };
    });
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);
    setError(null);

    // Enhanced validation
    const requiredFields = {
      industry: "Industry",
      targetAudience: "Target Audience",
      technology: "Technology"
    };

    const missingFields = Object.entries(requiredFields)
      .filter(([key, label]) => {
        if (Array.isArray(formData[key])) {
          return formData[key].length === 0;
        }
        return !formData[key];
      })
      .map(([_, label]) => label);

    if (missingFields.length > 0) {
      setError(`Please fill in the following required fields: ${missingFields.join(", ")}`);
      setLoading(false);
      return;
    }

    try {
      console.log("Submitting form data:", formData);
      const response = await axios.post("http://127.0.0.1:8000/api/survey/", formData, {
        headers: {
          'Content-Type': 'application/json'
        }
      });
      
      if (response.data && response.data.response) {
        console.log("Server response:", response.data);
        navigate("/output", { state: { response: response.data.response } });
      } else {
        throw new Error("Invalid response format from server");
      }
    } catch (error) {
      console.error("Detailed error:", error);
      const errorMessage = error.response?.data?.error || 
                          error.message || 
                          "An unexpected error occurred";
      setError(`Error: ${errorMessage}`);
      
      if (error.response) {
        console.error("Response data:", error.response.data);
        console.error("Response status:", error.response.status);
      }
    } finally {
      setLoading(false);
    }
  };

  const handleGetActivity = async () => {
    try {
      const response = await axios.get("http://127.0.0.1:8000/api/activity/");
      console.log(response.data);
      alert(`Last activity: ${response.data.response}`);
    } catch (error) {
      console.error("Error fetching activity:", error);
      alert("Error fetching activity");
    }
  };

  return (
    <div className="survey-container">
      {error && (
        <div className="error-message" style={{
          padding: '10px',
          margin: '10px 0',
          backgroundColor: '#ffebee',
          color: '#c62828',
          borderRadius: '4px',
          border: '1px solid #ef9a9a'
        }}>
          {error}
        </div>
      )}
      {loading && (
        <div className="loading" style={{
          padding: '10px',
          margin: '10px 0',
          backgroundColor: '#e3f2fd',
          color: '#1976d2',
          borderRadius: '4px'
        }}>
          Processing your survey...
        </div>
      )}
      <div className="nav-buttons">
        <button onClick={() => navigate('/history')} className="survey-button">View History</button>
      </div>
      <h1 className="survey-title">Project & Technology Survey</h1>
      <form onSubmit={handleSubmit}>
        <fieldset className="survey-fieldset">
          <legend>Which industry does your project belong to?</legend>
          {["Healthcare", "Technology", "Finance", "Education", "Entertainment", "Retail/E-commerce", "Environment/Sustainability", "Other"].map((option) => (
            <div key={option}>
              <input type="radio" id={option} name="industry" value={option} onChange={handleChange} />
              <label htmlFor={option}>{option}</label>
            </div>
          ))}
          {formData.industry === "Other" && <input type="text" name="industryOther" placeholder="Please specify" className="survey-input" onChange={handleChange} />}
        </fieldset>

        <fieldset className="survey-fieldset">
          <legend>Who is your target audience?</legend>
          {["Consumers (B2C)", "Small businesses", "Enterprises", "Governments", "Specific groups"].map((option) => (
            <div key={option}>
              <input type="radio" id={option} name="targetAudience" value={option} onChange={handleChange} />
              <label htmlFor={option}>{option}</label>
            </div>
          ))}
        </fieldset>

        {[{
          legend: "What authentication and security features do you need?",
          name: "securityFeatures",
          options: ["OAuth", "JWT", "MFA", "SSL"]
        },
        {
          legend: "What technology do you plan to implement?",
          name: "technology",
          options: ["AI", "Blockchain", "SaaS", "E-commerce", "IoT", "Mobile App Development"]
        },
        {
          legend: "Web Platform: What front-end technologies will you use?",
          name: "webFrontend",
          options: ["React", "Vue.js", "Angular", "Svelte"]
        },
        {
          legend: "Web Platform: What backend framework do you prefer?",
          name: "webBackend",
          options: ["Node.js", "Django", "Flask", "Ruby on Rails", "Laravel", "Spring Boot", "ASP.NET"]
        },
        {
          legend: "Choose your preferred hosting platform?",
          name: "webHosting",
          options: ["AWS", "Google Cloud", "Azure", "DigitalOcean", "Heroku"]
        },
        {
          legend: "Choose your preferred database?",
          name: "webDatabase",
          options: ["SQL", "NoSQL", "Firebase"]
        }].map((section) => (
          <fieldset className="survey-fieldset" key={section.name}>
            <legend>{section.legend}</legend>
            {section.options.map((option) => (
              <div key={option}>
                <input type="checkbox" id={option} name={section.name} value={option} onChange={handleChange} />
                <label htmlFor={option}>{option}</label>
              </div>
            ))}
          </fieldset>
        ))}

        <button  type="submit" className="survey-button">Submit Survey</button>
      </form>
      <button onClick={handleGetActivity} className="survey-button">Get Last Activity</button>
    </div>
  );
};

export default SurveyForm;
