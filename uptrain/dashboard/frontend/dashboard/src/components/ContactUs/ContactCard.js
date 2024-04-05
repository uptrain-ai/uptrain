import Image from "next/image";
import React, { useState } from "react";

const ContactCard = (props) => {
  const [isHovered, setIsHovered] = useState(false);

  const handleMouseEnter = () => {
    setIsHovered(true);
  };

  const handleMouseLeave = () => {
    setIsHovered(false);
  };

  return (
    <a
      className={`bg-[#23232D] rounded-xl p-8 max-w-[380px] w-full mont border-2 cursor-pointer text-left ${
        isHovered ? "border-[#5587FD]" : "border-[#23232D]"
      }`}
      onMouseEnter={handleMouseEnter}
      onMouseLeave={handleMouseLeave}
      onClick={props.onClick}
    >
      {props.children}
      <h2
        className={` font-semibold text-xl mb-4 ${
          isHovered ? "text-[#5587FD]" : "text-[#EFEFEF]"
        }`}
      >
        {props.heading}
      </h2>
      <p
        className={`font-medium text-base mb-4 ${
          isHovered ? "text-[#EFEFEF]" : "text-[#57575E]"
        }`}
      >
        {props.parah}
      </p>
      {isHovered ? (
        <Image src={`${process.env.NEXT_PUBLIC_BASE_PATH}/RightPointingArrowBlue.svg`} width={18} height={18} alt="Arrow Icon"/>
      ) : (
        <Image src={`${process.env.NEXT_PUBLIC_BASE_PATH}/RightPointingArrow.svg`} width={18} height={18} alt="Arrow Icon"/>
      )}
    </a>
  );
};

export default ContactCard;
