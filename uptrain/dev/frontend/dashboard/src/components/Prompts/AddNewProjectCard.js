import Image from 'next/image';
import React from 'react'

const AddNewProjectCard = (props) => {
    return (
      <button
        className="bg-[#1C1C25] w-full h-full min-h-[150px] px-4 rounded-xl flex items-center justify-center flex-col cursor-pointer"
        onClick={props.onClick}
      >
        <Image src="/Add.png" width={34} height={34} className="mb-2" />
        <p className="text-[#6B6B6B] ">Add New Prompt</p>
      </button>
    );
  };

export default AddNewProjectCard