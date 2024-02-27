import React, { useEffect } from "react";
import Prism from "prismjs";

const CodeViewer = ({ children, horizontal }) => {
  useEffect(() => {
    if (typeof window !== "undefined") {
      Prism.highlightAll();
    }
  }, [children]);

  return (
    <div className="text-white text-sm">
      <code
        className="language-js"
        style={
          horizontal
            ? { wordBreak: "break-word" }
            : {
                whiteSpace: "pre-wrap",
                wordBreak: "break-word",
              }
        }
      >
        {children}
      </code>
    </div>
  );
};

export default React.memo(CodeViewer);
