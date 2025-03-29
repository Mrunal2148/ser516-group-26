import React, { useState, useEffect } from "react";
import { Card, CardContent, CardHeader, TextField, Typography } from "@mui/material";
import Button from "@mui/material/Button";
import List from "@mui/material/List";
import ListItem from "@mui/material/ListItem";
import ListItemText from "@mui/material/ListItemText";
import Alert from "@mui/material/Alert";

export default function AddProject() {
  const [links, setLinks] = useState([]);
  const [newLink, setNewLink] = useState("");
  const [error, setError] = useState("");

  useEffect(() => {
    fetch("http://127.0.0.1:5005/links.json")
      .then((response) => response.json())
      .then((data) => setLinks(data))
      .catch((error) => console.error("Error fetching links:", error));
  }, []);

  const addLink = () => {
    const githubRepoRegex = /^https:\/\/github\.com\/[^\/]+\/[^\/]+$/;
    const formattedLink = `https://github.com/${newLink}`;
    
    if (!newLink) {
      setError("Please enter a GitHub repository name.");
      return;
    }
    
    if (!githubRepoRegex.test(formattedLink)) {
      setError("Invalid GitHub repository URL format. Use 'user/repo'.");
      return;
    }

    setError("");
    const updatedLinks = [...links, formattedLink];
    setLinks(updatedLinks);
    setNewLink("");

    fetch("http://127.0.0.1:5005/save-links", {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify(updatedLinks),
    })
      .then((response) => response.json())
      .then(() => {
        fetch("http://127.0.0.1:5005/links.json")
          .then((response) => response.json())
          .then((data) => setLinks(data))
          .catch((error) => console.error("Error fetching links:", error));
      })
      .catch((error) => console.error("There was a problem with the fetch operation:", error));
  };

  return (
    <div className="p-6 flex justify-center items-center min-h-screen">
      <Card sx={{ maxWidth: 500, width: "100%", p: 2, boxShadow: 3 }}>
        <CardHeader title="Add GitHub Project" sx={{ textAlign: "center" }} />
        <CardContent>
          <Typography variant="body1" gutterBottom>
            Add your GitHub repositories to track them easily.
          </Typography>
          {error && <Alert severity="error" sx={{ mb: 2 }}>{error}</Alert>}
          <TextField
            fullWidth
            label="GitHub Repository"
            placeholder="user/repo"
            variant="outlined"
            value={newLink}
            onChange={(e) => setNewLink(e.target.value)}
            error={Boolean(error)}
            helperText={error}
            sx={{ mb: 2 }}
          />
          <Button variant="contained" color="secondary" fullWidth onClick={addLink}>
            Add Link
          </Button>
          <List sx={{ mt: 2 }}>
            {links.slice(1).map((link, index) => (
              <ListItem key={index} divider>
                <ListItemText primary={link} />
              </ListItem>
            ))}
          </List>
        </CardContent>
      </Card>
    </div>
  );
}
