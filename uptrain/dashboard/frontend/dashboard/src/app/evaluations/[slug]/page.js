"use client";
import { useRouter } from "next/navigation";
import React, { useLayoutEffect } from "react";

const page = () => {
  const router = useRouter();

  useLayoutEffect(() => {
    router.push("/evaluations");
  }, []);

  return <div>Loading</div>;
};

export default page;
