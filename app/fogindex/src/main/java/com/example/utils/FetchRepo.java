package com.example.utils;

import org.eclipse.jgit.api.Git;
import org.eclipse.jgit.lib.Repository;
import org.eclipse.jgit.revwalk.RevCommit;

import java.io.File;
import java.net.URI;
import java.net.URISyntaxException;
import java.util.regex.Pattern;

public class FetchRepo {

    private static final String SHARED_BASE_DIR = "/shared/repos";

    public static Object fetchRepo(String repoUrl) throws Exception {
        if (repoUrl == null || repoUrl.isEmpty()) {
            throw new IllegalArgumentException("No repository URL provided. Please enter a valid GitHub repository URL.");
        }

        URI parsed;
        try {
            parsed = new URI(repoUrl);
        } catch (URISyntaxException e) {
            throw new IllegalArgumentException("Invalid URL format.", e);
        }

        if (!"github.com".equalsIgnoreCase(parsed.getHost()) || parsed.getPath().split("/").length < 3) {
            throw new IllegalArgumentException("Invalid GitHub repository URL. Ensure it follows the format 'https://github.com/owner/repo'.");
        }

        String repoPath = parsed.getPath().replaceFirst("^/", "");
        if (repoPath.endsWith(".git")) {
            repoPath = repoPath.substring(0, repoPath.length() - 4);
        }

        if (!Pattern.matches("^[a-zA-Z0-9_.-]+/[a-zA-Z0-9_.-]+$", repoPath)) {
            throw new IllegalArgumentException("Malformed repository URL. Ensure the URL points to a valid GitHub repository.");
        }

        String[] parts = repoPath.split("/");
        String owner = parts[0];
        String repo = parts[1];
        File repoDir = new File(SHARED_BASE_DIR, owner + File.separator + repo);

        if (!repoDir.exists()) {
            return new Error("Clone the repo first.");
        }

        try (Git git = Git.open(repoDir)) {
            Repository repository = git.getRepository();
            RevCommit headCommit = git.log().setMaxCount(1).call().iterator().next();
            return new Object[]{headCommit.getName(), repoDir.getAbsolutePath()};
        } catch (Exception e) {
            return new Error("Error accessing repository: " + e.getMessage());
        }
    }
}
