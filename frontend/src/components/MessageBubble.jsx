import ReactMarkdown from "react-markdown";
import { FileText } from "lucide-react";

export default function MessageBubble({ role, content, sources }) {
  const isUser = role === "user";

  return (
    <div className={`message-row ${isUser ? "user" : "assistant"}`}>
      <div className="message-bubble">
        <ReactMarkdown>{content}</ReactMarkdown>

        {sources && sources.length > 0 && (
          <div className="sources-block">
            <span className="sources-label">Sources</span>
            {sources.map((src, idx) => (
              <div key={idx} className="source-chip" title={src.snippet}>
                <FileText size={12} />
                <span>{src.document_name} · p.{src.page}</span>
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  );
}
