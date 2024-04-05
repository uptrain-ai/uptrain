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
        display: true,
        postion: "top",
      },
      title: {
        display: false,
      },
    },
    scales: {
      x: {
        title: {
          display: true,
          text: props.selectedTab,
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
          font: {
            size: 16,
          },
          color: "#B9BDCE",
        },
      },
    },
  };

  const scores0 =
    props.data[props.selectedTab][0][`score_${props.selectedTab}`];
  const scores1 =
    props.data[props.selectedTab][1][`score_${props.selectedTab}`];

  const scorescountMap0 = {};
  const scorescountMap1 = {};

  scores0.forEach((value) => {
    if (scorescountMap0[value]) {
      scorescountMap0[value]++;
    } else {
      scorescountMap0[value] = 1;
    }
  });

  scores1.forEach((value) => {
    if (scorescountMap1[value]) {
      scorescountMap1[value]++;
    } else {
      scorescountMap1[value] = 1;
    }
  });

  const uniqueKeys = new Set();

  // Add keys from scorescountMap0 to the set
  scores0.forEach((key) => uniqueKeys.add(key));

  // Add keys from scorescountMap1 to the set
  scores1.forEach((key) => uniqueKeys.add(key));

  const labelsUntruncated = Array.from(uniqueKeys).sort((a, b) => a - b);

  const labels = labelsUntruncated.map((item) => Math.trunc(item * 100) / 100);

  const data = {
    labels,
    datasets: [
      {
        maxBarThickness: 24,
        label: props.data[props.selectedTab][0][props.chartKey],
        borderRadius: 5,
        data: labelsUntruncated.map((item) => scorescountMap0[item]),
        backgroundColor: "#5587FD",
        categoryPercentage: 0.4,
      },
      {
        maxBarThickness: 24,
        label: props.data[props.selectedTab][1][props.chartKey],
        borderRadius: 5,
        data: labelsUntruncated.map((item) => scorescountMap1[item]),
        backgroundColor: "#ABC4FF",
        categoryPercentage: 0.4,
      },
    ],
  };

  return <Bar options={options} data={data} />;
};

export default BarChart;
