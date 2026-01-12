import React from 'react';

function UploadImage({ onUpload }) {
  const handleChange = (e) => {
    const file = e.target.files[0] || null;
    onUpload(file);
    e.target.value = null;
  };

  return (
    <div className='upload-container'>
      <label htmlFor='file-upload' className='custom-file-upload'>
        📤 Upload Leaf Image
      </label>
      <input
        id='file-upload'
        type='file'
        accept='image/*'
        onChange={handleChange}
      />
    </div>
  );
}

export default UploadImage;
