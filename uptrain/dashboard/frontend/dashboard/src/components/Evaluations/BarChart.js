import React from "react";
import {
  Chart as ChartJS,
  CategoryScale,
  LinearScale,
  BarElement,
  Title,
  Tooltip,
  Legend,
} from "chart.js";
import { Bar } from "react-chartjs-2";

ChartJS.register(
  CategoryScale,
  LinearScale,
  BarElement,
  Title,
  Tooltip,
  Legend
);

const BarChart = (props) => {
  const options = {
    responsive: true,
    plugins: {
      legend: {
        display: false,
      },
      title: {
        display: false,
      },
    },
    scales: {
      x: {
        title: {
          display: true,
          text: `score_${props.selectedTab}`,
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
        title: {
          display: true,
          text: "Count",
          font: {
            size: 20,
            color: "#4E4E58",
          },
        },
        ticks: {
          precision: 0,
          font: {
            size: 16,
          },
          color: "#B9BDCE",
        },
      },
    },
    categoryPercentage: 0.5,
  };

  const scores = props.projectData[0]
    ? props.projectData[0].map(
        (item) => item.checks[`score_${props.selectedTab}`]
      )
    : [];

  const scorescountMap = {};

  scores.forEach((value) => {
    if (scorescountMap[value]) {
      scorescountMap[value]++;
    } else {
      scorescountMap[value] = 1;
    }
  });

  const labels = Object.keys(scorescountMap).sort((a, b) => a - b);

  const data = {
    labels,
    datasets: [
      {
        label: "Count",
        borderRadius: 5,
        data: labels.map((item) => scorescountMap[item]),
        backgroundColor: "#5587FD",
      },
    ],
  };

  return <Bar options={options} data={data} />;
};

export default BarChart;
