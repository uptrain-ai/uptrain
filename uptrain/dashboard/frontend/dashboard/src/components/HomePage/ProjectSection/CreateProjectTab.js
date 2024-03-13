import Image from "next/image";
import React from "react";

const CreateProjectTab = (props) => {
  return (
    <button
      className="bg-[#1C1C25] w-full h-full min-h-[150px] px-4 rounded-xl flex items-center justify-center flex-col cursor-pointer"
      onClick={props.setopenModal}
    >
      <Image src="/Add.png" width={34} height={34} className="mb-2" alt="add Icon"/>
      <p className="text-[#6B6B6B] ">Create New Project</p>
    </button>
  );
};

export default CreateProjectTab;
