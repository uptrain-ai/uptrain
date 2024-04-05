import ChartPage from "@/components/Evaluations/ChartPage/ChartPage";
import ProjectPage from "@/components/Evaluations/Homepage/ProjectPage";
import React from "react";

const page = ({ params: { slug } }) => {
  return (
    <>
      {slug.length == 2 && <ChartPage slug={slug} />}
      {slug.length == 1 && <ProjectPage slug={slug} />}
    </>
  );
};

export default page;
