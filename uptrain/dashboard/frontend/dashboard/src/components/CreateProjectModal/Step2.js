import React from "react";

const Step2 = (props) => {
  const handleSubmit = (event) => {
    event.preventDefault();

    props.next();
  };

  return (
    <div>
      <h2 className="text-lg text-[#B0B0B1] font-medium mb-5">New Prompt</h2>
      <form onSubmit={handleSubmit}>
        <input
          className="bg-[#171721] rounded-xl px-6 py-4 text-[#B6B6B9] w-full"
          placeholder="Prompt name"
          onChange={(e) => props.setPromptName(e.target.value)}
          value={
            props.promptVersionName ? props.promptVersionName : props.promptName
          }
          required
          disabled={props.promptVersionName}
        />
        <textarea
          className="bg-[#171721] rounded-xl px-6 py-4 text-[#B6B6B9] w-full mt-5 resize-none"
          placeholder="Your Prompt"
          onChange={(e) => props.setPrompt(e.target.value)}
          value={props.prompt}
          required
          rows={3}
        />
        <div className="flex justify-end mt-5">
          <button
            type="Submit"
            className="bg-[#5587FD] text-white px-10 py-2.5 font-semibold text-lg rounded-xl"
            onClick={props.next}
          >
            Next
          </button>
        </div>
      </form>
    </div>
  );
};

export default Step2;
