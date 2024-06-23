import json
from lzstring import LZString
from urllib.parse import quote

# Define the file contents
files = {
    "index.js": {
        "content": """
import React from 'react';
import ReactDOM from 'react-dom';
import App from './App';
import './index.css';

ReactDOM.render(
  <React.StrictMode>
    <App />
  </React.StrictMode>,
  document.getElementById('root')
);
"""
    },
    "App.js": {
        "content": """
import React from 'react';
import Header from './Header';
import Footer from './Footer';
import './App.css';

function App() {
  return (
    <div className="App">
      <Header />
      <main>
        <h1>Hello, World!</h1>
        <p>Welcome to our simple React app.</p>
      </main>
      <Footer />
    </div>
  );
}

export default App;
"""
    },
    "Header.js": {
        "content": """
import React from 'react';

function Header() {
  return (
    <header>
      <h1>My App</h1>
    </header>
  );
}

export default Header;
"""
    },
    "Footer.js": {
        "content": """
import React from 'react';

function Footer() {
  return (
    <footer>
      <p>&copy; 2024 My App. All rights reserved.</p>
    </footer>
  );
}

export default Footer;
"""
    },
    "index.css": {
        "content": """
body {
  margin: 0;
  font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', 'Roboto', 'Oxygen', 'Ubuntu', 'Cantarell', 'Fira Sans', 'Droid Sans', 'Helvetica Neue', sans-serif;
  -webkit-font-smoothing: antialiased;
  -moz-osx-font-smoothing: grayscale;
  background-color: #f5f5f5;
}

code {
  font-family: source-code-pro, Menlo, Monaco, Consolas, 'Courier New', monospace;
}

.App {
  text-align: center;
}

header {
  background-color: #282c34;
  padding: 20px;
  color: white;
}

footer {
  background-color: #282c34;
  padding: 10px;
  color: white;
  position: absolute;
  bottom: 0;
  width: 100%;
  text-align: center;
}
"""
    },
    "App.css": {
        "content": """
.App main {
  padding: 20px;
}
"""
    },
    "package.json": {
        "content": json.dumps({
            "name": "complex-react-app",
            "version": "1.0.0",
            "main": "index.js",
            "dependencies": {
                "react": "^18.0.0",
                "react-dom": "^18.0.0",
                "react-scripts": "^5.0.0"
            },
            "scripts": {
                "start": "react-scripts start",
                "build": "react-scripts build"
            },
            "eslintConfig": {
                "extends": [
                    "react-app",
                    "react-app/jest"
                ]
            },
            "browserslist": {
                "production": [
                    ">0.2%",
                    "not dead",
                    "not op_mini all"
                ],
                "development": [
                    "last 1 chrome version",
                    "last 1 firefox version",
                    "last 1 safari version"
                ]
            }
        })
    }
}

# Wrap the files dictionary in the expected structure
parameters = {
    "files": files
}

# Convert the parameters to a JSON string
parameters_json = json.dumps(parameters)

# Compress the JSON string
lz = LZString()
compressed_parameters = lz.compressToBase64(parameters_json)

# Encode the compressed string for the URL
encoded_compressed_parameters = quote(compressed_parameters)

# Construct the URL
api_url = f"https://codesandbox.io/api/v1/sandboxes/define?parameters={encoded_compressed_parameters}"

# Output the URL
print(api_url)
