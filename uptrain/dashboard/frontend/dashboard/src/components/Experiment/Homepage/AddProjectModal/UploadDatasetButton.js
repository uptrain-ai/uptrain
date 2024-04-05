import Image from "next/image";
import React, { useRef } from "react";

const UploadDatasetButton = (props) => {
  const fileInputRef = useRef(null);

  const handleClick = () => {
    fileInputRef.current.click();
  };

  const handleFileUpload = (event) => {
    const file = event.target.files[0];
    props.setSelectedFile(file);
  };

  return (
    <>
      <input
        type="file"
        ref={fileInputRef}
        onChange={handleFileUpload}
        style={{ display: "none" }}
      />
      <button
        className="bg-[#171721] w-full h-full min-h-[150px] px-4 rounded-xl flex items-center justify-center flex-col cursor-pointer"
        onClick={handleClick}
        type="button"
      >
        <Image
          src={`${process.env.NEXT_PUBLIC_BASE_PATH}/Add.png`}
          width={34}
          height={34}
          className="mb-2"
          alt="add Icon"
        />
        <p className="text-[#6B6B6B]">Upload Dataset</p>
      </button>
    </>
  );
};

export default UploadDatasetButton;
