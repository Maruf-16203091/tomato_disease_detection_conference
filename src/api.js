export async function predictDisease(imageFile) {
  const formData = new FormData();
  formData.append('image', imageFile);

  const response = await fetch('http://localhost:8000/predict', {
    method: 'POST',
    body: formData,
  });

  if (!response.ok) {
    throw new Error('API request failed');
  }

  return response.json();
}
