import { Routes, Route } from "react-router-dom";
import SurveyForm from "./component/surveyform";
import OutputPage from "./component/OutputPage";
import SurveyHistory from "./component/SurveyHistory";  // Add import

function App() {
  return (
    <Routes>
      <Route path="/" element={<SurveyForm />} />
      <Route path="/output" element={<OutputPage />} />
      <Route path="/history" element={<SurveyHistory />} />
    </Routes>
  );
}

export default App;
