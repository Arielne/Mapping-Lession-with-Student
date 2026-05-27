export default function UploadForm({ fields, submitLabel, onSubmit, busy }) {
  return (
    <form className="panel form" onSubmit={onSubmit}>
      {fields}
      <button className="primary" disabled={busy}>
        {busy ? "Uploading..." : submitLabel}
      </button>
    </form>
  );
}

