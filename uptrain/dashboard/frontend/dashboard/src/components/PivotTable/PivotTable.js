"use client";
import React, { useState } from "react";
import CustomSelect from "../CustomSelect/CustomSelect";

const PivotTable = () => {
  return (
    <div>
      <h2 className="text-lg font-medium">Pivot Table</h2>
      <CustomSelect title="Index" />
      <CustomSelect title="Index" />
      <CustomSelect title="Index" />
    </div>
  );
};

export default PivotTable;
