import { useLocation } from "react-router-dom";
import "./OutputPage.css";

const OutputPage = () => {
  const location = useLocation();
  const { response } = location.state;

  return (
    <div className="output-container">
      <h1 className="output-title">Survey Output</h1>
      <p className="output-content">{response}</p>
    </div>
  );
};

export default OutputPage;
