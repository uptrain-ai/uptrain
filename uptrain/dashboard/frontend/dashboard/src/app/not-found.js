import Image from "next/image";
import React from "react";

const page = () => {
  return (
    <div className="w-screen h-screen flex items-center justify-center flex-col">
      <Image
        src="/404.svg"
        width={310}
        height={310}
        className="w-1/5 h-auto grayscale mb-5"
      />
      <h1 className="text-5xl text-[#838383] font-semibold mb-8">
        Page Not Found
      </h1>
      <div className="text-[#515151] flex items-center flex-col gap-2">
        <p className="text-3xl font-medium">Oops! Something went wrong</p>
        <p className="text-xl font-medium">
          Try to refresh this page or Try again later
        </p>
      </div>
    </div>
  );
};

export default page;
