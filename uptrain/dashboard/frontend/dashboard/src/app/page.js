"use client";
import FilterSection from "@/components/FilterSection/FilterSection";
import CreateProjectModal from "@/components/CreateProjectModal/CreateProjectModal";
import ProjectSection from "@/components/HomePage/ProjectSection/ProjectSection";
import Layout from "@/components/Layout";
import SpinningLoader from "@/components/UI/SpinningLoader";
import {
  selectUptrainAccessKey,
  selectUserName,
} from "@/store/reducers/userInfo";
import React, { useEffect, useState } from "react";
import { useSelector } from "react-redux";

const fetchData = async (uptrainAccessKey, setData, timeFilter) => {
  const num_days =
    timeFilter === 0 ? 1 : timeFilter === 1 ? 7 : timeFilter === 2 ? 30 : 10000;

  try {
    const response = await fetch(
      process.env.NEXT_PUBLIC_BACKEND_URL +
        `api/public/get_projects_list?num_days=${num_days}`,
      {
        method: "GET",
        headers: {
          "Content-Type": "application/json",
          "uptrain-access-token": `${uptrainAccessKey}`,
        },
      }
    );

    if (response.ok) {
      const responseData = await response.json();
      setData(responseData.data);
    } else {
      console.error("Failed to submit API Key:", response.statusText);
      // Handle error cases
    }
  } catch (error) {
    console.error("Error submitting API Key:", error.message);
    // Handle network errors or other exceptions
  }
};

const page = () => {
  const [timeFilter, setTimeFilter] = useState(1);
  const [data, setData] = useState(null);
  const [openModal, setopenModal] = useState(false);

  const uptrainAccessKey = useSelector(selectUptrainAccessKey);
  const userName = useSelector(selectUserName);

  useEffect(() => {
    setData(null);
    const fetchDataAsync = async () => {
      await fetchData(uptrainAccessKey, setData, timeFilter);
    };

    fetchDataAsync();
  }, [uptrainAccessKey, timeFilter]);

  const reloadData = () => {
    setData(null);
    const fetchDataAsync = async () => {
      await fetchData(uptrainAccessKey, setData, timeFilter);
    };

    fetchDataAsync();
  };

  return (
    <Layout heading={`Hello ${userName}`}>
      <div className="flex gap-10 w-full items-start">
        {openModal && (
          <CreateProjectModal
            close={() => {
              setopenModal(false);
            }}
            reloadData={reloadData}
          />
        )}
        <div className="flex-1 mb-5">
          {data ? (
            <ProjectSection
              data={data}
              setopenModal={() => {
                setopenModal(true);
              }}
            />
          ) : (
            <div class="flex justify-center items-center h-screen">
              <SpinningLoader />
            </div>
          )}
        </div>
        <div className="bg-[#23232D] text-[#5C5C66] rounded-xl p-4 max-w-[300px] w-full mb-8">
          <FilterSection
            TimeFilter={timeFilter}
            setTimeFilter={setTimeFilter}
            duration
          />
        </div>
      </div>
    </Layout>
  );
};

export default page;
