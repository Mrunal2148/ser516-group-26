import React, { useState } from 'react';

const GitHubUrlInput = ({ onFilesFetched }) => {
  const [url, setUrl] = useState('');
  const [loading, setLoading] = useState(false);
  const [err, setErr] = useState('');

  const fetchGitHubCode = async () => {
    setLoading(true);
    setErr('');
    const formData = new FormData();
    formData.append('github_url', url);

    try {
      //const response = await fetch('http://localhost:8001/fetch-github-folder', {
      const response = await fetch('http://localhost:8000/fetch-github-folder', {
        method: 'POST',
        body: formData
      });
      const data = await response.json();
      if (data.files && data.zip_file_name) {
        const fakeZipFile = new File([''], data.zip_file_name);
        onFilesFetched(data.files, fakeZipFile);
      } else {
        setErr('Failed to fetch files');
      }
    } catch {
      setErr('Something went wrong');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div style={{ marginBottom: '20px' }}>
      <input
        type="text"
        value={url}
        onChange={(e) => setUrl(e.target.value)}
        placeholder="GitHub repo ZIP URL"
        style={{ width: '70%', marginRight: '10px' }}
      />
      <button onClick={fetchGitHubCode} disabled={loading}>
        {loading ? 'Fetching...' : 'Fetch from GitHub'}
      </button>
      {err && <p style={{ color: 'red' }}>{err}</p>}
    </div>
  );
};

export default GitHubUrlInput;
