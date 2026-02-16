/**
 * Netlify Function: Download Package from GitHub Registry
 * 
 * This function retrieves package information and download URLs
 * from the snakeer_packages_lib repository using GitHub REST API.
 * 
 * Environment variables needed:
 * - GITHUB_TOKEN: GitHub personal access token (optional, for private repos)
 */

exports.handler = async (event, context) => {
  // Enable CORS
  const headers = {
    'Access-Control-Allow-Origin': '*',
    'Access-Control-Allow-Headers': 'Content-Type',
    'Access-Control-Allow-Methods': 'GET, POST, OPTIONS'
  };

  // Handle preflight requests
  if (event.httpMethod === 'OPTIONS') {
    return {
      statusCode: 200,
      headers,
      body: ''
    };
  }

  try {
    // Parse query parameters or body
    let packageName, version;
    
    if (event.httpMethod === 'GET') {
      const params = new URLSearchParams(event.queryStringParameters);
      packageName = params.get('package');
      version = params.get('version');
    } else if (event.httpMethod === 'POST') {
      const body = JSON.parse(event.body);
      packageName = body.packageName;
      version = body.version;
    }

    // Validate
    if (!packageName) {
      return {
        statusCode: 400,
        headers,
        body: JSON.stringify({ error: 'Missing required field: packageName' })
      };
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
          return {
            statusCode: 404,
            headers,
            body: JSON.stringify({ error: `Package '${packageName}' not found` })
          };
        }
        throw new Error(`GitHub API error: ${response.statusText}`);
      }

      const data = await response.json();
      const versions = data
        .filter(item => item.type === 'dir')
        .map(item => item.name);

      return {
        statusCode: 200,
        headers,
        body: JSON.stringify({
          package: packageName,
          versions: versions,
          latest: versions[0] || null
        })
      };
    }

    // Get specific version
    const packageUrl = `https://api.github.com/repos/${REPO_OWNER}/${REPO_NAME}/contents/packages/${packageName}/${version}`;
    
    const response = await fetch(packageUrl, { headers: requestHeaders });
    
    if (!response.ok) {
      if (response.status === 404) {
        return {
          statusCode: 404,
          headers,
          body: JSON.stringify({ 
            error: `Package '${packageName}@${version}' not found` 
          })
        };
      }
      throw new Error(`GitHub API error: ${response.statusText}`);
    }

    const data = await response.json();
    
    // Find the archive file
    const archiveFile = data.find(item => 
      item.name.endsWith('.zip') || item.name.endsWith('.tar.gz')
    );

    if (!archiveFile) {
      return {
        statusCode: 404,
        headers,
        body: JSON.stringify({ 
          error: `No package archive found for '${packageName}@${version}'` 
        })
      };
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

    return {
      statusCode: 200,
      headers,
      body: JSON.stringify({
        package: packageName,
        version: version,
        filename: archiveFile.name,
        size: archiveFile.size,
        download_url: archiveFile.download_url,
        html_url: archiveFile.html_url,
        metadata: metadata
      })
    };

  } catch (error) {
    console.error('Download error:', error);
    
    return {
      statusCode: 500,
      headers,
      body: JSON.stringify({
        success: false,
        error: error.message
      })
    };
  }
};
