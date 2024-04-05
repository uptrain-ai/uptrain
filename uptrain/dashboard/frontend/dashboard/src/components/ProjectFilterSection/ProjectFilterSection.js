import React from "react";
import CustomMultiSelect from "../DropDowns/CustomMultiSelect";

function createArrayUpToNumber(number) {
  // Initialize an empty array to store the numbers
  let resultArray = [];

  // Loop from 1 to the given number and push each number to the array
  for (let i = 1; i <= number; i++) {
    resultArray.push(i);
  }

  return resultArray;
}

const ProjectFilterSection = (props) => {
  let selections = ["index", "scores"];

  const hasConfidence =
    props.projectData &&
    props.projectData[0][0].hasOwnProperty(
      `score_confidence_${props.selectedTab}`
    );

  if (hasConfidence) {
    selections.push("confidence");
  }

  const confidences =
    hasConfidence && props.projectData && props.projectData[0]
      ? props.projectData[0].map(
          (item) => item[`score_confidence_${props.selectedTab}`]
        )
      : [];

  const uniqueConfidences = Array.from(
    new Set(confidences.filter((confidence) => confidence !== null))
  );

  const scores =
    props.projectData && props.projectData[0]
      ? props.projectData[0].map((item) => item[`score_${props.selectedTab}`])
      : [];

  const uniqueScores = Array.from(
    new Set(scores.filter((score) => score !== null))
  );
  const indexes = createArrayUpToNumber(
    props.projectData && props.projectData[0].length
  );

  const handleColumnSelect = (title) => {
    props.setProjectFilters((prev) => {
      // Check if index key is present
      if (prev.hasOwnProperty(title)) {
        // If present, remove the index key
        const { [title]: removedKey, ...rest } = prev;
        return rest;
      } else {
        // If not present, add the index key with an empty array
        return {
          ...prev,
          [title]: [],
        };
      }
    });
  };

  const handleIndexSelect = (title) => {
    props.setProjectFilters((prev) => {
      const { index } = prev;
      const updatedIndex = [...index]; // Create a copy of the index array

      const keyIndex = updatedIndex.indexOf(title);

      if (keyIndex !== -1) {
        updatedIndex.splice(keyIndex, 1); // Remove the item from the copied array
      } else {
        updatedIndex.push(title); // Add the item to the copied array
      }

      return {
        ...prev,
        index: updatedIndex, // Set the updated index array in the state
      };
    });
  };

  const handleConfidenceSelect = (title) => {
    props.setProjectFilters((prev) => {
      const { confidence } = prev;
      const updatedConfidence = [...confidence];

      const keyIndex = updatedConfidence.indexOf(title);

      if (keyIndex !== -1) {
        updatedConfidence.splice(keyIndex, 1);
      } else {
        updatedConfidence.push(title);
      }

      return {
        ...prev,
        confidence: updatedConfidence,
      };
    });
  };

  const handleScoreSelect = (title) => {
    props.setProjectFilters((prev) => {
      const { scores } = prev;
      const updatedScores = [...scores]; // Create a copy of the index array

      const keyIndex = updatedScores.indexOf(title);

      if (keyIndex !== -1) {
        updatedScores.splice(keyIndex, 1); // Remove the item from the copied array
      } else {
        updatedScores.push(title); // Add the item to the copied array
      }

      return {
        ...prev,
        scores: updatedScores, // Set the updated index array in the state
      };
    });
  };

  const keysArray = Object.keys(props.projectFilters);
  const selectedIndexes =
    props.projectFilters &&
    (props.projectFilters.hasOwnProperty("index")
      ? indexes.filter((item) => !props.projectFilters["index"].includes(item))
      : indexes);
  const selectedScores =
    props.projectFilters &&
    (props.projectFilters.hasOwnProperty("scores")
      ? uniqueScores.filter(
          (item) => !props.projectFilters["scores"].includes(item)
        )
      : indexes);
  const selectedConfidences =
    props.projectFilters &&
    (props.projectFilters.hasOwnProperty("confidence")
      ? uniqueConfidences.filter(
          (item) => !props.projectFilters["confidence"].includes(item)
        )
      : indexes);

  return (
    <div className="mt-10">
      <h2 className="text-lg font-medium">Project Filters</h2>
      <CustomMultiSelect
        selections={selections}
        selected={keysArray}
        onSelect={handleColumnSelect}
        title="Choose column"
        placeholder={keysArray.length > 0 && `${keysArray.length} selected`}
      />
      {keysArray.includes("index") && (
        <CustomMultiSelect
          selections={indexes}
          selected={selectedIndexes}
          onSelect={handleIndexSelect}
          title="Choose index"
          placeholder={
            selectedIndexes.length > 0 && `${selectedIndexes.length} selected`
          }
        />
      )}
      {keysArray.includes("scores") && (
        <CustomMultiSelect
          selections={uniqueScores}
          selected={selectedScores}
          onSelect={handleScoreSelect}
          title="Choose scores"
          placeholder={
            selectedScores.length > 0 && `${selectedScores.length} selected`
          }
        />
      )}
      {keysArray.includes("confidence") && (
        <CustomMultiSelect
          selections={uniqueConfidences}
          selected={selectedConfidences}
          onSelect={handleConfidenceSelect}
          title="Choose confidence"
          placeholder={
            selectedConfidences.length > 0 &&
            `${selectedConfidences.length} selected`
          }
        />
      )}
    </div>
  );
};

export default ProjectFilterSection;
