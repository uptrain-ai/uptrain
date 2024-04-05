import React from "react";

const Header = (props) => {
  return (
    <div
      className={`flex justify-between items-center my-10 gap-10 ${props.className}`}
    >
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
    </div>
  );
};

export default Header;
