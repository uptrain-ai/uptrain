"use client";
import Layout from "@/components/Layout";
import Image from "next/image";
import React, { useState } from "react";
import { InlineWidget } from "react-calendly";

const ContactCard = (props) => {
  const [isHovered, setIsHovered] = useState(false);

  const handleMouseEnter = () => {
    setIsHovered(true);
  };

  const handleMouseLeave = () => {
    setIsHovered(false);
  };

  return (
    <div
      className={`bg-[#23232D] rounded-xl p-8 max-w-[380px] w-full mont border-2 cursor-pointer ${
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
        <Image src="/RightPointingArrowBlue.svg" width={18} height={18} />
      ) : (
        <Image src="/RightPointingArrow.svg" width={18} height={18} />
      )}
    </div>
  );
};

const CalendlyPopUp = (props) => {
  return (
    <div
      className="fixed top-0 left-0 w-screen h-screen backdrop-blur flex items-center justify-center overflow-auto "
      onClick={props.onClick}
    >
      <div className="rounded-xl border-[#5587FD] bg-[#23232D] overflow-auto w-3/4 h-5/6">
        <InlineWidget url="https://calendly.com/uptrain-sourabh/30min" />
      </div>
    </div>
  );
};

const page = () => {
  const [openCalendlyPopUp, setOpenCalendlyPopUp] = useState(false);

  return (
    <Layout heading="Contact Us">
      {openCalendlyPopUp && (
        <CalendlyPopUp
          onClick={() => {
            setOpenCalendlyPopUp(false);
          }}
        />
      )}
      <div className="flex gap-6 flex-1 ">
        <ContactCard
          parah="Upon clicking, you'll be directed to a form page where you can compose
        your query and submit it to us."
          heading="Share your thoughts"
        >
          <Image
            src="/ContactUs-Thoughts.png"
            width={63}
            height={63}
            alt=""
            className="mb-5 w-[63px] h-[63px]"
          />
        </ContactCard>
        <ContactCard
          parah="Upon clicking, you'll be taken to a page where you can schedule a call with a UpTrain team member."
          heading="Book a call"
          onClick={() => {
            setOpenCalendlyPopUp(true);
          }}
        >
          <Image
            src="/ContactUs-Calls.png"
            width={63}
            height={63}
            alt=""
            className="mb-5 w-[63px] h-[63px]"
          />
        </ContactCard>
      </div>
    </Layout>
  );
};

export default page;
