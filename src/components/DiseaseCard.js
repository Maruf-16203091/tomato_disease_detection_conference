import React from 'react';

function formatDiseaseText(text) {
  if (!text) return '';

  return text
    .replace(/___/g, ' ')
    .replace(/_/g, ' ')
    .replace(/\b\w/g, c => c.toUpperCase());
}

function DiseaseCard({ data }) {
  return (
    <div className="disease-card">
      <h2>Disease: {formatDiseaseText(data.disease)}</h2>

      <p>
        <strong>Confidence:</strong> {data.confidence.toFixed(2)}%
      </p>

      <div className="advice">
        <h3>Recommended Actions:</h3>
        <p>{formatDiseaseText(data.advice)}</p>
      </div>

      <div className="reasoning">
        <h3>Reasoning:</h3>
        <p>{formatDiseaseText(data.reasoning)}</p>
      </div>
    </div>
  );
}

export default DiseaseCard;
