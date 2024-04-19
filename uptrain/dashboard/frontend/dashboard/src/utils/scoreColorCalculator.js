export const scoreColorCalculator = (score) => {
  let result;
  if (typeof score === "string") {
    score = parseInt(score);
  }

  switch (true) {
    case score >= 0 && score < 0.1:
      result = "#E30401";
      break;
    case score >= 0.1 && score < 0.2:
      result = "#E93107";
      break;
    case score >= 0.2 && score < 0.3:
      result = "#EE5F0D";
      break;
    case score >= 0.3 && score < 0.4:
      result = "#F38D13";
      break;
    case score >= 0.4 && score < 0.5:
      result = "#F9BC19";
      break;
    case score >= 0.5 && score < 0.6:
      result = "#FEEC1F";
      break;
    case score >= 0.6 && score < 0.7:
      result = "#CEE919";
      break;
    case score >= 0.7 && score < 0.8:
      result = "#9DE313";
      break;
      8;
    case score >= 0.8 && score < 0.9:
      result = "#6BDD0D";
      break;
    case score >= 0.8 && score < 0.9:
      result = "#39D807";
      break;
    default:
      result = "#05D201";
  }

  return result;
};
