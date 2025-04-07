import { StrictMode } from 'react'
import { createRoot } from 'react-dom/client'
import './index.css'
import App from './App.tsx'

// Add error handling for initial render
console.log('Starting application render...');

try {
  const rootElement = document.getElementById('root');
  
  if (!rootElement) {
    console.error('Root element not found in DOM!');
  } else {
    console.log('Root element found, creating React root');
    
    const root = createRoot(rootElement);
    
    root.render(
      <StrictMode>
        <App />
      </StrictMode>,
    );
    
    console.log('React application successfully rendered');
  }
} catch (error) {
  console.error('Error rendering React application:', error);
}
