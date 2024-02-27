import React from "react";

const DownArrow = (props) => {
  return (
    <svg
      xmlns="http://www.w3.org/2000/svg"
      width="8"
      height="5"
      viewBox="0 0 8 5"
      fill="none"
      className={`${props.Selected && "rotate-180"} transition  delay-75`}
    >
      <path
        d="M7.83493 0.676388L4.54461 4.72246C4.23248 5.09251 3.75137 5.09251 3.45214 4.72246L0.161822 0.676388C-0.150313 0.293265 0.00575475 0 0.486859 0H7.50989C8.00432 0 8.14707 0.293673 7.83493 0.676388Z"
        fill="#5C5C66"
      />
    </svg>
  );
};

export default DownArrow;
