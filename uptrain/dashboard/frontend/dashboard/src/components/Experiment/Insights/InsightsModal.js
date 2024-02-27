import Image from "next/image";
import React from "react";

const TextSection = (props) => {
  return (
    <div className="mt-5 text-[#8A8A8A] text-sm font-medium leading-5">
      <h2 className="text-[#EDEDED] font-medium text-lg">
        Get Early Access to Insights
      </h2>
      <p className="mt-3 ">
        <span className="text-[#B6B6B9] ">Demo Content</span> : Let's start by
        comparing the generated answer with the question to determine{" "}
        <span className="text-[#B6B6B9] ">Demo Content</span> the semantic
        similarity. We need to{" "}
        <span className="text-[#B6B6B9] ">Demo Content</span> ignore any
        differences in style, grammar, or punctuation.
      </p>
      <br />
      <p>
        Empathic Intuition: I agree, we should focus{" "}
        <span className="text-[#B6B6B9] ">Demo Content</span> on the meaning and
        content rather than the presentation.
      </p>
      <br />
      <p>
        Fact-checker Freddy: Absolutely, we need to{" "}
        <span className="text-[#B6B6B9] ">Demo Content</span> ensure that the
        generated answer is relevant to the{" "}
        <span className="text-[#B6B6B9] ">Demo Content</span> question and
        doesn't contain any irrelevant information.
      </p>
      <br />
      <p>
        Context Charlie: It's important to consider the wider context of the{" "}
        <span className="text-[#B6B6B9] ">Demo Content</span> question and
        answer pair. We should make sure that the answer respects and reflects
        the inherent context.
      </p>
    </div>
  );
};

const InsightsModal = (props) => {
  const handleClick = (event) => {
    event.stopPropagation();
  };

  return (
    <div
      className="fixed top-0 left-0 w-screen h-screen backdrop-blur flex items-center justify-center overflow-auto p-10 pt-40 z-10"
      onClick={props.close}
    >
      <div
        className="rounded-xl border-[#5587FD] bg-[#23232D] p-8 max-w-[746px] w-full max-h-[700px] overflow-auto"
        onClick={handleClick}
      >
        <Image
          src="/InsightsAccessImage.png"
          width={683}
          height={318}
          className="w-full h-auto"
        />
        <TextSection />
      </div>
    </div>
  );
};

export default InsightsModal;