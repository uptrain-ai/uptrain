"use client";
import React from "react";
import SideBar from "./SideBar/SideBar";
import Header from "./Header";
import Image from "next/image";
import KeyModal from "./KeyModal/KeyModal";
import { selectUptrainAccessKey } from "@/store/reducers/userInfo";
import { useSelector } from "react-redux";
import FilterContainer from "./FilterContainer/FilterContainer";
import FilterSection from "./FilterSection/FilterSection";
import CompareSection from "./CompareSection/CompareSection";
import ProjectFilterSection from "./ProjectFilterSection/ProjectFilterSection";

const MainArea = (props) => {
  return (
    <>
      <Image
        src="/BackgroudDottedBoxTopLeft.png"
        width={250}
        height={350}
        className="fixed top-0 right-0 w-64 h-80 -z-10"
        alt=""
      ></Image>
      <Image
        src="/BackgroudDottedBoxTopLeft.png"
        width={250}
        height={350}
        className="fixed bottom-0 left-52 w-64 h-80 transform rotate-180 -z-10"
        alt=""
      ></Image>
      <div className="flex gap-10 flex-1">
        <div className="flex-1">
          <Header heading={props.heading} project={props.project} />
          <div className="flex items-start flex-1 gap-10 w-full mb-5">
            {props.children}
          </div>
        </div>
        <FilterContainer show={props.duration || props.compare}>
          <FilterSection
            TimeFilter={props.TimeFilter}
            setTimeFilter={props.setTimeFilter}
            duration={props.duration}
            projectNames={props.projectNames}
            selectedProject={props.selectedProject}
            handleProjectChange={props.handleProjectChange}
          />
          {props.setProjectFilters && (
            <ProjectFilterSection
              setProjectFilters={props.setProjectFilters}
              projectData={props.projectData}
              selectedTab={props.selectedTab}
              projectFilters={props.projectFilters}
            />
          )}
          {/* <PivotTable /> */}
          {props.compare && (
            <CompareSection
              projectData={props.projectData}
              filteredProjects={props.filteredProjects}
              selectedCompareProject={props.selectedCompareProject}
              setSelectedCompareProject={props.setSelectedCompareProject}
              selectedVersion1={props.selectedVersion1}
              setSelectedVersion1={props.setSelectedVersion1}
              selectedVersion2={props.selectedVersion2}
              setSelectedVersion2={props.setSelectedVersion2}
            />
          )}
        </FilterContainer>
      </div>
    </>
  );
};

const Layout = (props) => {
  const uptrainAccessKey = useSelector(selectUptrainAccessKey);

  return (
    <div className="flex w-screen overflow-y-auto overflow-x-hidden relative">
      {!uptrainAccessKey && <KeyModal />}
      <SideBar />
      <div className="flex-1 relative h-screen mx-10 flex flex-col">
        <MainArea
          heading={props.heading}
          project={props.project}
          TimeFilter={props.TimeFilter}
          setTimeFilter={props.setTimeFilter}
          duration={props.duration}
          projectNames={props.projectNames}
          selectedProject={props.selectedProject}
          handleProjectChange={props.handleProjectChange}
          projectData={props.projectData}
          compare={props.compare}
          filteredProjects={props.filteredProjects}
          selectedCompareProject={props.selectedCompareProject}
          setSelectedCompareProject={props.setSelectedCompareProject}
          selectedVersion1={props.selectedVersion1}
          setSelectedVersion1={props.setSelectedVersion1}
          selectedVersion2={props.selectedVersion2}
          setSelectedVersion2={props.setSelectedVersion2}
          setProjectFilters={props.setProjectFilters}
          selectedTab={props.selectedTab}
          projectFilters={props.projectFilters}
        >
          {props.children}
        </MainArea>
      </div>
    </div>
  );
};

export default Layout;
