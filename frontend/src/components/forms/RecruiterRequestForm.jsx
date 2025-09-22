import { useState } from 'react';
import { recruiterService } from '../../services/recruiterService';
import Button from '../common/Button';
import Input from '../common/Input';

const RecruiterRequestForm = ({ onSuccess, onCancel }) => {
  const [formData, setFormData] = useState({
    reason: '',
  });
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');

  const handleChange = (e) => {
    setFormData({
      ...formData,
      [e.target.name]: e.target.value,
    });
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);
    setError('');

    try {
      await recruiterService.submitRequest(formData.reason);
      onSuccess && onSuccess();
    } catch (error) {
      setError(error.response?.data?.error || 'Failed to submit request');
    } finally {
      setLoading(false);
    }
  };

  return (
    <form onSubmit={handleSubmit} className="space-y-4">
      <div>
        <label htmlFor="reason" className="block text-sm font-medium text-gray-700 mb-2">
          Why do you want to become a recruiter?
        </label>
        <textarea
          id="reason"
          name="reason"
          value={formData.reason}
          onChange={handleChange}
          rows="4"
          className="input-field"
          placeholder="Please explain why you want recruiter access..."
          required
        />
      </div>

      {error && (
        <div className="text-red-600 text-sm">{error}</div>
      )}

      <div className="flex space-x-3">
        <Button type="submit" loading={loading}>
          Submit Request
        </Button>
        {onCancel && (
          <Button type="button" variant="secondary" onClick={onCancel}>
            Cancel
          </Button>
        )}
      </div>
    </form>
  );
};

export default RecruiterRequestForm;
