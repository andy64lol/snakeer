/**
 * Vercel Serverless Function: Upload Package to GitHub Registry
 * 
 * This function uploads a package to the snakeer_packages_lib repository
 * using the GitHub REST API.
 * 
 * Environment variables needed:
 * - GITHUB_TOKEN: GitHub personal access token with repo access
 */

export default async function handler(req, res) {
  // Enable CORS
  res.setHeader('Access-Control-Allow-Origin', '*');
  res.setHeader('Access-Control-Allow-Methods', 'POST, OPTIONS');
  res.setHeader('Access-Control-Allow-Headers', 'Content-Type');

  // Handle preflight
  if (req.method === 'OPTIONS') {
    res.status(200).end();
    return;
  }

  // Only allow POST requests
  if (req.method !== 'POST') {
    return res.status(405).json({ error: 'Method not allowed. Use POST.' });
  }

  try {
    const { packageName, version, content, filename } = req.body;

    // Validate required fields
    if (!packageName || !version || !content) {
      return res.status(400).json({ 
        error: 'Missing required fields: packageName, version, content' 
      });
    }

    // GitHub configuration
    const GITHUB_TOKEN = process.env.GITHUB_TOKEN;
    const REPO_OWNER = 'andy64lol';
    const REPO_NAME = 'snakeer_packages_lib';
    
    if (!GITHUB_TOKEN) {
      return res.status(500).json({ error: 'GITHUB_TOKEN not configured' });
    }

    // File path in the repository
    const filePath = `packages/${packageName}/${version}/${filename || packageName + '-' + version + '.zip'}`;
    const message = `Upload ${packageName}@${version}`;

    // Check if file already exists
    const checkUrl = `https://api.github.com/repos/${REPO_OWNER}/${REPO_NAME}/contents/${filePath}`;
    
    let sha = null;
    try {
      const checkResponse = await fetch(checkUrl, {
        headers: {
          'Authorization': `token ${GITHUB_TOKEN}`,
          'Accept': 'application/vnd.github.v3+json'
        }
      });
      
      if (checkResponse.status === 200) {
        const fileData = await checkResponse.json();
        sha = fileData.sha;
      }
    } catch (e) {
      // File doesn't exist, which is fine
    }

    // Prepare the content (base64 encoded)
    const encodedContent = content;

    // Create or update file
    const apiUrl = `https://api.github.com/repos/${REPO_OWNER}/${REPO_NAME}/contents/${filePath}`;
    
    const requestBody = {
      message: message,
      content: encodedContent,
      branch: 'main'
    };

    if (sha) {
      requestBody.sha = sha;
    }

    const response = await fetch(apiUrl, {
      method: 'PUT',
      headers: {
        'Authorization': `token ${GITHUB_TOKEN}`,
        'Accept': 'application/vnd.github.v3+json',
        'Content-Type': 'application/json'
      },
      body: JSON.stringify(requestBody)
    });

    if (!response.ok) {
      const errorData = await response.json();
      throw new Error(`GitHub API error: ${errorData.message || response.statusText}`);
    }

    const data = await response.json();

    return res.status(200).json({
      success: true,
      message: `Package ${packageName}@${version} uploaded successfully`,
      url: data.content.html_url,
      download_url: data.content.download_url
    });

  } catch (error) {
    console.error('Upload error:', error);
    return res.status(500).json({
      success: false,
      error: error.message
    });
  }
}
