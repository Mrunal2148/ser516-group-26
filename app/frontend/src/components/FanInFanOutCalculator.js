import React, { useState } from 'react';
import DirectoryTree from './DirectoryTree';
import GitHubUrlInput from './GitHubUrlInput';

const FanInFanOutCalculator = () => {
  const [selectedFile, setSelectedFile] = useState(null);
  const [selectedFiles, setSelectedFiles] = useState([]);
  const [availableFiles, setAvailableFiles] = useState([]);
  const [methodNames, setMethodNames] = useState(['']);
  const [results, setResults] = useState(null);
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(false);

  const handleGitHubFetched = (files, zipFile) => {
    setAvailableFiles(files);
    setSelectedFile(zipFile);
    setError('');
  };

  const handleFileUpload = (e) => {
    const file = e.target.files?.[0];
    if (!file || !file.name.endsWith('.zip')) {
      setError('Please upload a ZIP file');
      return;
    }
    setSelectedFile(file);
    const formData = new FormData();
    formData.append('folder', file);

    fetch('http://localhost:8001/upload-folder', {
      method: 'POST',
      body: formData
    })
      .then(res => res.json())
      .then(data => {
        setAvailableFiles(data.files || []);
        setError('');
      })
      .catch(() => setError('Failed to extract ZIP file'));
  };

  const handleAddMethod = () => setMethodNames([...methodNames, '']);
  const handleRemoveMethod = (index) =>
    setMethodNames(methodNames.filter((_, i) => i !== index));
  const handleMethodChange = (index, value) => {
    const updated = [...methodNames];
    updated[index] = value;
    setMethodNames(updated);
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    if (!selectedFile || selectedFiles.length === 0 || methodNames.every(m => !m.trim())) {
      setError('Please provide a ZIP file, at least one method name, and select files');
      return;
    }

    setLoading(true);
    setError('');
    setResults(null);

    const formData = new FormData();
    formData.append('folder', selectedFile);
    formData.append('scope', JSON.stringify({
      selected_files: selectedFiles,
      function_names: methodNames.filter(m => m.trim() !== '')
    }));

    try {
      const res = await fetch('http://localhost:8000/metrics/combined-scoped-multi', {
        method: 'POST',
        body: formData
      });
      const data = await res.json();
      setResults(data.results || {});
    } catch (err) {
      setError('Error calculating metrics');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div style={{ maxWidth: '800px', margin: 'auto', padding: '20px' }}>
      <h2>Fan-In / Fan-Out Metrics Calculator</h2>

      <GitHubUrlInput onFilesFetched={handleGitHubFetched} />

      <p>Or upload a ZIP:</p>
      <input type="file" accept=".zip" onChange={handleFileUpload} />

      {availableFiles.length > 0 && (
        <DirectoryTree
          files={availableFiles}
          selectedFiles={selectedFiles}
          onFileSelectionChange={setSelectedFiles}
        />
      )}

      <form onSubmit={handleSubmit}>
        <h4>Method Names</h4>
        {methodNames.map((m, i) => (
          <div key={i} style={{ marginBottom: '8px' }}>
            <input
              type="text"
              value={m}
              onChange={(e) => handleMethodChange(i, e.target.value)}
              placeholder="Enter method name"
              style={{ marginRight: '10px' }}
            />
            {methodNames.length > 1 && (
              <button type="button" onClick={() => handleRemoveMethod(i)}>Remove</button>
            )}
          </div>
        ))}
        <button type="button" onClick={handleAddMethod}>Add Method</button>
        <br /><br />
        <button type="submit" disabled={loading}>
          {loading ? 'Calculating...' : 'Calculate'}
        </button>
      </form>

      {error && <p style={{ color: 'red' }}>{error}</p>}

      {results && (
        <div style={{ marginTop: '20px' }}>
          <h4>Results:</h4>
          {Object.entries(results).map(([method, data]) => (
            <div key={method} style={{ padding: '10px', border: '1px solid #ccc', marginBottom: '10px' }}>
              <b>{method}</b>
              <p>Total Fan-in: {data.total_fan_in}</p>
              <p>Total Fan-out: {data.total_fan_out}</p>
              <h5>Per File:</h5>
              {Object.entries(data.per_file_results || {}).map(([file, val]) => (
                <div key={file}>
                  {file}: fan-in: {val.fan_in}, fan-out: {val.fan_out}
                </div>
              ))}
            </div>
          ))}
        </div>
      )}
    </div>
  );
};

export default FanInFanOutCalculator;
