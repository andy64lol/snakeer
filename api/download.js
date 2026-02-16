/**
 * Vercel Serverless Function: Download Package from GitHub Registry
 * 
 * This function retrieves package information and download URLs
 * from the snakeer_packages_lib repository using GitHub REST API.
 * 
 * Environment variables needed:
 * - GITHUB_TOKEN: GitHub personal access token (optional, for private repos)
 */

export default async function handler(req, res) {
  // Enable CORS
  res.setHeader('Access-Control-Allow-Origin', '*');
  res.setHeader('Access-Control-Allow-Methods', 'GET, POST, OPTIONS');
  res.setHeader('Access-Control-Allow-Headers', 'Content-Type');

  // Handle preflight
  if (req.method === 'OPTIONS') {
    res.status(200).end();
    return;
  }

  try {
    // Get parameters from query or body
    let packageName, version;
    
    if (req.method === 'GET') {
      packageName = req.query.package;
      version = req.query.version;
    } else if (req.method === 'POST') {
      packageName = req.body.packageName;
      version = req.body.version;
    }

    // Validate
    if (!packageName) {
      return res.status(400).json({ error: 'Missing required field: packageName' });
    }

    // GitHub configuration
    const GITHUB_TOKEN = process.env.GITHUB_TOKEN;
    const REPO_OWNER = 'andy64lol';
    const REPO_NAME = 'snakeer_packages_lib';

    const requestHeaders = {
      'Accept': 'application/vnd.github.v3+json',
      'User-Agent': 'Snakeer-Package-Manager'
    };

    if (GITHUB_TOKEN) {
      requestHeaders['Authorization'] = `token ${GITHUB_TOKEN}`;
    }

    // If version not specified, list available versions
    if (!version) {
      const versionsUrl = `https://api.github.com/repos/${REPO_OWNER}/${REPO_NAME}/contents/packages/${packageName}`;
      
      const response = await fetch(versionsUrl, { headers: requestHeaders });
      
      if (!response.ok) {
        if (response.status === 404) {
          return res.status(404).json({ error: `Package '${packageName}' not found` });
        }
        throw new Error(`GitHub API error: ${response.statusText}`);
      }

      const data = await response.json();
      const versions = data
        .filter(item => item.type === 'dir')
        .map(item => item.name);

      return res.status(200).json({
        package: packageName,
        versions: versions,
        latest: versions[0] || null
      });
    }

    // Get specific version
    const packageUrl = `https://api.github.com/repos/${REPO_OWNER}/${REPO_NAME}/contents/packages/${packageName}/${version}`;
    
    const response = await fetch(packageUrl, { headers: requestHeaders });
    
    if (!response.ok) {
      if (response.status === 404) {
        return res.status(404).json({ 
          error: `Package '${packageName}@${version}' not found` 
        });
      }
      throw new Error(`GitHub API error: ${response.statusText}`);
    }

    const data = await response.json();
    
    // Find the archive file
    const archiveFile = data.find(item => 
      item.name.endsWith('.zip') || item.name.endsWith('.tar.gz')
    );

    if (!archiveFile) {
      return res.status(404).json({ 
        error: `No package archive found for '${packageName}@${version}'` 
      });
    }

    // Get metadata if available
    let metadata = null;
    const metadataFile = data.find(item => item.name === 'metadata.json');
    
    if (metadataFile) {
      try {
        const metaResponse = await fetch(metadataFile.download_url);
        if (metaResponse.ok) {
          metadata = await metaResponse.json();
        }
      } catch (e) {
        console.log('Metadata fetch failed:', e);
      }
    }

    return res.status(200).json({
      package: packageName,
      version: version,
      filename: archiveFile.name,
      size: archiveFile.size,
      download_url: archiveFile.download_url,
      html_url: archiveFile.html_url,
      metadata: metadata
    });

  } catch (error) {
    console.error('Download error:', error);
    return res.status(500).json({
      success: false,
      error: error.message
    });
  }
}
