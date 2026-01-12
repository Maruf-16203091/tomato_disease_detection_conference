import React from 'react';
import DiseaseCard from './DiseaseCard';

function DiseaseList({ prediction }) {
  return (
    <div className='disease-list'>
      <DiseaseCard data={prediction} />
    </div>
  );
}

export default DiseaseList;
