import DOMPurify from 'dompurify';

export default function SafeHTML({ html, allowedTags, allowedAttributes, className }) {
  const clean = DOMPurify.sanitize(html || '', {
    ALLOWED_TAGS: allowedTags,
    ALLOWED_ATTR: allowedAttributes,
    // Keep URLs safe; no javascript: URLs
    SAFE_FOR_TEMPLATES: true,
    FORBID_ATTR: ['style', 'onerror', 'onclick', 'onload'],
    FORBID_TAGS: ['script', 'iframe', 'object', 'embed']
  });
  return (
    <div className={className} dangerouslySetInnerHTML={{ __html: clean }} />
  );
}


