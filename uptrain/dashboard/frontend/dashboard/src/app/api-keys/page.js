"use client";
import ApiKeySection from "@/components/ApiKeys/ApiKeySection";
import CreditsSection from "@/components/ApiKeys/CreditsSection";
import WorkingSection from "@/components/ApiKeys/WorkingSection";
import Layout from "@/components/Layout";
import React from "react";

const page = () => {
  return (
    <Layout heading="API Keys">
      <div className="bg-[#23232D] rounded-xl p-8 w-[calc(100vw-640px)] mb-5">
        {/* <ApiKeySection />
        <CreditsSection /> */}
        <WorkingSection />
      </div>
    </Layout>
  );
};

export default page;
