import { useEffect, useRef, useState } from "react";
import { Send } from "lucide-react";
import MessageBubble from "./MessageBubble";
import TypingIndicator from "./TypingIndicator";
import { streamMessage } from "../api/client";

export default function ChatWindow({ sessionId, selectedIds, hasDocuments }) {
  const [messages, setMessages] = useState([]);
  const [input, setInput] = useState("");
  const [isStreaming, setIsStreaming] = useState(false);
  const bottomRef = useRef(null);

  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages, isStreaming]);

  const handleSend = async () => {
    const query = input.trim();
    if (!query || isStreaming) return;

    setMessages((prev) => [...prev, { role: "user", content: query }]);
    setInput("");
    setIsStreaming(true);

    setMessages((prev) => [...prev, { role: "assistant", content: "", sources: [] }]);

    let accumulated = "";
    try {
      await streamMessage(
        sessionId,
        query,
        selectedIds.length > 0 ? selectedIds : null,
        (delta) => {
          accumulated += delta;
          setMessages((prev) => {
            const updated = [...prev];
            updated[updated.length - 1] = { role: "assistant", content: accumulated };
            return updated;
          });
        },
        () => setIsStreaming(false)
      );
    } catch (err) {
      setMessages((prev) => {
        const updated = [...prev];
        updated[updated.length - 1] = {
          role: "assistant",
          content: "Something went wrong reaching the server. Is the backend running?",
        };
        return updated;
      });
      setIsStreaming(false);
    }
  };

  const handleKeyDown = (e) => {
    if (e.key === "Enter" && !e.shiftKey) {
      e.preventDefault();
      handleSend();
    }
  };

  return (
    <div className="chat-window">
      <div className="messages">
        {messages.length === 0 && (
          <div className="welcome-state">
            <h2>Ask something about your documents</h2>
            <p>
              {hasDocuments
                ? "Try asking a specific question about the content you uploaded."
                : "Upload a PDF on the left to get started."}
            </p>
          </div>
        )}

        {messages.map((msg, idx) => (
          <MessageBubble key={idx} role={msg.role} content={msg.content} sources={msg.sources} />
        ))}

        {isStreaming && messages[messages.length - 1]?.content === "" && <TypingIndicator />}

        <div ref={bottomRef} />
      </div>

      <div className="input-bar">
        <textarea
          rows={1}
          placeholder={hasDocuments ? "Ask a question about your documents..." : "Upload a document first..."}
          value={input}
          onChange={(e) => setInput(e.target.value)}
          onKeyDown={handleKeyDown}
          disabled={!hasDocuments}
        />
        <button onClick={handleSend} disabled={!hasDocuments || isStreaming || !input.trim()}>
          <Send size={16} />
        </button>
      </div>
    </div>
  );
}
