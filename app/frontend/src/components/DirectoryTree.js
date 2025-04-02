import React from 'react';

const DirectoryTree = ({ files, selectedFiles, onFileSelectionChange }) => {
  const toggleFile = (filePath) => {
    const updated = selectedFiles.includes(filePath)
      ? selectedFiles.filter(f => f !== filePath)
      : [...selectedFiles, filePath];
    onFileSelectionChange(updated);
  };

  return (
    <div style={{ border: '1px solid #ddd', padding: '10px', marginTop: '20px' }}>
      <h4>Select Files</h4>
      {files.map(file => (
        <div key={file.path}>
          <input
            type="checkbox"
            checked={selectedFiles.includes(file.path)}
            onChange={() => toggleFile(file.path)}
          />
          {file.path}
        </div>
      ))}
    </div>
  );
};

export default DirectoryTree;
