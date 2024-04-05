import React from "react";

function convertToCamelCase(str) {
  return str
    .replace(/_([a-z])/g, function (match, letter) {
      return letter.toUpperCase();
    })
    .replace(/^([a-z])/, function (match, letter) {
      return letter.toUpperCase();
    });
}

function findObjectByCheckName(array, searchString) {
  return array.find((obj) => obj.check_name === searchString);
}

const CustomTabButton = (props) => {
  const checkName = convertToCamelCase(props.title);
  const data = props.checks && findObjectByCheckName(props.checks, checkName);

  return (
    <div className="min-w-[220px] flex-1 h-10 relative inline-block">
      <button
        className={`border-b-4  pb-2 w-full font-medium text-lg text-center overflow-x-hidden ${
          props.selected
            ? "border-[#5587FD] text-white"
            : "border-[#5C5C66] text-[#5C5C66]"
        }`}
        onClick={props.onClick}
        onMouseEnter={() => props.setData && props.setData(data)}
        onMouseLeave={() => props.setData && props.setData(null)}
      >
        <p className="px-2">{props.title}</p>
      </button>
    </div>
  );
};

export default CustomTabButton;
