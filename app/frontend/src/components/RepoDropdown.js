import React from "react";

const RepoDropdown = ({ repositories, selectedRepo, setSelectedRepo }) => {
    return (
        <div>
            <label>Select Repository: </label>
            <select onChange={(e) => setSelectedRepo(e.target.value)} value={selectedRepo}>
                {repositories.map(repo => (
                    <option key={repo.repo_url} value={repo.repo_url}>
                        {repo.repo_url}
                    </option>
                ))}
            </select>
        </div>
    );
};

export default RepoDropdown;
