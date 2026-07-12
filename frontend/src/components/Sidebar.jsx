import { useRef, useState } from "react";
import { Upload, FileText, Trash2, Loader2 } from "lucide-react";
import { uploadDocument, deleteDocument } from "../api/client";

export default function Sidebar({ documents, onDocumentsChange, selectedIds, onSelectionChange }) {
  const fileInputRef = useRef(null);
  const [uploading, setUploading] = useState(false);
  const [error, setError] = useState(null);

  const handleFileChange = async (e) => {
    const file = e.target.files[0];
    if (!file) return;

    setUploading(true);
    setError(null);
    try {
      await uploadDocument(file);
      onDocumentsChange();
    } catch (err) {
      setError(err.message);
    } finally {
      setUploading(false);
      e.target.value = "";
    }
  };

  const handleDelete = async (docId) => {
    await deleteDocument(docId);
    onDocumentsChange();
    onSelectionChange(selectedIds.filter((id) => id !== docId));
  };

  const toggleSelection = (docId) => {
    if (selectedIds.includes(docId)) {
      onSelectionChange(selectedIds.filter((id) => id !== docId));
    } else {
      onSelectionChange([...selectedIds, docId]);
    }
  };

  return (
    <aside className="sidebar">
      <div className="sidebar-header">
        <h1>DocIntel</h1>
        <p className="tagline">Ask questions, get cited answers.</p>
      </div>

      <button
        className="upload-btn"
        onClick={() => fileInputRef.current.click()}
        disabled={uploading}
      >
        {uploading ? <Loader2 className="spin" size={16} /> : <Upload size={16} />}
        {uploading ? "Indexing..." : "Upload PDF"}
      </button>
      <input
        type="file"
        accept=".pdf"
        ref={fileInputRef}
        onChange={handleFileChange}
        style={{ display: "none" }}
      />

      {error && <p className="error-text">{error}</p>}

      <div className="doc-list">
        {documents.length === 0 && (
          <p className="empty-state">No documents yet. Upload a PDF to get started.</p>
        )}
        {documents.map((doc) => (
          <div
            key={doc.document_id}
            className={`doc-item ${selectedIds.includes(doc.document_id) ? "selected" : ""}`}
            onClick={() => toggleSelection(doc.document_id)}
          >
            <FileText size={16} />
            <div className="doc-item-info">
              <span className="doc-name">{doc.filename}</span>
              <span className="doc-meta">{doc.chunk_count} chunks</span>
            </div>
            <Trash2
              size={14}
              className="delete-icon"
              onClick={(e) => {
                e.stopPropagation();
                handleDelete(doc.document_id);
              }}
            />
          </div>
        ))}
      </div>

      <p className="selection-hint">
        {selectedIds.length === 0
          ? "Querying across all documents"
          : `Querying ${selectedIds.length} selected document${selectedIds.length > 1 ? "s" : ""}`}
      </p>
    </aside>
  );
}
