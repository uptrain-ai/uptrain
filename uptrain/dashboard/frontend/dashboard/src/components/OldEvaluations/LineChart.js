import React from "react";
import {
  Chart as ChartJS,
  LinearScale,
  CategoryScale,
  BarElement,
  PointElement,
  LineElement,
  Legend,
  Tooltip,
  LineController,
  BarController,
} from "chart.js";
import { Chart } from "react-chartjs-2";

ChartJS.register(
  LinearScale,
  CategoryScale,
  BarElement,
  PointElement,
  LineElement,
  Legend,
  Tooltip,
  LineController,
  BarController
);

const LineChart = (props) => {
  let run_for = [];
  let score = [];
  let count = [];

  // Iterate through the data array and push values to respective arrays
  props.projectData[4] &&
    props.projectData[4].forEach((obj) => {
      run_for.push(obj.run_for);
      score.push(obj[`score_${props.selectedTab}`]);
      count.push(obj.count);
    });

  const labels = run_for;

  const data = {
    labels,
    datasets: [
      {
        type: "line",
        label: "Score",
        borderColor: "#5587FD",
        backgroundColor: "#5587FD",
        borderWidth: 4,
        fill: false,
        data: score,
        yAxisID: "y",
      },
      {
        type: "bar",
        label: "Evaluations",
        backgroundColor: "#192C59",
        borderColor: "#192C59",
        data: count,
        borderWidth: 4,
        yAxisID: "y1",
      },
    ],
  };

  const options = {
    radius: 0,
    responsive: true,
    plugins: {
      title: {
        display: true,
      },
    },
    scales: {
      x: {
        title: {
          display: true,
          text: "Date",
          font: {
            size: 20,
            color: "#4E4E58",
          },
        },
        ticks: {
          color: "#B9BDCE",
          font: {
            size: 14,
          },
        },
      },
      y: {
        position: "left",
        title: {
          display: true,
          text: "Score",
          font: {
            size: 20,
            color: "#4E4E58",
          },
        },
        min: 0,
        max: 1,
        ticks: {
          // forces step size to be 20 units
          stepSize: 0.5,
          font: {
            size: 16,
          },
          color: "#B9BDCE",
        },
      },
      y1: {
        position: "right",
        title: {
          display: true,
          text: "Evaluations",
          font: {
            size: 20,
            color: "#4E4E58",
          },
        },
        ticks: {
          // forces step size to be 20 units
          stepSize: 100,
          font: {
            size: 16,
          },
          color: "#B9BDCE",
        },
      },
    },
  };

  return <Chart options={options} type="bar" data={data} />;
};

export default LineChart;