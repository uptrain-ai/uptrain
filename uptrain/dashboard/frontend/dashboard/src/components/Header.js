import Image from "next/image";
import React from "react";

const Header = (props) => {
  return (
    <div className="flex justify-between items-center my-10 gap-10">
      <div className="flex justify-between items-center flex-1">
        <h1 className="text-3xl text-white">{props.heading}</h1>
        {props.project && (
          <div className="flex items-center">
            <p className="font-medium text-base text-[#5C5C66]">
              Project:{" "}
              <span className="text-lg text-[#A8A8A8]">{props.project}</span>
            </p>
          </div>
        )}
      </div>
      <div className="flex items-center justify-end gap-7 max-w-[300px] w-full">
        <Image src="/FileIcon.svg" width={18} height={18} alt="" />
        <Image src="/QuestionIcon.svg" width={18} height={18} alt="" />
        <Image src="/NotificationIcon.svg" width={18} height={18} alt="" />
        <div className="flex gap-4">
          <div className="w-9 h-9 rounded-full bg-white"></div>
          <Image src="/DropDownIcon.svg" width={18} height={18} alt="" />
        </div>
      </div>
    </div>
  );
};

export default Header;
