"use client";
import CalendlyPopUp from "@/components/ContactUs/CalendlyPopUp";
import ContactCard from "@/components/ContactUs/ContactCard";
import Layout from "@/components/Layout";
import Image from "next/image";
import React, { useState } from "react";

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
          onClick={() => {
            window.open(
              "https://docs.google.com/forms/d/e/1FAIpQLSezGUkkC0JoEvx-0gCrRSmGutA-jqyb7kl2lomXv302_C3MnQ/viewform?ts=65e1846d",
              "_blank"
            );
          }}
        >
          <Image
            src={`${process.env.NEXT_PUBLIC_BASE_PATH}/ContactUs-Thoughts.png`}
            width={63}
            height={63}
            alt="contact us form Image"
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
            src={`${process.env.NEXT_PUBLIC_BASE_PATH}/ContactUs-Calls.png`}
            width={63}
            height={63}
            alt="contact us candely Image"
            className="mb-5 w-[63px] h-[63px]"
          />
        </ContactCard>
      </div>
    </Layout>
  );
};

export default page;
