import { useEffect, useState } from 'react';
import api from '../services/api';

export default function usePublicJob(jobId) {
  const [job, setJob] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    if (!jobId) return;
    const controller = new AbortController();
    setLoading(true);
    setError(null);
    (async () => {
      try {
        const url = `/recruiter/jobs/${jobId}`;
        const resp = await api.get(url, { signal: controller.signal });
        setJob(resp.data);
      } catch (e) {
        if (e?.name === 'CanceledError' || e?.code === 'ERR_CANCELED') return;
        setError('Job not found');
      } finally {
        setLoading(false);
      }
    })();
    return () => controller.abort();
  }, [jobId]);

  return { job, loading, error };
}


