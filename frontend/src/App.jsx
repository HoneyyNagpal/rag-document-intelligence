import { useEffect, useState, useCallback } from "react";
import Sidebar from "./components/Sidebar";
import ChatWindow from "./components/ChatWindow";
import { fetchDocuments } from "./api/client";

function generateSessionId() {
  return `session_${Math.random().toString(36).slice(2)}_${Date.now()}`;
}

export default function App() {
  const [documents, setDocuments] = useState([]);
  const [selectedIds, setSelectedIds] = useState([]);
  const [sessionId] = useState(generateSessionId);

  const loadDocuments = useCallback(async () => {
    try {
      const docs = await fetchDocuments();
      setDocuments(docs);
    } catch {
      /* backend might not be up yet, fail silently on first load */
    }
  }, []);

  useEffect(() => {
    loadDocuments();
  }, [loadDocuments]);

  return (
    <div className="app-shell">
      <Sidebar
        documents={documents}
        onDocumentsChange={loadDocuments}
        selectedIds={selectedIds}
        onSelectionChange={setSelectedIds}
      />
      <ChatWindow sessionId={sessionId} selectedIds={selectedIds} hasDocuments={documents.length > 0} />
    </div>
  );
}
