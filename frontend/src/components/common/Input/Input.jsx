import PropTypes from 'prop-types';

const Input = ({ 
  label, 
  error, 
  className = '', 
  id,
  name,
  ...props 
}) => {
  const inputClasses = `
    w-full px-3 py-2 border rounded-lg focus:outline-none focus:ring-2 focus:ring-primary-500 focus:border-transparent
    ${error ? 'border-red-300 focus:ring-red-500' : 'border-gray-300'}
    ${className}
  `.trim();

  const resolvedId = id || name || undefined;

  return (
    <div className="space-y-1">
      {label && (
        <label htmlFor={resolvedId} className="block text-sm font-medium text-gray-700">
          {label}
        </label>
      )}
      <input
        id={resolvedId}
        name={name}
        className={inputClasses}
        {...props}
      />
      {error && (
        <p className="text-sm text-red-600">{error}</p>
      )}
    </div>
  );
};

Input.propTypes = {
  label: PropTypes.string,
  error: PropTypes.string,
  className: PropTypes.string,
};

export default Input;
