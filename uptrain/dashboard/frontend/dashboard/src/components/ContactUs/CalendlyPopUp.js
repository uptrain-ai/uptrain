import React from 'react'
import { InlineWidget } from 'react-calendly';

const CalendlyPopUp = (props) => {
    return (
      <div
        className="fixed top-0 left-0 w-screen h-screen backdrop-blur flex items-center justify-center overflow-auto "
        onClick={props.onClick}
      >
        <div className="rounded-xl border-[#5587FD] bg-[#23232D] overflow-auto w-3/4 h-5/6">
          <InlineWidget url="https://calendly.com/uptrain-sourabh/30min" />
        </div>
      </div>
    );
  };

export default CalendlyPopUp