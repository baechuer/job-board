import { useEffect, useState } from 'react';
import api from '../services/api';

const ApiTest = () => {
  const [result, setResult] = useState('');
  const [loading, setLoading] = useState(false);

  const testApi = async () => {
    setLoading(true);
    try {
      console.log('Testing API call to /recruiter/jobs/3');
      const response = await api.get('/recruiter/jobs/3');
      console.log('API Response:', response);
      setResult(JSON.stringify(response.data, null, 2));
    } catch (error) {
      console.error('API Error:', error);
      setResult(`Error: ${error.message}\nStatus: ${error.response?.status}\nData: ${JSON.stringify(error.response?.data)}`);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="p-8">
      <h1 className="text-2xl font-bold mb-4">API Test</h1>
      <button 
        onClick={testApi} 
        disabled={loading}
        className="bg-blue-500 text-white px-4 py-2 rounded disabled:opacity-50"
      >
        {loading ? 'Testing...' : 'Test API Call'}
      </button>
      
      <div className="mt-4">
        <h2 className="text-lg font-semibold mb-2">Result:</h2>
        <pre className="bg-gray-100 p-4 rounded text-sm overflow-auto">
          {result || 'Click the button to test the API'}
        </pre>
      </div>
    </div>
  );
};

export default ApiTest;
