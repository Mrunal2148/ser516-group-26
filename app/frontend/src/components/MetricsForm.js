import React, { useState, useEffect } from 'react';
import GitHubUrlInput from './GitHubUrlInput';
import DirectoryTree from './DirectoryTree';

const MetricsForm = ({ embedded = false }) => {
  const [file, setFile] = useState(null);
  const [functionNames, setFunctionNames] = useState(['']);
  const [availableFiles, setAvailableFiles] = useState([]);
  const [selectedFiles, setSelectedFiles] = useState([]);
  const [results, setResults] = useState(null);
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(false);
  const [isZipFile, setIsZipFile] = useState(false);
  const [isGitHubFetch, setIsGitHubFetch] = useState(false);

  // 📥 Handle GitHub ZIP Upload
  const handleGitHubFilesFetched = (files, zipFile) => {
    setAvailableFiles(files);
    setFile(zipFile);
    setIsZipFile(true);
    setIsGitHubFetch(true);
    setError('');
  };

  const handleGitHubError = (message) => {
    setError(message);
  };

  // 📤 Form submission
  const handleSubmit = async (e) => {
    e.preventDefault();

    if (!file || functionNames.filter(f => f.trim()).length === 0) {
      setError('Please select a file and provide at least one method name');
      return;
    }

    if (isZipFile && selectedFiles.length === 0) {
      setError('Please select files from the ZIP');
      return;
    }

    setLoading(true);
    setError('');
    setResults(null);

    try {
      const formData = new FormData();
      const endpoint = isZipFile
        ? 'http://localhost:8000/metrics/combined-scoped-multi'
        : 'http://localhost:8000/metrics/combined-multi';

      if (isZipFile) {
        formData.append('folder', file);
        formData.append('scope', JSON.stringify({
          selected_files: selectedFiles,
          function_names: functionNames,
        }));
      } else {
        formData.append('file', file);
        formData.append('function_names', JSON.stringify(functionNames));
      }

      const res = await fetch(endpoint, { method: 'POST', body: formData });
      const json = await res.json();

      if (!res.ok) {
        throw new Error(json.detail || 'Error calculating metrics');
      }

      setResults(json.results);
    } catch (err) {
      setError(err.message || 'Unexpected error');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="metric-form-container">
      {!embedded && <h2 className="text-xl font-bold mb-4">Fan-In / Fan-Out Metrics</h2>}

      <form onSubmit={handleSubmit} className="space-y-4">
        <GitHubUrlInput onFilesFetched={handleGitHubFilesFetched} onError={handleGitHubError} />

        {!isGitHubFetch && (
          <div>
            <label>Upload Java File or ZIP</label>
            <input
              type="file"
              accept=".java,.zip"
              onChange={(e) => {
                const f = e.target.files[0];
                if (!f.name.endsWith('.java') && !f.name.endsWith('.zip')) {
                  setError('Only .java or .zip files allowed');
                  return;
                }

                setFile(f);
                setIsZipFile(f.name.endsWith('.zip'));
                setIsGitHubFetch(false);
                setError('');
              }}
            />
          </div>
        )}

        {isZipFile && availableFiles.length > 0 && (
          <DirectoryTree
            files={availableFiles}
            selectedFiles={selectedFiles}
            onFileSelectionChange={setSelectedFiles}
          />
        )}

        <div>
          <label>Method Name(s)</label>
          {functionNames.map((name, idx) => (
            <input
              key={idx}
              className="block w-full border p-1 mb-1"
              type="text"
              value={name}
              onChange={(e) => {
                const copy = [...functionNames];
                copy[idx] = e.target.value;
                setFunctionNames(copy);
              }}
            />
          ))}
          <button type="button" onClick={() => setFunctionNames([...functionNames, ''])}>
            ➕ Add Method
          </button>
        </div>

        <button type="submit" disabled={loading}>
          {loading ? 'Calculating...' : 'Calculate Metrics'}
        </button>
      </form>

      {error && <p className="text-red-600 mt-4">{error}</p>}

      {results && (
        <div className="results mt-4">
          {Object.entries(results).map(([method, data]) => (
            <div key={method} className="border p-2 my-2 bg-gray-50">
              <strong>{method}</strong>
              <p>Fan-in: {data.total_fan_in ?? data.fan_in}</p>
              <p>Fan-out: {data.total_fan_out ?? data.fan_out}</p>

              {data.per_file_results && (
                <details className="mt-2">
                  <summary className="cursor-pointer text-sm text-blue-600">Per File Details</summary>
                  {Object.entries(data.per_file_results).map(([file, val]) => (
                    <div key={file} className="pl-4 text-sm">
                      📄 <b>{file}</b> → Fan-in: {val.fan_in}, Fan-out: {val.fan_out}
                    </div>
                  ))}
                </details>
              )}
            </div>
          ))}
        </div>
      )}
    </div>
  );
};

export default MetricsForm;
