import React, { useState } from 'react';
import UploadImage from './components/UploadImage';
import DiseaseList from './components/DiseaseList';
import { predictDisease } from './api';
import './styles.css';

function App() {
  const [selectedImage, setSelectedImage] = useState(null);
  const [prediction, setPrediction] = useState(null);
  const [loading, setLoading] = useState(false);

  const handleImageUpload = async (imageFile) => {
    setSelectedImage(URL.createObjectURL(imageFile));
    setPrediction(null);
    setLoading(true);

    try {
      const result = await predictDisease(imageFile);

      // ⏳ Force loader visibility (UX)
      setTimeout(() => {
        if (result.status === 'rejected') {
          setPrediction({
            disease: 'Unknown',
            confidence: 0,
            advice: result.message,
            reasoning: 'The model could not confidently identify the disease.',
          });
        } else {
          setPrediction({
            disease: result.disease,
            confidence: result.confidence,
            advice: result.recommended_action,
            reasoning: result.explanation,
          });
        }
        setLoading(false);
      }, 1500); // 👈 loader visible for 1.5s

    } catch (error) {
      console.error(error);
      alert('Server error. Please try again.');
      setLoading(false);
    }
  };

  return (
    <div className="app-container">
      <header>
        <h1>🍅 Tomato Disease Detector</h1>
        <p>Upload a leaf image and get disease prediction with advice</p>
      </header>

      <UploadImage onUpload={handleImageUpload} />

      {(selectedImage || loading || prediction) && (
        <div className="result-section">
          {selectedImage && (
            <div className={`image-preview ${loading ? 'image-preview-blur' : ''}`}>
              <img src={selectedImage} alt="Uploaded leaf" />
            </div>

          )}

          {loading && (
            <div className="loader-overlay">
              <div className="loader-box">
                <div className="loader"></div>
                <p>🕵️‍♂️🍅 Case under investigation…</p>
              </div>
            </div>
          )}

          {!loading && prediction && (
            <div className="prediction-panel">
              <DiseaseList prediction={prediction} />
            </div>
          )}
        </div>
      )}


      <footer className="footer">
        <div className="footer-bg">
          <div className="footer-content">
            <p>
              ⚠️ <strong>Disclaimer:</strong> This tomato disease detection tool
              is a research prototype developed for academic purposes.
              Predictions are for demonstration and conference presentation
              only. Consult agricultural experts for real-world decisions.
            </p>
          </div>
        </div>
      </footer>
    </div>
  );
}

export default App;
