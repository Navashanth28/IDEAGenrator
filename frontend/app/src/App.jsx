import { Routes, Route } from "react-router-dom";
import SurveyForm from "./component/surveyform";
import OutputPage from "./component/OutputPage";

function App() {
  return (
    <Routes>
      <Route path="/" element={<SurveyForm />} />
      <Route path="/output" element={<OutputPage />} />
    </Routes>
  );
}

export default App;
