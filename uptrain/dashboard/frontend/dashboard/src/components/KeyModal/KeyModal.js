"use client";
import React, { useState } from "react";
import { useDispatch } from "react-redux";
import { addUserData } from "@/store/reducers/userInfo";

const KeyModal = () => {
  const [apiKey, setApiKey] = useState(""); // State to manage API key input
  const dispatch = useDispatch();

  const handleApiKey = async (e) => {
    e.preventDefault(); // Prevent default form submission behavior

    try {
      const response = await fetch(
        process.env.NEXT_PUBLIC_BACKEND_URL + "api/public/user",
        {
          method: "POST",
          headers: {
            "Content-Type": "application/json",
            "uptrain-access-token": `${apiKey}`,
          },
        }
      );

      if (response.ok) {
        const responseData = await response.json();
        dispatch(addUserData(responseData));
      } else {
        console.error("Failed to submit API Key:", response.statusText);
        // Handle error cases
      }
    } catch (error) {
      console.error("Error submitting API Key:", error.message);
      // Handle network errors or other exceptions
    }
  };

  const handleInputChange = (e) => {
    setApiKey(e.target.value); // Update API key state on input change
  };

  return (
    <div className="fixed top-0 left-0 w-screen h-screen backdrop-blur flex items-center justify-center overflow-auto p-10 z-20">
      <div className="rounded-xl border-[#5587FD] bg-[#23232D] p-8 max-w-[50%] w-full max-h-[100%] overflow-auto">
        <h1 className="text-2xl text-white mb-5">Enter your Uptrain API Key</h1>
        <form onSubmit={handleApiKey}>
          <input
            type="text"
            className="bg-[#171721] rounded-xl flex justify-between py-2.5 px-5 items-center mt-1.5 flex-1 w-full mb-5 text-white"
            placeholder="Enter key"
            value={apiKey}
            onChange={handleInputChange}
          />
          <button type="submit" className="bg-[#5587FD] px-5 py-2 rounded">
            Submit
          </button>
        </form>
      </div>
    </div>
  );
};

export default KeyModal;
